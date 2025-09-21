"""
Main OMR Processor Module

This module provides the main OMR processing pipeline that integrates
preprocessing, bubble detection, template matching, and scoring functionality.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from datetime import datetime

# Import OMR engine modules
from .preprocessing.image_processor import ImageProcessor, preprocess_omr_image
from .detection.bubble_detector import BubbleDetector, detect_omr_answers
from .detection.template_matcher import TemplateMatcherOMR, match_omr_template
from .scoring.score_calculator import ScoreCalculator, calculate_omr_score, OverallResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OMRProcessor:
    """
    Main OMR processing class that orchestrates the entire evaluation pipeline.
    
    This processor handles the complete workflow from raw image input to
    final scored results, including preprocessing, detection, and scoring.
    """
    
    def __init__(self, 
                 preprocessing_config: Optional[Dict] = None,
                 detection_config: Optional[Dict] = None,
                 scoring_config: Optional[Dict] = None):
        """
        Initialize the OMR processor with configuration options.
        
        Args:
            preprocessing_config: Configuration for image preprocessing
            detection_config: Configuration for bubble detection
            scoring_config: Configuration for scoring
        """
        # Initialize components with configurations
        self.image_processor = ImageProcessor(**(preprocessing_config or {}))
        self.bubble_detector = BubbleDetector(**(detection_config or {}))
        self.template_matcher = TemplateMatcherOMR()
        self.score_calculator = ScoreCalculator()
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0
        }
        
        logger.info("OMR Processor initialized successfully")
    
    def process_single_sheet(self, 
                           image_path: str,
                           answer_key_path: str,
                           student_id: Optional[str] = None,
                           output_dir: Optional[str] = None,
                           save_intermediate: bool = False) -> Dict[str, Any]:
        """
        Process a single OMR sheet through the complete pipeline.
        
        Args:
            image_path: Path to the OMR sheet image
            answer_key_path: Path to the answer key JSON file
            student_id: Optional student identifier
            output_dir: Optional directory to save results and intermediate files
            save_intermediate: Whether to save intermediate processing images
            
        Returns:
            Dictionary containing processing results and metadata
        """
        start_time = datetime.now()
        logger.info(f"Starting OMR processing for: {image_path}")
        
        try:
            # Step 1: Load and validate input image
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert to grayscale for processing
            if len(original_image.shape) == 3:
                gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = original_image.copy()
            
            # Step 2: Validate sheet format using template matcher
            validation_result = self.template_matcher.validate_sheet_format(gray_image)
            
            if not validation_result['is_valid']:
                logger.warning(f"Sheet validation failed: {validation_result['issues']}")
            
            # Step 3: Preprocess the image
            logger.info("Preprocessing image...")
            preprocessed_image = self.image_processor.preprocess_omr_image(gray_image)
            
            # Step 4: Detect bubbles and extract answers
            logger.info("Detecting bubbles and extracting answers...")
            detection_result = self.bubble_detector.detect_answers(preprocessed_image)
            
            detected_answers = detection_result['answers']
            confidence_scores = detection_result['confidence_scores']
            
            # Step 5: Calculate scores
            logger.info("Calculating scores...")
            scoring_result = self.score_calculator.calculate_overall_score(
                answer_key_path, detected_answers, confidence_scores, student_id
            )
            
            # Step 6: Compile final results
            processing_time = (datetime.now() - start_time).total_seconds()
            
            final_result = {
                'success': True,
                'student_id': student_id,
                'image_path': image_path,
                'processing_timestamp': start_time.isoformat(),
                'processing_time_seconds': processing_time,
                'validation': validation_result,
                'detection_summary': {
                    'total_bubbles_detected': detection_result['total_bubbles_detected'],
                    'rows_detected': detection_result['rows_detected'],
                    'questions_answered': len([a for a in detected_answers.values() if a is not None]),
                    'questions_unanswered': len([a for a in detected_answers.values() if a is None]),
                    'average_confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
                },
                'scoring_result': scoring_result,
                'detected_answers': detected_answers,
                'confidence_scores': confidence_scores,
                'processing_notes': detection_result.get('processing_notes', []) + validation_result.get('issues', [])
            }
            
            # Step 7: Save results and intermediate files if requested
            if output_dir:
                self._save_processing_results(
                    final_result, output_dir, 
                    original_image, preprocessed_image if save_intermediate else None
                )
            
            # Update statistics
            self.processing_stats['successful_processing'] += 1
            
            logger.info(f"OMR processing completed successfully in {processing_time:.2f} seconds")
            logger.info(f"Overall score: {scoring_result.overall_percentage:.1f}% ({scoring_result.overall_grade})")
            
            return final_result
            
        except Exception as e:
            # Handle processing errors
            processing_time = (datetime.now() - start_time).total_seconds()
            
            error_result = {
                'success': False,
                'student_id': student_id,
                'image_path': image_path,
                'processing_timestamp': start_time.isoformat(),
                'processing_time_seconds': processing_time,
                'error': str(e),
                'error_type': type(e).__name__
            }
            
            self.processing_stats['failed_processing'] += 1
            
            logger.error(f"OMR processing failed: {e}")
            return error_result
            
        finally:
            self.processing_stats['total_processed'] += 1
            # Update average processing time
            if self.processing_stats['total_processed'] > 0:
                total_time = (self.processing_stats['average_processing_time'] * 
                            (self.processing_stats['total_processed'] - 1) + processing_time)
                self.processing_stats['average_processing_time'] = total_time / self.processing_stats['total_processed']
    
    def process_batch(self, 
                     image_paths: List[str],
                     answer_key_path: str,
                     output_dir: str,
                     student_ids: Optional[List[str]] = None,
                     save_intermediate: bool = False) -> Dict[str, Any]:
        """
        Process multiple OMR sheets in batch.
        
        Args:
            image_paths: List of paths to OMR sheet images
            answer_key_path: Path to the answer key JSON file
            output_dir: Directory to save results
            student_ids: Optional list of student identifiers (must match image_paths length)
            save_intermediate: Whether to save intermediate processing images
            
        Returns:
            Dictionary containing batch processing results
        """
        logger.info(f"Starting batch processing of {len(image_paths)} OMR sheets")
        
        if student_ids and len(student_ids) != len(image_paths):
            raise ValueError("Number of student IDs must match number of image paths")
        
        batch_results = []
        successful_count = 0
        failed_count = 0
        
        for i, image_path in enumerate(image_paths):
            student_id = student_ids[i] if student_ids else None
            
            logger.info(f"Processing sheet {i+1}/{len(image_paths)}: {Path(image_path).name}")
            
            result = self.process_single_sheet(
                image_path, answer_key_path, student_id, output_dir, save_intermediate
            )
            
            batch_results.append(result)
            
            if result['success']:
                successful_count += 1
            else:
                failed_count += 1
        
        # Generate batch summary
        batch_summary = {
            'total_sheets': len(image_paths),
            'successful_processing': successful_count,
            'failed_processing': failed_count,
            'success_rate': (successful_count / len(image_paths)) * 100 if image_paths else 0,
            'batch_results': batch_results,
            'processing_statistics': self.processing_stats.copy()
        }
        
        # Save batch summary
        self._save_batch_summary(batch_summary, output_dir)
        
        logger.info(f"Batch processing completed: {successful_count}/{len(image_paths)} successful")
        return batch_summary
    
    def _save_processing_results(self, 
                               result: Dict[str, Any],
                               output_dir: str,
                               original_image: np.ndarray,
                               preprocessed_image: Optional[np.ndarray] = None):
        """
        Save processing results to files.
        
        Args:
            result: Processing result dictionary
            output_dir: Output directory
            original_image: Original input image
            preprocessed_image: Preprocessed image (optional)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename base
        student_id = result.get('student_id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{student_id}_{timestamp}"
        
        # Save JSON results
        if result['success']:
            json_path = output_path / f"{base_filename}_results.json"
            self.score_calculator.export_results(
                result['scoring_result'], str(json_path), 'json'
            )
            
            # Save CSV results
            csv_path = output_path / f"{base_filename}_results.csv"
            self.score_calculator.export_results(
                result['scoring_result'], str(csv_path), 'csv'
            )
        
        # Save images if requested
        if preprocessed_image is not None:
            preprocessed_path = output_path / f"{base_filename}_preprocessed.jpg"
            cv2.imwrite(str(preprocessed_path), preprocessed_image)
        
        # Save processing log
        log_path = output_path / f"{base_filename}_processing_log.json"
        import json
        with open(log_path, 'w', encoding='utf-8') as f:
            # Create a serializable version of the result
            log_data = {
                'success': result['success'],
                'student_id': result['student_id'],
                'image_path': result['image_path'],
                'processing_timestamp': result['processing_timestamp'],
                'processing_time_seconds': result['processing_time_seconds'],
                'validation': result.get('validation', {}),
                'detection_summary': result.get('detection_summary', {}),
                'processing_notes': result.get('processing_notes', [])
            }
            if not result['success']:
                log_data['error'] = result.get('error', '')
                log_data['error_type'] = result.get('error_type', '')
            
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _save_batch_summary(self, batch_summary: Dict[str, Any], output_dir: str):
        """
        Save batch processing summary.
        
        Args:
            batch_summary: Batch summary dictionary
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = output_path / f"batch_summary_{timestamp}.json"
        
        import json
        
        # Create a serializable version of the summary
        serializable_summary = {
            'total_sheets': batch_summary['total_sheets'],
            'successful_processing': batch_summary['successful_processing'],
            'failed_processing': batch_summary['failed_processing'],
            'success_rate': batch_summary['success_rate'],
            'processing_statistics': batch_summary['processing_statistics'],
            'individual_results': [
                {
                    'success': r['success'],
                    'student_id': r.get('student_id'),
                    'image_path': r['image_path'],
                    'processing_time_seconds': r['processing_time_seconds'],
                    'overall_score': r['scoring_result'].overall_score if r['success'] else None,
                    'overall_percentage': r['scoring_result'].overall_percentage if r['success'] else None,
                    'overall_grade': r['scoring_result'].overall_grade if r['success'] else None,
                    'error': r.get('error') if not r['success'] else None
                }
                for r in batch_summary['batch_results']
            ]
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch summary saved to: {summary_path}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get current processing statistics.
        
        Returns:
            Dictionary containing processing statistics
        """
        return self.processing_stats.copy()
    
    def reset_statistics(self):
        """Reset processing statistics."""
        self.processing_stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0
        }
        logger.info("Processing statistics reset")


# Convenience functions for direct usage

def process_omr_sheet(image_path: str,
                     answer_key_path: str,
                     student_id: Optional[str] = None,
                     output_dir: Optional[str] = None,
                     **config) -> Dict[str, Any]:
    """
    Convenience function to process a single OMR sheet.
    
    Args:
        image_path: Path to the OMR sheet image
        answer_key_path: Path to the answer key JSON file
        student_id: Optional student identifier
        output_dir: Optional directory to save results
        **config: Additional configuration options
        
    Returns:
        Dictionary containing processing results
    """
    processor = OMRProcessor(
        preprocessing_config=config.get('preprocessing_config'),
        detection_config=config.get('detection_config'),
        scoring_config=config.get('scoring_config')
    )
    
    return processor.process_single_sheet(
        image_path, answer_key_path, student_id, output_dir,
        config.get('save_intermediate', False)
    )


def process_omr_batch(image_paths: List[str],
                     answer_key_path: str,
                     output_dir: str,
                     student_ids: Optional[List[str]] = None,
                     **config) -> Dict[str, Any]:
    """
    Convenience function to process multiple OMR sheets.
    
    Args:
        image_paths: List of paths to OMR sheet images
        answer_key_path: Path to the answer key JSON file
        output_dir: Directory to save results
        student_ids: Optional list of student identifiers
        **config: Additional configuration options
        
    Returns:
        Dictionary containing batch processing results
    """
    processor = OMRProcessor(
        preprocessing_config=config.get('preprocessing_config'),
        detection_config=config.get('detection_config'),
        scoring_config=config.get('scoring_config')
    )
    
    return processor.process_batch(
        image_paths, answer_key_path, output_dir, student_ids,
        config.get('save_intermediate', False)
    )