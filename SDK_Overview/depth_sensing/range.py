import pyzed.sl as sl
import math

def main():
    # Create a camera object
    zed = sl.Camera()

    # Init parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL_LIGHT
    init_params.coordinate_units = sl.UNIT.METER
    init_params.depth_minimum_distance = 0.15

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Error opening the camera: ", err)
        exit(1)

    # Retrieve Depth Data
    image = sl.Mat()
    depth_map = sl.Mat()
    point_cloud = sl.Mat()
    normal_map = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT)
        zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
        zed.retrieve_measure(normal_map, sl.MEASURE.NORMALS)
    
        # Get the depth value at the center of the image
        width = image.get_width()
        height = image.get_height()
        center_x = width // 2
        center_y = height // 2
        depth_value = depth_map.get_value(center_x, center_y)
        print(f"Depth value at the center: {depth_value} meters")

        # Get the depth value at the top-left corner of the image
        depth_value_top_left = depth_map.get_value(1, 1)
        print(f"Depth value at the top-left corner: {depth_value_top_left} meters")

        # Get the distance from the center of image using the point cloud
        point3D = point_cloud.get_value(center_x, center_y)
        print(f"3D coordinates at the center: {point3D[1][0]} m, {point3D[1][1]} m, {point3D[1][2]} m, {point3D[1][3]}")

        # Get the normal vector at the center of the image
        normal_vector = normal_map.get_value(center_x, center_y)
        print(f"Normal vector at the center: {normal_vector[1][0]} m, {normal_vector[1][1]} m, {normal_vector[1][2]} m")
    
if __name__ == "__main__":
    print("Starting depth sensing example...")
    main()
    print("Done")
