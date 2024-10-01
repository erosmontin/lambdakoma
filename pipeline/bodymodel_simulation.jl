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
slicen = parse(Int,ARGS[6])
if length(ARGS) < 4
    println("Error: This script requires at least 3 arguments.")
    println("Usage: julia bodymodel_simulation.jl <T> <model> <tissue_properties> <sequence> <saving_directory> <_slice>")
    exit(1)
end
Sensitivities_directory = nothing

if length(ARGS) > 6
    if !isnothing(ARGS[7])
        Sensitivities_directory = ARGS[7]
    end
end


println("Model: ", model)
println("Tissue Properties: ", prop)
println("Sequence: ", seq)
println("Output Directory: ", directory)
println("Slice: ", slicen)
println("B0: ", B0)
println("Sensitivities Directory: ", B0)

GPU = false
println(length(ARGS))

if length(ARGS) > 7
    GPU = parse(Bool, lowercase(ARGS[8]))
end

NT=1
if !GPU
    println("Running on CPU")
    if length(ARGS) > 8
        NT=parse(Int,ARGS[9])
    end

end
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
_slice = structure.raw[:, :, slicen];


if isnothing(Sensitivities_directory)
    if !isdir(Sensitivities_directory)
        println("Sensitivities Directory ", Sensitivities_directory, " does not exist.")
        exit(1)
    else
        files = readdir(Sensitivities_directory)
        slices = []
        for file in files
            O=joinpath(Sensitivities_directory, file)
            println(O)
            _structure_ = niread(O)
            _slice_ = _structure_.raw[:, :, slicen]
            # Append the _slice to the slices array
            push!(slices, _slice_)
        end
        # Concatenate the slices along the 4th dimension to create a 4D array
        sensitivities = cat(dims=4, slices...)
    end
    end




# Plot selected _slice
# plot_image(_slice)

# Define spin position arrays
Δx = 1e-3 * voxelSize;              # Voxel size
M, N = size(_slice);          # Number of spins in x and y
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
ρ = zeros(size(_slice)[1], size(_slice)[2]);
T1 = zeros(size(_slice)[1], size(_slice)[2]);
T2 = zeros(size(_slice)[1], size(_slice)[2]);
T2s = zeros(size(_slice)[1], size(_slice)[2]);
Δw = zeros(size(_slice)[1], size(_slice)[2]);
for index in range(1, length(propertyLine))
    mask = _slice .== parse(Int, propertyLine[index][1])
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

filename = directory * "/k.npz"

npzwrite(filename, K)
D=Dict("version"=> "v0.0v", "KS"=>filename, "origin"=>[0,0,0], "spacing"=>[1,1,1], "direction"=>[1,0,0,0,1,0,0,0,1],"_slice"=>slicen, "sequence"=>seq, "model"=>model, "properties"=>prop
)

jsonfilename = directory * "/info.json"
json_data = JSON.json(D)
open(jsonfilename, "w") do io
    write(io, json_data)
end


