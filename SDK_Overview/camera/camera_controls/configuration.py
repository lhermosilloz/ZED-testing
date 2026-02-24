import pyzed.sl as sl

def main():
    # Create ZED Camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

if __name__ == "__main__":
    print("Running Camera Controls Config sample ...")
    main()
    print("Done")