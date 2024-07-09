using KomaMRI
using NIfTI
using NPZ
using JSON
using NPZ

# myscript.jl
B0= parse(Float64,ARGS[1])
model = ARGS[2]
prop = ARGS[3]
seq = ARGS[4]
directory = ARGS[5]
slice = parse(Int,ARGS[6])

if length(ARGS) < 4
    println("Error: This script requires at least 3 arguments.")
    println("Usage: julia bodymodel_simulation.jl <T> <model> <tissue_properties> <sequence> <saving_directory> <slice>")
    exit(1)
end
println("Model: ", model)
println("Tissue Properties: ", prop)
println("Sequence: ", seq)
println("Output Directory: ", directory)
println("Slice: ", slice)


if !isfile(model)
    println("Model File ", model, " does not exist.")
    exit(1)
end

if !isfile(prop)
    println("Tissue Properties File ", prop, " does not exist.")
    exit(1)
end

if !isfile(seq)
    println("Sequence File ", seq, " does not exist.")
    exit(1)
end


# For NIfTI files
structure = niread(model);
voxelSize = [structure.header.pixdim[i] for i = 2:min(structure.header.dim[1], 3)+1][1];
slice = structure.raw[:, :, slice];

# Plot selected slice
# plot_image(slice)

# Define spin position arrays
Δx = 1e-3 * voxelSize;              # Voxel size
M, N = size(slice);          # Number of spins in x and y
FOVx = (M-1)*Δx;             # Field of view in x
FOVy = (N-1)*Δx;             # Field of view in y
x = -FOVx/2:Δx:FOVx/2;       # x spin coordinates vector
y = -FOVy/2:Δx:FOVy/2;       # y spin coordinates vector
x, y = x .+ y'*0, x*0 .+ y'; # x and y grid points

# Read properties file

propertiesFile = open(prop, "r");
propertiesArray = readlines(propertiesFile);
property_value = zeros(0);
propertyLine = [];
extractedProperties = [];
for index in range(2, length(propertiesArray))
    append!(propertyLine, [split(propertiesArray[index], " ")]);
end
close(propertiesFile);

# value = parse(Float64, value)

# Define proton density, T1, T2, T2s, chemical shift arrays
ρ = zeros(size(slice)[1], size(slice)[2]);
T1 = zeros(size(slice)[1], size(slice)[2]);
T2 = zeros(size(slice)[1], size(slice)[2]);
T2s = zeros(size(slice)[1], size(slice)[2]);
Δw = zeros(size(slice)[1], size(slice)[2]);
for index in range(1, length(propertyLine))
    mask = slice .== parse(Int, propertyLine[index][1])
    ρ[mask] .= parse(Float64, propertyLine[index][4])
    T1[mask] .= parse(Float64, propertyLine[index][2])
    T2[mask] .= parse(Float64, propertyLine[index][3])
    Δw[mask] .= parse(Float64, propertyLine[index][5])
    
end
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
seq = read_seq(seq); # Pulseq file
println("Sequence read")
sim_params = KomaMRICore.default_sim_params();
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

filename = directory * "/k.npz"

npzwrite(filename, K)
D=Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"slice"=>slice, "sequence"=>seq, "model"=>model, "properties"=>prop
)

jsonfilename = directory * "/info.json"
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end


