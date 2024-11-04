import numpy as np
import argparse
from scipy.io import savemat

def npz_to_mat(npz_file, mat_file):
    # Load the .npz file
    data = np.load(npz_file)
    
    # Convert the data to a dictionary
    data_dict = {"K":data}
    
    # Save the data to a .mat file
    savemat(mat_file, data_dict)


import glob
import os
for npz_file in glob.glob(os.path.join("/g/KOMA/", "**", "*.npz"), recursive=True):
    print(npz_file)
    SL=npz_file.split("/")[-2]
    MAT='/g/KOMA_MAT/'+SL+'k.mat'
    os.makedirs(os.path.dirname(MAT), exist_ok=True)
    npz_to_mat(npz_file, MAT)

# npz_to_mat('data.npz', 'data.mat')