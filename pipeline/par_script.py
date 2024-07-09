import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import pyable_eros_montin.imaginable as ima
import multiprocessing as mp
import os
import common as c

if __name__ == "__main__":
    B0 = 3.0
    MODEL = "pipeline/model.nii.gz"
    PROP = "pipeline/Tissue_300MHz.prop"
    SEQ = "pipeline/sdl_pypulseq.seq"
    OUTDIR = "/tmp/KOMA"
    GPU = False
    NT = 4

    L=pn.Timer()
    os.makedirs(OUTDIR, exist_ok=True)
    M=ima.Imaginable(MODEL)
    args = [(int(SL), B0, MODEL, PROP, SEQ, OUTDIR, GPU, NT) for SL in range(50,M.getImageSize(2))]
    num_processors = 4
    with mp.Pool(num_processors) as pool:
        results = pool.starmap(c.process_slice, args)

    results = list(results)
    # Stack the 2D arrays into a 3D array
    stacked_results = np.stack([result[0] for result in results])
    slice_numbers = [result[1] for result in results]
    stacked_results = stacked_results[np.argsort(slice_numbers)]
    
    # reorder the axes to match the image
    stacked_results = np.transpose(stacked_results, (1, 2, 0))
    # Save the stacked results
    
    ima.saveNumpy(stacked_results, OUTDIR + "/reconstructed_image.nii.gz")    
    
    print("Time taken: ", L.stop())