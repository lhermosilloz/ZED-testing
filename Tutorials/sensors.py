import pyzed.sl as sl

def main():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    # No depth computation is required
    init_params.depth_mode = sl.DEPTH_MODE.NONE

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS :
        print(repr(err))
        zed.close()
        exit(1)

    sensors_data = sl.SensorsData()

    ts_handler = sl.Timestamp()

    while zed.grab() == sl.ERROR_CODE_SUCCESS:
        zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)   # TIME_REFERENCE.CURRENT extracts most recent data available

    