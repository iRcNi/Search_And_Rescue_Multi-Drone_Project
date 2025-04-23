import matplotlib.pyplot as plt

def plot_decomposition_and_paths(selected_points, all_paths, image_path):
    img = plt.imread(image_path)
    plt.imshow(img, extent=[0, 600, 600, 0])

    colors = ['green', 'blue', 'orange', 'purple']
    start_x, start_y = selected_points[0]
    plt.plot(start_x, start_y, 'r*', markersize=12, label='Start')

    for i, (polygon, cells, path) in enumerate(all_paths[:4]):
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black', linewidth=2, label=f"Polygon {i + 1}")
        for cell in cells:
            x, y = cell.xy
            plt.plot(x, y, color='gray', linestyle='--')
        if path:  # Check if path is not empty
            path_x, path_y = zip(*path)
            plt.plot(path_x, path_y, color=colors[i], marker='o', linestyle='-', linewidth=1, label=f"Path {i + 1}")
            plt.plot([start_x, path[0][0]], [start_y, path[0][1]], 'r--', linewidth=2, label=f'Start to Path {i + 1}')

    plt.title("Decomposed Areas & Paths")
    plt.legend()
    plt.grid(True)
    plt.show()
