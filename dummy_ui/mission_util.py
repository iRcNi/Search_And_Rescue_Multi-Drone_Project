import csv

def csv_to_mission(csv_file, mission_file, altitude=20):
    waypoints = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            waypoints.append((lat, lon))
    with open(mission_file, 'w') as f:
        f.write("QGC WPL 110\n")
        seq = 0
        f.write(f"{seq}\t0\t16\t0\t0\t0\t0\t0\t0\t0\t0\t1\n")
        seq += 1
        for lat, lon in waypoints:
            f.write(f"{seq}\t0\t16\t3\t0\t0\t0\t0\t{lat}\t{lon}\t{altitude}\t1\n")
            seq += 1
    print(f"Mission file '{mission_file}' created with {len(waypoints)} waypoints.")

