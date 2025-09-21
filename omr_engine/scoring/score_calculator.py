"""
Score Calculator Module for OMR Processing

This module provides functionality to calculate scores based on detected answers
and answer keys, with support for various scoring rules and detailed analytics.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScoringRule:
    """
    Represents a scoring rule for a subject or question type.
    """
    correct_points: float = 1.0
    incorrect_penalty: float = 0.0
    unanswered_penalty: float = 0.0
    max_score: float = 20.0
    min_score: float = 0.0


@dataclass
class QuestionResult:
    """
    Represents the result for a single question.
    """
    question_number: int
    subject: str
    correct_answer: str
    student_answer: Optional[str]
    is_correct: bool
    points_earned: float
    confidence_score: float
    notes: List[str]


@dataclass
class SubjectResult:
    """
    Represents the result for a subject.
    """
    subject_name: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    raw_score: float
    percentage: float
    grade: str
    question_results: List[QuestionResult]


@dataclass
class OverallResult:
    """
    Represents the overall OMR evaluation result.
    """
    student_id: Optional[str]
    exam_id: str
    total_questions: int
    total_correct: int
    total_incorrect: int
    total_unanswered: int
    overall_score: float
    overall_percentage: float
    overall_grade: str
    subject_results: List[SubjectResult]
    processing_timestamp: datetime
    confidence_metrics: Dict[str, float]
    processing_notes: List[str]


class ScoreCalculator:
    """
    A class for calculating OMR scores based on answer keys and detected answers.
    """
    
    def __init__(self):
        """Initialize the score calculator."""
        self.default_scoring_rule = ScoringRule()
        self.grade_boundaries = {
            'A+': 95.0,
            'A': 90.0,
            'A-': 85.0,
            'B+': 80.0,
            'B': 75.0,
            'B-': 70.0,
            'C+': 65.0,
            'C': 60.0,
            'C-': 55.0,
            'D': 50.0,
            'F': 0.0
        }
    
    def load_answer_key(self, answer_key_path: str) -> Dict[str, Any]:
        """
        Load answer key from JSON file.
        
        Args:
            answer_key_path: Path to the answer key JSON file
            
        Returns:
            Dictionary containing answer key data
        """
        try:
            with open(answer_key_path, 'r', encoding='utf-8') as f:
                answer_key = json.load(f)
            
            logger.info(f"Loaded answer key for exam: {answer_key.get('exam_info', {}).get('exam_name', 'Unknown')}")
            return answer_key
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Answer key file not found: {answer_key_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in answer key file: {e}")
    
    def get_scoring_rule(self, answer_key: Dict[str, Any], subject: str) -> ScoringRule:
        """
        Get the scoring rule for a specific subject.
        
        Args:
            answer_key: Answer key dictionary
            subject: Subject name
            
        Returns:
            ScoringRule object for the subject
        """
        scoring_rules = answer_key.get('scoring_rules', {})
        subject_rule = scoring_rules.get(subject, scoring_rules.get('default', {}))
        
        return ScoringRule(
            correct_points=subject_rule.get('correct_points', self.default_scoring_rule.correct_points),
            incorrect_penalty=subject_rule.get('incorrect_penalty', self.default_scoring_rule.incorrect_penalty),
            unanswered_penalty=subject_rule.get('unanswered_penalty', self.default_scoring_rule.unanswered_penalty),
            max_score=subject_rule.get('max_score', self.default_scoring_rule.max_score),
            min_score=subject_rule.get('min_score', self.default_scoring_rule.min_score)
        )
    
    def calculate_question_score(self, correct_answer: str, 
                               student_answer: Optional[str],
                               scoring_rule: ScoringRule,
                               confidence_score: float = 1.0) -> Tuple[float, bool, List[str]]:
        """
        Calculate score for a single question.
        
        Args:
            correct_answer: The correct answer (A, B, C, D)
            student_answer: The student's answer (A, B, C, D, or None)
            scoring_rule: Scoring rule to apply
            confidence_score: Confidence in the detected answer (0-1)
            
        Returns:
            Tuple of (points_earned, is_correct, notes)
        """
        notes = []
        
        if student_answer is None:
            # Unanswered question
            points = -scoring_rule.unanswered_penalty
            is_correct = False
            notes.append("Question not answered")
        elif student_answer.upper() == correct_answer.upper():
            # Correct answer
            points = scoring_rule.correct_points
            is_correct = True
            if confidence_score < 0.8:
                notes.append(f"Low confidence detection ({confidence_score:.2f})")
        else:
            # Incorrect answer
            points = -scoring_rule.incorrect_penalty
            is_correct = False
            notes.append(f"Incorrect answer: {student_answer} (correct: {correct_answer})")
        
        # Apply confidence-based adjustment for low confidence detections
        if confidence_score < 0.5 and student_answer is not None:
            points *= 0.5  # Reduce points for very low confidence
            notes.append("Score reduced due to low detection confidence")
        
        return points, is_correct, notes
    
    def calculate_subject_score(self, subject_name: str,
                              answer_key: Dict[str, Any],
                              detected_answers: Dict[int, Optional[str]],
                              confidence_scores: Dict[int, float]) -> SubjectResult:
        """
        Calculate score for a specific subject.
        
        Args:
            subject_name: Name of the subject
            answer_key: Answer key dictionary
            detected_answers: Dictionary of question_number -> detected_answer
            confidence_scores: Dictionary of question_number -> confidence_score
            
        Returns:
            SubjectResult object
        """
        subject_answers = answer_key['answer_key'].get(subject_name, {})
        scoring_rule = self.get_scoring_rule(answer_key, subject_name)
        
        question_results = []
        total_points = 0.0
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        
        for question_str, correct_answer in subject_answers.items():
            question_num = int(question_str)
            student_answer = detected_answers.get(question_num)
            confidence = confidence_scores.get(question_num, 1.0)
            
            points, is_correct, notes = self.calculate_question_score(
                correct_answer, student_answer, scoring_rule, confidence
            )
            
            total_points += points
            
            if student_answer is None:
                unanswered_count += 1
            elif is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
            
            question_results.append(QuestionResult(
                question_number=question_num,
                subject=subject_name,
                correct_answer=correct_answer,
                student_answer=student_answer,
                is_correct=is_correct,
                points_earned=points,
                confidence_score=confidence,
                notes=notes
            ))
        
        # Ensure score is within bounds
        total_points = max(scoring_rule.min_score, min(scoring_rule.max_score, total_points))
        
        # Calculate percentage
        percentage = (total_points / scoring_rule.max_score) * 100 if scoring_rule.max_score > 0 else 0
        
        # Determine grade
        grade = self.calculate_grade(percentage)
        
        return SubjectResult(
            subject_name=subject_name,
            total_questions=len(subject_answers),
            correct_answers=correct_count,
            incorrect_answers=incorrect_count,
            unanswered=unanswered_count,
            raw_score=total_points,
            percentage=percentage,
            grade=grade,
            question_results=question_results
        )
    
    def calculate_grade(self, percentage: float) -> str:
        """
        Calculate letter grade based on percentage.
        
        Args:
            percentage: Score percentage (0-100)
            
        Returns:
            Letter grade string
        """
        for grade, threshold in self.grade_boundaries.items():
            if percentage >= threshold:
                return grade
        return 'F'
    
    def calculate_overall_score(self, answer_key_path: str,
                              detected_answers: Dict[int, Optional[str]],
                              confidence_scores: Dict[int, float],
                              student_id: Optional[str] = None) -> OverallResult:
        """
        Calculate the overall OMR score for all subjects.
        
        Args:
            answer_key_path: Path to the answer key JSON file
            detected_answers: Dictionary of question_number -> detected_answer
            confidence_scores: Dictionary of question_number -> confidence_score
            student_id: Optional student identifier
            
        Returns:
            OverallResult object containing complete scoring information
        """
        logger.info("Starting overall score calculation")
        
        # Load answer key
        answer_key = self.load_answer_key(answer_key_path)
        
        # Calculate scores for each subject
        subject_results = []
        total_questions = 0
        total_correct = 0
        total_incorrect = 0
        total_unanswered = 0
        total_points = 0.0
        max_possible_points = 0.0
        
        for subject_name in answer_key['answer_key'].keys():
            subject_result = self.calculate_subject_score(
                subject_name, answer_key, detected_answers, confidence_scores
            )
            
            subject_results.append(subject_result)
            
            total_questions += subject_result.total_questions
            total_correct += subject_result.correct_answers
            total_incorrect += subject_result.incorrect_answers
            total_unanswered += subject_result.unanswered
            total_points += subject_result.raw_score
            
            # Get max possible points for this subject
            scoring_rule = self.get_scoring_rule(answer_key, subject_name)
            max_possible_points += scoring_rule.max_score
        
        # Calculate overall percentage and grade
        overall_percentage = (total_points / max_possible_points) * 100 if max_possible_points > 0 else 0
        overall_grade = self.calculate_grade(overall_percentage)
        
        # Calculate confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(confidence_scores)
        
        # Generate processing notes
        processing_notes = self._generate_processing_notes(
            subject_results, confidence_metrics, total_questions
        )
        
        result = OverallResult(
            student_id=student_id,
            exam_id=answer_key.get('exam_info', {}).get('exam_id', 'unknown'),
            total_questions=total_questions,
            total_correct=total_correct,
            total_incorrect=total_incorrect,
            total_unanswered=total_unanswered,
            overall_score=total_points,
            overall_percentage=overall_percentage,
            overall_grade=overall_grade,
            subject_results=subject_results,
            processing_timestamp=datetime.now(),
            confidence_metrics=confidence_metrics,
            processing_notes=processing_notes
        )
        
        logger.info(f"Score calculation complete: {overall_percentage:.1f}% ({overall_grade})")
        return result
    
    def _calculate_confidence_metrics(self, confidence_scores: Dict[int, float]) -> Dict[str, float]:
        """
        Calculate confidence-related metrics.
        
        Args:
            confidence_scores: Dictionary of question_number -> confidence_score
            
        Returns:
            Dictionary of confidence metrics
        """
        if not confidence_scores:
            return {}
        
        scores = list(confidence_scores.values())
        
        return {
            'average_confidence': sum(scores) / len(scores),
            'min_confidence': min(scores),
            'max_confidence': max(scores),
            'low_confidence_count': sum(1 for s in scores if s < 0.7),
            'high_confidence_count': sum(1 for s in scores if s >= 0.9)
        }
    
    def _generate_processing_notes(self, subject_results: List[SubjectResult],
                                 confidence_metrics: Dict[str, float],
                                 total_questions: int) -> List[str]:
        """
        Generate processing notes based on the results.
        
        Args:
            subject_results: List of subject results
            confidence_metrics: Confidence metrics
            total_questions: Total number of questions
            
        Returns:
            List of processing notes
        """
        notes = []
        
        # Check for low confidence detections
        if confidence_metrics.get('low_confidence_count', 0) > 0:
            notes.append(f"{confidence_metrics['low_confidence_count']} questions had low confidence detection")
        
        # Check for subjects with many unanswered questions
        for subject in subject_results:
            unanswered_ratio = subject.unanswered / subject.total_questions if subject.total_questions > 0 else 0
            if unanswered_ratio > 0.2:  # More than 20% unanswered
                notes.append(f"{subject.subject_name}: {subject.unanswered} questions unanswered")
        
        # Check overall performance
        total_answered = sum(s.correct_answers + s.incorrect_answers for s in subject_results)
        if total_answered < total_questions * 0.8:  # Less than 80% answered
            notes.append("Many questions were not answered - check image quality")
        
        # Check for consistent low performance
        low_performing_subjects = [s.subject_name for s in subject_results if s.percentage < 40]
        if len(low_performing_subjects) > len(subject_results) / 2:
            notes.append("Multiple subjects show low performance - verify answer key alignment")
        
        return notes
    
    def export_results(self, result: OverallResult, output_path: str, format: str = 'json'):
        """
        Export results to a file.
        
        Args:
            result: OverallResult object to export
            output_path: Path for the output file
            format: Export format ('json' or 'csv')
        """
        if format.lower() == 'json':
            self._export_json(result, output_path)
        elif format.lower() == 'csv':
            self._export_csv(result, output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, result: OverallResult, output_path: str):
        """Export results as JSON."""
        # Convert dataclass to dictionary for JSON serialization
        result_dict = {
            'student_id': result.student_id,
            'exam_id': result.exam_id,
            'processing_timestamp': result.processing_timestamp.isoformat(),
            'overall_summary': {
                'total_questions': result.total_questions,
                'total_correct': result.total_correct,
                'total_incorrect': result.total_incorrect,
                'total_unanswered': result.total_unanswered,
                'overall_score': result.overall_score,
                'overall_percentage': result.overall_percentage,
                'overall_grade': result.overall_grade
            },
            'subject_results': [
                {
                    'subject_name': s.subject_name,
                    'total_questions': s.total_questions,
                    'correct_answers': s.correct_answers,
                    'incorrect_answers': s.incorrect_answers,
                    'unanswered': s.unanswered,
                    'raw_score': s.raw_score,
                    'percentage': s.percentage,
                    'grade': s.grade,
                    'question_results': [
                        {
                            'question_number': q.question_number,
                            'correct_answer': q.correct_answer,
                            'student_answer': q.student_answer,
                            'is_correct': q.is_correct,
                            'points_earned': q.points_earned,
                            'confidence_score': q.confidence_score,
                            'notes': q.notes
                        }
                        for q in s.question_results
                    ]
                }
                for s in result.subject_results
            ],
            'confidence_metrics': result.confidence_metrics,
            'processing_notes': result.processing_notes
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results exported to JSON: {output_path}")
    
    def _export_csv(self, result: OverallResult, output_path: str):
        """Export results as CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Question', 'Subject', 'Correct Answer', 'Student Answer',
                'Is Correct', 'Points Earned', 'Confidence', 'Notes'
            ])
            
            # Write question results
            for subject in result.subject_results:
                for question in subject.question_results:
                    writer.writerow([
                        question.question_number,
                        question.subject,
                        question.correct_answer,
                        question.student_answer or '',
                        question.is_correct,
                        question.points_earned,
                        f"{question.confidence_score:.3f}",
                        '; '.join(question.notes)
                    ])
        
        logger.info(f"Results exported to CSV: {output_path}")


def calculate_omr_score(answer_key_path: str,
                       detected_answers: Dict[int, Optional[str]],
                       confidence_scores: Dict[int, float],
                       student_id: Optional[str] = None) -> OverallResult:
    """
    Convenience function to calculate OMR scores.
    
    Args:
        answer_key_path: Path to the answer key JSON file
        detected_answers: Dictionary of question_number -> detected_answer
        confidence_scores: Dictionary of question_number -> confidence_score
        student_id: Optional student identifier
        
    Returns:
        OverallResult object containing complete scoring information
    """
    calculator = ScoreCalculator()
    return calculator.calculate_overall_score(
        answer_key_path, detected_answers, confidence_scores, student_id
    )