import pyzed.sl as sl

def main():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    # Use a right-handed Y-up coordinate system
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.coordinate_units = sl.UNIT.METER    # Set units in meters

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Enable positional tracking with default parameters
    tracking_parameters = sl.PositionalTrackingParameters()
    err = zed.enable_positional_tracking(tracking_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Track the camera position during 1000 frames
    i = 0
    zed_pose = sl.Pose()
    sensors_data = sl.SensorsData()
    runtime_parameters = sl.RuntimeParameters()

    while i < 200:
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Get the pose of the left eye of the camera with reference to the world frame
            zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

            # Display the translation and timestamp
            py_translation = sl.Translation()
            tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
            ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
            tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
            print("Translation: Tx: {0}, Ty: {1}, Tz: {2}, Timestamp: {3}\n".format(tx, ty, tz, zed_pose.timestamp.get_milliseconds()))

            # Display the orientation quaternion
            py_orientation = sl.Orientation()
            ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
            oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
            oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
            ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
            print("Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

        
            zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.IMAGE)
            zed_imu = sensors_data.get_imu_data()
            # Get IMU orientation
            zed_imu_pose = sl.Transform()
            ox = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[0], 3)
            oy = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[1], 3)
            oz = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[2], 3)
            ow = round(zed_imu.get_pose(zed_imu_pose).get_orientation().get()[3], 3)
            print("IMU Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))
            # Get IMU acceleration
            acceleration = [0,0,0]
            zed_imu.get_linear_acceleration(acceleration)
            ax = round(acceleration[0], 3)
            ay = round(acceleration[1], 3)
            az = round(acceleration[2], 3)
            print("IMU Acceleration: Ax: {0}, Ay: {1}, Az {2}\n".format(ax, ay, az))

            i = i + 1

    # Disable positional tracking and close the camera
    zed.disable_positional_tracking()
    zed.close()

if __name__ == "__main__":
    main()