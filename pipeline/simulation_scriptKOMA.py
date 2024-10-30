import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import common as c
L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation


import sys
OUTDIR="/g/KOMA"
if len(sys.argv) > 1:
    OUTDIR=sys.argv[1]
SL=98
if len(sys.argv) > 2:
    SL=int(sys.argv[2])

import os
os.makedirs(OUTDIR,exist_ok=True)
SEQ="pipeline/sdl_miniflash.seq"
MODEL="pipeline/model.nii.gz"
PROP="pipeline/Tissue_300MHz.prop"
FIELD="ggg.mhd"
B0=7.0
NT=10
GPU=False
# T,SL=c.process_sliceKOMAMRI(SL, B0, MODEL, PROP, SEQ, OUTDIR, GPU,NT)
import matplotlib.pyplot as plt
import numpy as np
T=np.load("/g/k.npz")
import cloudmrhub.cm2D as cmh
R=cmh.cm2DReconRSS()
R.setPrewhitenedSignal(np.expand_dims(T,axis=-1))
O=R.getOutput()
plt.imshow(np.abs(O), cmap='gray')
# plt.title(f'Reconstructed Image (RSS) {L.stop()/60.0:.2f} min, slice {SL}')
plt.colorbar()
plt.show()