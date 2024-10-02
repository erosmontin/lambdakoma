import pynico_eros_montin.pynico as pn
import cloudmrhub.cm2D as cmh
import numpy as np


def process_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES=None,GPU=False, NT=10):
    #old version
    # simulate the slice
    data = simulate_2D_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES,GPU, NT)
    R=cmh.cm2DReconRSS()
    R.setPrewhitenedSignal(data)
    return R.getOutput(),SL

def simulate_2D_slice(SL, B0, MODEL, PROP, SEQ, OUTDIR, SENSITIVITIES=None,GPU=False, NT=10):
    # old version
    OUTDIR = OUTDIR + f"/{SL}"
    G=pn.GarbageCollector()
    G.throw(OUTDIR)
    B=pn.BashIt()
    B.setCommand(f"julia --threads=auto -O3 pipeline/bodymodel_simulation_old.jl {B0} {MODEL} {PROP} {SEQ} {OUTDIR} {SL} {SENSITIVITIES} {GPU} {NT}")
    B.run()
    # reconstruct the image
    info=pn.Pathable(OUTDIR + "/info.json")
    J=info.readJson()
    data = np.load(J["KS"])
    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=-1)
    G.trash()
    return data

def process_slicev1(SL, B0, T1,T2,T2star,dW,PD,FOVi,FOVj,dx, SEQ, OUTDIR,SENS_DIR ,GPU,NT):
    # new version
    # simulate the slice
    data = simulate_2D_slicev1(SL, B0, T1,T2,T2star,dW,PD,FOVi,FOVj,dx, SEQ, OUTDIR,SENS_DIR ,GPU, NT)
    R=cmh.cm2DReconRSS()
    R.setPrewhitenedSignal(data)
    return R.getOutput(),SL

def simulate_2D_slicev1(SL, B0, T1,T2,T2star,dW,PD,FOVi,FOVj,dx, SEQ, OUTDIR,SENS_DIR ,GPU,NT):
    OUTDIR = OUTDIR + f"/{SL}"
    G=pn.GarbageCollector()
    G.throw(OUTDIR)
    B=pn.BashIt()
    
    B.setCommand(f"julia --threads=auto -O3 pipeline/simulator.jl {B0} {T1} {T2} {T2star} {dW} {PD} {FOVi} {FOVj} {dx} {SEQ} {OUTDIR} {SL} {SENS_DIR} {GPU} {NT}")
    print(B.getCommand())
    print("--"*10)
    B.run()
    # reconstruct the image
    info=pn.Pathable(OUTDIR + "/info.json")
    J=info.readJson()
    data = np.load(J["KS"])
    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=-1)
    G.trash()
    return data


import zipfile
import cloudmrhub.cm2D as cmh
import pyable_eros_montin.imaginable as ima
import os
import shutil
def readMarieOutput(file,b1mpath=None,target=None):
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
    OUT={"b1m":[],"NC":None,"B0":J["headers"]["Inputs"]["b0"],"T1":None,"T2":None,"dW":None,"T2star":None,"PD":None}
    if target:
        _t=ima.Imaginable(target)
    for d in J["data"]:
        if d["description"]=="b1m":
            of=os.path.join(O.getPath(),d["filename"])
            f=os.path.join(b1mpath,d["filename"])
            if target:
                _p=ima.Imaginable(of)
                _p.resampleOnTargetImage(_t)
                _p.writeImageAs(f)
            else:
                shutil.move(of,b1mpath)
            OUT["b1m"].append(f)
        if "noisecovariance" in d["description"].lower():
            f=os.path.join(O.getPath(),d["filename"])
            OUT["NC"]=f
        if "t1" in d["description"].lower():
            f=os.path.join(O.getPath(),d["filename"])
            OUT["T1"]=f
        if d["description"].lower()=="t2":
            f=os.path.join(O.getPath(),d["filename"])
            OUT["T2"]=f
        if "dw" in d["description"].lower():
            f=os.path.join(O.getPath(),d["filename"])
            OUT["dW"]=f
        if d["description"].lower()=="t2star":
            OUT["T2star"]=f
        if "rhoh" in d["description"].lower():
            OUT["PD"]=f
            
    return OUT
        
        
    
        
        
        
    
    
    
if __name__=="__main__":
    OUT="/home/eros/Downloads/Duke_5mm_7T_PWC_GMTcoil_ultimatesurfacebasis_TMD(1).zip"
    print(readMarieOutput(OUT))