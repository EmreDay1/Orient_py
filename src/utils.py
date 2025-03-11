"""
utils.py - Utility functions for OrientPy
"""
import math

def create_vector(x=0, y=0, z=0):
    """Create a 3D vector dictionary with the given values."""
    return {'x': float(x), 'y': float(y), 'z': float(z)}

def vector_magnitude(vector):
    """Calculate the magnitude (length) of a 3D vector."""
    return math.sqrt(vector['x']**2 + vector['y']**2 + vector['z']**2)

def apply_calibration(raw_data, offsets):
    """Apply calibration offsets to sensor data."""
    return {
        'x': raw_data['x'] - offsets['x'],
        'y': raw_data['y'] - offsets['y'],
        'z': raw_data['z'] - offsets['z']
    }

def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * (math.pi / 180.0)

def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * (180.0 / math.pi)
