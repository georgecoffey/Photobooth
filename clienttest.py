#
# George Coffey's Photobooth program
#
# Connects to Bluetooth Low Energy remote and controls a canon camera
#
#
import os
import asyncio
import gphoto2 as gp
from bleak import BleakClient
from escpos.printer import Usb
from PIL import Image


DEVICE_ADDRESS = "68:09:47:53:08:86"
UUID_SHUTTER = "beb5483e-36e1-4688-b7f5-ea07361b2600"
UUID_LIGHTS = "beb5483e-36e1-4688-b7f5-ea07361b2601"


async def background_worker():
    """Simulates doing other tasks while connected to the BLE device."""
    while True:
        print("[Worker] Doing other background work...")
        await asyncio.sleep(0.25)


async def ble_client_task(address):
    """Manages the BleakClient connection and listens/reads data."""
    async with BleakClient(address) as client:
        print(f"[BLE] Connected to {address}: {client.is_connected}")
        while client.is_connected:
            # Example: read a characteristic or wait for notifications
            value = await client.read_gatt_char(UUID_SHUTTER)
            print(f"[BLE] Read value: {value.decode()}")
            await asyncio.sleep(5)


async def main():
    # Run both the BLE client and the background task concurrently
    await asyncio.gather(
        ble_client_task(DEVICE_ADDRESS),
        background_worker(),
    )


if __name__ == "__main__":
    asyncio.run(main())
