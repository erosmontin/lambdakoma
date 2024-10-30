using KomaMRI
using NIfTI
using NPZ
using JSON
using NPZ

# myscript.jl
B0=7.0
slicen=30

t1="/tmp/287c2766-a4a4-4d95-90e2-5d078f52da4e/data/t1.nii.gz"
t2="/tmp/287c2766-a4a4-4d95-90e2-5d078f52da4e/data/t2.nii.gz"
rho="/tmp/287c2766-a4a4-4d95-90e2-5d078f52da4e/data/rhoh.nii.gz"

T1 = niread(t1);
T1 = T1.raw[:, :, slicen];


T2 = niread(t2);
T2 = T2.raw[:, :, slicen];


voxelSize =5

# Plot selected slice
# plot_image(slice)

# Define spin position arrays
Δx = 1e-3 * voxelSize;              # Voxel size
M, N = size(T1);          # Number of spins in x and y
FOVx = (M-1)*Δx;             # Field of view in x
FOVy = (N-1)*Δx;             # Field of view in y
x = -FOVx/2:Δx:FOVx/2;       # x spin coordinates vector
y = -FOVy/2:Δx:FOVy/2;       # y spin coordinates vector
x, y = x .+ y'*0, x*0 .+ y'; # x and y grid points

ρ =  niread(rho);

ρ = ρ.raw[:, :, slicen];

Δw = zeros(size(T1)[1], size(T1)[2]);
T2s = zeros(size(T1)[1], size(T1)[2]);
T1 = T1*1e-3;
T2 = T2*1e-3;
T2s = T2s*1e-3;

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
seq = read_seq("/data/PROJECTS/Architecture/lambdaKoma/pipeline/sdl_miniflash.seq"); # Pulseq file

println("Sequence read")
sim_params = KomaMRICore.default_sim_params();

if !GPU
    sim_params["gpu"] = false
    sim_params["Nthreads"] = NT
 
end
println("Simulation parameters set")
sys = Scanner(B0=B0);
println("Scanner created")
raw = simulate(obj, seq, sys; sim_params);
println("Simulation done")

Np =size(raw.profiles)[1]
Nf= size(raw.profiles[1].data)[1]

K=zeros(ComplexF32,Np,Nf)
for i in range(1,Np)
    K[i,:]=raw.profiles[i].data
end

if !isdir(directory)
    mkpath(directory)
end

filename = "/g/k.npz"

npzwrite(filename, K)
D=Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"slice"=>slice, "sequence"=>seq, "model"=>model, "properties"=>prop
)

jsonfilename = directory * "/info.json"
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end


