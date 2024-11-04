using KomaNYU
using NIfTI
using NPZ
using JSON
using NPZ
using Printf

direction = "coronal"

# B0, T1,T2, T2s, Δw, ρ,FOVx,FOVy,Δx, seq, directory, slicen, Sensitivities_directory, GPU, NT, 
function read_nifti_slice(model, ind::Integer)
    slice=niread(model)
    selectdim(slice,3,ind)
end
function upsample(x::AbstractArray{T,N},ratio::NTuple{M,Int}=ntuple(Returns(1),M)) where {T,N,M}
    M ≤ N || throw(DomainError((M,N),"M must be ≤ N"))
    return repeat(x;inner=(ratio...,ntuple(Returns(1),N-M)...))
end

function ensure_file_or_dir(file::String)
    (isfile(file) || isdir(file)) && return file
    @printf(stderr,"\"%s\" does not exist.",file)
    exit(1)
end

if length(ARGS) < 11
    @printf(stderr,"This script requires at least 11 inputs\nUsage: julia simulator.jl B0 T1 T2 T2s Δw ρ desired_res[1] desired_res[2] seq directory slice [sensitivities_directory] [GPU]")
    exit(1)
end

GPU = length(ARGS) > 12 && parse(Bool, lowercase(ARGS[13]))
inputs = (;
    B0 = parse(Float64,ARGS[1]),
    T1 = ensure_file_or_dir(ARGS[2]),
    T2 = ensure_file_or_dir(ARGS[3]),
    T2s = ensure_file_or_dir(ARGS[4]),
    Δw = ensure_file_or_dir(ARGS[5]),
    ρ = ensure_file_or_dir(ARGS[6]),
    desired_resolution = parse.(Float64,(ARGS[7],ARGS[8])),
    seq = ensure_file_or_dir(ARGS[9]),
    directory = ARGS[10],
    slice = parse(Int,ARGS[11]),
    B1m = length(ARGS) > 11 ? ensure_file_or_dir(ARGS[12]) : nothing,
    GPU = GPU
)

nifti_ρ = niread(inputs.ρ)
(M,N,_) = size(nifti_ρ)
original_resolution = Tuple(nifti_ρ.header.pixdim[2:3]).*1e-3
any(≤(0),original_resolution) && error("resolution must be positive")
ratio = ceil.(Int,original_resolution./inputs.desired_resolution)
resolution = original_resolution./ratio

res_str = res->"$(res[1]*1e3) mm × $(res[2]*1e3) mm"
@info """
Resolution
    Original: $(res_str(original_resolution))
     Desired: $(res_str(inputs.desired_resolution))
      Actual: $(res_str(resolution))
       Ratio: $(ratio[1]) × $(ratio[2])
"""

data = (;
    ρ = selectdim(nifti_ρ,3,inputs.slice),
    T1 = 1e-3.*read_nifti_slice(inputs.T1, inputs.slice),
    T2 = 1e-3.*read_nifti_slice(inputs.T2, inputs.slice),
    T2s = 1e-3.*read_nifti_slice(inputs.T2s, inputs.slice),
    Δw = read_nifti_slice(inputs.Δw, inputs.slice),
    B1m = isnothing(inputs.B1m) ? ones(ComplexF64,M,N,1) : cat((read_nifti_slice(joinpath(inputs.B1m,file),inputs.slice) for file in readdir(inputs.B1m))...;dims=3)
)

data = (;((k,upsample(v,ratio)) for (k,v) in pairs(data))...)

M, N = size(data.ρ)

# Define the phantom
ρmask = map(!iszero,data.ρ)
B1mmat = reshape(data.B1m,length(data.ρ),:)

if lowercase(direction) == "axial"
    x = range(start=-(M-1)//2,stop=(M-1)//2,length=M).*resolution[1]
    y = range(start=-(N-1)//2,stop=(N-1)//2,length=N).*resolution[2]
    x = reshape(repeat(x,outer=N),M,N)
    y = reshape(repeat(y,inner=M),M,N)
    zG=zeros(eltype(x),count(ρmask))
    xG= x[ρmask]
    yG= y[ρmask]

elseif lowercase(direction) == "saggital"
    z=range(start=-(N-1)//2,stop=(N-1)//2,length=N).*resolution[2]
    y = range(start=-(M-1)//2,stop=(M-1)//2,length=M).*resolution[1]
    z = reshape(repeat(z,outer=M),N,M)'
    y = reshape(repeat(y,inner=N),N,M)'
    
    zG=z[ρmask]
    yG=y[ρmask]
    xG = zeros(eltype(z),count(ρmask))
elseif lowercase(direction) == "coronal"
    z = range(start=-(M-1)//2,stop=(M-1)//2,length=M).*resolution[1]
    x = range(start=-(N-1)//2,stop=(N-1)//2,length=N).*resolution[2]
    z = reshape(repeat(z,outer=N),M,N)
    x = reshape(repeat(x,inner=M),M,N)
    zG=z[ρmask]
    xG=x[ρmask]
    yG = ones(eltype(zG),count(ρmask))
else
    error("Invalid direction: $direction")
end



obj = Phantom{Float64}(
    name = "duke_2d",
	x = xG,
	y = yG,
	z = zG,
	ρ = data.ρ[ρmask],
	T1 = data.T1[ρmask],
	T2 = data.T2[ρmask],
	T2s = data.T2s[ρmask],
	Δw = data.Δw[ρmask],
    Bm = B1mmat[view(ρmask,:),:]
)

seq = read_seq(inputs.seq)
sim_params = KomaNYUCore.default_sim_params()
sim_params["gpu"] = inputs.GPU
sim_params["Nthreads"] = Threads.nthreads()
sys = Scanner(B0=inputs.B0)

println("Generating k-space with")
@printf("     phantom: %s\n",string(obj.name))
@printf("    sequence: %s\n",string(seq))
@printf("     scanner: %s\n",string(sys))
signal = simulate(obj, seq, sys; sim_params)

Np = length(signal.profiles)
Nf = size(signal.profiles[1].data,1)
Nrx = size(obj.Bm,2)

kspacelengths = map(length∘Base.Fix2(getfield,:data),signal.profiles)
@info "Generated k-space with\n"*
@sprintf("    %d trajectories\n",Np)*
if allequal(kspacelengths)
    @sprintf("    %d samples per trajectory\n",first(kspacelengths))
else
    @sprintf("    %d-%d samples per trajectory\n",extrema(kspacelengths)...)
end*
@sprintf("    %d receive coils\n",Nrx)

K=zeros(ComplexF32,Np,Nf,Nrx)
for i=1:Np
    K[i,:,:] .= signal.profiles[i].data
end

!isdir(inputs.directory) && mkpath(inputs.directory)
filename = joinpath(inputs.directory,"k.npz")
npzwrite(filename, K)
prop=Dict("B0"=>inputs.B0, "T1"=>inputs.T1, "T2"=>inputs.T2, "T2s"=>inputs.T2s, "Δw"=>inputs.Δw, "ρ"=>inputs.ρ, "res"=>resolution)
D=merge(prop,Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"_slice"=>inputs.slice, "sequence"=>inputs.seq))

jsonfilename = joinpath(inputs.directory,"info.json")
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end
