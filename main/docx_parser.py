from docx import Document
from django.core.files.base import ContentFile
import re


def parse_docx_test(docx_file):
    """
    Parse DOCX test file and return questions with answers.
    
    Expected format:
    ## 1-savol
    Question text here?
    A) Answer 1
    B) Answer 2
    C) Answer 3
    D) Answer 4
    Javob: A
    
    Returns: List of dicts with question data
    """
    try:
        doc = Document(docx_file)
        questions_data = []
        current_question = None
        current_answers = []
        correct_answer = None
        question_number = 0
        question_text_lines = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            
            if not text:
                continue
            
            print(f"DEBUG: Processing line: {text[:50]}")  # Debug output
            
            # Check for question marker: ## N-savol
            if '##' in text and 'savol' in text.lower():
                # Save previous question if exists
                if current_question and current_answers:
                    questions_data.append({
                        'number': question_number,
                        'text': current_question,
                        'answers': current_answers,
                        'correct_answer': correct_answer
                    })
                    print(f"DEBUG: Saved question {question_number}")
                
                # Extract question number
                match = re.search(r'(\d+)-savol', text)
                if match:
                    question_number = int(match.group(1))
                else:
                    question_number += 1
                
                current_question = None
                current_answers = []
                correct_answer = None
                question_text_lines = []
                print(f"DEBUG: Started question {question_number}")
                continue
            
            # Check for answer options: A) B) C) D)
            answer_match = re.match(r'^([A-D])\)\s*(.+)', text)
            if answer_match:
                letter = answer_match.group(1)
                answer_text = answer_match.group(2).strip()
                current_answers.append({
                    'letter': letter,
                    'text': answer_text
                })
                print(f"DEBUG: Added answer {letter}")
                continue
            
            # Check for correct answer: Javob: A
            if text.lower().startswith('javob:'):
                correct_answer = text.split(':')[1].strip().upper()
                print(f"DEBUG: Correct answer: {correct_answer}")
                continue
            
            # If not any of above, it's question text
            if question_number > 0 and not current_question and not text.startswith('##'):
                current_question = text
                print(f"DEBUG: Question text: {text[:30]}")
        
        # Don't forget last question
        if current_question and current_answers:
            questions_data.append({
                'number': question_number,
                'text': current_question,
                'answers': current_answers,
                'correct_answer': correct_answer
            })
            print(f"DEBUG: Saved last question {question_number}")
        
        print(f"DEBUG: Total questions parsed: {len(questions_data)}")
        return questions_data
    
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_questions_from_docx(course, docx_file):
    """
    Parse DOCX and save questions to database
    """
    from main.models import Question, Answer
    
    questions_data = parse_docx_test(docx_file)
    
    if not questions_data:
        return 0, "DOCX faylni o'qishda xatolik yuz berdi"
    
    # Delete old questions for this course
    Question.objects.filter(course=course).delete()
    
    created_count = 0
    for q_data in questions_data:
        # Create question
        question = Question.objects.create(
            course=course,
            number=q_data['number'],
            text=q_data['text']
        )
        
        # Create answers
        for answer_data in q_data['answers']:
            is_correct = (answer_data['letter'] == q_data['correct_answer'])
            Answer.objects.create(
                question=question,
                text=answer_data['text'],
                is_correct=is_correct
            )
        
        created_count += 1
    
    return created_count, f"{created_count} ta savol muvaffaqiyatli yuklandi"
