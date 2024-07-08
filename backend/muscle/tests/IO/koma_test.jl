using KomaMRI;
using MAT;

# Choose seq definition using coment/uncomment
filename = "C:/Users/artiga02/mtrk_designer_gui/app/mtrk_designer_api/sdl_pypulseq.seq"; # Pulseq file
seq = read_seq(filename); # Pulseq file
# seq = PulseDesigner.EPI_example(); # EPI example

# Simulate with default parameter and specified sequence
sim_params = KomaMRICore.default_sim_params();
obj = brain_phantom2D();
sys = Scanner();
raw = simulate(obj, seq, sys; sim_params);

# Function to export raw data in mat format
function export_2_mat_raw(raw_ismrmrd, matfolder; matfilename="raw.mat");
    if haskey(raw_ismrmrd.params, "userParameters")
        dict_for_mat = Dict()
        dict_user_params = raw_ismrmrd.params["userParameters"]
        for (key, value) in dict_user_params
            if key == "Δt_rf"
                dict_for_mat["dt_rf"] = value
            elseif key == "Δt"
                dict_for_mat["dt_rf"] = value
            else
                dict_for_mat[key] = value
            end
        end
        matwrite(joinpath(matfolder, "sim_params.mat"), dict_for_mat)

        not_Koma = raw_ismrmrd.params["systemVendor"] != "KomaMRI.jl"
        t = Float64[]
        signal = ComplexF64[]
        current_t0 = 0
        for p in raw_ismrmrd.profiles
        	dt = p.head.sample_time_us != 0 ? p.head.sample_time_us * 1e-3 : 1
        	t0 = p.head.acquisition_time_stamp * 1e-3 #This parameter is used in Koma to store the time offset
            N =  p.head.number_of_samples != 0 ? p.head.number_of_samples : 1
            if not_Koma
        		t0 = current_t0 * dt
                current_t0 += N
            end
            if N != 1
                append!(t, t0.+(0:dt:dt*(N-1)))
            else
                append!(t, t0)
            end
            append!(signal, p.data[:,1]) #Just one coil
            #To generate gap
            append!(t, t[end])
            append!(signal, [Inf + Inf*1im])
        end
        raw_dict = hcat(t, signal)
        matwrite(joinpath(matfolder, matfilename), Dict("raw" => raw_dict))
    end

end

# Export raw data in mat format
mat_folder = "Downloads";
mat_file_name="raw.mat";
export_2_mat_raw(raw, mat_folder; matfilename=mat_file_name);

