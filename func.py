import pyvista as pv
import meshio
def read_gmsh_file(file_path):
    mesh = meshio.read(file_path)
    mesh.points *= 1000
    unstructured_grid = pv.wrap(mesh)
    return unstructured_grid


def generate_points_on_side(origin, direction, length, n):
    step_size = length / (n - 1)  # Calculate the step size
    points = [origin + direction * step_size * i for i in range(n)]
    return points
