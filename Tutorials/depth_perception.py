import pyzed.sl as sl
import math

def main():
    # Create a ZED camera
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.sdk_verbose = True  # Enable verbose logging
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Set the depth mode to performance
    init_params.coordinate_units = sl.UNIT.MILLIMETER   # Use millimeter units

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Error {}, exit program".format(err))
        exit()

    # Capture 50 images and depth, then stop
    i = 0
    image = sl.Mat()
    depth = sl.Mat()
    point_cloud = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()
    while i < 50:
        # Grab an image
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns sl.ERROR_CODE.SUCCESS
            zed.retrieve_image(image, sl.VIEW.LEFT) # Get left image
            zed.retrieve_measure(depth, sl.MEASURE.DEPTH)   # Retrieve depth matrix
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)   # Retrieve colored point cloud
            
            # Pointcloud depths
            # Get and print distance value in mm at the center of the image
            # Measure distance camera - object
            x = round(image.get_width() / 2)
            y = round(image.get_height() / 2)
            err_p, point_cloud_value = point_cloud.get_value(x, y)
            pc_distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] + 
                                    point_cloud_value[1] * point_cloud_value[1] + 
                                    point_cloud_value[2] * point_cloud_value[2])
            print("Distance to camera at ({0}, {1}): {2} mm".format(x, y, pc_distance), end="\r")

            err_d, depth_value = depth.get_value(x, y)
            print("Distance to camera at ({0}, {1}): {2} mm".format(x, y, depth_value), end="\r")

            i = i + 1

    # Close the camera
    zed.close()

if __name__ == "__main__":
    main()