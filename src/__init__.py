"""
OrientPy - A lightweight orientation estimation library for Raspberry Pi Pico
Combines accelerometer and gyroscope data to estimate device orientation
"""

from .filter import ComplementaryFilter
from .processor import OrientProcessor
from .utils import create_vector, vector_magnitude
from .viz import OrientPlotter

__version__ = '1.0.0'
