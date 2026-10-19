#
# George Coffey's Photobooth program
#
# Connects to Bluetooth Low Energy remote and controls a canon camera
#
#
import os
import RPi.GPIO as GPIO
import asyncio
import gphoto2 as gp
from bleak import BleakClient
from escpos.printer import Usb
from PIL import Image
import signal

DEVICE_ADDRESS = "68:09:47:53:08:86"
UUID_SHUTTER = "beb5483e-36e1-4688-b7f5-ea07361b2600"
UUID_LIGHTS = "beb5483e-36e1-4688-b7f5-ea07361b2601"

pinLED1 = 4
pinLED2 = 3


def handle_lights(sender, data):
	print(f"Lights: {data.hex()}")

def handle_shutter(sender, data):
	print(f"Shutter: {data.hex()}")
	GPIO.output(pinLED2, GPIO.HIGH)
	print(request_shutter)
	filename = take_picture()
	print_picture(filename)
	print("print picture")
	GPIO.output(pinLED2, GPIO.LOW)

def take_picture():
	print("Snap Image")
	camera.init()
	print('Capturing image')
	file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
	print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
	target = os.path.join('/tmp', file_path.name)
	print('Copying image to', target)
	camera_file = camera.file_get(
	file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
	camera_file.save(target)
	camera.exit()
	return target

def print_picture(filename):
	image_resize(filename)
	printer.image(filename)
	printer.cut()

# original images are 5184X3456, new size is 576X384

def image_resize(filename):
	print('resize image')
	img = Image.open(filename)
	res = img.resize((576, 384))
	res.save(filename)

async def camera_check():
	print("Checking camera")

async def dmx_send():
	print("Sending DMX codes")

async def main():
	global client
	global printer
	global camera

	global request_shutter
	global request_shutter_last

#--------------- Shutdown Tasks

	loop = asyncio.get_running_loop()

	def shutdown_handler():
		print("\nSignal received! Tearing down tasks...")
		for task in asyncio.all_tasks(loop):
			task.cancel()
		GPIO.output(pinLED1, GPIO.LOW)
		GPIO.output(pinLED2, GPIO.LOW)

	loop.add_signal_handler(signal.SIGINT, shutdown_handler)

#--------------- Setup GPIO Config

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)         # Ignore warnings in our case
	GPIO.setup(pinLED1, GPIO.OUT)
	GPIO.setup(pinLED2, GPIO.OUT)
	GPIO.output(pinLED1, GPIO.LOW)
	GPIO.output(pinLED2, GPIO.LOW)


#---------------

	request_shutter = 0;

	camera = gp.Camera()

	printer = Usb(0x04b8, 0x0e32, 0, profile='TM-T20II')

#--------------- Create tasks to re-send DMX every so often

#--------------- Create task to check on camera

	task_cam = asyncio.create_task(camera_check())
	task_dmx = asyncio.create_task(dmx_send())

#--------------- Create task to print image once picture is taken

	try:
		while True:
			try:
				print(f"Connecting to {DEVICE_ADDRESS}...")

				async with BleakClient(DEVICE_ADDRESS) as client:
					print("Connected!")
					GPIO.output(pinLED1, GPIO.HIGH)

					await client.start_notify(
						UUID_SHUTTER,
						handle_shutter
					)

					await client.start_notify(
						UUID_LIGHTS,
						handle_lights
					)

					print("Waiting for changes...")

					while client.is_connected:
						await asyncio.sleep(1)
						await asyncio.create_task(camera_check())

					print("Remote disconnected.")
					GPIO.output(pinLED1, GPIO.LOW)

			except Exception as e:
				print(f"Error: {e}")

			print("Reconnecting in 5 seconds...")
			GPIO.output(pinLED1, GPIO.LOW)
			await asyncio.sleep(5)

	except asyncio.CancelledError:
		print("Main task cancelled via custom signal handler.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
