##################################
# Program Name: my_devices.py
# Authors: Andrés Ferrer
# Centro de Electrónica Industrial (CEI)
# Universidad Politécnica de Madrid (UPM)
# Last Modification: 16/01/2026
##################################

##################################
# Change Log:
# - Release
# - 
# - 
##################################

import time
import csv

from class_definition import DeviceManager
from my_devices import device_list
from datetime import datetime, timedelta

# Create a DeviceManager instance with the list of devices
manager = DeviceManager(device_list)
manager.scan_and_assign()  # Scan connected devices and assign them to objects

# Initialize thermometer device
thermo = manager.get_device_by_id("RS_Therm")
if thermo:
    thermo.connect()  # Establish serial connection
    thermo.initialize()  # Send initial command to prepare thermometer

# Configure multimeters for voltage and current measurements
voltmeter = manager.get_device_by_id("BK_V")
voltmeter.DC_voltage_config()  # Set multimeter to DC voltage mode

ammeter = manager.get_device_by_id("BK_I")
ammeter.DC_current_config()  # Set multimeter to DC current mode

# Test configuration
start_time_str = "2025-11-28 08:55:00"  # Scheduled start time
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
safe_start_time = start_time.strftime("%Y%m%d_%H%M%S")
duration_minutes = 10*90  # Test duration in minutes
interval_seconds = 10
  # Measurement interval in seconds
output_file = f"measurements_{safe_start_time}.csv"  # Output CSV file name

print(f"Wait for starting time: {start_time}")
while datetime.now() < start_time:
    time.sleep(1)  # Wait until the scheduled start time

print("Test begins:")
end_time = start_time + timedelta(minutes=duration_minutes)

# Open CSV file for writing measurements
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write header row
    writer.writerow(["timestamp", "voltage_V", "current_A", "T1_C", "T2_C", "T3_C", "T4_C"])

    # Measurement loop
    while datetime.now() < end_time:
        ini = time.perf_counter()  # Start timing for interval control
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        voltage = float(voltmeter.DC_voltage_measurement().strip())
        current = float(ammeter.DC_current_measurement().strip())
        try:
            temps = thermo.read_temperatures(debug=True)
        except Exception as e:
            print(f'Error leyendo temperaturas: {e}')
            temps = ['RECONNECT', 'RECONNECT', 'RECONNECT', 'RECONNECT']
            # Registrar reconexión en CSV
            writer.writerow([timestamp, '---', '---'] + temps)
            continue
        thermo.serial_obj.reset_input_buffer() #clean input buffer to avoid data accumulation

        # Write data row to CSV
        # Si temps indica reconexión, ya se registró antes
        writer.writerow([timestamp, f"{voltage:.7f}", f"{current:.7f}"] + [t if t is not None else "---" for t in temps])
        print(f"{timestamp} | V={voltage:.7f} V | I={current:.7f} A | Temps={temps}")

        end = time.perf_counter()
        print(f"Adquisition time: {end-ini}")
        time.sleep(max(0, interval_seconds - (end - ini)))  # Maintain interval timing

print(f"Test has ended. Data stored in {output_file}")