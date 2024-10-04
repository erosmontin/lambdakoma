import pyvista as pv
import meshio
import numpy as np
from scipy.spatial.transform import Rotation as R

def read_gmsh_file(file_path,scale=1000):
    mesh = meshio.read(file_path)
    mesh.points *= scale
    unstructured_grid = pv.wrap(mesh)
    return unstructured_grid


def generate_points_on_side(origin, direction, length, n):
    step_size = length / (n - 1)  # Calculate the step size
    points = [origin + direction * step_size * i for i in range(n)]
    return points
def add_rectangle_to_plot(plotter, length, width, height, center,rotation=[0,90,45]):
    # Create a box (rectangular prism)
    box = pv.Box(bounds=(0, length, 0, width, 0, height))
    
    box.points += np.array(center)
    plotter.add_mesh(box, color='yellow', opacity=0)

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

def add_slice(plotter, KSPACESIZE, ORIGINKSPACE,D,rotation=[0,0,0],n=64):
    S=KSPACESIZE
    S[2]=S[2]//2+ORIGINKSPACE[2]
    directors,origin=add_rectangle_to_plot(plotter, *S, center=ORIGINKSPACE,rotation=rotation)
    first_direction = directors[0]
    points = generate_points_on_side(origin, first_direction, KSPACESIZE[0], n)

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
    return OUT