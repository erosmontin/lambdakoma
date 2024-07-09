import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np

L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation
SL=90
OUTDIR="/g/KOMA"
SEQ="pipeline/sdl_pypulseq.seq"
MODEL="pipeline/model.nii.gz"
PROP="pipeline/Tissue_300MHz.prop"
FIELD="ggg.mhd"
B0=3.0


B.setCommand(f" julia --threads=auto -O3 pipeline/bodymodel_simulation.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL}")
B.run()


# reconstruct the image
info=pn.Pathable(OUTDIR + "/info.json")
J=info.readJson()

data = np.load(J["KS"])

R=cmh.cm2DReconRSS()
data = np.expand_dims(data, axis=-1)
R.setPrewhitenedSignal(data)

import matplotlib.pyplot as plt
plt.imshow(np.abs(R.getOutput()), cmap='gray')
plt.title(f'Reconstructed Image (RSS) {L.stop()/60.0:.2f} min')
plt.colorbar()
plt.show()

