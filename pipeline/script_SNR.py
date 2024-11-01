import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import cloudmrhub.cm as cm
import numpy as np
import common as c
import matplotlib.pyplot as plt

import sys
L=pn.Timer()
L.start()
B=pn.BashIt()

#customize the calculation

OUTDIR="/g/KOMA"
if len(sys.argv) > 1:
    OUTDIR = sys.argv[1]

SL=90
if len(sys.argv) > 2:
    SL = int(sys.argv[2])

SEQ="pipeline/sdl_pypulseq.seq"
#SEQ="pipeline/sdl_miniflash.seq"

T1=None
T2=None
dW=None
T2s=None
B0=None



import pyable_eros_montin.imaginable as ima
import numpy as np


FIELD=c.readMarieOutput("cloudMR_overlap.zip")

import SimpleITK as sitk
B0=FIELD["B0"]
NT=20
GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()
SENS_DIR=pn.Pathable(FIELD["b1m"][0]).getPath()
desired_spin_resolution = (2e-3,2e-3)

NC=sitk.ReadImage(FIELD["NC"])

GPU=False
A=pn.Pathable(OUTDIR+'/')
A.ensureDirectoryExistence()


import os
k=OUTDIR + f"/{SL}/k.npz"
if os.path.exists(k):
    data=np.load(k)
else:
    data=c.simulate_2D_slice(SL, B0, FIELD["T1"],FIELD["T2"],FIELD["T2star"],FIELD["dW"],FIELD["PD"],desired_spin_resolution,SEQ,OUTDIR,SENS_DIR,GPU,NT,debug=True)


np.savez('kspace.npz',data=data)



R=cmh.cm2DKellmanRSS()
R.setSignalKSpace(data)
R.setNoiseCovariance(sitk.GetArrayFromImage(NC))

T=R.getOutput()
plt.imshow(np.abs(T), cmap='viridis',vmax=np.max(np.abs(T))/3)
_tim=L.stop()
plt.title(f'Reconstructed SNR Map')
plt.colorbar()
plt.savefig(f'SNR{SL:02d}.png',dpi=300)
# plt.show()
plt.close()



R=cmh.cm2DReconRSS()
R.setSignalKSpace(data)
R.setNoiseCovariance(sitk.GetArrayFromImage(NC))
T=R.getOutput()
plt.imshow(np.abs(T), cmap='gray',vmax=np.max(np.abs(T))/3)
_tim=L.stop()
plt.title(f'Reconstructed Image RSS')
plt.colorbar()
plt.savefig(f'RSS{SL:02d}.png',dpi=300)
# plt.show()
plt.close()


# Create a mosaic of each slice in the third dimension
num_slices = data.shape[2]
cols = int(np.ceil(np.sqrt(num_slices)))
rows = int(np.ceil(num_slices / cols))

fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
axes = axes.flatten()

for i in range(num_slices):
    ax = axes[i]
    ax.imshow(np.abs(data[:, :, i]), cmap='gray',vmax=np.max(np.abs(data))/8)
    ax.axis('off')
    ax.set_title(f'Coil {i+1}')

# Hide any unused subplots
for i in range(num_slices, len(axes)):
    axes[i].axis('off')

plt.tight_layout()
plt.savefig(f'mosaic{SL:02d}.png', dpi=300)
plt.close()





FA=1
PA=4
ACL=128
L=cmh.cm2DGFactorSENSE()
L.setAcceleration([FA,PA])
US,REF=cm.mimicAcceleration2D(data,[FA,PA],ACL=[np.nan,ACL])

L.setSignalKSpace(US)
L.setNoiseCovariance(sitk.GetArrayFromImage(NC))
L.setReferenceKSpace(REF)
L.setAutocalibrationLines(ACL)
L.setMaskCoilSensitivityMatrixBasedOnEspirit()
OUT=L.getOutput()
plt.imshow(1.0/np.abs(OUT), cmap='gray')
plt.title(f'Inverse G Factor R = {FA} x {PA}')
plt.colorbar()
plt.savefig(f'ig{SL:02d}{FA}{PA}.png',dpi=300)
# plt.show()
plt.close()

plt.imshow(np.abs(OUT), cmap='gray')
plt.title(f'G Factor R = {FA} x {PA}')
plt.colorbar()
plt.savefig(f'g{SL:02d}{FA}{PA}.png',dpi=300)
# plt.show()
plt.close()

FA=4
PA=1
ACL=128
L=cmh.cm2DGFactorSENSE()
L.setAcceleration([FA,PA])
US,REF=cm.mimicAcceleration2D(data,[FA,PA],ACL=[np.nan,ACL])

L.setSignalKSpace(US)
L.setNoiseCovariance(sitk.GetArrayFromImage(NC))
L.setReferenceKSpace(REF)
L.setAutocalibrationLines(ACL)
L.setMaskCoilSensitivityMatrixBasedOnEspirit()
L.prepareCoilSensitivityMatrixPlot()
plt.savefig(f'coil{SL:02d}.png',dpi=300)
plt.close()
OUT=L.getOutput()
plt.imshow(1.0/np.abs(OUT), cmap='gray')
plt.title(f'Inverse G Factor R = {FA} x {PA}')
plt.colorbar()
plt.savefig(f'ig{SL:02d}{FA}{PA}.png',dpi=300)
# plt.show()
plt.close()

plt.imshow(np.abs(OUT), cmap='gray')
plt.title(f'G Factor R = {FA} x {PA}')
plt.colorbar()
plt.savefig(f'g{SL:02d}{FA}{PA}.png',dpi=300)
# plt.show()
plt.close()