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
isosurface = isosurface.smooth(n_iter=100, relaxation_factor=0.1)

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


# def callback(*args):
#     # Get the click position
#     x, y = args[0], args[1]
#     position = plotter.pick_mouse_position((x, y))

#     # Add a sphere at the click position
#     if position is not None:
#         sphere = pv.Sphere(radius=0.1, center=position)
#         plotter.add_mesh(sphere)
from scipy.spatial.transform import Rotation as R

def add_rectangle_to_plot(plotter, length, width, height, center,rotation=[0,0,0]):
    # Create a box (rectangular prism)
    box = pv.Box(bounds=(0, length, 0, width, 0, height))
    
    box.points += np.array(center)
    plotter.add_mesh(box, color='yellow', opacity=0.2)

    box.rotate_x(rotation[0],inplace=True)
    box.rotate_y(rotation[1],inplace=True)
    box.rotate_z(rotation[2],inplace=True)
       # Define the box's local x, y, and z axes
    local_axes = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    # Calculate the rotation matrix
    r = R.from_euler('xyz', rotation, degrees=True)
    rotation_matrix = r.as_matrix()

    # Rotate the local axes with the box
    rotated_axes = rotation_matrix @ local_axes.T

    # Normalize the rotated axes to unit vectors
    normalized_axes = rotated_axes / np.linalg.norm(rotated_axes, axis=0)

    # Define the global x, y, and z axes
    global_axes = np.eye(3)

    # Calculate the direction cosines
    direction_cosines = normalized_axes.T @ global_axes

    # Calculate the origin after rotation
    origin = rotation_matrix @ np.array(center)

    return direction_cosines,origin,


KSPACESIZE=[256,256,6]
ORIGINKSPACE=[-KSPACESIZE[0]//2,-KSPACESIZE[1]//2,20]
directors,origin=add_rectangle_to_plot(plotter, *KSPACESIZE, center=ORIGINKSPACE,rotation=[0,0,0])

print(directors)
n = 64
first_direction = directors[0]
points = generate_points_on_side(origin, first_direction, KSPACESIZE[0], n)


# Add the points to the plot
import pyable_eros_montin.imaginable as ima
D=ima.Imaginable(MODEL)
INDEX=[]
for point in points:
    plotter.add_points(point, color='red')
    INDEX.append(D.getIndexFromCoordinates(point))


second_direction = directors[1]
# import time
for point in points:
    # time.sleep(0.1)
    line = pv.Line(point, point + second_direction * KSPACESIZE[1])
    plotter.add_mesh(line, color='blue')





unstructured_grid = read_gmsh_file('/g/models/data/coil/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005.msh')

plotter.add_mesh(unstructured_grid,opacity=0.1)

# Set the callback function
# plotter.iren.add_observer('LeftButtonPressEvent', callback)
# Start the plotter's interaction loop




res=KSPACESIZE
res[0]=float(res[0])/n
res[2]=float(res[2])/1

OUT={
    "points":[list(t) for t in points],
    "index":INDEX,
    "direction":directors,
    "origin":list(origin),
    "spacing":res,
    "KSIZE":KSPACESIZE
}

import pynico_eros_montin.pynico as pn
O=pn.Pathable("./OUT.json")
O.writeJson(OUT)

plotter.show()



sys.exit(app.exec_())