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

##################################
# Info:
# VISA_device_list=
#   id:=
#   brand:=
#   model:=
#   serial:=
#   terminator:=
# VISA_device_list=
#   id:=
#   brand:=
#   model:=
#   serial:=
#   port:=
#   baudrate:=
#   timeout:=
#   hardware_id:=
##################################

from class_definition import Multimeter, Thermometer

##################################

VISA_device_list = [
    Multimeter(id="BK_V", brand="BK Precision", model="5491B", serial="124A24190", terminator='\n'),
    Multimeter(id="BK_I", brand="BK Precision", model="5491B", serial="124A24198", terminator='\n'),
]

RS232_device_list = [
    Thermometer(id="RS_Therm", brand="RS", model="RS1384", serial="120811110", port="COM3", baudrate=19200, timeout=2,
                hardware_id="USB\\VID_067B&PID_2303\\5&2e05d5bd&0&3")
]

device_list = VISA_device_list + RS232_device_list
