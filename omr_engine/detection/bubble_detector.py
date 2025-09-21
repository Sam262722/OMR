"""
Bubble Detection Module for OMR Processing

This module provides functionality to detect and extract bubble answers from OMR sheets.
It uses OpenCV for image processing and contour detection to identify filled bubbles.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BubbleDetector:
    """
    A class for detecting and analyzing bubbles in OMR sheets.
    
    This detector uses contour analysis and pixel intensity to determine
    which bubbles are filled and extract the corresponding answers.
    """
    
    def __init__(self, 
                 min_bubble_area: int = 100,
                 max_bubble_area: int = 2000,
                 fill_threshold: float = 0.6,
                 aspect_ratio_tolerance: float = 0.3):
        """
        Initialize the bubble detector with configuration parameters.
        
        Args:
            min_bubble_area: Minimum area for a valid bubble contour
            max_bubble_area: Maximum area for a valid bubble contour
            fill_threshold: Threshold for determining if a bubble is filled (0-1)
            aspect_ratio_tolerance: Tolerance for bubble aspect ratio (should be close to 1 for circles)
        """
        self.min_bubble_area = min_bubble_area
        self.max_bubble_area = max_bubble_area
        self.fill_threshold = fill_threshold
        self.aspect_ratio_tolerance = aspect_ratio_tolerance
        
    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for bubble detection.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Preprocessed binary image ready for contour detection
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding for better bubble detection
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def find_bubble_contours(self, binary_image: np.ndarray) -> List[Tuple]:
        """
        Find potential bubble contours in the binary image.
        
        Args:
            binary_image: Binary image with bubbles as white regions
            
        Returns:
            List of tuples containing (contour, bounding_box, area)
        """
        # Find contours
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        bubble_candidates = []
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_bubble_area or area > self.max_bubble_area:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check aspect ratio (bubbles should be roughly circular)
            aspect_ratio = float(w) / h
            if abs(aspect_ratio - 1.0) > self.aspect_ratio_tolerance:
                continue
            
            # Calculate circularity (4π*area/perimeter²)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Filter by circularity (should be close to 1 for circles)
            if circularity < 0.3:
                continue
            
            bubble_candidates.append((contour, (x, y, w, h), area))
        
        return bubble_candidates
    
    def is_bubble_filled(self, image: np.ndarray, contour: np.ndarray, 
                        bounding_box: Tuple[int, int, int, int]) -> Tuple[bool, float]:
        """
        Determine if a bubble is filled based on pixel intensity analysis.
        
        Args:
            image: Original grayscale image
            contour: Bubble contour
            bounding_box: Bounding box (x, y, w, h)
            
        Returns:
            Tuple of (is_filled, fill_percentage)
        """
        x, y, w, h = bounding_box
        
        # Create a mask for the bubble
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [contour], 255)
        
        # Extract the region of interest
        roi_mask = mask[y:y+h, x:x+w]
        roi_image = image[y:y+h, x:x+w]
        
        # Calculate the mean intensity within the bubble
        bubble_pixels = roi_image[roi_mask[0:roi_image.shape[0], 0:roi_image.shape[1]] > 0]
        
        if len(bubble_pixels) == 0:
            return False, 0.0
        
        mean_intensity = np.mean(bubble_pixels)
        
        # Calculate fill percentage (lower intensity = more filled for dark marks)
        # Normalize to 0-1 scale where 1 is completely filled
        fill_percentage = 1.0 - (mean_intensity / 255.0)
        
        is_filled = fill_percentage >= self.fill_threshold
        
        return is_filled, fill_percentage
    
    def group_bubbles_by_rows(self, bubble_data: List[Dict], 
                             row_tolerance: int = 20) -> List[List[Dict]]:
        """
        Group bubbles into rows based on their y-coordinates.
        
        Args:
            bubble_data: List of bubble dictionaries with position info
            row_tolerance: Tolerance for grouping bubbles into the same row
            
        Returns:
            List of rows, each containing a list of bubbles
        """
        if not bubble_data:
            return []
        
        # Sort bubbles by y-coordinate
        sorted_bubbles = sorted(bubble_data, key=lambda b: b['y'])
        
        rows = []
        current_row = [sorted_bubbles[0]]
        current_y = sorted_bubbles[0]['y']
        
        for bubble in sorted_bubbles[1:]:
            if abs(bubble['y'] - current_y) <= row_tolerance:
                # Same row
                current_row.append(bubble)
            else:
                # New row
                rows.append(sorted(current_row, key=lambda b: b['x']))
                current_row = [bubble]
                current_y = bubble['y']
        
        # Add the last row
        if current_row:
            rows.append(sorted(current_row, key=lambda b: b['x']))
        
        return rows
    
    def detect_answers(self, image: np.ndarray, 
                      questions_per_row: int = 5,
                      options_per_question: int = 4) -> Dict:
        """
        Detect answers from an OMR sheet image.
        
        Args:
            image: Input OMR sheet image
            questions_per_row: Number of questions per row
            options_per_question: Number of options per question (A, B, C, D)
            
        Returns:
            Dictionary containing detected answers and confidence scores
        """
        logger.info("Starting bubble detection process")
        
        # Preprocess the image
        binary_image = self.preprocess_for_detection(image)
        
        # Find bubble contours
        bubble_candidates = self.find_bubble_contours(binary_image)
        logger.info(f"Found {len(bubble_candidates)} potential bubbles")
        
        # Analyze each bubble
        bubble_data = []
        for contour, (x, y, w, h), area in bubble_candidates:
            is_filled, fill_percentage = self.is_bubble_filled(image, contour, (x, y, w, h))
            
            bubble_data.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'area': area,
                'is_filled': is_filled,
                'fill_percentage': fill_percentage,
                'contour': contour
            })
        
        # Group bubbles by rows
        rows = self.group_bubbles_by_rows(bubble_data)
        logger.info(f"Grouped bubbles into {len(rows)} rows")
        
        # Extract answers
        answers = {}
        confidence_scores = {}
        
        for row_idx, row_bubbles in enumerate(rows):
            # Group bubbles in this row by questions
            bubbles_per_question = len(row_bubbles) // questions_per_row
            
            for q_idx in range(questions_per_row):
                question_num = row_idx * questions_per_row + q_idx + 1
                start_idx = q_idx * bubbles_per_question
                end_idx = start_idx + bubbles_per_question
                
                question_bubbles = row_bubbles[start_idx:end_idx]
                
                # Find the filled bubble(s) for this question
                filled_bubbles = [b for b in question_bubbles if b['is_filled']]
                
                if len(filled_bubbles) == 1:
                    # Single answer detected
                    option_idx = question_bubbles.index(filled_bubbles[0])
                    answer = chr(ord('A') + option_idx)
                    answers[question_num] = answer
                    confidence_scores[question_num] = filled_bubbles[0]['fill_percentage']
                elif len(filled_bubbles) > 1:
                    # Multiple answers detected - take the one with highest fill percentage
                    best_bubble = max(filled_bubbles, key=lambda b: b['fill_percentage'])
                    option_idx = question_bubbles.index(best_bubble)
                    answer = chr(ord('A') + option_idx)
                    answers[question_num] = answer
                    confidence_scores[question_num] = best_bubble['fill_percentage'] * 0.8  # Reduce confidence for multiple marks
                else:
                    # No answer detected
                    answers[question_num] = None
                    confidence_scores[question_num] = 0.0
        
        result = {
            'answers': answers,
            'confidence_scores': confidence_scores,
            'total_bubbles_detected': len(bubble_data),
            'rows_detected': len(rows),
            'processing_notes': []
        }
        
        # Add processing notes
        if len(bubble_data) == 0:
            result['processing_notes'].append("No bubbles detected - check image quality")
        
        multiple_answers = sum(1 for q, conf in confidence_scores.items() 
                             if conf < 1.0 and answers[q] is not None)
        if multiple_answers > 0:
            result['processing_notes'].append(f"{multiple_answers} questions had multiple marks")
        
        unanswered = sum(1 for answer in answers.values() if answer is None)
        if unanswered > 0:
            result['processing_notes'].append(f"{unanswered} questions were not answered")
        
        logger.info(f"Detection complete: {len(answers)} questions processed")
        return result
    
    def visualize_detection(self, image: np.ndarray, detection_result: Dict) -> np.ndarray:
        """
        Create a visualization of the bubble detection results.
        
        Args:
            image: Original image
            detection_result: Result from detect_answers method
            
        Returns:
            Image with detection results overlaid
        """
        # Create a copy of the image for visualization
        if len(image.shape) == 3:
            vis_image = image.copy()
        else:
            vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # This is a simplified visualization - in a full implementation,
        # you would draw the detected bubbles and their states
        
        return vis_image


def detect_omr_answers(image_path: str, **kwargs) -> Dict:
    """
    Convenience function to detect OMR answers from an image file.
    
    Args:
        image_path: Path to the OMR sheet image
        **kwargs: Additional parameters for BubbleDetector
        
    Returns:
        Dictionary containing detected answers and metadata
    """
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Create detector and process
    detector = BubbleDetector(**kwargs)
    return detector.detect_answers(image)