
def simulate_2D_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES=None,GPU=False, NT=10):
    # old version
    OUTDIR = OUTDIR + f"/{SL}"
    G=pn.GarbageCollector()
    G.throw(OUTDIR)
    B=pn.BashIt()
    B.setCommand(f"julia --threads=auto -O3 pipeline/bodymodel_simulation_old.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL} {SENSITIVITIES} {GPU} {NT}")
    # B.run()
    # reconstruct the image
    info=pn.Pathable(OUTDIR + "/info.json")
    J=info.readJson()
    data = np.load(J["KS"])
    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=-1)
    G.trash()
    return data
    
  def process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES=None,GPU=False, NT=10):
    #old version
    # simulate the slice
    data = simulate_2D_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES,GPU, NT)
    R=cmh.cm2DReconRSS()
    R.setPrewhitenedSignal(data)
    return R.getOutput(),SL
