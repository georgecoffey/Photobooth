

# 1. Load your image (or read your video frame)
#image = cv2.imread('clove.jpg')
#image2 = cv2.imread('scull.jpg')

#

# 2. Create a named window explicitly allowing it to be normal/resizable
#cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# 3. Force the named window into full-screen mode
#cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)



import cv2
import time

window_name = "Full Screen Window"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


img = cv2.imread('wildflower.jpg')
cv2.imshow(window_name, img)

# List of image files to cycle through
image_paths = ['clove.jpg', 'scull.jpg', 'wildflower.jpg']

for path in image_paths:
	print(path)
	img = cv2.imread(path)
	cv2.imshow(window_name, img)

	# Wait 2 seconds (2000 ms) before moving to the next image
	# If the user presses 'q', exit early
	if cv2.waitKey(2000) & 0xFF == ord('q'):
		break

img = cv2.imread('clove.jpg')
cv2.imshow(window_name, img)
time.sleep(3)

cv2.destroyAllWindows()
