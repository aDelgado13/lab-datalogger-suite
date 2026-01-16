# Multimeter & Thermometer Datalogger

A Python-based datalogger capable of reading simultaneously from:

- A digital multimeter configured as a voltmeter  
- A digital multimeter configured as an ammeter  
- A four‑channel thermometer  

The program logs measurements at fixed intervals, stores them in a CSV file, and automatically generates an HTML report with interactive charts and a complete data table.

---

## 🚀 Features

- Simultaneous acquisition from multiple serial devices  
- Automatic configuration of multimeters (DC Voltage / DC Current)  
- Temperature acquisition from a 4‑channel thermometer  
- Configurable sampling interval and test duration  
- CSV export of all measurements  
- Automatic HTML report generation including:
  - Interactive charts (Chart.js)
  - Full data table
  - Dark‑theme layout  
- Error handling and sensor reconnection logic

---

## 📂 Project Structure

/project
│── main.py
│── class_definition.py
│── my_devices.py
│── measurements_YYYYMMDD_HHMMSS.csv


---

## 🛠️ Requirements

- Python 3.8+
- Standard libraries:
  - `time`
  - `datetime`
  - `csv`
  - `json`
  - `pathlib`
- Serial communication drivers for your instruments
- Supported hardware (my_Devices.py):
  - BK Precision multimeter (voltage)
  - BK Precision multimeter (current)
  - RS thermometer (4 channels)
- NIVisa software needed.
- 
---

## ▶️ How to Use

1. Configure your devices in `my_devices.py`
2. Set:
   - Start time  
   - Test duration  
   - Sampling interval  
3. Run the program:

```bash
python main.py
