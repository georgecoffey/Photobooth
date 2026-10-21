#
# George Coffey's Photobooth program
#
# Connects to Bluetooth Low Energy remote and controls a canon camera
#
#
import time
import signal
import os
import io
import cv2
import asyncio
import numpy as np
import gphoto2 as gp
import RPi.GPIO as GPIO
from bleak import BleakClient
from escpos.printer import Usb
from PIL import Image, ImageOps

DEVICE_ADDRESS = "68:09:47:53:08:86"
UUID_SHUTTER = "beb5483e-36e1-4688-b7f5-ea07361b2600"
UUID_LIGHTS = "beb5483e-36e1-4688-b7f5-ea07361b2601"

pinLED1 = 4
pinLED2 = 3

window_name = "Photobooth"

event_texts = {
	gp.GP_EVENT_CAPTURE_COMPLETE: "Capture Complete",
        gp.GP_EVENT_FILE_ADDED: "File Added",
	gp.GP_EVENT_FOLDER_ADDED: "Folder Added",
	gp.GP_EVENT_TIMEOUT: "Timeout",
	}

def event_text(event_type):
	if event_type in event_texts:
		return event_texts[event_type]
	return "Unknown Event"

def handle_lights(sender, data):
	print(f"Lights: {data.hex()}")

def handle_shutter(sender, data):
	request_shutter = 1
	asyncio.sleep(0.2)
	print(f"Shutter: {data.hex()}")
	GPIO.output(pinLED2, GPIO.HIGH)
	print(request_shutter)
	filename = take_picture()
	print_picture(filename)
	print("print picture")
	GPIO.output(pinLED2, GPIO.LOW)
	request_shutter = 0

def take_picture():
	print('Taking Picture')
	#----- take a picture
	request_shutter = 1
	file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
	print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
	target = os.path.join('/tmp', file_path.name)
	print('Copying image to', target)
	camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
	camera_file.save(target)

	#----- Clear out camera event queue to prevent errors

	typ,data = camera.wait_for_event(200)
	while typ != gp.GP_EVENT_TIMEOUT:

		print("Event: %s, data: %s" % (event_text(typ),data))

		if typ == gp.GP_EVENT_FILE_ADDED:
			fn = os.path.join(data.folder,data.name)
			print("New file: %s" % fn)
			#self.download_file(fn)

		#try to grab another event
		typ,data = camera.wait_for_event(1)

	# time.sleep(0.2)
	# camera.exit()
	# time.sleep(0.2)
	# camera.init()


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

#--------------- Check if the damera is busy

def camera_busy(camera):
	try:
		# Perform a lightweight operation to "poke" the camera
		camera.get_summary()
		return False
	except gp.GPhoto2Error as e:
		# Check if the error code matches the camera busy definition (-110)
		if e.code == gp.GP_ERROR_CAMERA_BUSY:
			return True
		else:
		# Re-raise if it's a different kind of error (e.g., disconnected)
			raise e

#--------------- Get preview image

async def camera_check():
	print("preview image")
	asyncio.sleep(1)
	if request_shutter == 0:
		#------ Capture preview frame from camera

		camera_file = camera.capture_preview()
		file_data = camera_file.get_data_and_size()

		#------ Convert image to a PIL Image, then to a NumPy array for OpenCV, then convert the color

		image_stream = io.BytesIO(file_data)
		pil_image = Image.open(image_stream).convert('RGB')
		frame = np.array(ImageOps.mirror(pil_image))
		frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

		#------ Display the image

		cv2.imshow(window_name , frame_bgr)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			print("q pressed")

	else:
		print("Camera Busy")



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
		camera.exit()

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

#--------------- Setup Fullscreen window

	indow_name = "Full Screen Window"
	cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
	cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

	img = cv2.imread('wildflower.jpg')
	cv2.imshow(window_name, img)
	cv2.waitKey(1)

#--------------- Setup Camera

	request_shutter = 0;

	camera = gp.Camera()
	camera.init()


	printer = Usb(0x04b8, 0x0e32, 0, profile='TM-T20II')

#--------------- Create tasks to re-send DMX every so often

#--------------- Create task to check on camera


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
						await asyncio.sleep(2)
						await camera_check()

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
