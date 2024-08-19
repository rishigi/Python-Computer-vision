import cv2
import mediapipe as mp
import numpy as np

mp_selfie_segmentation = mp.solutions.selfie_segmentation
mp_drawing = mp.solutions.drawing_utils

def calculate_ripeness_percentage(fruit_region, mask):
    # Convert the fruit region to HSV color space
    hsv_image = cv2.cvtColor(fruit_region, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for different stages of ripeness (adjust based on the fruit)
    # Example: ripe color is yellow, unripe color is green
    ripe_lower = np.array([20, 100, 100])
    ripe_upper = np.array([30, 255, 255])
    
    unripe_lower = np.array([35, 100, 100])
    unripe_upper = np.array([85, 255, 255])
    
    # Create masks for ripe and unripe regions
    ripe_mask = cv2.inRange(hsv_image, ripe_lower, ripe_upper)
    unripe_mask = cv2.inRange(hsv_image, unripe_lower, unripe_upper)
    
    # Calculate the percentage of ripe and unripe areas
    ripe_area = cv2.countNonZero(ripe_mask & mask)
    unripe_area = cv2.countNonZero(unripe_mask & mask)
    
    # Total fruit area
    total_area = cv2.countNonZero(mask)
    
    if total_area == 0:
        return 0  # Avoid division by zero
    
    # Calculate ripeness percentage
    ripeness_percentage = (ripe_area / total_area) * 100
    return ripeness_percentage


# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Selfie Segmentation
with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and get the segmentation mask
        results = selfie_segmentation.process(image)

        # Convert the image color back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract the mask (0 for background, 1 for foreground)
        mask = results.segmentation_mask > 0.5
        mask = mask.astype(np.uint8)

        # Extract the fruit region
        fruit_region = cv2.bitwise_and(image, image, mask=mask)

        # Calculate the ripeness percentage based on color analysis
        ripeness_percentage = calculate_ripeness_percentage(fruit_region, mask)

        # Display the ripeness percentage on the image
        cv2.putText(image, f'Ripeness: {ripeness_percentage:.2f}%', 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the processed image
        cv2.imshow('Fruit Ripeness Detection', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
