koma_test.jl is the test, it is importing my sdl_pypulseq.seq spin echo sequence, simulating it, and outputting the raw data in mat format. 

You will need to change the paths to make them match your configuration:
- Line 5: where you put the .seq file
- Line 60: where you output the .mat file

The function to output in mat format comes from Koma (https://github.com/JuliaHealth/KomaMRI.jl/blob/27ae34f7ce13768864b0c05920c138743e740e3a/src/ui/ExportMATFunctions.jl) in case you want to export anything else
