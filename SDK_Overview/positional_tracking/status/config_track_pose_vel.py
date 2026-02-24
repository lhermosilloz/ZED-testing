import pyzed.sl as sl

def main():
    # Create a camera object
    zed = sl.Camera()

    # Init params
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.coordinate_units = sl.UNIT.METER

    # Open
    op_err = zed.open(init_params)
    if op_err != sl.ERROR_CODE.SUCCESS:
        print("Error opening the camera: ", op_err)
        exit(1)

    # Enable positional tracking
    tracking_params = sl.PositionalTrackingParameters()
    track_err = zed.enable_positional_tracking(tracking_params)

    # Get the runtime parameters
    zed_pose = sl.Pose()
    runtime_parameters = sl.RuntimeParameters()

    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # Get the pose of the camera relative to the world frame
        state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

        # Display translation and timestamp
        py_translation = sl.Translation()
        tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
        ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
        tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
        print("Translation: tx: {0}, ty: {1}, tz: {2}, timestamp: {3}\n".format(tx, ty, tz, zed_pose.timestamp))

        # Display orientation quaternion
        py_orientation = sl.Orientation()
        ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
        oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
        oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
        ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
        print("Orientation: ox: {0}, oy:  {1}, oz: {2}, ow: {3}\n".format(ox, oy, oz, ow))

        # Get the pose of the camera realtive to the world frame
        state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.CAMERA)

        # Display linear velocity
        vx = zed_pose.twist[0]
        vy = zed_pose.twist[1]
        vz = zed_pose.twist[2]
        print("Translation: vx: {0}, vy:  {1}, vz:  {2}, timestamp: {3}\n".format(vx, vy, vz, zed_pose.timestamp))

        # Display angular velocity
        x = zed_pose.twist[3]
        y = zed_pose.twist[4]
        z = zed_pose.twist[5]
        print("Orientation: x: {0}, y: {1}, z: {2}\n".format(x, y, z))

if __name__ == "__main__":
    print("Starting configuration tracker for pose and velocity...")
    main()
    print("Done")