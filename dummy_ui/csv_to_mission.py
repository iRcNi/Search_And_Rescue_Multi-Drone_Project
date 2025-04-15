import csv

def csv_to_mission(csv_file, mission_file, altitude=20):
    waypoints = []

    # Read the CSV and extract lat/lon
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            waypoints.append((lat, lon))

    # Start building the mission file
    with open(mission_file, 'w') as f:
        f.write("QGC WPL 110\n")  # Header

        seq = 0
        frame = 3  # GLOBAL
        command = 16  # NAV_WAYPOINT
        current = 1  # First command
        autocontinue = 1
        param1 = 0  # Hold time
        param2 = 0
        param3 = 0
        param4 = 0

        # Home command (can be edited later)
        f.write(f"{seq}\t0\t16\t0\t0\t0\t0\t0\t0\t0\t0\t1\n")
        seq += 1

        for lat, lon in waypoints:
            f.write(f"{seq}\t0\t{command}\t{frame}\t{param1}\t{param2}\t{param3}\t{param4}\t{lat}\t{lon}\t{altitude}\t{autocontinue}\n")
            seq += 1

    print(f"Mission file '{mission_file}' created with {len(waypoints)} waypoints.")

# Example usage:
csv_to_mission("coverage_path_part_1.csv", "auto_mission_1.waypoints", altitude=20)
csv_to_mission("coverage_path_part_2.csv", "auto_mission_2.waypoints", altitude=20)
