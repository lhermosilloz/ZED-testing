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

    # Get the camera parameters from CalibrationParameters

    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters

    # Focal length of the left eye in pixels
    print("Focal length of left eye in pixels: ", calibration_params.left_cam.fx)

    # First radial distortion coefficient
    print("First radial distortion coefficient: ", calibration_params.left_cam.disto[0])

    # Translation between left and right eye on x-axis
    print("Translation between left and right eye on x-axis: ", calibration_params.stereo_transform.get_translation().get()[0])

    # Horizontal field of view of the left eye in degrees
    print("Horizontal field of view of left eye in degrees: ", calibration_params.left_cam.h_fov)

if __name__ == "__main__":
    print("Running Camera Parameters sample ...")
    main()
    print("Done")