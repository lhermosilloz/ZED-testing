import os

import pyzed.sl as sl


def main():
    # Create camera object
    zed = sl.Camera()

    # Set configuration
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    sensors_data = sl.SensorsData()

    while zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.IMAGE) # Retrieve only frame synced data

        # Extract IMU data
        imu_data = sensors_data.get_imu_data()

        # Retrieve linear acceleration and angualar velocity
        linear_acceleration = imu_data.get_linear_acceleration()
        angular_velocity = imu_data.get_angular_velocity()

        os.system('cls' if os.name == 'nt' else 'clear')
        print("Linear acceleration: ", linear_acceleration)
        print("Angular velocity: ", angular_velocity)

if __name__ == "__main__":
    print("Running IMU sample ...")
    main()
    print("Done")
