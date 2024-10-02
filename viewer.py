import nibabel as nib
import pyvista as pv
import numpy as np
from pyvistaqt import BackgroundPlotter

from PyQt5.QtWidgets import QApplication
import sys
import pyable_eros_montin.imaginable as ima
img = nib.load('/g/models/data/sigma_e.nii.gz')

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
isosurface = isosurface.smooth(n_iter=100, relaxation_factor=0.1)

plotter.add_axes()

isosurface.show_edges = True

plotter.add_mesh(isosurface, color='green',opacity=0.1)



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


def callback(*args):
    # Get the click position
    x, y = args[0], args[1]
    position = plotter.pick_mouse_position((x, y))

    # Add a sphere at the click position
    if position is not None:
        sphere = pv.Sphere(radius=0.1, center=position)
        plotter.add_mesh(sphere)

import meshio
def read_gmsh_file(file_path):
    mesh = meshio.read(file_path)
    mesh.points *= 1000
    unstructured_grid = pv.wrap(mesh)
    return unstructured_grid


unstructured_grid = read_gmsh_file('/g/models/data/coil/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005.msh')

plotter.add_mesh(unstructured_grid,opacity=0.3)

# Set the callback function
# plotter.iren.add_observer('LeftButtonPressEvent', callback)
# Start the plotter's interaction loop
plotter.show()

sys.exit(app.exec_())