JULIA_CPU_TARGET="generic;skylake-avx512,clone_all;znver2,clone_all"

julia -e 'using Pkg; Pkg.add(["KomaMRI","FileIO","JLD2","NIfTI","Plots","JSON", "CUDA"]); Pkg.precompile()'
