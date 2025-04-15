import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

# GPS bounds of your image
gps_top_left = (21.497549, 39.249365)     # (lat1, lon1)
gps_bottom_right = (21.499448, 39.246958) # (lat2, lon2)

# Convert GPS to image pixel coordinates
def gps_to_image_coords(lat, lon, width=600, height=600):
    lat1, lon1 = gps_top_left
    lat2, lon2 = gps_bottom_right

    x = ((lon - lon1) / (lon2 - lon1)) * width
    y = ((lat1 - lat) / (lat1 - lat2)) * height  # y axis flipped
    return x, y

# Extract GPS from filename
def extract_gps_from_filename(filepath):
    name = os.path.basename(filepath)
    name = os.path.splitext(name)[0]  # Remove extension
    parts = name.split('_')
    if len(parts) < 2:
        raise ValueError(f"Filename format invalid: {name}")
    lat_str, lon_str = parts[:2]
    return float(lat_str), float(lon_str)

# Plot all image-named GPS points on satellite map
def plot_all_gps_points(directory, image_file="satellite.png"):
    img = mpimg.imread(image_file)

    plt.figure(figsize=(6, 6))
    plt.imshow(img, extent=[0, 600, 600, 0])

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            try:
                lat, lon = extract_gps_from_filename(filename)
                x, y = gps_to_image_coords(lat, lon)
                plt.plot(x, y, 'ro', markersize=5)
            except Exception as e:
                print(f"Skipping {filename}: {e}")

    plt.title("All GPS Points on Satellite Image")
    plt.xticks([])
    plt.yticks([])
    plt.tick_params(left=False, bottom=False)
    plt.show()

# Example usage
plot_all_gps_points("waypoints")  # Replace with your folder name
