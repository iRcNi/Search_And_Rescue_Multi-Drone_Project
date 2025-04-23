import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from geometry_utils import split_polygon_into_equal_areas, boustrophedon_decomposition, generate_coverage_path
from file_io import export_path_to_csv, image_to_gps
from mission_util import csv_to_mission
from plotting import plot_decomposition_and_paths

# Constants
image_path = "satellite.png"
selected_points = []
num_areas = 2

# GUI event handlers
def on_click(event):
    x = event.x
    y = event.y
    selected_points.append((x, y))
    canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')

def confirm_points():
    if len(selected_points) < 3:
        messagebox.showwarning("Insufficient Points", "Select at least 3 points to form a polygon.")
        return
    if selected_points[0] != selected_points[-1]:
        selected_points.append(selected_points[0])

    sub_polygons = split_polygon_into_equal_areas(selected_points, num_areas)
    all_paths = []
    for i, sub_polygon in enumerate(sub_polygons):
        cells = boustrophedon_decomposition(sub_polygon)
        path = generate_coverage_path(cells)
        export_path_to_csv(path, i + 1)
        all_paths.append((sub_polygon, cells, path))

    plot_decomposition_and_paths(selected_points, all_paths, image_path)
    for i in range(len(sub_polygons)):
        csv_to_mission(f"coverage_path_part_{i + 1}.csv", f"auto_mission_{i + 1}.waypoints", altitude=20)

# Setup GUI
root = tk.Tk()
root.title("Polygon Selection on Satellite Image")

image = Image.open(image_path).resize((600, 600))
photo = ImageTk.PhotoImage(image)
canvas = tk.Canvas(root, width=600, height=600, bg='white')
canvas.create_image(0, 0, anchor=tk.NW, image=photo)
canvas.grid(row=0, column=0, padx=10, pady=10)
canvas.bind("<Button-1>", on_click)

confirm_button = tk.Button(root, text="Confirm Points", command=confirm_points)
confirm_button.grid(row=1, column=0, pady=10)

root.mainloop()
