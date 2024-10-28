using KomaNYU
using NIfTI
using NPZ
using JSON
using NPZ
using Printf

if length(ARGS) < 4
    println(stderr,"Error: This script requires at least 3 arguments.")
    println(stderr,"Usage: julia bodymodel_simulation.jl <B0> <model> <tissue_properties> <sequence> <saving_directory> <slice_index> <sensitivities_dir>")
    exit(1)
end

B0    = parse(Float64,ARGS[1])
model = ARGS[2]
prop  = ARGS[3]
seq   = ARGS[4]
directory = ARGS[5]
sliceind = parse(Int,ARGS[6])
b1m_dir = length(ARGS) > 6 ? ARGS[7] : ""
GPU = length(ARGS) > 7 && parse(Bool, lowercase(ARGS[8]))
NT = Threads.nthreads()

println("B0: ", B0)
println("Model: ", model)
println("Tissue Prop.: ", prop)
println("Sequence: ", seq)
println("Output Dir.: ", directory)
println("Slice: ", sliceind)
println("Sensitivities Dir.: ", isempty(b1m_dir) ? "not supplied" : b1m_dir)
@printf("Running on %s with %d CPU threads\n",GPU ? "GPU" : "CPU",NT)

if !isempty(b1m_dir) && !isdir(b1m_dir)
    @printf(stderr,"Error: Coil sensitivities directory \"%s\" does not exist\n",b1m_dir)
    exit(1)
end
if !isfile(prop)
    @printf(stderr,"Error: Tissue properties file %s does not exist.\n",prop)
    exit(1)
end
if !isfile(seq)
    @printf(stderr,"Error: Sequence file %s does not exist.\n",seq)
    exit(1)
end

# For NIfTI files
structure = niread(model)
if length(structure.header.pixdim) < 2
    @printf(stderr,"Error parsing model file:\nmodel.header.pixdim should have at least 2 entries.\n")
end
voxelSize = structure.header.pixdim[2]
_slice = structure.raw[:, :, sliceind]

sensitivities = ones(ComplexF64,size(_slice)...,1)
if !isempty(b1m_dir)
    files = joinpath.(Ref(b1m_dir),readdir(b1m_dir))
    foreach(println,files)
    slices = [niread(file).raw[:,:,sliceind] for file in files]
    # Concatenate the slices along the 4th dimension to create a 4D array
    sensitivities = cat(dims=4, slices...)
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
propertiesFile = open(prop, "r")
propertiesArray = readlines(propertiesFile)
property_value = zeros(0)
propertyLine = []
extractedProperties = []
for index in range(2, length(propertiesArray))
    append!(propertyLine, [split(propertiesArray[index], " ")])
end
close(propertiesFile)

# Define proton density, T1, T2, T2s, chemical shift arrays
ρ   = zeros(M,N)
T1  = zeros(M,N)
T2  = zeros(M,N)
T2s = zeros(M,N)
Δw  = zeros(M,N)
for index in range(1, length(propertyLine))
    mask = _slice .== parse(Int, propertyLine[index][1])
    ρ[mask] .= parse(Float64, propertyLine[index][4])
    T1[mask] .= parse(Float64, propertyLine[index][2])
    T2[mask] .= parse(Float64, propertyLine[index][3])
    Δw[mask] .= parse(Float64, propertyLine[index][5])
end
T1 = T1*1e-3
T2 = T2*1e-3
T2s = T2s*1e-3

# Define the phantom
ρmask = map(!iszero,ρ)
sensmat = reshape(sensitivities,length(ρ),:)
obj = Phantom{Float64}(
    name = "duke_2d",
	x = x[ρmask],
	y = y[ρmask],
    z = zeros(eltype(x),count(ρmask)),
	ρ = ρ[ρmask],
	T1 = T1[ρmask],
	T2 = T2[ρmask],
	T2s = T2s[ρmask],
	Δw = Δw[ρmask],
    Bm = sensmat[view(ρmask,:),:]
)

# Simulate phantom
seq = read_seq(seq) # Pulseq file
sim_params = KomaNYUCore.default_sim_params()
sim_params["gpu"] = GPU
sim_params["Nthreads"] = NT
sys = Scanner(B0=B0)

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

# save using ISMRMRD h5 file specification
#raw_data = signal_to_raw_data(signal, seq; phantom_name=obj.name, sys=sys, sim_params=sim_params)
raw_data_file = ISMRMRDFile(joinpath(directory,"kspace.h5"))
println("Saving raw simulation data to $(raw_data_file)")
save(raw_data_file,signal)
