import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np

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