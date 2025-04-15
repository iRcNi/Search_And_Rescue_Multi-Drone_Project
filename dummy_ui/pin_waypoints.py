import os
import folium

# === Configuration ===
images_folder = "/home/mohammed/Documents/Search_And_Rescue_Multi-Drone_Project/Search_And_Rescue_Multi-Drone_Project/pymavlink_testing/waypoints"  # Change this to your actual path

# === Initialize a map ===
# Start centered around the first point we read, fallback default if none found
map_center = [21.5, 39.2]
m = folium.Map(location=map_center, zoom_start=10)

# === Add waypoints ===
first_point = True

for filename in os.listdir(images_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        try:
            parts = filename.split("_")
            if len(parts) >= 2:
                lat = float(parts[0])
                lon = float(parts[1])
                if first_point:
                    m.location = [lat, lon]  # Center map on first valid point
                    first_point = False
                folium.Marker(
                    location=[lat, lon],
                    popup=filename,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# === Save the map ===
m.save("waypoints_map.html")
print("✅ Map saved as waypoints_map.html")
