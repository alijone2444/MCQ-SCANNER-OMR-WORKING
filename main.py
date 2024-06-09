from cropimage import findExam
from edgeDection import process_mcq_image
import cv2

# Example usage:
efile_path = "mcq.jpeg"
main = cv2.imread(efile_path)


# Resize the image (if needed)
main_resized = cv2.resize(main, (400, 400))

# Display the resized image
cv2.imshow('Resized Image', main_resized)
cv2.waitKey(0)

# Find exam and process MCQ image
wrapped_efile = findExam(efile_path)
finala = process_mcq_image(wrapped_efile)

print("Detected Answers:", finala)

cv2.destroyAllWindows()  # Close all OpenCV windows
