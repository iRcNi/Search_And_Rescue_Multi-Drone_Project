from pymavlink import mavutil
from pynput import keyboard
import time

# Connect to the drone
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
print("Waiting for connection...")
master.wait_heartbeat()
print("Heartbeat received.")

# Function to change flight mode
def set_flight_mode(mode):
    mode_id = master.mode_mapping().get(mode)
    if mode_id is None:
        print(f"Flight mode {mode} not recognized!")
        return
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    print(f"Flight mode changed to {mode}")

# Start mission
set_flight_mode('GUIDED')

# Arm the drone
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)

# Takeoff to 100 meters
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 100  # 100 meters altitude
)

time.sleep(10)  # Give time for takeoff

# Set mode to AUTO (start mission)
set_flight_mode('AUTO')
print("Mission started... Press 's' to stop and hold position.")

# Flag to stop the loop
stop_flag = False

def on_press(key):
    global stop_flag
    try:
        if key.char == 's':  # If 's' is pressed
            print("Key 's' was pressed! Stopping the mission...")
            set_flight_mode('BRAKE')  # or use 'LOITER' for smooth stop
            stop_flag = True
    except AttributeError:
        pass

# Start listening for key press
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Keep the script running, but exit if stop_flag is True
while not stop_flag:
    time.sleep(0.1)  # Avoid high CPU usage

print("Mission paused. Exiting script.")
