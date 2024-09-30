import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import common as c
L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation
SL=98
OUTDIR="/g/KOMA"
SEQ="pipeline/sdl_pypulseq.seq"
MODEL="pipeline/model.nii.gz"
PROP="pipeline/Tissue_300MHz.prop"
FIELD="ggg.mhd"
B0=7.0
NT=10
GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()
T,SL=c.process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, GPU,NT)
import matplotlib.pyplot as plt
plt.imshow(np.abs(T), cmap='gray')
plt.title(f'Reconstructed Image (RSS) {L.stop()/60.0:.2f} min, slice {SL}')
plt.colorbar()
plt.show()

