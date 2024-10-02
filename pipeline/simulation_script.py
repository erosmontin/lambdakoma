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

SL=28
if len(sys.argv) > 2:
    SL = int(sys.argv[2])

SEQ="pipeline/sdl_pypulseq.seq"
SEQ="pipeline/sdl_miniflash.seq"

T1=None
T2=None
dW=None
T2s=None
B0=None



import pyable_eros_montin.imaginable as ima
import numpy as np


FIELD=c.readMarieOutput("pipeline/Duke_5mm_7T_PWC_GMTcoil_ultimatesurfacebasis_TMD.zip")


B0=FIELD["B0"]
NT=10
GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()
SENS_DIR=pn.Pathable(FIELD["b1m"][0]).getPath()
FOVi=0.3
FOVj=0.3
dx=.5/1000

T,SL=c.process_slicev1(SL, B0, FIELD["T1"],FIELD["T2"],FIELD["T2star"],FIELD["dW"],FIELD["PD"],FOVi,FOVj,dx, SEQ, OUTDIR,SENS_DIR ,GPU,NT)
import matplotlib.pyplot as plt
plt.imshow(np.abs(T), cmap='gray')
_tim=L.stop()
plt.title(f'Reconstructed Image (RSS) {float(_tim["time"])/60.0:.2f} min, slice {SL}')
# origin of axis  at bottom left
plt.gca().invert_yaxis()

plt.colorbar()
plt.show()


