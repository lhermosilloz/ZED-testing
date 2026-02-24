import pyzed.sl as sl
import keyboard

def main():
    # Create camera object
    zed = sl.Camera()

    # Set configuration
    init_params = sl.InitParameters()

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    # Set the streaming parameters
    stream = sl.StreamingParameters()
    stream.codec = sl.STREAMING_CODEC.H264
    stream.bitrate = 8000
    stream.port = 30000

    # Enable streaming with the streaming parameters
    err = zed.enable_streaming(stream)

    while True:
        if keyboard.is_pressed('q'):
            break
        zed.grab()
    
    zed.disable_streaming()

if __name__ == "__main__":
    print("Starting streaming example")
    main()
    print("Done")
