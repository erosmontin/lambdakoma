import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np
import common as c

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

SEQ="pipeline/sdl_pypulseq.seq"
SEQ="pipeline/sdl_miniflash.seq"
MODEL="pipeline/model.nii.gz"
PROP="pipeline/Tissue_300MHz.prop"
FIELD=c.readMarieOutput("pipeline/marie.zip",target=MODEL)


B0=7.0
NT=10
GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()
SENS_DIR=pn.Pathable(FIELD["b1m"][0])
T,SL=c.process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR,SENS_DIR ,GPU,NT)
import matplotlib.pyplot as plt
plt.imshow(np.abs(T), cmap='gray')
_tim=L.stop()
plt.title(f'Reconstructed Image (RSS) {float(_tim["time"])/60.0:.2f} min, slice {SL}')
plt.colorbar()
plt.show()

