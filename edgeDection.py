import cv2
import os
import numpy as np
from sort_pixels import sort_pixels

def show_image(window_name, image):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)

def process_mcq_image(image):
    # Read the image
    if image is None:
        print("Error: Unable to load image.")
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_image("Gray Image", gray)

    clahe = cv2.createCLAHE(clipLimit=0.9, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    show_image("Equalized Image", equalized)

    canny_edges = cv2.Canny(gray, 100, 200)
    show_image("Canny Edges", canny_edges)

    # Apply Laplacian filter to the edges detected by Canny
    laplacian_image = cv2.Laplacian(canny_edges, cv2.CV_64F)
    laplacian_image = cv2.convertScaleAbs(laplacian_image)
    show_image("Laplacian Image", laplacian_image)

    threshold = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    denoised = cv2.fastNlMeansDenoising(threshold, h=0)
    show_image("Denoised Image", denoised)

    # Apply blur filter
    blurred = cv2.blur(denoised, (5, 5))  # You can adjust the kernel size as needed
    show_image("Blurred Image", blurred)

    # Find contours
    contours, _ = cv2.findContours(laplacian_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    answers_locations = []
    random_answers = {}
    rectangles = []
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            rectangles.append(approx)

    # Process each rectangle separately
    for idx, rectangle in enumerate(rectangles):
        x, y, w, h = cv2.boundingRect(rectangle)
        # Draw the rectangle on the original image
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Add text to the rectangle indicating its dimensions
        text = f"{x + w // 2}, {y + h // 2}"
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Print the location of the rectangle
        print(f"Rectangle Location: Center=({x + w // 2}, {y + h // 2})")
        answers_locations.append((x + w // 2, y + h // 2))
        # Extract the region of interest
        roi = equalized[y:y + h, x:x + w]
        roi = cv2.medianBlur(roi, 7)
        roi_color = image[y:y + h, x:x + w]

        # Apply Hough Circle Transform
        rows = roi.shape[0]
        circles = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=2, minDist=rows/4, param1=100, param2=30, minRadius=1,
                                   maxRadius=50)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x_circle, y_circle, r) in circles:
                # Create a mask for the circle
                mask = np.zeros_like(roi)
                cv2.circle(mask, (x_circle, y_circle), r, 255, -1)
                # Apply the mask to the thresholded ROI to check fill percentage
                circle_region = cv2.bitwise_and(threshold[y:y + h, x:x + w], threshold[y:y + h, x:x + w], mask=mask)
                white_pixels = np.sum(circle_region == 255)
                total_pixels = np.pi * r * r
                fill_ratio = white_pixels / total_pixels

                # Classify the circle based on the x-coordinate of its center
                if 0 <= x_circle < 40:
                    classification = 'a'
                elif 50 <= x_circle < 75:
                    classification = 'b'
                elif 80 <= x_circle < 105:
                    classification = 'c'
                elif 105 <= x_circle < 150:
                    classification = 'd'
                else:
                    classification = 'unknown'
                # Consider a circle filled if more than a threshold ratio of its area is white
                if fill_ratio > 0.5:  # Adjust the threshold as needed
                    # Apply the mask to the colored ROI
                    masked_roi_color = cv2.bitwise_and(roi_color, roi_color, mask=mask)
                    # Display the masked ROI
                    show_image(f"Filled Circle Mask ({x_circle},{y_circle})", masked_roi_color)
                    # Print the dimensions of the filled circle along with its classification
                    print(
                        f"Filled Circle in ROI {idx + 1}: Center=({x_circle}, {y_circle}), Radius={r}, Classification={classification}")
                    random_answers[(x + w // 2, y + h // 2)] = classification

    try:
        sorted_array = sort_pixels(answers_locations)
        print('locations',answers_locations)
        print('sorted',sorted_array)

        print('random_answers',random_answers)
        realanswers = []
        for loc in sorted_array:
            if loc in random_answers:
                realanswers.append(random_answers[loc])
        print(realanswers)
    except:
        print('error')
    # Resize the image for display
    height, width = image.shape[:2]
    max_height = 800
    max_width = 800

    if height > max_height or width > max_width:
        scaling_factor = min(max_height / float(height), max_width / float(width))
        image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

    # Display the image with rectangles
    show_image("Image with Rectangles", image)

    return realanswers

# Example usage
# script_dir = os.path.dirname(__file__)
# image_path = os.path.join(script_dir, 'mcq.jpeg')
# image = cv2.imread(image_path)
# realanswers = process_mcq_image(image)
# print("Detected Answers:", realanswers)
