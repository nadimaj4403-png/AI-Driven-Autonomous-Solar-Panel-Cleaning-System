import cv2
import numpy as np

def capture_image():
    """Capture image from camera."""
    cap = cv2.VideoCapture(0)  # 0 for default camera
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite('panel_image.jpg', frame)
        return 'panel_image.jpg'
    return None

def detect_dirt(image_path, threshold=0.1):
    """
    Simple dirt detection: Convert to grayscale, threshold for dark spots (dirt).
    Returns True if dirty (dirt percentage > threshold).
    """
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Threshold to find dark areas (dirt)
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)
    # Calculate dirt percentage
    dirt_pixels = np.sum(thresh == 255)
    total_pixels = thresh.size
    dirt_percentage = dirt_pixels / total_pixels
    
    print(f"Dirt percentage: {dirt_percentage:.2f}")
    return dirt_percentage > threshold  # True if dirty

#*******************2

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
SENSOR_PIN = 18  # GPIO pin for sensor (e.g., light sensor)
PUMP_PIN = 17    # GPIO pin for relay controlling pump
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(PUMP_PIN, GPIO.OUT)

def check_sensor():
    """Check if sensor condition is met (e.g., sufficient light)."""
    return GPIO.input(SENSOR_PIN) == GPIO.HIGH  # Adjust logic based on sensor

def activate_cleaning(duration=10):
    """Activate water jet for cleaning."""
    print("Activating water jet...")
    GPIO.output(PUMP_PIN, GPIO.HIGH)  # Turn on pump
    time.sleep(duration)  # Clean for specified seconds
    GPIO.output(PUMP_PIN, GPIO.LOW)  # Turn off
    print("Cleaning complete.")

def cleanup():
    GPIO.cleanup()

    #***********3

    from image_processor import capture_image, detect_dirt
from hardware_control import check_sensor, activate_cleaning, cleanup
import time

def main():
    print("Starting Solar Panel Cleaning System with Sensor Trigger...")
    try:
        while True:
            # Step 1: Check sensor (e.g., wait for light/daytime)
            if not check_sensor():
                print("Sensor condition not met. Waiting...")
                time.sleep(60)  # Check every minute
                continue
            
            # Step 2: Capture image once sensor triggers
            print("Sensor triggered. Capturing image...")
            image_path = capture_image()
            if not image_path:
                print("Failed to capture image.")
                time.sleep(60)
                continue
            
            # Step 3: Check for dirt
            is_dirty = detect_dirt(image_path, threshold=0.1)  # Adjust threshold
            
            if is_dirty:
                print("Panel is dirty. Initiating cleaning...")
                activate_cleaning(duration=10)  # Clean for 10 seconds
            else:
                print("Panel is clean.")
            
            # Wait before next sensor check (e.g., 1 hour after processing)
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cleanup()

if __name__ == "__main__":
    main()