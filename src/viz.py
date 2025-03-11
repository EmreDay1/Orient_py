"""
viz.py - Data visualization for OrientPy using matplotlib

This module provides utilities for plotting orientation data using matplotlib,
which works well with Thonny IDE.
"""
import math
import utime

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    print("Warning: matplotlib not available. Install it for visualization support.")

class MatplotlibPlotter:
    """
    Orientation data plotter using matplotlib.
    Provides real-time visualization of IMU data.
    """
    
    def __init__(self, buffer_size=200, update_interval=100):
        """
        Initialize the matplotlib plotter.
        
        Args:
            buffer_size: Maximum number of data points to store (default: 200)
            update_interval: Plot update interval in ms (default: 100)
        """
        if not matplotlib_available:
            print("Matplotlib is not available. Install it for visualization.")
            return
            
        self.buffer_size = buffer_size
        self.update_interval = update_interval
        
        # Data buffers
        self.time_buffer = []
        self.pitch_buffer = []
        self.roll_buffer = []
        self.accel_pitch_buffer = []
        self.accel_roll_buffer = []
        self.gyro_pitch_buffer = []
        self.gyro_roll_buffer = []
        
        # Keep track of which plots to show
        self.show_accel = False
        self.show_gyro = False
        
        # For timing
        self.start_time = utime.ticks_ms()
        self.last_update = self.start_time
        
        # Set up figure and axes
        self.setup_plot()
        
    def setup_plot(self):
        """Initialize the matplotlib figure and axes."""
        if not matplotlib_available:
            return
            
        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        # Set up lines for each data series
        self.pitch_line, = self.ax.plot([], [], 'r-', label='Pitch')
        self.roll_line, = self.ax.plot([], [], 'm-', label='Roll')
        self.accel_pitch_line, = self.ax.plot([], [], 'b:', label='Accel Pitch')
        self.accel_roll_line, = self.ax.plot([], [], 'g:', label='Accel Roll')
        self.gyro_pitch_line, = self.ax.plot([], [], 'y--', label='Gyro Pitch')
        self.gyro_roll_line, = self.ax.plot([], [], 'c--', label='Gyro Roll')
        
        # Configure plot
        self.ax.set_title('OrientPy Orientation Data')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Angle (degrees)')
        self.ax.set_ylim(-90, 90)
        self.ax.grid(True)
        self.ax.legend(loc='upper right')
        
        # Set up animation
        self.ani = FuncAnimation(
            self.fig, 
            self._update_plot, 
            interval=self.update_interval,
            blit=True
        )
        
        # Show plot in non-blocking mode
        plt.ion()
        plt.show()
        
    def add_data_point(self, angles, accel_angles=None, gyro_angles=None):
        """
        Add a new data point to the plot.
        
        Args:
            angles: Dict with 'pitch' and 'roll' from filter
            accel_angles: Dict with 'pitch' and 'roll' from accelerometer
            gyro_angles: Dict with 'pitch' and 'roll' from gyroscope
        """
        if not matplotlib_available:
            return
            
        # Record current time
        current_time = utime.ticks_diff(utime.ticks_ms(), self.start_time) / 1000.0
        self.time_buffer.append(current_time)
        
        # Add filter angles
        self.pitch_buffer.append(angles['pitch'])
        self.roll_buffer.append(angles['roll'])
        
        # Add accelerometer angles if provided
        if accel_angles:
            self.accel_pitch_buffer.append(accel_angles['pitch'])
            self.accel_roll_buffer.append(accel_angles['roll'])
        else:
            # Add None to maintain buffer alignment
            self.accel_pitch_buffer.append(None)
            self.accel_roll_buffer.append(None)
            
        # Add gyroscope angles if provided
        if gyro_angles:
            self.gyro_pitch_buffer.append(gyro_angles['pitch'])
            self.gyro_roll_buffer.append(gyro_angles['roll'])
        else:
            # Add None to maintain buffer alignment
            self.gyro_pitch_buffer.append(None)
            self.gyro_roll_buffer.append(None)
            
        # Trim buffers if they exceed buffer size
        if len(self.time_buffer) > self.buffer_size:
            self.time_buffer.pop(0)
            self.pitch_buffer.pop(0)
            self.roll_buffer.pop(0)
            self.accel_pitch_buffer.pop(0)
            self.accel_roll_buffer.pop(0)
            self.gyro_pitch_buffer.pop(0)
            self.gyro_roll_buffer.pop(0)
            
        # Update the plot manually if enough time has passed
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self.last_update) >= self.update_interval:
            self.update_display(self.show_accel, self.show_gyro)
            self.last_update = now
            
    def update_display(self, show_accel=False, show_gyro=False):
        """
        Update the plot display with current settings.
        
        Args:
            show_accel: Whether to show accelerometer data
            show_gyro: Whether to show gyroscope data
        """
        if not matplotlib_available or not hasattr(self, 'fig'):
            return
            
        # Save settings
        self.show_accel = show_accel
        self.show_gyro = show_gyro
        
        # Update data in plot lines
        self.pitch_line.set_data(self.time_buffer, self.pitch_buffer)
        self.roll_line.set_data(self.time_buffer, self.roll_buffer)
        
        # Handle accelerometer data
        if show_accel:
            # Filter out None values
            x_accel_pitch = []
            y_accel_pitch = []
            x_accel_roll = []
            y_accel_roll = []
            
            for i, t in enumerate(self.time_buffer):
                if i < len(self.accel_pitch_buffer) and self.accel_pitch_buffer[i] is not None:
                    x_accel_pitch.append(t)
                    y_accel_pitch.append(self.accel_pitch_buffer[i])
                    
                if i < len(self.accel_roll_buffer) and self.accel_roll_buffer[i] is not None:
                    x_accel_roll.append(t)
                    y_accel_roll.append(self.accel_roll_buffer[i])
                    
            self.accel_pitch_line.set_data(x_accel_pitch, y_accel_pitch)
            self.accel_roll_line.set_data(x_accel_roll, y_accel_roll)
        else:
            self.accel_pitch_line.set_data([], [])
            self.accel_roll_line.set_data([], [])
            
        # Handle gyroscope data
        if show_gyro:
            # Filter out None values
            x_gyro_pitch = []
            y_gyro_pitch = []
            x_gyro_roll = []
            y_gyro_roll = []
            
            for i, t in enumerate(self.time_buffer):
                if i < len(self.gyro_pitch_buffer) and self.gyro_pitch_buffer[i] is not None:
                    x_gyro_pitch.append(t)
                    y_gyro_pitch.append(self.gyro_pitch_buffer[i])
                    
                if i < len(self.gyro_roll_buffer) and self.gyro_roll_buffer[i] is not None:
                    x_gyro_roll.append(t)
                    y_gyro_roll.append(self.gyro_roll_buffer[i])
                    
            self.gyro_pitch_line.set_data(x_gyro_pitch, y_gyro_pitch)
            self.gyro_roll_line.set_data(x_gyro_roll, y_gyro_roll)
        else:
            self.gyro_pitch_line.set_data([], [])
            self.gyro_roll_line.set_data([], [])
            
        # Update x-axis limits to show the most recent data
        if self.time_buffer:
            t_min = self.time_buffer[0]
            t_max = max(t_min + 10, self.time_buffer[-1] + 2)  # Add some padding
            self.ax.set_xlim(t_min, t_max)
            
        # Redraw the plot
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
    def _update_plot(self, frame):
        """Update function for animation."""
        # This gets called automatically by the animation
        lines = [
            self.pitch_line, self.roll_line,
            self.accel_pitch_line, self.accel_roll_line,
            self.gyro_pitch_line, self.gyro_roll_line
        ]
        return lines
        
    def highlight_region(self, start_time, end_time, color='yellow', alpha=0.3):
        """
        Highlight a region of the plot.
        
        Args:
            start_time: Start time of region
            end_time: End time of region
            color: Color of highlighted region
            alpha: Transparency (0-1)
        """
        if not matplotlib_available or not hasattr(self, 'ax'):
            return
            
        # Add a rectangle patch to highlight the region
        rect = plt.Rectangle(
            (start_time, -90), 
            end_time - start_time, 
            180,  # Height covers the whole plot (-90 to 90)
            color=color, 
            alpha=alpha,
            zorder=0  # Put it behind the data
        )
        self.ax.add_patch(rect)
        
        # Redraw
        self.fig.canvas.draw_idle()
        
    def save_figure(self, filename="orientation_plot.png"):
        """
        Save the current plot to a file.
        
        Args:
            filename: Name of the file to save to
        """
        if not matplotlib_available or not hasattr(self, 'fig'):
            return
            
        self.fig.savefig(filename)
        print(f"Plot saved to {filename}")
        
    def clear(self):
        """Clear all data and reset the plot."""
        if not matplotlib_available:
            return
            
        # Clear data buffers
        self.time_buffer = []
        self.pitch_buffer = []
        self.roll_buffer = []
        self.accel_pitch_buffer = []
        self.accel_roll_buffer = []
        self.gyro_pitch_buffer = []
        self.gyro_roll_buffer = []
        
        # Reset lines
        self.pitch_line.set_data([], [])
        self.roll_line.set_data([], [])
        self.accel_pitch_line.set_data([], [])
        self.accel_roll_line.set_data([], [])
        self.gyro_pitch_line.set_data([], [])
        self.gyro_roll_line.set_data([], [])
        
        # Reset time
        self.start_time = utime.ticks_ms()
        self.last_update = self.start_time
        
        # Clear any highlighted regions
        for patch in self.ax.patches:
            patch.remove()
            
        # Reset axis limits
        self.ax.set_xlim(0, 10)
        
        # Redraw
        self.fig.canvas.draw_idle()
        
    def close(self):
        """Close the plot."""
        if not matplotlib_available:
            return
            
        plt.close(self.fig)


class SimpleDataLogger:
    """
    Simple data logger for recording orientation data when 
    visualization is not needed or available.
    """
    
    def __init__(self, buffer_size=1000):
        """
        Initialize the data logger.
        
        Args:
            buffer_size: Maximum number of data points to store
        """
        self.buffer_size = buffer_size
        self.time_buffer = []
        self.pitch_buffer = []
        self.roll_buffer = []
        self.accel_pitch_buffer = []
        self.accel_roll_buffer = []
        self.gyro_pitch_buffer = []
        self.gyro_roll_buffer = []
        
        self.start_time = utime.ticks_ms()
        
    def add_data_point(self, angles, accel_angles=None, gyro_angles=None):
        """
        Add a new data point to the log.
        
        Args:
            angles: Dict with 'pitch' and 'roll' from filter
            accel_angles: Dict with 'pitch' and 'roll' from accelerometer
            gyro_angles: Dict with 'pitch' and 'roll' from gyroscope
        """
        # Record current time
        current_time = utime.ticks_diff(utime.ticks_ms(), self.start_time) / 1000.0
        self.time_buffer.append(current_time)
        
        # Add filter angles
        self.pitch_buffer.append(angles['pitch'])
        self.roll_buffer.append(angles['roll'])
        
        # Add accelerometer angles if provided
        if accel_angles:
            self.accel_pitch_buffer.append(accel_angles['pitch'])
            self.accel_roll_buffer.append(accel_angles['roll'])
        else:
            # Add None to maintain buffer alignment
            self.accel_pitch_buffer.append(None)
            self.accel_roll_buffer.append(None)
            
        # Add gyroscope angles if provided
        if gyro_angles:
            self.gyro_pitch_buffer.append(gyro_angles['pitch'])
            self.gyro_roll_buffer.append(gyro_angles['roll'])
        else:
            # Add None to maintain buffer alignment
            self.gyro_pitch_buffer.append(None)
            self.gyro_roll_buffer.append(None)
            
        # Trim buffers if they exceed buffer size
        if len(self.time_buffer) > self.buffer_size:
            self.time_buffer.pop(0)
            self.pitch_buffer.pop(0)
            self.roll_buffer.pop(0)
            self.accel_pitch_buffer.pop(0)
            self.accel_roll_buffer.pop(0)
            self.gyro_pitch_buffer.pop(0)
            self.gyro_roll_buffer.pop(0)
    
    def save_data(self, filename):
        """
        Save logged data to a CSV file.
        
        Args:
            filename: Name of the file to save data to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write('time,pitch,roll,accel_pitch,accel_roll,gyro_pitch,gyro_roll\n')
                
                # Write data
                for i in range(len(self.time_buffer)):
                    f.write(f'{self.time_buffer[i]},{self.pitch_buffer[i]},{self.roll_buffer[i]},')
                    
                    if i < len(self.accel_pitch_buffer) and self.accel_pitch_buffer[i] is not None:
                        f.write(f'{self.accel_pitch_buffer[i]},')
                    else:
                        f.write(',')
                        
                    if i < len(self.accel_roll_buffer) and self.accel_roll_buffer[i] is not None:
                        f.write(f'{self.accel_roll_buffer[i]},')
                    else:
                        f.write(',')
                        
                    if i < len(self.gyro_pitch_buffer) and self.gyro_pitch_buffer[i] is not None:
                        f.write(f'{self.gyro_pitch_buffer[i]},')
                    else:
                        f.write(',')
                        
                    if i < len(self.gyro_roll_buffer) and self.gyro_roll_buffer[i] is not None:
                        f.write(f'{self.gyro_roll_buffer[i]}\n')
                    else:
                        f.write('\n')
                        
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def clear(self):
        """Clear all logged data."""
        self.time_buffer = []
        self.pitch_buffer = []
        self.roll_buffer = []
        self.accel_pitch_buffer = []
        self.accel_roll_buffer = []
        self.gyro_pitch_buffer = []
        self.gyro_roll_buffer = []
        self.start_time = utime.ticks_ms()
