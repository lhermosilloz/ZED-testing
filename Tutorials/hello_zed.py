import pyzed.sl as sl

def main():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit()

    # Get camera information (serial number)
    zed_serial = zed.get_camera_information().serial_number
    print("Hello, this is my serial number: {}".format(zed_serial))

    zed.close()

if __name__ == "__main__":
    main()