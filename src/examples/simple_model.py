from machine import I2C, Pin
import utime
import math

# Import the OrientPy library
from OrientPy import OrientProcessor

# MPU6050 Constants
MPU6050_ADDR = const(0x68)
MPU6050_ACCEL_XOUT_H = const(0x3B)
MPU6050_GYRO_XOUT_H = const(0x43)
MPU6050_PWR_MGMT_1 = const(0x6B)
MPU6050_SMPLRT_DIV = const(0x19)
MPU6050_CONFIG = const(0x1A)
MPU6050_GYRO_CONFIG = const(0x1B)
MPU6050_ACCEL_CONFIG = const(0x1C)

def init_mpu6050(i2c):
    """Initialize the MPU6050 sensor."""
    # Wake up the MPU6050
    i2c.writeto_mem(MPU6050_ADDR, MPU6050_PWR_MGMT_1, bytearray([0]))
    utime.sleep_ms(100)  # Wait for sensor to wake up
    
    # Set sample rate (1kHz)
    i2c.writeto_mem(MPU6050_ADDR, MPU6050_SMPLRT_DIV, bytearray([0]))
    
    # Set DLPF (Digital Low Pass Filter)
    i2c.writeto_mem(MPU6050_ADDR, MPU6050_CONFIG, bytearray([3]))
    
    # Set gyroscope range to ±250°/s
    i2c.writeto_mem(MPU6050_ADDR, MPU6050_GYRO_CONFIG, bytearray([0]))
    
    # Set accelerometer range to ±2g
    i2c.writeto_mem(MPU6050_ADDR, MPU6050_ACCEL_CONFIG, bytearray([0]))
    
    print("MPU6050 initialized")

def read_accel(i2c):
    """Read accelerometer data in m/s²."""
    # Read 6 bytes (X, Y, Z values, each 16-bit)
    data = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H, 6)
    
    # Convert raw values to m/s²
    accel_scale = 16384.0  # for ±2g range
    g = 9.81  # Earth's gravity in m/s²
    
    # Combine high and low bytes and convert to signed values
    x = ((data[0] << 8) | data[1])
    if x >= 0x8000:
        x = x - 0x10000
    x = (x / accel_scale) * g
    
    y = ((data[2] << 8) | data[3])
    if y >= 0x8000:
        y = y - 0x10000
    y = (y / accel_scale) * g
    
    z = ((data[4] << 8) | data[5])
    if z >= 0x8000:
        z = z - 0x10000
    z = (z / accel_scale) * g
    
    return {'x': x, 'y': y, 'z': z}
    
def read_gyro(i2c):
    """Read gyroscope data in rad/s."""
    # Read 6 bytes (X, Y, Z values, each 16-bit)
    data = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYRO_XOUT_H, 6)
    
    # Convert raw values to rad/s
    gyro_scale = 131.0  # for ±250°/s range
    deg_to_rad = 0.0174533  # π/180
    
    # Combine high and low bytes and convert to signed values
    x = ((data[0] << 8) | data[1])
    if x >= 0x8000:
        x = x - 0x10000
    x = (x / gyro_scale) * deg_to_rad
    
    y = ((data[2] << 8) | data[3])
    if y >= 0x8000:
        y = y - 0x10000
    y = (y / gyro_scale) * deg_to_rad
    
    z = ((data[4] << 8) | data[5])
    if z >= 0x8000:
        z = z - 0x10000
    z = (z / gyro_scale) * deg_to_rad
    
    return {'x': x, 'y': y, 'z': z}

def run_demo():
    """Run a minimal OrientPy demo with MPU6050."""
    print("Starting OrientPy demo...")
    
    # Initialize I2C
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    
    # Check if MPU6050 is connected
    devices = i2c.scan()
    if MPU6050_ADDR not in devices:
        print(f"MPU6050 not found! Devices found: {[hex(d) for d in devices]}")
        return
    
    # Initialize MPU6050
    init_mpu6050(i2c)
    
    # Initialize OrientProcessor
    orient = OrientProcessor(update_rate=100)  # 100Hz update rate
    
    # Calibrate gyroscope
    print("Calibrating gyroscope... Keep the sensor still.")
    
    def gyro_reader():
        return read_gyro(i2c)
    
    orient.calibrate_gyro(gyro_reader, samples=100)
    print("Calibration complete!")
    
    # Set filter weight (higher = more responsive but noisier)
    orient.set_filter_weights(gyro_weight=0.98)
    
    print("\nReading orientation data...")
    print("Move the sensor to see changes in pitch and roll.")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Read sensor data
            accel = read_accel(i2c)
            gyro = read_gyro(i2c)
            
            # Update orientation
            orient.update(accel, gyro)
            
            # Get orientation in degrees
            angles = orient.get_orientation(in_degrees=True)
            
            # Print the values
            print(f"Pitch: {angles['pitch']:7.2f}°  Roll: {angles['roll']:7.2f}°", end="\r")
            
            # Small delay
            utime.sleep_ms(20)
            
    except KeyboardInterrupt:
        print("\nDemo stopped.")

run_demo()
