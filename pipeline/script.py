import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np


B=pn.BashIt()
SL=70
OUTDIR="/g/KOMA"
SEQ="sdl_pypulseq.seq"
MODEL="model.nii.gz"
PROP="Tissue_300MHz.prop"
FIELD="ggg.mhd"

B.setCommand(f" julia bodymodel_simulation.jl {MODEL} {PROP} {SEQ} {OUTDIR} {SL}")

B.run()
info=pn.Pathable(OUTDIR + "/info.json")
J=info.readJson()

data = np.load(J["KS"])

R=cmh.cm2DReconRSS()
data = np.expand_dims(data, axis=-1)
R.setPrewhitenedSignal(data)

import matplotlib.pyplot as plt
plt.imshow(np.abs(R.getOutput()), cmap='gray')
plt.show()
