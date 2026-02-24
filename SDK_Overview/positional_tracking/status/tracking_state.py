import pyzed.sl as sl

def main():
    # Create camera object
    zed = sl.Camera()
    zed.open()

    tracking_params = sl.PositionalTrackingParameters()
    zed.enable_positional_tracking(tracking_params)

    camera_pose = sl.Pose()

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            state = zed.get_position(camera_pose)

            print("Tracking state: ", state)
            print("Tracking state (string): ", state.name)

if __name__ == "__main__":
    print("Starting positional tracking state example...")
    main()
    print("Done")
