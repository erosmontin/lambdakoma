import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np

L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation
SL=90
OUTDIR="/g/KOMA"
SEQ="sdl_pypulseq.seq"
MODEL="model.nii.gz"
PROP="Tissue_300MHz.prop"
FIELD="ggg.mhd"
B0=3.0

# # fixed the size of the m
# import pyable_eros_montin.imaginable as ima
# IM=ima.Imaginable(MODEL)
# IM.cropImage([0,0,SL],[0,0,SL+1])
# NSL=1 #julia start from 1....
# M=pn.Pathable(MODEL)
# M.addPrefix("cropped_")
# NMODEL=M.getPosition()
# IM.writeImageAs(NMODEL)

B.setCommand(f" julia --threads=auto -O3 bodymodel_simulation.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL}")
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

