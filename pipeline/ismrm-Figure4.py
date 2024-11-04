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

OUTDIR="/g/KOMA_coronal"
if len(sys.argv) > 1:
    OUTDIR = sys.argv[1]

import os
os.makedirs(OUTDIR,exist_ok=True)


SL=90
if len(sys.argv) > 2:
    SL = int(sys.argv[2])

# SEQ="seq/sdl_pypulseq_TE10_TR4000_os2_largeCrush_xSpoil.seq" #1
# SEQ="seq/sdl_pypulseq_TE10_TR600_os2_largeCrush_xSpoil.seq" #3
SEQ="seq/sdl_pypulseq_TE80_TR4000_os2_largeCrush_xSpoil.seq" #2


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

OUT=f"{OUTDIR}/{SL}/"
import os
k=OUTDIR + f"/{SL}/k.npz"
if os.path.exists(k):
    data=np.load(k)["data"]
else:
    data=c.simulate_2D_slice(SL, B0, FIELD["T1"],FIELD["T2"],FIELD["T2star"],FIELD["dW"],FIELD["PD"],desired_spin_resolution,SEQ,OUTDIR,SENS_DIR,GPU,NT,debug=True)
    np.savez(k,data=data)

BARTDIR=pn.createRandomTemporaryPathableFromFileName('a.cfl')
BARTDIR.appendPathRandom()
BARTDIR.ensureDirectoryExistence()
bartk=f'{BARTDIR.getPath()}/k'

bartr=f'{BARTDIR.getPath()}/r'
c.write_cfl(data,bartk)

import subprocess

command = [
    'docker', 'run', 
    '--mount', f'type=bind,source={BARTDIR.getPath()},target=/cfl',
    '--mount', f'type=bind,source={OUT},target=/output',

    '-it', '--entrypoint', '/bin/bash', 
    'docker.io/biocontainers/bart:v0.4.04-2-deb_cv1',
    '-c', 'bart fft -i 7 /cfl/k s && bart rss 8 s s2 && bart toimg s2 /output/r'
]

# Run the command with subprocess
result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)
print(result.stderr)


import shutil
shutil.copyfile(f'{bartr}*.png',f'{OUTDIR}/{SL}/')
