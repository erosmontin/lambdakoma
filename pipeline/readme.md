# installation
1.  Install julia

```
# Download the Julia tar.gz file
wget https://julialang-s3.julialang.org/bin/linux/x64/1.6/julia-1.6.2-linux-x86_64.tar.gz

# Extract the tar.gz file
tar -xvzf julia-1.6.2-linux-x86_64.tar.gz

# Move the extracted folder to /opt directory
sudo mv julia-1.6.2 /opt/

# Create a symbolic link to the Julia binary in the /usr/local/bin directory
sudo ln -s /opt/julia-1.6.2/bin/julia /usr/local/bin/julia


# Install and optimize packages
JULIA_CPU_TARGET="generic;skylake-avx512,clone_all;znver2,clone_all"

julia -e 'using Pkg; Pkg.add(["KomaMRI","FileIO","JLD2","NIfTI","Plots","JSON", "CUDA","NPZ"]); Pkg.precompile()'
```

2. Install Python Packages
- create the env

```
#create an environment 
python3 -m venv CMT
source CMT/bin/activate
````

- install [cloudmrhub](https://github.com/cloudmrhub-com/cloudmrhub)
```
pip install git+https://github.com/cloudmrhub-com/cloudmrhub.git

```



- install [pynico](https://github.com/erosmontin/pynico)


```
pip install git+https://github.com/erosmontin/pynico

```

- install numpy
```
pip install numpy
```

# usage 
- Julia 
```julia

julia simulator.jl B0 T1map T2map T2smap DeltaW protonDensitymap FoVx FOVy dx sequence_name.pulseq /path/to/output/directory SLICENUM SENS_Directory GPU NunmberOfThreads

```

- python create a script file

```python
python pipeline/simulation_script.py /path/to/outputpath sliceNumber
```


# koma MRI Julia Customization 

- sim params
Dict{String, Any} with 9 entries:
  -  "return_type" => "raw"
  - "Nblocks"     => 20
  - "gpu"         => true
  - "Nthreads"    => 1
  - "gpu_device"  => 0
  - "sim_method"  => Bloch()
  - "precision"   => "f32"
  - "Δt"          => 0.001
  - "Δt_rf"       => 5.0e-5


- Scanner

  -  B0: (::Real, =1.5, [T]) main magnetic field strength
  - B1: (::Real, =10e-6, [T]) maximum RF amplitude
  - Gmax: (::Real, =60e-3, [T/m]) maximum gradient amplitude
  - Smax: (::Real, =500, [mT/m/ms]) gradient's maximum slew-rate
  - ADC_Δt: (::Real, =2e-6, [s]) ADC raster time
  - seq_Δt: (::Real, =1e-5, [s]) sequence-block raster time
  - GR_Δt: (::Real, =1e-5, [s]) gradient raster time
  - RF_Δt: (::Real, =1e-6, [s]) RF raster time
  - RF_ring_down_T: (::Real, =20e-6, [s]) RF ring down time
  - RF_dead_time_T: (::Real, =100e-6, [s]) RF dead time
  - ADC_dead_time_T: (::Real, =10e-6, [s]) ADC dead time



