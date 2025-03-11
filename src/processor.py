"""
processor.py - Orientation data processor for OrientPy
"""
import utime
from .filter import ComplementaryFilter

class OrientProcessor:
    """
    Processes IMU data using orientation filter and handles
    sensor calibration, timing, and orientation updates.
    """
    
    def __init__(self, update_rate=100):
        """
        Initialize the orientation processor.
        
        Args:
            update_rate: Processing rate in Hz
        """
        self.update_rate = update_rate
        self.filter = ComplementaryFilter(update_rate)
        
        # Sensor offsets (calibration)
        self.accel_offset = {'x': 0, 'y': 0, 'z': 0}
        self.gyro_offset = {'x': 0, 'y': 0, 'z': 0}
        
        # Update timing
        self.last_update = utime.ticks_ms()
        self.min_interval = 1000 // update_rate  # ms
    
    def calibrate_gyro(self, read_gyro_func, samples=100, delay_ms=5):
        """
        Calibrate gyroscope by calculating zero offset.
        
        Args:
            read_gyro_func: Function that returns gyro readings
            samples: Number of samples to collect
            delay_ms: Delay between samples in milliseconds
            
        Returns:
            Dict with gyro offset values
        """
        print("Calibrating gyroscope - keep device still...")
        
        sum_x, sum_y, sum_z = 0, 0, 0
        
        for _ in range(samples):
            gyro = read_gyro_func()
            sum_x += gyro['x']
            sum_y += gyro['y']
            sum_z += gyro['z']
            utime.sleep_ms(delay_ms)
            
        self.gyro_offset = {
            'x': sum_x / samples,
            'y': sum_y / samples,
            'z': sum_z / samples
        }
        
        print("Calibration complete.")
        return self.gyro_offset
    
    def should_update(self):
        """Check if it's time to update based on the update rate."""
        now = utime.ticks_ms()
        elapsed = utime.ticks_diff(now, self.last_update)
        return elapsed >= self.min_interval
    
    def update(self, accel, gyro):
        """
        Update orientation estimate with new sensor readings.
        
        Args:
            accel: Dict with accelerometer readings in m/s²
            gyro: Dict with gyroscope readings in rad/s
            
        Returns:
            Dict with orientation angles, or None if not time to update
        """
        if not self.should_update():
            return None
            
        now = utime.ticks_ms()
        dt = utime.ticks_diff(now, self.last_update) / 1000.0
        self.last_update = now
        
        # Apply calibration offsets to gyro data
        calibrated_gyro = {
            'x': gyro['x'] - self.gyro_offset['x'],
            'y': gyro['y'] - self.gyro_offset['y'],
            'z': gyro['z'] - self.gyro_offset['z']
        }
        
        # Update orientation filter
        return self.filter.update(accel, calibrated_gyro, dt)
    
    def get_orientation(self, in_degrees=False):
        """Get current orientation angles."""
        return self.filter.get_angles(in_degrees)
    
    def set_filter_weights(self, gyro_weight=None, pitch_weight=None, roll_weight=None):
        """Update filter parameters."""
        return self.filter.set_weights(gyro_weight, pitch_weight, roll_weight)
