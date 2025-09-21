# Answer Keys Directory

This directory contains answer key templates and configurations for different exam versions.

## File Structure

- `sample_answer_key.json` - Sample answer key for testing
- `exam_version_a.json` - Answer key for exam version A
- `exam_version_b.json` - Answer key for exam version B
- `exam_version_c.json` - Answer key for exam version C
- `exam_version_d.json` - Answer key for exam version D

## Answer Key Format

Each answer key file follows this JSON structure:

```json
{
  "exam_info": {
    "exam_id": "UNIQUE_EXAM_ID",
    "exam_name": "Exam Name",
    "version": "A",
    "total_questions": 100,
    "subjects": 5,
    "questions_per_subject": 20,
    "max_score_per_subject": 20,
    "total_max_score": 100
  },
  "answer_key": {
    "subject_1": {
      "name": "Subject Name",
      "questions": {
        "1": "A", "2": "B", ...
      }
    }
  },
  "scoring_rules": {
    "correct_answer": 1,
    "wrong_answer": 0,
    "no_answer": 0,
    "multiple_answers": 0
  }
}
```

## Subject Configuration

The system supports 5 subjects with 20 questions each:

1. **Subject 1**: Mathematics (Questions 1-20)
2. **Subject 2**: Physics (Questions 21-40)
3. **Subject 3**: Chemistry (Questions 41-60)
4. **Subject 4**: Biology (Questions 61-80)
5. **Subject 5**: English (Questions 81-100)

## Scoring Rules

- **Correct Answer**: 1 point
- **Wrong Answer**: 0 points
- **No Answer**: 0 points
- **Multiple Answers**: 0 points (invalid response)

## Usage

The OMR processing engine will:

1. Load the appropriate answer key based on exam version
2. Compare detected answers with the answer key
3. Calculate scores per subject (0-20 points each)
4. Calculate total score (0-100 points)
5. Generate detailed results with subject-wise breakdown

## Adding New Answer Keys

To add a new answer key:

1. Copy `sample_answer_key.json`
2. Update the `exam_info` section with new exam details
3. Update the `answer_key` section with correct answers
4. Ensure question numbering follows the standard format
5. Verify all 100 questions are included