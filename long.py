import gphoto2 as gp
import time

def safe_low_light_capture(camera, exposure_time_seconds):
    # 1. Trigger the shutter button fully via configuration (Example for Canon)
    # This prevents the script from blocking prematurely on camera.capture()
    print("Triggering shutter...")

    # Alternatively, you can use camera.trigger_capture() if supported
    # but for Canon, eosremoterelease gives finer control.
    try:
        cfg = camera.get_config()
        remote_node = cfg.get_child_by_name('eosremoterelease')

        # 'Immediate Full Press' to shoot right away
        remote_node.set_value('Immediate Full Press')
        camera.set_config(cfg)
    except gp.GPhoto2Error:
        # Fallback for non-Canon cameras
        camera.trigger_capture()

    # 2. Wait out the exposure duration + buffer writing overhead safely
    # This keeps the I/O channel open without throwing errors
    extra_buffer_time = 5  # Give the camera an extra 5 seconds to process
    total_wait = exposure_time_seconds + extra_buffer_time

    print(f"Waiting {total_wait}s for low-light capture and storage to finish...")
    timeout = time.time() + total_wait

    while time.time() < timeout:
        # Check if the camera sent a 'File Added' event
        event_type, event_data = camera.wait_for_event(1000) # wait 1000ms per iteration

        if event_type == gp.GP_EVENT_FILE_ADDED:
            print(f"Success! Image captured: {event_data.name} in {event_data.folder}")

            # Release the shutter button back to normal (if using eosremoterelease)
            try:
                remote_node.set_value('None')
                camera.set_config(cfg)
            except:
                pass

            return event_data

    raise TimeoutError("Camera took too long to return the image. Check if Noise Reduction is on.")

safe_low_light_capture();
