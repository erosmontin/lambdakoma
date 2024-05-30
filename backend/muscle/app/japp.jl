# Define simulation parameters and perform simulation


#print all the directories in the current LOAD_PATH
# push!(LOAD_PATH, pwd())
using KomaMRI
using FileIO, JLD2


sim_params = KomaMRICore.default_sim_params()
raw = simulate(brain_phantom2D(), PulseDesigner.EPI_example(), Scanner(); sim_params)

# Save the raw data to a file
FileIO.save("/tmp/raw.jld2", "raw", raw)
println("Raw data saved to /tmp/raw.jld2")




