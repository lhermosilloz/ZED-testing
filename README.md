# ZED Camera Comprehensive Dashboard

A real-time, multi-featured dashboard for ZED stereo cameras that displays all camera capabilities including live feeds, depth sensing, positional tracking, IMU sensors, and more.

## Features

### 🎥 **Live Camera Feed**
- Dual stereo camera view (left/right)
- Real-time image capture and display
- Camera information and statistics
- Configurable resolution and FPS

### 🔍 **Depth Sensing** 
- Real-time depth map visualization
- Point cloud generation and display
- Distance measurements at center point
- Configurable depth modes (Performance/Quality/Ultra)

### 🧭 **Positional Tracking**
- 3D camera trajectory visualization
- Real-time pose estimation (position + orientation)
- X, Y, Z position tracking over time
- World frame reference tracking

### 📊 **IMU Sensors**
- Linear acceleration (X, Y, Z axes)
- Angular velocity (X, Y, Z axes) 
- Real-time sensor data plotting
- Synchronized timestamp data

### ⚙️ **Camera Controls**
- Resolution settings (HD2K, HD1080, HD720, VGA)
- FPS control (15, 30, 60, 100)
- Exposure adjustment (Auto/Manual)
- Brightness control
- Recording and streaming controls

### 📈 **Performance Diagnostics**
- Real-time FPS monitoring
- System information display
- Performance metrics visualization
- Camera status and health monitoring

## Prerequisites

### Required Software
1. **ZED SDK** - Download and install from [Stereolabs](https://www.stereolabs.com/developers/release/)
2. **Python 3.7+** with tkinter support
3. **CUDA** (recommended for optimal performance)

### Hardware Requirements
- ZED, ZED Mini, ZED 2, or ZED 2i camera
- USB 3.0 port (USB-C for ZED 2/2i)
- NVIDIA GPU with CUDA support (recommended)
- Minimum 4GB RAM

## Installation

### Quick Setup
1. **Clone or download** this repository
2. **Install ZED SDK** from Stereolabs website
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the launcher**:
   ```bash
   python launch_dashboard.py
   ```

### Manual Setup
If you prefer manual installation:
```bash
pip install matplotlib numpy opencv-python Pillow
python zed_comprehensive_dashboard.py
```

## Usage

### Getting Started
1. **Connect your ZED camera** to your computer
2. **Launch the dashboard** using `python launch_dashboard.py`
3. **Click "Start Camera"** to begin data acquisition
4. **Explore the tabs** to view different capabilities:
   - **Live Feed**: Camera streams and info
   - **Depth Sensing**: Depth maps and measurements  
   - **Positional Tracking**: 3D trajectory and pose
   - **Sensors (IMU)**: Acceleration and gyroscope data
   - **Camera Controls**: Settings and recording
   - **Diagnostics**: Performance metrics

### Key Controls
- **Start/Stop Camera**: Main control for data acquisition
- **Enable Tracking**: Toggle positional tracking
- **Recording**: Start/stop video recording
- **Streaming**: Enable local H.264 streaming
- **Camera Settings**: Adjust resolution, FPS, exposure, brightness

### Real-time Features
- All displays update in real-time (10 FPS refresh rate)
- Data history maintained for trending (last 100 points)
- Interactive matplotlib plots for detailed analysis
- Live performance monitoring

## Configuration

### Camera Settings
- **Resolution**: Choose from HD2K, HD1080, HD720, or VGA
- **Frame Rate**: 15, 30, 60, or 100 FPS (depending on resolution)
- **Depth Mode**: Performance, Quality, or Ultra modes
- **Exposure**: Auto or manual (0-100%)
- **Brightness**: Adjustable (0-8 scale)

### Recording Settings
- **Output Path**: Configurable recording directory
- **Format**: Standard ZED SVO format
- **Streaming**: H.264 codec on port 30000

## Architecture

### Core Components
1. **Main Dashboard** (`ZEDComprehensiveDashboard`)
   - Multi-threaded architecture for smooth performance
   - Separate camera acquisition thread
   - Real-time GUI updates

2. **Data Management**
   - Efficient buffer management with `collections.deque`
   - Real-time data storage and retrieval
   - Thread-safe operations

3. **Visualization**
   - Matplotlib integration for real-time plotting
   - OpenCV for image processing
   - Tkinter for GUI framework

### Threading Model
- **Main Thread**: GUI updates and user interaction
- **Camera Thread**: ZED data acquisition loop
- **Display Updates**: Scheduled GUI refreshes (100ms intervals)

## Troubleshooting

### Common Issues

**Camera Not Detected**
- Ensure ZED SDK is properly installed
- Check USB connection and port
- Verify camera permissions
- Try different USB port or cable

**Poor Performance**
- Lower resolution or FPS settings
- Disable unnecessary features (depth, tracking)
- Close other applications using GPU
- Check CUDA installation

**Import Errors**
- Install missing dependencies: `pip install -r requirements.txt`
- Ensure ZED SDK Python bindings are installed
- Check Python version compatibility (3.7+)

**Display Issues**
- Verify tkinter is installed with Python
- Update graphics drivers
- Check matplotlib backend compatibility

### Performance Optimization

1. **Reduce Update Frequency**
   - Modify `self.root.after(100, ...)` to higher values (200ms, 500ms)

2. **Limit Data History**
   - Reduce `max_data_points` for less memory usage

3. **Disable Features**
   - Turn off tracking when not needed
   - Use lower depth quality settings
   - Reduce plot complexity

## Development

### Extending the Dashboard
The modular design makes it easy to add new features:

1. **Add New Tabs**:
   ```python
   def create_my_new_tab(self):
       self.my_frame = ttk.Frame(self.notebook)
       self.notebook.add(self.my_frame, text="My Feature")
       # Add widgets...
   ```

2. **Add New Visualizations**:
   ```python
   def update_my_visualization(self):
       # Update plots in the main update loop
       pass
   ```

3. **Add New Controls**:
   ```python
   def my_control_callback(self):
       # Handle user input
       pass
   ```

### Code Structure
```
zed_comprehensive_dashboard.py
├── ZEDComprehensiveDashboard (Main class)
│   ├── __init__() - Initialize dashboard
│   ├── setup_ui() - Create GUI elements
│   ├── camera_loop() - Data acquisition thread
│   ├── update_displays() - GUI refresh loop
│   └── Various update methods for each feature
├── Control methods (start/stop, settings)
└── main() - Application entry point
```

## License

This project is provided as-is for educational and development purposes. The ZED SDK is proprietary software from Stereolabs and requires separate licensing.

## Support

For ZED SDK related issues, please refer to:
- [Stereolabs Documentation](https://www.stereolabs.com/docs/)
- [ZED SDK API Reference](https://www.stereolabs.com/docs/api/)
- [Community Forum](https://community.stereolabs.com/)

For dashboard-specific issues:
- Check the troubleshooting section above
- Review error messages in the console
- Ensure all dependencies are properly installed

## Changelog

### Version 1.0.0
- Initial release with comprehensive ZED camera dashboard
- Real-time visualization of all major ZED capabilities
- Multi-tabbed interface with intuitive controls
- Performance monitoring and diagnostics
- Recording and streaming functionality