import pyzed.sl as sl

def main():
    # Create a camera object
    zed = sl.Camera()

    # Set configuration
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    # The settings below can be set at runtime

    # Set exposure to 50% of camera framerate
    zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, 50)
    # Reset to auto exposure
    zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)

if __name__ == "__main__":
    print("Running Adjusting Camera Controls at runtime sample ...")
    main()
    print("Done")
