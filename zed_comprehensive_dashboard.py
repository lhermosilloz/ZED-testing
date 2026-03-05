"""
ZED Camera Comprehensive Real-Time Dashboard
============================================
A comprehensive dashboard showing all ZED camera capabilities in real-time:
- Live camera feed (left/right cameras)
- Depth sensing and point cloud visualization
- Positional tracking with 3D trajectory
- IMU sensor data (acceleration, gyroscope)
- Camera controls and settings
- Performance metrics and diagnostics
- Recording and streaming controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import pyzed.sl as sl
import threading
import time
from collections import deque
from datetime import datetime
import os


class ZEDComprehensiveDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ZED Camera Comprehensive Dashboard")
        self.root.geometry("1600x1000")
        
        # ZED Camera initialization
        self.zed = sl.Camera()
        self.init_params = sl.InitParameters()
        self.runtime_params = sl.RuntimeParameters()
        
        # Data storage for real-time plotting
        self.max_data_points = 100
        self.pose_history = deque(maxlen=self.max_data_points)
        self.imu_accel_data = {'x': deque(maxlen=self.max_data_points),
                              'y': deque(maxlen=self.max_data_points), 
                              'z': deque(maxlen=self.max_data_points)}
        self.imu_gyro_data = {'x': deque(maxlen=self.max_data_points),
                             'y': deque(maxlen=self.max_data_points),
                             'z': deque(maxlen=self.max_data_points)}
        self.timestamps = deque(maxlen=self.max_data_points)
        self.fps_data = deque(maxlen=50)
        
        # Control variables
        self.is_running = False
        self.is_recording = False
        self.is_streaming = False
        self.camera_thread = None
        
        # ZED objects for data
        self.image_left = sl.Mat()
        self.image_right = sl.Mat()
        self.depth_image = sl.Mat()
        self.point_cloud = sl.Mat()
        self.sensors_data = sl.SensorsData()
        self.pose = sl.Pose()
        
        self.setup_ui()
        self.initialize_camera()
        
    def setup_ui(self):
        """Setup the complete dashboard UI"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_live_feed_tab()
        self.create_depth_tab()
        self.create_tracking_tab()
        self.create_sensors_tab()
        self.create_controls_tab()
        self.create_diagnostics_tab()
        
        # Control panel at bottom
        self.create_control_panel()
        
    def create_live_feed_tab(self):
        """Live camera feed tab with stereo view"""
        self.feed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.feed_frame, text="Live Feed")
        
        # Camera feed display
        feed_container = ttk.LabelFrame(self.feed_frame, text="Stereo Camera Feed")
        feed_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left and Right camera labels
        camera_frame = ttk.Frame(feed_container)
        camera_frame.pack(fill='both', expand=True)
        
        left_frame = ttk.LabelFrame(camera_frame, text="Left Camera")
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        right_frame = ttk.LabelFrame(camera_frame, text="Right Camera")
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        self.left_camera_label = tk.Label(left_frame, bg='black', text='Left Camera\nNo Signal', 
                                         fg='white', font=('Arial', 12))
        self.left_camera_label.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.right_camera_label = tk.Label(right_frame, bg='black', text='Right Camera\nNo Signal', 
                                          fg='white', font=('Arial', 12))
        self.right_camera_label.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Camera info panel
        info_frame = ttk.LabelFrame(self.feed_frame, text="Camera Information")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.camera_info_text = tk.Text(info_frame, height=6, font=('Consolas', 9))
        self.camera_info_text.pack(fill='x', padx=5, pady=5)
        
    def create_depth_tab(self):
        """Depth sensing and point cloud visualization"""
        self.depth_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.depth_frame, text="Depth Sensing")
        
        # Depth visualization
        depth_container = ttk.LabelFrame(self.depth_frame, text="Depth Map & Point Cloud")
        depth_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for depth visualization
        self.depth_fig = Figure(figsize=(12, 6), dpi=80)
        
        # Depth map subplot
        self.depth_ax = self.depth_fig.add_subplot(121)
        self.depth_ax.set_title('Depth Map')
        self.depth_ax.set_xlabel('X (pixels)')
        self.depth_ax.set_ylabel('Y (pixels)')
        
        # Distance plot subplot  
        self.distance_ax = self.depth_fig.add_subplot(122)
        self.distance_ax.set_title('Center Point Distance Over Time')
        self.distance_ax.set_xlabel('Time')
        self.distance_ax.set_ylabel('Distance (mm)')
        self.distance_ax.grid(True)
        
        self.depth_canvas = FigureCanvasTkAgg(self.depth_fig, depth_container)
        self.depth_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Depth controls
        depth_controls = ttk.Frame(self.depth_frame)
        depth_controls.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(depth_controls, text="Depth Mode:").pack(side='left', padx=5)
        self.depth_mode_var = tk.StringVar(value="PERFORMANCE")
        depth_combo = ttk.Combobox(depth_controls, textvariable=self.depth_mode_var,
                                  values=["PERFORMANCE", "QUALITY", "ULTRA"])
        depth_combo.pack(side='left', padx=5)
        depth_combo.bind('<<ComboboxSelected>>', self.change_depth_mode)
        
        # Distance storage
        self.center_distances = deque(maxlen=self.max_data_points)
        
    def create_tracking_tab(self):
        """Positional tracking visualization"""
        self.tracking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tracking_frame, text="Positional Tracking")
        
        # Tracking visualization
        tracking_container = ttk.LabelFrame(self.tracking_frame, text="Camera Pose & Trajectory")
        tracking_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for tracking
        self.tracking_fig = Figure(figsize=(12, 8), dpi=80)
        
        # 3D trajectory plot
        self.trajectory_ax = self.tracking_fig.add_subplot(221, projection='3d')
        self.trajectory_ax.set_title('3D Camera Trajectory')
        self.trajectory_ax.set_xlabel('X (m)')
        self.trajectory_ax.set_ylabel('Y (m)')
        self.trajectory_ax.set_zlabel('Z (m)')
        
        # Position over time
        self.pos_x_ax = self.tracking_fig.add_subplot(222)
        self.pos_x_ax.set_title('X Position Over Time')
        self.pos_x_ax.set_ylabel('X (m)')
        self.pos_x_ax.grid(True)
        
        self.pos_y_ax = self.tracking_fig.add_subplot(223)
        self.pos_y_ax.set_title('Y Position Over Time')
        self.pos_y_ax.set_ylabel('Y (m)')
        self.pos_y_ax.grid(True)
        
        self.pos_z_ax = self.tracking_fig.add_subplot(224)
        self.pos_z_ax.set_title('Z Position Over Time')
        self.pos_z_ax.set_ylabel('Z (m)')
        self.pos_z_ax.set_xlabel('Time')
        self.pos_z_ax.grid(True)
        
        self.tracking_fig.tight_layout()
        
        self.tracking_canvas = FigureCanvasTkAgg(self.tracking_fig, tracking_container)
        self.tracking_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Tracking controls
        tracking_controls = ttk.Frame(self.tracking_frame)
        tracking_controls.pack(fill='x', padx=5, pady=5)
        
        self.tracking_enabled = tk.BooleanVar()
        ttk.Checkbutton(tracking_controls, text="Enable Positional Tracking", 
                       variable=self.tracking_enabled, command=self.toggle_tracking).pack(side='left', padx=5)
        
        ttk.Button(tracking_controls, text="Reset Tracking", 
                   command=self.reset_tracking).pack(side='left', padx=5)
        
    def create_sensors_tab(self):
        """IMU and sensor data visualization"""
        self.sensors_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sensors_frame, text="Sensors (IMU)")
        
        # IMU visualization
        imu_container = ttk.LabelFrame(self.sensors_frame, text="IMU Data - Accelerometer & Gyroscope")
        imu_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for IMU data
        self.imu_fig = Figure(figsize=(12, 8), dpi=80)
        
        # Acceleration plots
        self.accel_x_ax = self.imu_fig.add_subplot(231)
        self.accel_x_ax.set_title('Acceleration X')
        self.accel_x_ax.set_ylabel('m/s²')
        self.accel_x_ax.grid(True)
        
        self.accel_y_ax = self.imu_fig.add_subplot(232)
        self.accel_y_ax.set_title('Acceleration Y')
        self.accel_y_ax.set_ylabel('m/s²')
        self.accel_y_ax.grid(True)
        
        self.accel_z_ax = self.imu_fig.add_subplot(233)
        self.accel_z_ax.set_title('Acceleration Z')
        self.accel_z_ax.set_ylabel('m/s²')
        self.accel_z_ax.grid(True)
        
        # Gyroscope plots
        self.gyro_x_ax = self.imu_fig.add_subplot(234)
        self.gyro_x_ax.set_title('Angular Velocity X')
        self.gyro_x_ax.set_ylabel('rad/s')
        self.gyro_x_ax.set_xlabel('Time')
        self.gyro_x_ax.grid(True)
        
        self.gyro_y_ax = self.imu_fig.add_subplot(235)
        self.gyro_y_ax.set_title('Angular Velocity Y')
        self.gyro_y_ax.set_ylabel('rad/s')
        self.gyro_y_ax.set_xlabel('Time')
        self.gyro_y_ax.grid(True)
        
        self.gyro_z_ax = self.imu_fig.add_subplot(236)
        self.gyro_z_ax.set_title('Angular Velocity Z')
        self.gyro_z_ax.set_ylabel('rad/s')
        self.gyro_z_ax.set_xlabel('Time')
        self.gyro_z_ax.grid(True)
        
        self.imu_fig.tight_layout()
        
        self.imu_canvas = FigureCanvasTkAgg(self.imu_fig, imu_container)
        self.imu_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_controls_tab(self):
        """Camera controls and settings"""
        self.controls_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.controls_frame, text="Camera Controls")
        
        # Camera settings
        settings_frame = ttk.LabelFrame(self.controls_frame, text="Camera Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Resolution control
        res_frame = ttk.Frame(settings_frame)
        res_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(res_frame, text="Resolution:").pack(side='left')
        self.resolution_var = tk.StringVar(value="HD1080")
        resolution_combo = ttk.Combobox(res_frame, textvariable=self.resolution_var, width=15,
                                       values=["HD2K", "HD1080", "HD720", "VGA"])
        resolution_combo.pack(side='left', padx=10)
        
        # FPS control
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(fps_frame, text="FPS:").pack(side='left')
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(fps_frame, textvariable=self.fps_var, width=15,
                                values=["15", "30", "60", "100"])
        fps_combo.pack(side='left', padx=10)
        
        # Exposure control
        exposure_frame = ttk.Frame(settings_frame)
        exposure_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(exposure_frame, text="Exposure:").pack(side='left')
        self.exposure_var = tk.IntVar(value=0)
        exposure_scale = ttk.Scale(exposure_frame, from_=0, to=100, orient='horizontal',
                                  variable=self.exposure_var, command=self.update_exposure)
        exposure_scale.pack(side='left', fill='x', expand=True, padx=10)
        self.exposure_label = ttk.Label(exposure_frame, text="Auto")
        self.exposure_label.pack(side='left')
        
        # Brightness control
        brightness_frame = ttk.Frame(settings_frame)  
        brightness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(brightness_frame, text="Brightness:").pack(side='left')
        self.brightness_var = tk.IntVar(value=4)
        brightness_scale = ttk.Scale(brightness_frame, from_=0, to=8, orient='horizontal',
                                    variable=self.brightness_var, command=self.update_brightness)
        brightness_scale.pack(side='left', fill='x', expand=True, padx=10)
        self.brightness_label = ttk.Label(brightness_frame, text="4")
        self.brightness_label.pack(side='left')
        
        # Recording controls
        recording_frame = ttk.LabelFrame(self.controls_frame, text="Recording & Streaming")
        recording_frame.pack(fill='x', padx=5, pady=5)
        
        record_controls = ttk.Frame(recording_frame)
        record_controls.pack(fill='x', padx=5, pady=5)
        
        self.record_btn = ttk.Button(record_controls, text="Start Recording", 
                                    command=self.toggle_recording)
        self.record_btn.pack(side='left', padx=5)
        
        self.stream_btn = ttk.Button(record_controls, text="Start Streaming", 
                                    command=self.toggle_streaming)
        self.stream_btn.pack(side='left', padx=5)
        
        # Recording settings
        rec_settings = ttk.Frame(recording_frame)
        rec_settings.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(rec_settings, text="Output Path:").pack(side='left')
        self.output_path_var = tk.StringVar(value="./recordings/")
        ttk.Entry(rec_settings, textvariable=self.output_path_var, width=30).pack(side='left', padx=5, fill='x', expand=True)
        
    def create_diagnostics_tab(self):
        """Performance diagnostics and system info"""
        self.diagnostics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.diagnostics_frame, text="Diagnostics")
        
        # Performance metrics
        perf_frame = ttk.LabelFrame(self.diagnostics_frame, text="Performance Metrics")
        perf_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for performance
        self.perf_fig = Figure(figsize=(10, 6), dpi=80)
        
        # FPS plot
        self.fps_ax = self.perf_fig.add_subplot(111)
        self.fps_ax.set_title('Real-time FPS')
        self.fps_ax.set_ylabel('FPS')
        self.fps_ax.set_xlabel('Time')
        self.fps_ax.grid(True)
        
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, perf_frame)
        self.perf_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # System info
        info_frame = ttk.LabelFrame(self.diagnostics_frame, text="System Information")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.system_info_text = tk.Text(info_frame, height=8, font=('Consolas', 9))
        self.system_info_text.pack(fill='x', padx=5, pady=5)
        
    def create_control_panel(self):
        """Main control panel at bottom"""
        control_panel = ttk.Frame(self.root)
        control_panel.pack(fill='x', padx=5, pady=5)
        
        # Main controls
        self.start_btn = ttk.Button(control_panel, text="Start Camera", 
                                   command=self.start_camera, style='Accent.TButton')
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(control_panel, text="Stop Camera", 
                                  command=self.stop_camera, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label = ttk.Label(control_panel, text="Status: Camera not initialized")
        self.status_label.pack(side='right', padx=5)
        
    def initialize_camera(self):
        """Initialize ZED camera with default parameters"""
        try:
            # Set comprehensive camera parameters for stable connection
            self.init_params.camera_resolution = sl.RESOLUTION.HD1080
            self.init_params.camera_fps = 30
            self.init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
            self.init_params.coordinate_units = sl.UNIT.METER
            self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
            
            # Enable sensors and set stability parameters
            self.init_params.sensors_required = True
            self.init_params.grab_compute_capping_fps = 30
            self.init_params.enable_image_enhancement = True
            
            # Set runtime parameters for stable operation
            self.runtime_params.sensing_mode = sl.SENSING_MODE.STANDARD
            self.runtime_params.confidence_threshold = 100
            self.runtime_params.texture_confidence_threshold = 100
            
            self.status_label.config(text="Status: Camera initialized, ready to start")
            self.update_system_info()
            
        except Exception as e:
            self.status_label.config(text=f"Status: Initialization error - {str(e)}")
            
    def start_camera(self):
        """Start the camera and data acquisition"""
        if self.is_running:
            return
            
        try:
            # Open camera with retry logic
            print("Opening ZED camera...")
            err = self.zed.open(self.init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                error_msg = f"Failed to open camera: {repr(err)}"
                print(error_msg)
                messagebox.showerror("Camera Error", error_msg)
                return
            
            print("ZED camera opened successfully")
            
            # Enable positional tracking if requested
            if self.tracking_enabled.get():
                tracking_params = sl.PositionalTrackingParameters()
                tracking_params.enable_area_memory = True
                err = self.zed.enable_positional_tracking(tracking_params)
                if err != sl.ERROR_CODE.SUCCESS:
                    print(f"Warning: Failed to enable tracking: {repr(err)}")
                    messagebox.showwarning("Warning", f"Failed to enable tracking: {repr(err)}")
                else:
                    print("Positional tracking enabled")
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="Status: Camera running")
            
            # Start camera thread
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
            # Start real-time updates
            self.update_displays()
            
        except Exception as e:
            error_msg = f"Failed to start camera: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def stop_camera(self):
        """Stop the camera and data acquisition"""
        print("Stopping camera...")
        self.is_running = False
        
        # Wait for camera thread to finish
        if self.camera_thread and self.camera_thread.is_alive():
            print("Waiting for camera thread to finish...")
            self.camera_thread.join(timeout=5)  # Increased timeout
            
        # Disable tracking if enabled
        try:
            if self.tracking_enabled.get():
                self.zed.disable_positional_tracking()
                print("Positional tracking disabled")
        except Exception as e:
            print(f"Error disabling tracking: {e}")
            
        # Close camera
        try:
            self.zed.close()
            print("Camera closed successfully")
        except Exception as e:
            print(f"Error closing camera: {e}")
        
        # Update UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Camera stopped")
        
    def handle_camera_error(self):
        """Handle camera errors by stopping and notifying user"""
        print("Handling camera error...")
        self.stop_camera()
        messagebox.showerror("Camera Error", 
                           "Camera connection lost or too many errors occurred. "
                           "Please check the camera connection and try restarting.")
        
    def camera_loop(self):
        """Main camera data acquisition loop"""
        frame_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        print("Camera loop started")
        
        while self.is_running:
            try:
                # Grab frame with proper error handling
                grab_result = self.zed.grab(self.runtime_params)
                
                if grab_result == sl.ERROR_CODE.SUCCESS:
                    consecutive_errors = 0  # Reset error counter on success
                    
                    try:
                        # Get images
                        self.zed.retrieve_image(self.image_left, sl.VIEW.LEFT)
                        self.zed.retrieve_image(self.image_right, sl.VIEW.RIGHT)
                        
                        # Get depth data
                        self.zed.retrieve_measure(self.depth_image, sl.MEASURE.DEPTH)
                        self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA)
                        
                        # Get sensor data
                        self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.IMAGE)
                        
                        # Get pose if tracking enabled
                        if self.tracking_enabled.get():
                            self.zed.get_position(self.pose, sl.REFERENCE_FRAME.WORLD)
                        
                        # Calculate FPS
                        current_time = time.time()
                        if current_time > frame_time:
                            fps = 1.0 / (current_time - frame_time)
                            self.fps_data.append(fps)
                        frame_time = current_time
                        
                        # Store timestamp
                        self.timestamps.append(datetime.now())
                        
                    except Exception as data_error:
                        print(f"Data retrieval error: {data_error}")
                        consecutive_errors += 1
                        
                elif grab_result == sl.ERROR_CODE.CAMERA_NOT_DETECTED:
                    print("Camera disconnected!")
                    break
                    
                else:
                    consecutive_errors += 1
                    print(f"Grab failed: {repr(grab_result)} (consecutive errors: {consecutive_errors})")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"Too many consecutive errors ({consecutive_errors}), stopping camera")
                        break
                
                # Proper timing - match camera FPS
                time.sleep(1.0 / 30.0)  # 30 FPS = ~33ms between frames
                
            except Exception as e:
                consecutive_errors += 1
                print(f"Camera loop error: {e} (consecutive errors: {consecutive_errors})")
                
                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}), stopping camera")
                    break
                    
                time.sleep(0.1)  # Wait before retry
        
        print("Camera loop ended")
        
        # Ensure camera is properly stopped if loop exits due to errors
        if self.is_running:
            self.root.after(0, self.handle_camera_error)
                
    def update_displays(self):
        """Update all display elements"""
        if not self.is_running:
            return
            
        try:
            self.update_camera_feeds()
            self.update_depth_visualization()
            self.update_tracking_visualization()
            self.update_sensor_visualization()
            self.update_performance_metrics()
            
        except Exception as e:
            print(f"Display update error: {e}")
            
        # Schedule next update
        self.root.after(100, self.update_displays)
        
    def update_camera_feeds(self):
        """Update camera feed displays"""
        try:
            if self.image_left.get_data().size > 0:
                # Convert left image
                left_img = self.image_left.get_data()[:, :, :3]  # Remove alpha channel
                left_img = cv2.resize(left_img, (400, 300))
                left_img = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage and display
                import PIL.Image
                import PIL.ImageTk
                left_pil = PIL.Image.fromarray(left_img)
                left_photo = PIL.ImageTk.PhotoImage(left_pil)
                self.left_camera_label.configure(image=left_photo, text="")
                self.left_camera_label.image = left_photo
                
            if self.image_right.get_data().size > 0:
                # Convert right image  
                right_img = self.image_right.get_data()[:, :, :3]  # Remove alpha channel
                right_img = cv2.resize(right_img, (400, 300))
                right_img = cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage and display
                import PIL.Image
                import PIL.ImageTk
                right_pil = PIL.Image.fromarray(right_img)
                right_photo = PIL.ImageTk.PhotoImage(right_pil)
                self.right_camera_label.configure(image=right_photo, text="")
                self.right_camera_label.image = right_photo
                
            # Update camera info
            self.update_camera_info()
            
        except Exception as e:
            print(f"Camera feed update error: {e}")
            
    def update_camera_info(self):
        """Update camera information display"""
        try:
            info_text = f"""Camera Information:
Resolution: {self.image_left.get_width()} x {self.image_left.get_height()}
FPS: {self.fps_data[-1]:.1f} (Current) | {np.mean(self.fps_data):.1f} (Average)
Timestamp: {self.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()} ms
Frame Count: {len(self.timestamps)}
Depth Mode: {self.depth_mode_var.get()}
Tracking: {'Enabled' if self.tracking_enabled.get() else 'Disabled'}
"""
            self.camera_info_text.delete(1.0, tk.END)
            self.camera_info_text.insert(1.0, info_text)
            
        except Exception as e:
            print(f"Camera info update error: {e}")
            
    def update_depth_visualization(self):
        """Update depth map and distance measurements"""
        try:
            if self.depth_image.get_data().size > 0:
                # Get depth data
                depth_data = self.depth_image.get_data()
                
                # Get center point distance
                h, w = depth_data.shape
                center_x, center_y = w // 2, h // 2
                center_distance = depth_data[center_y, center_x]
                
                if not np.isnan(center_distance) and not np.isinf(center_distance):
                    self.center_distances.append(center_distance)
                
                # Update depth map display
                self.depth_ax.clear()
                self.depth_ax.imshow(depth_data, cmap='jet', vmin=0, vmax=10000)
                self.depth_ax.set_title('Depth Map')
                self.depth_ax.plot(center_x, center_y, 'r+', markersize=10, markeredgewidth=2)
                
                # Update distance plot
                if len(self.center_distances) > 1:
                    self.distance_ax.clear()
                    times = list(range(len(self.center_distances)))
                    self.distance_ax.plot(times, list(self.center_distances), 'b-', linewidth=2)
                    self.distance_ax.set_title(f'Center Distance: {center_distance:.0f}mm')
                    self.distance_ax.set_ylabel('Distance (mm)')
                    self.distance_ax.grid(True)
                
                self.depth_canvas.draw()
                
        except Exception as e:
            print(f"Depth visualization error: {e}")
            
    def update_tracking_visualization(self):
        """Update positional tracking displays"""
        if not self.tracking_enabled.get():
            return
            
        try:
            # Get pose data
            translation = sl.Translation()
            rotation = sl.Orientation()
            self.pose.get_translation(translation)
            self.pose.get_orientation(rotation)
            
            pos = translation.get()
            x, y, z = pos[0], pos[1], pos[2]
            
            # Store pose data
            self.pose_history.append((x, y, z))
            
            if len(self.pose_history) > 1:
                # Update 3D trajectory
                self.trajectory_ax.clear()
                positions = np.array(list(self.pose_history))
                self.trajectory_ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'b-', linewidth=2)
                self.trajectory_ax.scatter(x, y, z, c='red', s=50, marker='o')
                self.trajectory_ax.set_title('3D Camera Trajectory')
                self.trajectory_ax.set_xlabel('X (m)')
                self.trajectory_ax.set_ylabel('Y (m)')
                self.trajectory_ax.set_zlabel('Z (m)')
                
                # Update position plots
                times = list(range(len(self.pose_history)))
                
                self.pos_x_ax.clear()
                self.pos_x_ax.plot(times, positions[:, 0], 'r-', linewidth=2)
                self.pos_x_ax.set_title(f'X Position: {x:.3f}m')
                self.pos_x_ax.set_ylabel('X (m)')
                self.pos_x_ax.grid(True)
                
                self.pos_y_ax.clear()
                self.pos_y_ax.plot(times, positions[:, 1], 'g-', linewidth=2)
                self.pos_y_ax.set_title(f'Y Position: {y:.3f}m')
                self.pos_y_ax.set_ylabel('Y (m)')
                self.pos_y_ax.grid(True)
                
                self.pos_z_ax.clear()
                self.pos_z_ax.plot(times, positions[:, 2], 'b-', linewidth=2)
                self.pos_z_ax.set_title(f'Z Position: {z:.3f}m')
                self.pos_z_ax.set_ylabel('Z (m)')
                self.pos_z_ax.set_xlabel('Time')
                self.pos_z_ax.grid(True)
                
                self.tracking_canvas.draw()
                
        except Exception as e:
            print(f"Tracking visualization error: {e}")
            
    def update_sensor_visualization(self):
        """Update IMU sensor data displays"""
        try:
            # Get IMU data
            imu_data = self.sensors_data.get_imu_data()
            linear_acc = imu_data.get_linear_acceleration()
            angular_vel = imu_data.get_angular_velocity()
            
            # Store sensor data
            self.imu_accel_data['x'].append(linear_acc[0])
            self.imu_accel_data['y'].append(linear_acc[1])
            self.imu_accel_data['z'].append(linear_acc[2])
            
            self.imu_gyro_data['x'].append(angular_vel[0])
            self.imu_gyro_data['y'].append(angular_vel[1])
            self.imu_gyro_data['z'].append(angular_vel[2])
            
            if len(self.imu_accel_data['x']) > 1:
                times = list(range(len(self.imu_accel_data['x'])))
                
                # Update acceleration plots
                self.accel_x_ax.clear()
                self.accel_x_ax.plot(times, list(self.imu_accel_data['x']), 'r-', linewidth=2)
                self.accel_x_ax.set_title(f'Acceleration X: {linear_acc[0]:.3f} m/s²')
                self.accel_x_ax.set_ylabel('m/s²')
                self.accel_x_ax.grid(True)
                
                self.accel_y_ax.clear()
                self.accel_y_ax.plot(times, list(self.imu_accel_data['y']), 'g-', linewidth=2)
                self.accel_y_ax.set_title(f'Acceleration Y: {linear_acc[1]:.3f} m/s²')
                self.accel_y_ax.set_ylabel('m/s²')
                self.accel_y_ax.grid(True)
                
                self.accel_z_ax.clear()
                self.accel_z_ax.plot(times, list(self.imu_accel_data['z']), 'b-', linewidth=2)
                self.accel_z_ax.set_title(f'Acceleration Z: {linear_acc[2]:.3f} m/s²')
                self.accel_z_ax.set_ylabel('m/s²')
                self.accel_z_ax.grid(True)
                
                # Update gyroscope plots
                self.gyro_x_ax.clear()
                self.gyro_x_ax.plot(times, list(self.imu_gyro_data['x']), 'r-', linewidth=2)
                self.gyro_x_ax.set_title(f'Angular Velocity X: {angular_vel[0]:.3f} rad/s')
                self.gyro_x_ax.set_ylabel('rad/s')
                self.gyro_x_ax.set_xlabel('Time')
                self.gyro_x_ax.grid(True)
                
                self.gyro_y_ax.clear()
                self.gyro_y_ax.plot(times, list(self.imu_gyro_data['y']), 'g-', linewidth=2)
                self.gyro_y_ax.set_title(f'Angular Velocity Y: {angular_vel[1]:.3f} rad/s')
                self.gyro_y_ax.set_ylabel('rad/s')
                self.gyro_y_ax.set_xlabel('Time')
                self.gyro_y_ax.grid(True)
                
                self.gyro_z_ax.clear()
                self.gyro_z_ax.plot(times, list(self.imu_gyro_data['z']), 'b-', linewidth=2)
                self.gyro_z_ax.set_title(f'Angular Velocity Z: {angular_vel[2]:.3f} rad/s')
                self.gyro_z_ax.set_ylabel('rad/s')
                self.gyro_z_ax.set_xlabel('Time')
                self.gyro_z_ax.grid(True)
                
                self.imu_canvas.draw()
                
        except Exception as e:
            print(f"Sensor visualization error: {e}")
            
    def update_performance_metrics(self):
        """Update performance and diagnostics displays"""
        try:
            if len(self.fps_data) > 1:
                # Update FPS plot
                self.fps_ax.clear()
                times = list(range(len(self.fps_data)))
                self.fps_ax.plot(times, list(self.fps_data), 'b-', linewidth=2)
                self.fps_ax.axhline(y=np.mean(self.fps_data), color='r', linestyle='--', 
                                   label=f'Average: {np.mean(self.fps_data):.1f} FPS')
                self.fps_ax.set_title('Real-time FPS')
                self.fps_ax.set_ylabel('FPS')
                self.fps_ax.set_xlabel('Time')
                self.fps_ax.grid(True)
                self.fps_ax.legend()
                
                self.perf_canvas.draw()
                
        except Exception as e:
            print(f"Performance metrics error: {e}")
            
    def update_system_info(self):
        """Update system information display"""
        try:
            info_text = f"""ZED SDK Information:
CUDA Version: {sl.Camera.get_device_list()[0].camera_model if sl.Camera.get_device_list() else 'No camera detected'}
Available Cameras: {len(sl.Camera.get_device_list())}

System Status:
- Camera: {'Running' if self.is_running else 'Stopped'}
- Tracking: {'Enabled' if self.tracking_enabled.get() else 'Disabled'}
- Recording: {'Active' if self.is_recording else 'Inactive'}
- Streaming: {'Active' if self.is_streaming else 'Inactive'}

Current Settings:
- Resolution: {self.resolution_var.get()}
- FPS: {self.fps_var.get()}
- Depth Mode: {self.depth_mode_var.get()}
- Exposure: {self.exposure_var.get()}
- Brightness: {self.brightness_var.get()}
"""
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            
        except Exception as e:
            print(f"System info error: {e}")
            
    # Control methods
    def change_depth_mode(self, event=None):
        """Change depth sensing mode"""
        # Note: This would require camera restart in real implementation
        pass
        
    def toggle_tracking(self):
        """Enable/disable positional tracking"""
        if self.is_running:
            messagebox.showinfo("Info", "Tracking changes will take effect on next camera start")
            
    def reset_tracking(self):
        """Reset tracking data"""
        self.pose_history.clear()
        if self.is_running and self.tracking_enabled.get():
            # Reset tracking in ZED SDK
            self.zed.reset_positional_tracking(sl.Orientation(), sl.Translation())
            
    def update_exposure(self, value):
        """Update camera exposure"""
        exposure_val = int(float(value))
        if exposure_val == 0:
            self.exposure_label.config(text="Auto")
            if self.is_running:
                self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)
        else:
            self.exposure_label.config(text=str(exposure_val))
            if self.is_running:
                self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, exposure_val)
                
    def update_brightness(self, value):
        """Update camera brightness"""
        brightness_val = int(float(value))
        self.brightness_label.config(text=str(brightness_val))
        if self.is_running:
            self.zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, brightness_val)
            
    def toggle_recording(self):
        """Toggle video recording"""
        if not self.is_recording:
            # Start recording
            try:
                os.makedirs(self.output_path_var.get(), exist_ok=True)
                self.is_recording = True
                self.record_btn.config(text="Stop Recording")
                # In real implementation, would start ZED recording
                messagebox.showinfo("Info", "Recording started")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start recording: {e}")
        else:
            # Stop recording
            self.is_recording = False
            self.record_btn.config(text="Start Recording")
            messagebox.showinfo("Info", "Recording stopped")
            
    def toggle_streaming(self):
        """Toggle local streaming"""
        if not self.is_streaming:
            # Start streaming
            try:
                stream_params = sl.StreamingParameters()
                stream_params.codec = sl.STREAMING_CODEC.H264
                stream_params.port = 30000
                stream_params.bitrate = 8000
                
                if self.is_running:
                    err = self.zed.enable_streaming(stream_params)
                    if err == sl.ERROR_CODE.SUCCESS:
                        self.is_streaming = True
                        self.stream_btn.config(text="Stop Streaming")
                        messagebox.showinfo("Info", "Streaming started on port 30000")
                    else:
                        messagebox.showerror("Error", f"Failed to start streaming: {err}")
                else:
                    messagebox.showwarning("Warning", "Camera must be running to start streaming")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start streaming: {e}")
        else:
            # Stop streaming
            if self.is_running:
                self.zed.disable_streaming()
            self.is_streaming = False
            self.stream_btn.config(text="Start Streaming")
            messagebox.showinfo("Info", "Streaming stopped")


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run dashboard
    dashboard = ZEDComprehensiveDashboard(root)
    
    # Handle window closing
    def on_closing():
        if dashboard.is_running:
            dashboard.stop_camera()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()