using KomaNYU
using NIfTI
using NPZ
using JSON
using NPZ
using Printf

# B0, T1,T2, T2s, Δw, ρ,FOVx,FOVy,Δx, seq, directory, slicen, Sensitivities_directory, GPU, NT, 
function read_nifti_slice(model, ind::Integer)
    slice=niread(model)
    selectdim(slice,3,ind)
end

function ensure_file_or_dir(file::String)
    (isfile(file) || isdir(file)) && return file
    @printf(stderr,"\"%s\" does not exist.",file)
    exit(1)
end

if length(ARGS) < 12
    @printf(stderr,"This script requires at least 12 inputs\nUsage: julia simulator.jl B0(T) T1(ms) T2(ms) T2s(ms) Δw(rad*s) ρ FOVx(m) FOVy(m) Δx(m) seq directory slicen [Sensitivities_directory] [GPU] [NT]")
    exit(1)
end

GPU = length(ARGS) > 13 && parse(Bool, lowercase(ARGS[14]))
inputs = (;
    B0 = parse(Float64,ARGS[1]),
    T1 = ensure_file_or_dir(ARGS[2]),
    T2 = ensure_file_or_dir(ARGS[3]),
    T2s = ensure_file_or_dir(ARGS[4]),
    Δw = ensure_file_or_dir(ARGS[5]),
    ρ = ensure_file_or_dir(ARGS[6]),
    FOVx = parse(Float64,ARGS[7]),
    FOVy = parse(Float64,ARGS[8]),
    Δx = parse(Float64,ARGS[9]),
    seq = ensure_file_or_dir(ARGS[10]),
    directory = ARGS[11],
    slice = parse(Int,ARGS[12]),
    B1m = length(ARGS) > 12 ? ensure_file_or_dir(ARGS[13]) : nothing,
    GPU = GPU,
    NT = !GPU && length(ARGS) > 14 ? parse(Int,ARGS[15]) : 1
)

println("*** inputs to script ***")
for (k,v) in pairs(inputs)
    println(string(k)*": "*string(v))
end

data = (;
    ρ = read_nifti_slice(inputs.ρ, inputs.slice),
    T1 = 1e-3.*read_nifti_slice(inputs.T1, inputs.slice),
    T2 = 1e-3.*read_nifti_slice(inputs.T2, inputs.slice),
    T2s = 1e-3.*read_nifti_slice(inputs.T2s, inputs.slice),
    Δw = read_nifti_slice(inputs.Δw, inputs.slice),
    B1m = isnothing(inputs.B1m) ? ones(ComplexF64,size(ρ)...,1) : cat((read_nifti_slice(joinpath(inputs.B1m,file),inputs.slice) for file in readdir(inputs.B1m))...;dims=3)
)

M, N = size(data.ρ)
x = range(start=-(M-1)//2,stop=(M-1)//2,length=M).*inputs.Δx; # x grid points
y = range(start=-(N-1)//2,stop=(N-1)//2,length=N).*inputs.Δx; # y grid points
x, y = x .+ y'*0, x*0 .+ y'; # x and y grid points

# Define the phantom
ρmask = map(!iszero,data.ρ)
@show all(iszero,niread(inputs.ρ))
@show count(ρmask)
B1mmat = reshape(data.B1m,length(data.ρ),:)
obj = Phantom{Float64}(
    name = "duke_2d",
	x = x[ρmask],
	y = y[ρmask],
	z = zeros(eltype(x),count(ρmask)),
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
sim_params["Nthreads"] = inputs.NT
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
println("Generated k-space with")
@printf("    %d trajectories\n",Np)
if allequal(kspacelengths)
    @printf("    %d samples per trajectory\n",first(kspacelengths))
else
    @printf("    %d-%d samples per trajectory\n",extrema(kspacelengths)...)
end
@printf("    %d receive coils\n",Nrx)

K=zeros(ComplexF32,Np,Nf,Nrx)
for i=1:Np
    K[i,:,:] .= raw.profiles[i].data
end

if !isdir(directory)
    mkpath(directory)
end

filename = joinpath(inputs.directory,"k.npz")
npzwrite(filename, K)
prop=Dict("B0"=>inputs.B0, "T1"=>inputs.T1, "T2"=>inputs.T2, "T2s"=>inputs.T2s, "Δw"=>inputs.Δw, "ρ"=>inputs.ρ, "FOVx"=>inputs.FOVx, "FOVy"=>inputs.FOVy, "Δx"=>inputs.Δx)
D=merge(prop,Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"_slice"=>slicen, "sequence"=>seq));

jsonfilename = joinpath(inputs.directory,"info.json")
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end


