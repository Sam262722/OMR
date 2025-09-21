"""
Image preprocessing module for OMR sheet processing
Handles rotation, skew correction, and perspective distortion
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import math


class ImageProcessor:
    """
    Main class for OMR image preprocessing operations
    """
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug: bool):
        """Enable/disable debug mode for visualization"""
        self.debug_mode = debug
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Complete preprocessing pipeline for OMR sheets
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image ready for bubble detection
        """
        # Step 1: Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Step 2: Detect and correct perspective distortion
        corrected = self.correct_perspective(gray)
        
        # Step 3: Detect and correct skew
        deskewed = self.correct_skew(corrected)
        
        # Step 4: Enhance image quality
        enhanced = self.enhance_image(deskewed)
        
        return enhanced
    
    def detect_corners(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect the four corners of the OMR sheet using alignment marks
        
        Args:
            image: Grayscale input image
            
        Returns:
            Array of four corner points or None if not found
        """
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for circular alignment marks
        corners = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 500:  # Filter by area for alignment marks
                # Check if contour is roughly circular
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * math.pi * area / (perimeter * perimeter)
                
                if circularity > 0.7:  # Circular enough
                    # Get center of the circle
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        corners.append([cx, cy])
        
        if len(corners) >= 4:
            # Sort corners to get proper order (top-left, top-right, bottom-right, bottom-left)
            corners = np.array(corners, dtype=np.float32)
            return self._order_corners(corners[:4])
        
        return None
    
    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """
        Order corners in clockwise order starting from top-left
        
        Args:
            corners: Array of corner points
            
        Returns:
            Ordered corner points
        """
        # Calculate center point
        center = np.mean(corners, axis=0)
        
        # Sort by angle from center
        def angle_from_center(point):
            return math.atan2(point[1] - center[1], point[0] - center[0])
        
        # Sort corners by angle
        corners_with_angles = [(corner, angle_from_center(corner)) for corner in corners]
        corners_with_angles.sort(key=lambda x: x[1])
        
        # Extract sorted corners
        sorted_corners = np.array([corner for corner, _ in corners_with_angles], dtype=np.float32)
        
        # Ensure proper order: top-left, top-right, bottom-right, bottom-left
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Sum and difference to find corners
        s = sorted_corners.sum(axis=1)
        diff = np.diff(sorted_corners, axis=1)
        
        rect[0] = sorted_corners[np.argmin(s)]      # top-left
        rect[2] = sorted_corners[np.argmax(s)]      # bottom-right
        rect[1] = sorted_corners[np.argmin(diff)]   # top-right
        rect[3] = sorted_corners[np.argmax(diff)]   # bottom-left
        
        return rect
    
    def correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """
        Correct perspective distortion using detected corners
        
        Args:
            image: Input grayscale image
            
        Returns:
            Perspective-corrected image
        """
        corners = self.detect_corners(image)
        
        if corners is None:
            # If corners not detected, return original image
            return image
        
        # Define the desired output dimensions (A4 ratio)
        width = 800
        height = int(width * 297 / 210)  # A4 aspect ratio
        
        # Define destination points for perspective transform
        dst_points = np.array([
            [0, 0],                    # top-left
            [width - 1, 0],           # top-right
            [width - 1, height - 1],  # bottom-right
            [0, height - 1]           # bottom-left
        ], dtype=np.float32)
        
        # Calculate perspective transform matrix
        transform_matrix = cv2.getPerspectiveTransform(corners, dst_points)
        
        # Apply perspective correction
        corrected = cv2.warpPerspective(image, transform_matrix, (width, height))
        
        return corrected
    
    def detect_skew_angle(self, image: np.ndarray) -> float:
        """
        Detect skew angle using Hough line detection
        
        Args:
            image: Input grayscale image
            
        Returns:
            Skew angle in degrees
        """
        # Apply edge detection
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
        
        if lines is None:
            return 0.0
        
        # Calculate angles of detected lines
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            # Convert to angle from horizontal
            if angle > 90:
                angle = angle - 180
            angles.append(angle)
        
        # Find the most common angle (mode)
        if angles:
            # Use median to avoid outliers
            skew_angle = np.median(angles)
            return skew_angle
        
        return 0.0
    
    def correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Correct skew in the image
        
        Args:
            image: Input image
            
        Returns:
            Deskewed image
        """
        skew_angle = self.detect_skew_angle(image)
        
        # Only correct if skew is significant (> 0.5 degrees)
        if abs(skew_angle) < 0.5:
            return image
        
        # Get image dimensions
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Create rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
        
        # Apply rotation
        deskewed = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return deskewed
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better bubble detection
        
        Args:
            image: Input grayscale image
            
        Returns:
            Enhanced image
        """
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Apply Gaussian blur to reduce noise
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Apply sharpening filter
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
    
    def resize_image(self, image: np.ndarray, target_width: int = 800) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image: Input image
            target_width: Target width in pixels
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        aspect_ratio = height / width
        target_height = int(target_width * aspect_ratio)
        
        resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized


def preprocess_omr_image(image_path: str, output_path: Optional[str] = None) -> np.ndarray:
    """
    Convenience function to preprocess an OMR image from file
    
    Args:
        image_path: Path to input image
        output_path: Optional path to save processed image
        
    Returns:
        Preprocessed image array
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Create processor and preprocess
    processor = ImageProcessor()
    processed = processor.preprocess_image(image)
    
    # Save if output path provided
    if output_path:
        cv2.imwrite(output_path, processed)
    
    return processed