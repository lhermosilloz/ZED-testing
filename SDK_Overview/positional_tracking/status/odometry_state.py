import pyzed.sl as sl

def main():
    # Create a camera object
    zed = sl.Camera()
    zed.open()

    tracking_params = sl.PositionalTrackingParameters()
    zed.enable_positional_tracking(tracking_params)

    tracking_status = sl.PositionalTrackingStatus()

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            tracking_status = zed.get_positional_tracking_status()

            odom_status = tracking_status.odometry_status

            print("Odometry state: ", odom_status)
            print("Odometry state (string): ", odom_status.name)


if __name__ == "__main__":
    print("Starting odometry state example...")
    main()
    print("Done")
