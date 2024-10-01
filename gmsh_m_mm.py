import vtk
import meshio
import pyvista as pv
def read_gmsh_file(file_path):
    # Read the Gmsh file using meshio
    mesh = meshio.read(file_path)

    # Convert the meshio Mesh object to a vtkUnstructuredGrid object
    unstructured_grid = pv.wrap(mesh)

    return unstructured_grid

def plot_unstructured_grid(unstructured_grid):
    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(unstructured_grid)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.2, 0.4)

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Start the visualization
    interactor.Initialize()
    render_window.Render()
    interactor.Start()

def save_mesh_in_mm(unstructured_grid, output_file):
    # Scale the points of the mesh by 0.001 to convert from meters to millimeters
    unstructured_grid.points = unstructured_grid.points * 0.001

    # Create a dictionary for the cells
    cells = {cell_block.type: cell_block.data for cell_block in unstructured_grid.cells}

    # Save the mesh
    meshio.write(output_file, meshio.Mesh(unstructured_grid.points, cells))
# Use the functions
unstructured_grid = read_gmsh_file('/home/eros/Downloads/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005.msh')
plot_unstructured_grid(unstructured_grid)
save_mesh_in_mm(unstructured_grid, 'output_file.vtk')