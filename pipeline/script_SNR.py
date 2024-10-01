import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import common as c
import SimpleITK as sitk

import sys
L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation

OUTDIR="/g/KOMA"
if len(sys.argv) > 1:
    OUTDIR = sys.argv[1]

SL=98
if len(sys.argv) > 2:
    SL = int(sys.argv[2])

SEQ="pipeline/sdl_miniflash.seq"
MODEL="pipeline/model.nii.gz"
PROP="pipeline/Tissue_300MHz.prop"
FIELD=c.readMarieOutput("pipeline/marie.zip")

NC=sitk.ReadImage(FIELD["NC"][0])
B0=7.0
NT=10
GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()
data=c.simulate_2D_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR,FIELD["b1m"], GPU,NT)

R=cmh.cm2DReconRSS()
R.setSignalKSpace(data)
R.setNoiseCovariance(sitk.GetArrayFromImage(NC))

import matplotlib.pyplot as plt
plt.imshow(np.abs(T), cmap='gray')
_tim=L.stop()
plt.title(f'Reconstructed Image (RSS) {float(_tim["time"])/60.0:.2f} min, slice {SL}')
plt.colorbar()
plt.show()

