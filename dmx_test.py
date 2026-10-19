import time
import serial

PORT = '/dev/serial0'  # Windows example: "COM3"
BAUD = 250000

# DMX channel values: channels 1–5
channels = [255, 128, 64, 0, 255]

# A DMX packet consists of a start code (0) followed by channel data.
# Pad to 512 slots if you want a full DMX frame.
slots = channels + [0] * (512 - len(channels))
packet = bytes([0x00] + slots)

with serial.Serial(
    port=PORT,
    baudrate=BAUD,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    timeout=1,
) as ser:
    # Send DMX BREAK, then Mark After Break.
    ser.break_condition = True
    time.sleep(0.0001)  # 100 microseconds
    ser.break_condition = False
    time.sleep(0.000012)  # 12 microseconds
