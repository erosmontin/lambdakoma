# installation
## python script

```


JULIA_CPU_TARGET="generic;skylake-avx512,clone_all;znver2,clone_all"

julia -e 'using Pkg; Pkg.add(["KomaMRI","FileIO","JLD2","NIfTI","Plots","JSON", "CUDA"]); Pkg.precompile()'




sim params
Dict{String, Any} with 9 entries:
  "return_type" => "raw"
  "Nblocks"     => 20
  "gpu"         => true
  "Nthreads"    => 1
  "gpu_device"  => 0
  "sim_method"  => Bloch()
  "precision"   => "f32"
  "Δt"          => 0.001
  "Δt_rf"       => 5.0e-5


Scanner

B0: (::Real, =1.5, [T]) main magnetic field strength
B1: (::Real, =10e-6, [T]) maximum RF amplitude
Gmax: (::Real, =60e-3, [T/m]) maximum gradient amplitude
Smax: (::Real, =500, [mT/m/ms]) gradient's maximum slew-rate
ADC_Δt: (::Real, =2e-6, [s]) ADC raster time
seq_Δt: (::Real, =1e-5, [s]) sequence-block raster time
GR_Δt: (::Real, =1e-5, [s]) gradient raster time
RF_Δt: (::Real, =1e-6, [s]) RF raster time
RF_ring_down_T: (::Real, =20e-6, [s]) RF ring down time
RF_dead_time_T: (::Real, =100e-6, [s]) RF dead time
ADC_dead_time_T: (::Real, =10e-6, [s]) ADC dead time



