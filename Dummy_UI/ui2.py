import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # For displaying satellite image
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv

# Constants
image_path = "satellite.png"  # Satellite image file name
selected_points = []
num_areas = 2  # Number of equal areas to split into
padding = 10  # Padding for path from the border

def on_click(event):
    # Get click coordinates and round to nearest grid point
    x = event.x
    y = event.y
    selected_points.append((x, y))
    # Draw a point on the canvas
    canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')

def confirm_points():
    if len(selected_points) < 3:
        messagebox.showwarning("Insufficient Points", "Select at least 3 points to form a polygon.")
        return
    # Close the polygon by connecting the last point to the first
    if selected_points[0] != selected_points[-1]:
        selected_points.append(selected_points[0])

    # Split polygon into equal areas
    sub_polygons = split_polygon_into_equal_areas(selected_points, num_areas)

    # Plan paths for each sub-polygon
    all_paths = []
    for i, sub_polygon in enumerate(sub_polygons):
        cells = boustrophedon_decomposition(sub_polygon)
        path = generate_coverage_path(cells)
        export_path_to_csv(path, i + 1)
        all_paths.append((sub_polygon, cells, path))

    # Plot all sub-polygons and paths with starting position
    plot_decomposition_and_paths(all_paths)

def split_polygon_into_equal_areas(polygon_points, num_parts):
    polygon = Polygon(polygon_points)
    sub_polygons = [polygon]

    while len(sub_polygons) < num_parts:
        new_sub_polygons = []
        for poly in sub_polygons:
            min_x, min_y, max_x, max_y = poly.bounds
            split_line = LineString([((min_x + max_x) / 2, min_y), ((min_x + max_x) / 2, max_y)])
            split_result = split(poly, split_line)

            if split_result.geom_type == 'GeometryCollection':
                split_polygons = [geom for geom in list(split_result.geoms) if geom.geom_type == 'Polygon']
                if len(split_polygons) > 1:
                    new_sub_polygons.extend(split_polygons)
                else:
                    new_sub_polygons.append(poly)
            elif split_result.geom_type == 'Polygon':
                new_sub_polygons.append(split_result)
            else:
                new_sub_polygons.append(poly)

        sub_polygons = new_sub_polygons

    return sub_polygons

def boustrophedon_decomposition(polygon):
    buffered_polygon = polygon.buffer(-padding)
    if buffered_polygon.is_empty or not buffered_polygon.is_valid:
        buffered_polygon = polygon

    min_x, min_y, max_x, max_y = buffered_polygon.bounds
    cells = []
    x = min_x
    step_size = 20

    while x <= max_x:
        line = LineString([(x, min_y), (x, max_y)])
        intersections = buffered_polygon.intersection(line)
        
        if intersections.is_empty:
            x += step_size
            continue

        if intersections.geom_type == 'MultiLineString':
            for segment in intersections.geoms:
                if segment.geom_type == 'LineString':
                    cells.append(segment)
        elif intersections.geom_type == 'LineString':
            cells.append(intersections)

        x += step_size

    return cells

def generate_coverage_path(cells):
    path = []
    direction = 1
    for cell in cells:
        x, y = cell.xy
        if direction == 1:
            path.extend(list(zip(x, y)))
        else:
            path.extend(list(zip(x[::-1], y[::-1])))
        direction *= -1
    return path

def export_path_to_csv(path, part_number):
    filename = f"coverage_path_part_{part_number}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["X", "Y"])
        for point in path:
            writer.writerow(point)
    print(f"Path for part {part_number} saved to {filename}")

def plot_decomposition_and_paths(all_paths):
    # Load satellite image as background
    img = plt.imread(image_path)
    plt.imshow(img, extent=[0, 600, 600, 0])

    colors = ['green', 'blue', 'orange', 'purple']
    start_x, start_y = selected_points[0]
    plt.plot(start_x, start_y, 'r*', markersize=12, label='Starting Position')

    for i, (polygon, cells, path) in enumerate(all_paths):
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black', linewidth=2, label=f"Polygon {i + 1}")

        for cell in cells:
            x, y = cell.xy
            plt.plot(x, y, color='gray', linestyle='--')

        path_x, path_y = zip(*path)
        plt.plot(path_x, path_y, color=colors[i % len(colors)], marker='o', linestyle='-', linewidth=1, label=f"Path {i + 1}")

        # Draw independent paths from the starting point to the first point of each path plan
        first_path_point = path[0]
        plt.plot([start_x, first_path_point[0]], [start_y, first_path_point[1]], 'r--', linewidth=2, label=f'Start to Path {i + 1}')

    plt.title("Decomposed Areas & Independent Paths on Satellite Image")
    plt.legend()
    plt.grid(True)
    plt.show()

# Create the main GUI window
root = tk.Tk()
root.title("Polygon Selection on Satellite Image")

# Load and display the satellite image
image = Image.open(image_path)
image = image.resize((600, 600))
photo = ImageTk.PhotoImage(image)
canvas = tk.Canvas(root, width=600, height=600, bg='white')
canvas.create_image(0, 0, anchor=tk.NW, image=photo)
canvas.grid(row=0, column=0, padx=10, pady=10)

# Capture mouse clicks
canvas.bind("<Button-1>", on_click)

# Button to confirm points and proceed
confirm_button = tk.Button(root, text="Confirm Points", command=confirm_points)
confirm_button.grid(row=1, column=0, pady=10)

# Run the Tkinter main loop
root.mainloop()
