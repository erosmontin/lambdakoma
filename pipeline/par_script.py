import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import pyable_eros_montin.imaginable as ima
import multiprocessing as mp
import os
def process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, GPU, NT):
    OUTDIR = OUTDIR + f"/{SL}"
    G=pn.GarbageCollector()
    G.throw(OUTDIR)
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
    G.trash()
    return R.getOutput(),SL

if __name__ == "__main__":
    B0 = 3.0
    MODEL = "pipeline/model.nii.gz"
    PROP = "pipeline/Tissue_300MHz.prop"
    SEQ = "pipeline/sdl_pypulseq.seq"
    OUTDIR = "/tmp/KOMA"
    GPU = False
    NT = 2

    L=pn.Timer()
    os.makedirs(OUTDIR, exist_ok=True)

    args = [(int(SL), B0, MODEL, PROP, SEQ, OUTDIR, GPU, NT) for SL in range(50,96)]
    num_processors = 4
    with mp.Pool(num_processors) as pool:
        results = pool.starmap(process_slice, args)
    # Convert results to a list first, as map object doesn't support indexing
    
    results = list(results)

    # Stack the 2D arrays into a 3D array
    stacked_results = np.stack([result[0] for result in results])
    slice_numbers = [result[1] for result in results]
    
    
    # np.savez(OUTDIR + "/reconstructed_image.npz", stacked_results=stacked_results, slice_numbers=slice_numbers)
    
    stacked_results = stacked_results[np.argsort(slice_numbers)]
    
    # Save the stacked results
    stacked_results = np.transpose(stacked_results, (1, 2, 0))
    # Save the stacked results
    
    ima.saveNumpy(stacked_results, OUTDIR + "/reconstructed_image.nii.gz")    
    
    print("Time taken: ", L.stop())