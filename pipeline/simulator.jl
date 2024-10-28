using KomaNYU
using NIfTI
using NPZ
using JSON
using NPZ

# B0, T1,T2, T2s, Δw, ρ,FOVx,FOVy,Δx, seq, directory, slicen, Sensitivities_directory, GPU, NT, 
function read_nifti_slice(model, slicen)
    # For NIfTI files
    structure = niread(model)
    # voxelSize = [structure.header.pixdim[i] for i = 2:min(structure.header.dim[1], 3)+1][1]
    _slice = structure.raw[:, :, slicen]
    return _slice
end

B0= parse(Float64,ARGS[1])
_T1 = ARGS[2]
_T2 = ARGS[3]
_T2s = ARGS[4]
_Δw = ARGS[5]
_ρ = ARGS[6]
FOVx = parse(Float64,ARGS[7])
FOVy = parse(Float64,ARGS[8])
Δx = parse(Float64,ARGS[9])
seq = ARGS[10]
directory = ARGS[11]
slicen = parse(Int,ARGS[12])
if length(ARGS) < 12
    println("Error: This script requires at least 3 arguments.")
    println("Usage: julia simulator.jl B0(T) T1(ms) T2(ms) T2s(ms) Δw(rad*s) ρ FOVx(m) FOVy(m) Δx(m) seq directory slicen [Sensitivities_directory] [GPU] [NT]")
    exit(1)
end

Sensitivities_directory = nothing

if length(ARGS) > 12
    println("Sensitivities Directory: ", ARGS[13])
    if !isnothing(ARGS[13]) && isdir(ARGS[13])
        Sensitivities_directory = ARGS[13]
    end
end

GPU = false

if length(ARGS) > 13
    GPU = parse(Bool, lowercase(ARGS[14]))
end

NT=1
if !GPU
    println("Running on CPU")
    if length(ARGS) > 14
        NT=parse(Int,ARGS[15])
    end
end




println("B0: ", B0)
println("T1: ", _T1)
println("T2: ", _T2)
println("T2s: ", _T2s)

println("Δw: ", _Δw)
println("ρ: ", _ρ)
println("FOVx: ", FOVx)
println("FOVy: ", FOVy)
println("Δx: ", Δx)
println("Sequence: ", seq)
println("Directory: ", directory)
println("Slice: ", slicen)
println("Sensitivities Directory: ", Sensitivities_directory)
println("GPU: ", GPU)
println("Number of Threads: ", NT)

if !isfile(_T1)
    println("Model File ", T1, " does not exist.")
    exit(1)
end

if !isfile(_T2)
    println("Model File ", T2, " does not exist.")
    exit(1)
end

if !isfile(_T2s)
    println("Model File ", T2s, " does not exist.")
    exit(1)
end

if !isfile(_Δw)
    println("Model File ", Δw, " does not exist.")
    exit(1)
end

if !isfile(_ρ)
    println("Model File ", ρ, " does not exist.")
    exit(1)
end



if !isfile(seq)
    println("Sequence File ", seq, " does not exist.")
    exit(1)
end




ρ = read_nifti_slice(_ρ, slicen)
T1 = read_nifti_slice(_T1, slicen)
T2 = read_nifti_slice(_T2, slicen)
T2s = read_nifti_slice(_T2s, slicen)
Δw = read_nifti_slice(_Δw, slicen)
T1 = T1*1e-3; #(s)
T2 = T2*1e-3; #(s)
T2s = T2s*1e-3;#(s)


sensitivities = nothing
if !isnothing(Sensitivities_directory)
    if !isdir(Sensitivities_directory)
        println("Sensitivities Directory ", Sensitivities_directory, " does not exist.")
        exit(1)
    else
        files = readdir(Sensitivities_directory)
        slices = []
        for file in files
            O=joinpath(Sensitivities_directory, file)
            
            _slice_ = read_nifti_slice(O, slicen)
            push!(slices, _slice_)
        end
        sensitivities = cat(dims=4, slices...)
    end
end


M, N = size(ρ);          # Number of spins in x and y

             # Field of view in y
x = range(start=-(M-1)//2,stop=(M-1)//2,length=M).*Δx; # x grid points
y = range(start=-(N-1)//2,stop=(N-1)//2,length=N).*Δx; # y grid points
x, y = x .+ y'*0, x*0 .+ y'; # x and y grid points

prop=Dict("B0"=>B0, "T1"=>_T1, "T2"=>_T2, "T2s"=>_T2s, "Δw"=>_Δw, "ρ"=>_ρ, "FOVx"=>FOVx, "FOVy"=>FOVy, "Δx"=>Δx)

println(size(T1))
@show size(T2)
@show size(T2s)
@show size(Δw)
@show size(ρ)
@show size(x)
@show size(y)
# Define the phantom
obj = Phantom{Float64}(
    name = "duke_2d",
	x = x[ρ.!=0],
	y = y[ρ.!=0],
	z = 0*x[ρ.!=0],
	ρ = ρ[ρ.!=0],
	T1 = T1[ρ.!=0],
	T2 = T2[ρ.!=0],
	T2s = T2s[ρ.!=0],
	Δw = Δw[ρ.!=0],
);




println("Phantom created")
# Simulate phantom
seq = read_seq(seq); # Pulseq file

println("Sequence read")
sim_params = KomaNYUCore.default_sim_params();

if !GPU
    sim_params["gpu"] = false
    sim_params["Nthreads"] = NT
 
end
println("Simulation parameters set")
sys = Scanner(B0=B0);
println("Scanner created")
raw = simulate(obj, seq, sys; sim_params);
display(size(raw.profiles[1].data))
println("Simulation done")
if !isnothing(sensitivities)
	profile0 = raw.profiles[1]
	resize!(raw.profiles,size(sensitivities,4))
	for k=1:size(sensitivities,4)
		raw.profiles[k] = Profile(profile0.head,profile0.traj,profile0.data.*view(sensitivities,:,:,:,k))
	end
end
Np = length(raw.profiles)
Nf= size(raw.profiles[1].data,1)

@show raw.profiles
@show raw.profiles[1]
@show raw.profiles[1].data

K=zeros(ComplexF32,Np,Nf)
for i in range(1,Np)
    K[i,:]=raw.profiles[i].data
end

if !isdir(directory)
    mkpath(directory)
end

filename = directory * "/k.npz"

npzwrite(filename, K)

D=merge(prop,Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"_slice"=>slicen, "sequence"=>seq));

jsonfilename = directory * "/info.json"
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end


