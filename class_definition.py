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
import serial
import subprocess
import pyvisa

class VISA_device:
    def __init__(self, id, brand, model, serial, terminator):
        self.id = id
        self.brand = brand
        self.model = model
        self.serial = serial
        self.terminator = terminator
        self.visa_obj = None

    def connect(self, rm, resource):
        self.visa_obj = rm.open_resource(resource)
        self.visa_obj.read_termination = self.terminator
        self.visa_obj.timeout = 5000  # Aumentado para evitar timeout
        self.visa_obj.baud_rate = 9600
        self.visa_obj.data_bits = 8
        self.visa_obj.stop_bits = pyvisa.constants.StopBits.one
        self.visa_obj.parity = pyvisa.constants.Parity.none

    def identify(self):
        return self.visa_obj.query("*IDN?") if self.visa_obj else None


class Multimeter(VISA_device):
    def DC_voltage_config(self):
        if self.visa_obj:
            self.visa_obj.write(":FUNC VOLT:DC")
            time.sleep(0.5)
            self.visa_obj.write(":VOLT:DC:RANG:AUTO ON")
            time.sleep(0.5)
            self.visa_obj.write(":VOLT:DC:REF :STAT OFF")
            time.sleep(0.5)
        else:
            raise ConnectionError("The Device is not connected.")

    def DC_voltage_measurement(self):
        if self.visa_obj:
            self.visa_obj.write(":VOLT:DC:REF :ACQ")
            time.sleep(0.2)
            return self.visa_obj.query(":VOLT:DC:REF?")
        return None

    def DC_current_config(self):
        if self.visa_obj:
            self.visa_obj.write(":FUNC CURR:DC")
            time.sleep(0.5)
            self.visa_obj.write(":CURR:DC:RANG:AUTO ON")
            time.sleep(0.5)
            self.visa_obj.write(":CURR:DC:REF :STAT OFF")
            time.sleep(0.5)
        else:
            raise ConnectionError("The Device is not connected.")

    def DC_current_measurement(self):
        if self.visa_obj:
            self.visa_obj.write(":CURR:DC:REF :ACQ")
            time.sleep(0.2)
            return self.visa_obj.query(":CURR:DC:REF?")
        return None


class RS232_device:
    def __init__(self, id, brand, model, serial, port, baudrate, timeout):
        self.id = id
        self.brand = brand
        self.model = model
        self.serial = serial
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_obj = None

    def connect(self):
        self.serial_obj = serial.Serial(self.port, self.baudrate, timeout=self.timeout)


class Thermometer(RS232_device):
    def __init__(self, id, brand, model, serial, port, baudrate, timeout, hardware_id=None):
        super().__init__(id, brand, model, serial, port, baudrate, timeout)
        self.hardware_id = hardware_id

    
    def reconnect(self):
        try:       
            print("Liberando puerto antes de reinicio...")
            if self.serial_obj and self.serial_obj.is_open:
                self.serial_obj.close()
                time.sleep(2)  # Espera para liberar recursos
            if not self.hardware_id:
                raise ValueError("Hardware ID no configurado para PnPUtil.")
            print(f"Reiniciando dispositivo {self.hardware_id} con PnPUtil (restart-device)...")
            subprocess.run(f'pnputil /restart-device "{self.hardware_id}"', shell=True)
            time.sleep(5)
            self.connect()
            time.sleep(1)
            self.initialize()
            time.sleep(0.5)
            print("Reconexión completada.")
        except Exception as e:
            print(f"Error en reconnect: {e}")


    # def initialize(self):
    #     attempts = 0
    #     max_attempts = 3
    #     while attempts < max_attempts:
    #         attempts += 1
    #         self.serial_obj.write(b'A')
    #         #time.sleep(0.5)
    #         if self.serial_obj.in_waiting > 0:
    #             response = self.serial_obj.read(self.serial_obj.in_waiting)
    #             print(f"Initial response: {response}")
    #             return
    #     print("No se recibió respuesta tras varios intentos. Ejecutando reconnect()...")
    #     self.reconnect()

    def initialize(self):
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            attempts += 1
            print(f"Intento de inicialización #{attempts}")
            for _ in range(3):  # Enviar varias veces
                self.serial_obj.write(b'A')
                time.sleep(0.5)
            if self.serial_obj.in_waiting > 0:
                response = self.serial_obj.read(self.serial_obj.in_waiting)
                print(f"Initial response: {response}")
                # Validar si contiene un bloque válido
                if b'\x02' in response and b'\x03' in response:
                    print("Inicialización correcta.")
                    return
            time.sleep(1)
        print("No se recibió respuesta válida tras varios intentos. Ejecutando reconnect()...")
        self.reconnect()

    
    
    def read_temperatures(self, debug=False):
        start_time = time.time()
        canales_temp = {'T1': None, 'T2': None, 'T3': None, 'T4': None}
        if not hasattr(self, 'error_count'):
            self.error_count = 0
        max_errors = 5

        while True:
            if time.time() - start_time > self.timeout:
                return [None, None, None, None]
            for _ in range(4):
                bloque = self.serial_obj.read(12)
                if len(bloque) < 12 or bloque[0] != 0x02 or bloque[-1] != 0x03:
                    self.error_count += 1
                    if debug:
                        print(f"Bloque corrupto #{self.error_count}, descartando...")
                    if self.error_count >= max_errors:
                        print("Demasiados errores consecutivos. Ejecutando reconnect con restart-device...")
                        self.reconnect()
                        self.error_count = 0
                        return [None, None, None, None]  # Salir inmediatamente tras reconexión
                    continue
                # Bloque válido → reiniciar contador
                self.error_count = 0
                bloque = list(bloque)
                canal_bits = bloque[1] & 0b00000011
                canales = {0: 'T1', 1: 'T2', 2: 'T3', 3: 'T4'}
                canal = canales.get(canal_bits, None)
                status3 = bloque[3]
                if debug:
                    print(f"DEBUG Bloque: {' '.join(f'{b:02X}' for b in bloque)}, Canal={canal}, Status3={status3:02X}, Probe={self._is_probe_connected(status3)}")
                if canal is None:
                    continue
                if self._is_probe_connected(status3):
                    celsius = self._bytes_to_celsius(bloque[4], bloque[5], bloque[6])
                    canales_temp[canal] = celsius
                else:
                    if canales_temp[canal] is None:
                        canales_temp[canal] = None
            time.sleep(0.02)
            return [canales_temp['T1'], canales_temp['T2'], canales_temp['T3'], canales_temp['T4']]

    def _bytes_to_celsius(self, byte5, byte6, byte7):
        integer = (byte5 << 8) | byte6
        decimal = byte7 & 0x0F
        sign = (byte7 & 0x80) != 0
        fahrenheit = integer + decimal / 10.0
        if sign:
            fahrenheit = -fahrenheit
        celsius = (fahrenheit - 32) * 5.0 / 9.0
        return round(celsius, 2)

    def _is_probe_connected(self, status3):
        return bool(status3 & 0x08)


class DeviceManager:
    def __init__(self, device_list):
        self.devices = device_list
        self.rm = pyvisa.ResourceManager()

    def scan_and_assign(self):
        found_devices = self.rm.list_resources()
        for resource in found_devices:
            try:
                test_device = self.rm.open_resource(resource)
                idn = test_device.query("*IDN?").strip()
                for device in self.devices:
                    if device.serial in idn:
                        device.connect(self.rm, resource)
                        print(f"Assigned {device.id}")
            except Exception as e:
                print(f"Error with {resource}: {e}")

    def get_device_by_id(self, device_id):
        for device in self.devices:
            if device.id == device_id:
                return device
        return None
