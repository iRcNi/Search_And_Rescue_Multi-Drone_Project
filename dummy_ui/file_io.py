import csv

gps_top_left = (21.497549, 39.249365)
gps_bottom_right = (21.499448, 39.246958)


def export_path_to_csv(path, part_number):
    filename = f"coverage_path_part_{part_number}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["X", "Y", "Latitude", "Longitude"])
        for x, y in path:
            lat, lon = image_to_gps(x, y)
            writer.writerow([x, y, lat, lon])
    print(f"Path for part {part_number} saved to {filename}")

def image_to_gps(x, y):
    lat1, lon1 = gps_top_left
    lat2, lon2 = gps_bottom_right
    img_w, img_h = 600, 600
    lat = lat1 + ((img_h - y) / img_h) * (lat2 - lat1)
    lon = lon1 + (x / img_w) * (lon2 - lon1)
    return lat, lon

