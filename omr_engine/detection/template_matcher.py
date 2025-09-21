"""
Template Matching Module for OMR Processing

This module provides functionality to match OMR sheet templates and locate
specific regions like answer areas, alignment marks, and student information sections.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateMatcherOMR:
    """
    A class for template matching and region detection in OMR sheets.
    
    This matcher helps identify key areas of the OMR sheet by matching
    against known templates and alignment marks.
    """
    
    def __init__(self, match_threshold: float = 0.7):
        """
        Initialize the template matcher.
        
        Args:
            match_threshold: Minimum confidence score for template matches (0-1)
        """
        self.match_threshold = match_threshold
        self.templates = {}
        
    def load_template(self, template_name: str, template_image: np.ndarray):
        """
        Load a template for matching.
        
        Args:
            template_name: Name identifier for the template
            template_image: Template image (grayscale)
        """
        if len(template_image.shape) == 3:
            template_image = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        
        self.templates[template_name] = template_image
        logger.info(f"Loaded template '{template_name}' with size {template_image.shape}")
    
    def find_alignment_marks(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Find alignment marks (typically small squares or circles) in the OMR sheet.
        
        Args:
            image: Input OMR sheet image (grayscale)
            
        Returns:
            List of (x, y) coordinates of detected alignment marks
        """
        # Create a template for typical alignment marks (small filled squares)
        mark_size = 15
        alignment_template = np.zeros((mark_size, mark_size), dtype=np.uint8)
        cv2.rectangle(alignment_template, (2, 2), (mark_size-3, mark_size-3), 255, -1)
        
        # Perform template matching
        result = cv2.matchTemplate(image, alignment_template, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the match exceeds the threshold
        locations = np.where(result >= self.match_threshold)
        
        # Convert to list of coordinates
        marks = []
        for pt in zip(*locations[::-1]):  # Switch x and y
            marks.append(pt)
        
        # Remove duplicate detections (non-maximum suppression)
        marks = self._non_max_suppression(marks, result, mark_size)
        
        logger.info(f"Found {len(marks)} alignment marks")
        return marks
    
    def _non_max_suppression(self, locations: List[Tuple[int, int]], 
                           confidence_map: np.ndarray, 
                           template_size: int) -> List[Tuple[int, int]]:
        """
        Apply non-maximum suppression to remove duplicate detections.
        
        Args:
            locations: List of detected locations
            confidence_map: Template matching confidence map
            template_size: Size of the template used
            
        Returns:
            Filtered list of locations
        """
        if not locations:
            return []
        
        # Convert to numpy array for easier processing
        locations = np.array(locations)
        
        # Get confidence scores for each location
        scores = [confidence_map[y, x] for x, y in locations]
        
        # Sort by confidence score (descending)
        indices = np.argsort(scores)[::-1]
        
        keep = []
        suppression_distance = template_size
        
        for i in indices:
            x, y = locations[i]
            
            # Check if this location is too close to any already kept location
            too_close = False
            for kept_x, kept_y in keep:
                distance = np.sqrt((x - kept_x)**2 + (y - kept_y)**2)
                if distance < suppression_distance:
                    too_close = True
                    break
            
            if not too_close:
                keep.append((x, y))
        
        return keep
    
    def detect_answer_regions(self, image: np.ndarray, 
                            num_questions: int = 100,
                            questions_per_row: int = 5) -> List[Dict]:
        """
        Detect and locate answer bubble regions in the OMR sheet.
        
        Args:
            image: Input OMR sheet image
            num_questions: Total number of questions expected
            questions_per_row: Number of questions per row
            
        Returns:
            List of dictionaries containing region information
        """
        height, width = image.shape[:2]
        
        # Calculate approximate regions based on standard OMR layout
        # This is a simplified approach - in practice, you'd use alignment marks
        
        num_rows = (num_questions + questions_per_row - 1) // questions_per_row
        
        # Assume answer area takes up middle 60% of the sheet
        answer_start_y = int(height * 0.2)
        answer_end_y = int(height * 0.8)
        answer_height = answer_end_y - answer_start_y
        
        answer_start_x = int(width * 0.1)
        answer_end_x = int(width * 0.9)
        answer_width = answer_end_x - answer_start_x
        
        regions = []
        
        row_height = answer_height // num_rows
        question_width = answer_width // questions_per_row
        
        for row in range(num_rows):
            for col in range(questions_per_row):
                question_num = row * questions_per_row + col + 1
                if question_num > num_questions:
                    break
                
                x = answer_start_x + col * question_width
                y = answer_start_y + row * row_height
                w = question_width
                h = row_height
                
                regions.append({
                    'question_number': question_num,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'row': row,
                    'column': col
                })
        
        logger.info(f"Detected {len(regions)} answer regions")
        return regions
    
    def extract_student_info_region(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract the student information region from the OMR sheet.
        
        Args:
            image: Input OMR sheet image
            
        Returns:
            Cropped image of the student info region, or None if not found
        """
        height, width = image.shape[:2]
        
        # Assume student info is in the top portion of the sheet
        info_region = image[0:int(height * 0.15), 0:width]
        
        return info_region
    
    def calculate_sheet_orientation(self, image: np.ndarray) -> float:
        """
        Calculate the orientation/rotation angle of the OMR sheet.
        
        Args:
            image: Input OMR sheet image
            
        Returns:
            Rotation angle in degrees (positive = clockwise)
        """
        # Find alignment marks
        marks = self.find_alignment_marks(image)
        
        if len(marks) < 2:
            logger.warning("Insufficient alignment marks for orientation calculation")
            return 0.0
        
        # Sort marks by position to find corner marks
        marks = sorted(marks, key=lambda p: (p[1], p[0]))  # Sort by y, then x
        
        # Use the first two marks to calculate angle
        if len(marks) >= 2:
            p1, p2 = marks[0], marks[1]
            
            # Calculate angle between the line connecting marks and horizontal
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            
            angle = np.arctan2(dy, dx) * 180 / np.pi
            
            # Normalize angle to [-45, 45] range
            while angle > 45:
                angle -= 90
            while angle < -45:
                angle += 90
            
            logger.info(f"Calculated sheet orientation: {angle:.2f} degrees")
            return angle
        
        return 0.0
    
    def validate_sheet_format(self, image: np.ndarray, 
                            expected_marks: int = 4) -> Dict:
        """
        Validate that the OMR sheet matches the expected format.
        
        Args:
            image: Input OMR sheet image
            expected_marks: Expected number of alignment marks
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'confidence': 1.0
        }
        
        # Check image dimensions
        height, width = image.shape[:2]
        aspect_ratio = width / height
        
        # Typical OMR sheets have aspect ratio around 0.7-0.8 (A4 portrait)
        if aspect_ratio < 0.5 or aspect_ratio > 1.2:
            validation_result['issues'].append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
            validation_result['confidence'] *= 0.8
        
        # Check for alignment marks
        marks = self.find_alignment_marks(image)
        if len(marks) < expected_marks:
            validation_result['issues'].append(
                f"Found {len(marks)} alignment marks, expected {expected_marks}"
            )
            validation_result['confidence'] *= 0.7
        
        # Check image quality (contrast, sharpness)
        gray_std = np.std(image)
        if gray_std < 30:  # Low contrast
            validation_result['issues'].append("Low image contrast detected")
            validation_result['confidence'] *= 0.9
        
        # Check for blur using Laplacian variance
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        if laplacian_var < 100:  # Blurry image
            validation_result['issues'].append("Image appears blurry")
            validation_result['confidence'] *= 0.8
        
        # Overall validation
        if validation_result['confidence'] < 0.6:
            validation_result['is_valid'] = False
        
        if validation_result['issues']:
            logger.warning(f"Sheet validation issues: {validation_result['issues']}")
        else:
            logger.info("Sheet format validation passed")
        
        return validation_result
    
    def create_processing_mask(self, image: np.ndarray, 
                             regions: List[Dict]) -> np.ndarray:
        """
        Create a mask highlighting the regions to be processed.
        
        Args:
            image: Input image
            regions: List of region dictionaries
            
        Returns:
            Binary mask image
        """
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        for region in regions:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
        
        return mask


def match_omr_template(image_path: str, template_path: str, **kwargs) -> Dict:
    """
    Convenience function to match an OMR sheet against a template.
    
    Args:
        image_path: Path to the OMR sheet image
        template_path: Path to the template image
        **kwargs: Additional parameters for TemplateMatcherOMR
        
    Returns:
        Dictionary containing matching results and detected regions
    """
    # Load images
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    if template is None:
        raise ValueError(f"Could not load template from {template_path}")
    
    # Create matcher and process
    matcher = TemplateMatcherOMR(**kwargs)
    matcher.load_template("main_template", template)
    
    # Validate sheet format
    validation = matcher.validate_sheet_format(image)
    
    # Detect regions
    regions = matcher.detect_answer_regions(image)
    
    # Calculate orientation
    orientation = matcher.calculate_sheet_orientation(image)
    
    return {
        'validation': validation,
        'regions': regions,
        'orientation': orientation,
        'alignment_marks': matcher.find_alignment_marks(image)
    }