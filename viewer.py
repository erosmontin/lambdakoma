import nibabel as nib
import pyvista as pv
import numpy as np
from pyvistaqt import BackgroundPlotter

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets

from func import *
import sys
import pyable_eros_montin.imaginable as ima
MODEL='/g/models/data/sigma_e.nii.gz'
img = nib.load(MODEL)

b1 = nib.load('/g/models/data/b1m_001.nii.gz')

# Get the data, affine transformation, and header from the NIfTI file
data = img.get_fdata()
data/=np.max(data)
data=data>0
affine = img.affine
header = img.header

volume = pv.wrap(data.astype(np.uint8))

# Generate an isosurface at a specified value
# Apply a threshold to the volume
thresholded_volume = volume.threshold(0)

# Generate an isosurface at a specified value
isosurface = thresholded_volume.contour()
app = QApplication([])
plotter = BackgroundPlotter()

isosurface.transform(header.get_base_affine(),inplace=True)
isosurface.rotate_z(180)

#smooth isosurface
isosurface = isosurface.smooth(n_iter=10, relaxation_factor=0.1)

plotter.add_axes()

isosurface.show_edges = True

plotter.add_mesh(isosurface, color='green',opacity=0.8)



# Load the second image and get its data
coils_data = b1.get_fdata()
coils_data /= np.max(coils_data)

# Create a PyVista object from the data
coils_volume = pv.wrap(coils_data)

# Apply the same threshold and contour operations
coils_thresholded_volume = coils_volume.threshold(0)

isosurface = coils_thresholded_volume.contour()
isosurface.transform(header.get_base_affine(), inplace=True)
isosurface.rotate_z(180)
plotter.add_mesh(isosurface, 'red',opacity=0.8)


b2= nib.load('/g/models/data/b1m_002.nii.gz')
# Load the second image and get its data
coils_data = b2.get_fdata()
coils_data /= np.max(coils_data)

# Create a PyVista object from the data
coils_volume = pv.wrap(coils_data)

# Apply the same threshold and contour operations
coils_thresholded_volume = coils_volume.threshold(0)

isosurface = coils_thresholded_volume.contour()
isosurface.transform(header.get_base_affine(), inplace=True)
isosurface.rotate_z(180)
plotter.add_mesh(isosurface, 'blue',opacity=0.8)




unstructured_grid = read_gmsh_file('/g/models/data/coil/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005.msh')

plotter.add_mesh(unstructured_grid,opacity=0.1)





for i in [10,20,40,80]:
    KSPACESIZE=[256,256,6]    
    ORIGINKSPACE=[-KSPACESIZE[0]//2,-KSPACESIZE[1]//2,i]
    D=ima.Imaginable(MODEL)
    OUT=[]
    OUT.append(add_slice(plotter, KSPACESIZE, ORIGINKSPACE,D,rotation=[20,90,45],n=64))
    for key, value in OUT[-1].items():
        if isinstance(value, np.ndarray):
            OUT[-1][key] = value.tolist()



# Convert numpy arrays to lists

import pynico_eros_montin.pynico as pn
O=pn.Pathable("OUT.json")
O.writeJson(OUT)

plotter.show()



sys.exit(app.exec_())