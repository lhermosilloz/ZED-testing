import pyzed.sl as sl

def main():
    # Create camera object
    zed = sl.Camera()

    # Set configuration
    init_params = sl.InitParameters()
    init_params.set_from_stream("192.168.137.15", 30000)

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            pass

    

if __name__ == "__main__":
    main()
