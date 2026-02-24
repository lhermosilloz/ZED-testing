import pyzed.sl as sl
import sys

def main():
    # Create a camera object
    zed = sl.Camera()

    # Set configuration
    init_params = sl.InitParameters()

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    # Enable recording with filename
    output_path = sys.argv[1] if len(sys.argv) > 1 else "output.svo"
    recordingParameters = sl.RecordingParameters()
    recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H264
    recordingParameters.video_filename = output_path
    err = zed.enable_recording(recordingParameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Enable recording failed with H264: {err}")
        print("Trying H265...")
        recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H265
        err = zed.enable_recording(recordingParameters)
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"Enable recording failed with H265: {err}")
            zed.close()
            exit(-1)

    for i in range(10):
        # Each new frame is added to the SVO file
        zed.grab()

    # Disable recording
    zed.disable_recording()

if __name__ == "__main__":
    print("Starting video recording example")
    main()
    print("Done")