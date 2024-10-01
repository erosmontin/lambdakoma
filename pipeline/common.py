import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np

def process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES=None,GPU=False, NT=10):
    OUTDIR = OUTDIR + f"/{SL}"
    G=pn.GarbageCollector()
    G.throw(OUTDIR)
    B=pn.BashIt()
    B.setCommand(f"julia --threads=auto -O3 pipeline/bodymodel_simulation.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL} {GPU} {NT}")
    B.run()
    # reconstruct the image
    info=pn.Pathable(OUTDIR + "/info.json")
    J=info.readJson()
    data = np.load(J["KS"])
    R=cmh.cm2DReconRSS()
    data = np.expand_dims(data, axis=-1)
    R.setPrewhitenedSignal(data)
    G.trash()
    return R.getOutput(),SL

import zipfile
import scipy.io
import cloudmrhub.cm2D as cmh
import pyable_eros_montin.imaginable as ima
import os
import shutil
def readMarieOutput(file,b1mpath=None):
    #unzip the file
    if b1mpath is None:
        b1mpath=pn.createTemporaryPathableDirectory().getPosition()

    O=pn.createTemporaryPathableDirectory()
    b1mpath=pn.checkDirEndsWithSlash(b1mpath)
    os.makedirs(b1mpath,exist_ok=True)
    print(O.getPath())
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(O.getPath())
    O.addBaseName("info.json")
    J=O.readJson()
    OUT={"b1m":[],"NC":[]}
    for d in J["data"]:
        if d["description"]=="b1m":
            of=os.path.join(O.getPath(),d["filename"])
            f=os.path.join(b1mpath,d["filename"])
            shutil.move(of,b1mpath)
            OUT["b1m"].append(f)
        if "noisecovariance" in d["description"].lower():
            f=os.path.join(O.getPath(),d["filename"])
            OUT["NC"].append(f)
    return OUT
        
        
    
        
        
        
    
    
    
if __name__=="__main__":
    OUT="/home/eros/Downloads/Duke_5mm_7T_PWC_GMTcoil_ultimatesurfacebasis_TMD(1).zip"
    print(readMarieOutput(OUT))