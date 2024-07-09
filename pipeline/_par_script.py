import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import pyable_eros_montin.imaginable as ima
import multiprocessing as mp
import os
def process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, GPU, NT):
    OUTDIR = OUTDIR + f"/{SL}"
    B=pn.BashIt()
    B.setCommand(f"julia --threads=auto -O3 pipeline/bodymodel_simulation.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL} {GPU} {NT}")
    B.run()
    # reconstruct the image
    info=pn.Pathable(OUTDIR + "/info.json")
    J=info.readJson()
    data = np.load(J["KS"])
    R=cmh.cm2DReconRSS()
    data = np.expand_dims(data, axis=-1)
    R.setPrewhitenedSignal(data)
    return R.getOutput(),SL

if __name__ == "__main__":
    B0 = 3.0
    MODEL = "pipeline/model.nii.gz"
    PROP = "pipeline/Tissue_300MHz.prop"
    SEQ = "pipeline/sdl_pypulseq.seq"
    OUTDIR = "/tmp/KOMA"
    GPU = False
    NT = 2

    os.makedirs(OUTDIR, exist_ok=True)
    
    #load npz
    data = np.load(OUTDIR + "/reconstructed_image.npz")

    # Access arrays from the loaded file
    stacked_results = data['stacked_results']
    slice_numbers = data['slice_numbers']
    
    # np.savez(OUTDIR + "/reconstructed_image.npz", stacked_results=stacked_results, slice_numbers=slice_numbers)
    
    stacked_results = stacked_results[np.argsort(slice_numbers)]
    stacked_results = np.transpose(stacked_results, (1, 2, 0))
    # Save the stacked results
    
    ima.saveNumpy(stacked_results, OUTDIR + "/reconstructed_image.npy")    
    