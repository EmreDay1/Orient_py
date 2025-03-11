"""
filter.py - Complementary filter implementation for OrientPy
"""
import math
import utime

class ComplementaryFilter:
    """
    Implements a complementary filter for combining accelerometer 
    and gyroscope data to estimate device orientation.
    """
    
    def __init__(self, update_rate=100, gyro_weight=0.95):
        """
        Initialize the orientation filter.
        
        Args:
            update_rate: Filter update frequency in Hz
            gyro_weight: Weight for gyroscope data (0-1)
        """
        self.update_rate = update_rate
        self.set_weights(gyro_weight)
        
        # Current orientation in radians
        self.pitch = 0.0
        self.roll = 0.0
        
        # Timing
        self.last_update = utime.ticks_ms()
        self.dt = 1.0 / update_rate  # seconds
        
    def set_weights(self, gyro_weight=None, pitch_weight=None, roll_weight=None):
        """
        Set filter weights for balancing gyro vs accelerometer data.
        Higher values favor gyroscope data (good for dynamic motion).
        Lower values favor accelerometer data (good for static accuracy).
        
        Args:
            gyro_weight: Weight for both pitch and roll (0-1)
            pitch_weight: Specific weight for pitch calculation
            roll_weight: Specific weight for roll calculation
        
        Returns:
            True if valid weights, False otherwise
        """
        # Use specific weights if provided, otherwise use general weight
        if gyro_weight is not None:
            if not 0 <= gyro_weight <= 1:
                return False
            self.pitch_weight = gyro_weight
            self.roll_weight = gyro_weight
        
        if pitch_weight is not None:
            if not 0 <= pitch_weight <= 1:
                return False
            self.pitch_weight = pitch_weight
            
        if roll_weight is not None:
            if not 0 <= roll_weight <= 1:
                return False
            self.roll_weight = roll_weight
            
        return True
        
    def update(self, accel, gyro, dt=None):
        """
        Update orientation estimate with new sensor data.
        
        Args:
            accel: Dict with 'x', 'y', 'z' accelerometer values in m/s²
            gyro: Dict with 'x', 'y', 'z' gyroscope values in rad/s
            dt: Time delta in seconds (calculated automatically if None)
            
        Returns:
            Dict containing 'pitch' and 'roll' in radians
        """
        # Calculate time step since last update if not provided
        now = utime.ticks_ms()
        if dt is None:
            dt = utime.ticks_diff(now, self.last_update) / 1000.0
            if dt <= 0:  # Avoid division by zero and negative time
                dt = self.dt
        self.last_update = now
        self.dt = dt
        
        # Calculate orientation angles from accelerometer data
        # These are absolute but noisy measurements
        accel_pitch = self._get_accel_pitch(accel)
        accel_roll = self._get_accel_roll(accel)
        
        # Update orientation using complementary filter
        # This combines absolute accelerometer angles with integrated gyroscope rates
        self.pitch = self.pitch_weight * (self.pitch + gyro['y'] * dt) + \
                    (1 - self.pitch_weight) * accel_pitch
                    
        self.roll = self.roll_weight * (self.roll + gyro['x'] * dt) + \
                   (1 - self.roll_weight) * accel_roll
        
        return self.get_angles()
    
    def _get_accel_pitch(self, accel):
        """Calculate pitch angle from accelerometer data."""
        # Avoid division by zero with small epsilon
        epsilon = 1e-10
        
        # Pitch: rotation around Y-axis
        # Using atan2 for proper quadrant handling
        denominator = math.sqrt(accel['y']**2 + accel['z']**2)
        if abs(denominator) < epsilon:
            denominator = epsilon if denominator >= 0 else -epsilon
            
        return math.atan2(-accel['x'], denominator)
    
    def _get_accel_roll(self, accel):
        """Calculate roll angle from accelerometer data."""
        # Avoid division by zero with small epsilon
        epsilon = 1e-10
        
        # Roll: rotation around X-axis
        # Using atan2 for proper quadrant handling
        denominator = math.sqrt(accel['x']**2 + accel['z']**2)
        if abs(denominator) < epsilon:
            denominator = epsilon if denominator >= 0 else -epsilon
            
        return math.atan2(accel['y'], denominator)
    
    def get_angles(self, in_degrees=False):
        """
        Get current orientation angles.
        
        Args:
            in_degrees: If True, return angles in degrees; if False, in radians
            
        Returns:
            Dict with 'pitch' and 'roll' keys
        """
        if in_degrees:
            return {
                'pitch': math.degrees(self.pitch),
                'roll': math.degrees(self.roll)
            }
        return {
            'pitch': self.pitch,
            'roll': self.roll
        }
    
    def reset(self):
        """Reset orientation to zero."""
        self.pitch = 0.0
        self.roll = 0.0
        self.last_update = utime.ticks_ms()
