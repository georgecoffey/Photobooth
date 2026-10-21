import io
import cv2
import gphoto2 as gp
import numpy as np
from PIL import Image, ImageOps

def main():
    # Initialize gphoto2 camera
    camera = gp.Camera()
    camera.init()

    cv2.namedWindow('Live Preview', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Live Preview', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        while True:
            # Capture preview frame from camera into memory
            camera_file = camera.capture_preview()
            file_data = camera_file.get_data_and_size()

            # Convert binary data to a PIL Image, then to a NumPy array for OpenCV
            image_stream = io.BytesIO(file_data)
            pil_image = Image.open(image_stream).convert('RGB')
            frame = np.array(ImageOps.mirror(pil_image))

            # Convert RGB (PIL) to BGR (OpenCV format)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.imshow('Live Preview', frame_bgr)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.exit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
