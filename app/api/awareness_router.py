"""
app/api/awareness_router.py — Misinformation Awareness Center & interactive literacy quizzes.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import QuizModuleDB, UserQuizAttemptDB, UserDB
from app.models.schemas import (
    QuizModuleResponse,
    QuizQuestion,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.auth import get_optional_current_user, CurrentUser

router = APIRouter(prefix="/api/awareness", tags=["Misinformation Awareness Center"])


@router.get("/modules", response_model=List[QuizModuleResponse])
def get_awareness_modules(db: Session = Depends(get_db)):
    """Returns educational modules and media literacy tutorials."""
    modules = db.query(QuizModuleDB).all()
    result = []
    for m in modules:
        questions = json.loads(m.questions_json)
        result.append(QuizModuleResponse(
            id=m.id,
            title=m.title,
            category=m.category,
            difficulty=m.difficulty,
            summary=m.summary,
            content=m.content,
            questions=[QuizQuestion(**q) for q in questions],
            total_questions=len(questions),
        ))
    return result


@router.get("/modules/{module_id}", response_model=QuizModuleResponse)
def get_single_module(module_id: str, db: Session = Depends(get_db)):
    """Returns a single awareness tutorial and its interactive test."""
    m = db.query(QuizModuleDB).filter(QuizModuleDB.id == module_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Educational module not found.")
    questions = json.loads(m.questions_json)
    return QuizModuleResponse(
        id=m.id,
        title=m.title,
        category=m.category,
        difficulty=m.difficulty,
        summary=m.summary,
        content=m.content,
        questions=[QuizQuestion(**q) for q in questions],
        total_questions=len(questions),
    )


@router.post("/modules/{module_id}/submit", response_model=QuizSubmitResponse)
def submit_quiz(
    module_id: str,
    req: QuizSubmitRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluates quiz submissions, produces explanations for each question,
    and updates the user's digital media awareness score!
    """
    m = db.query(QuizModuleDB).filter(QuizModuleDB.id == module_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Module not found.")

    questions = json.loads(m.questions_json)
    score = 0
    max_score = len(questions)
    feedback = []

    for q in questions:
        qid = q["question_id"]
        chosen = req.answers.get(qid)
        is_correct = (chosen == q["correct_index"])
        if is_correct:
            score += 1

        feedback.append({
            "question_id": qid,
            "question": q["question"],
            "chosen_index": chosen,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    percentage = round((score / max(max_score, 1)) * 100.0, 1)
    passed = percentage >= 70.0

    new_awareness = 50
    if current_user:
        user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
        if user:
            # Increment awareness score upon completion
            boost = int(percentage * 0.25)
            user.awareness_score = min(100, max(user.awareness_score, user.awareness_score + boost))
            new_awareness = user.awareness_score
            
            attempt = UserQuizAttemptDB(
                user_id=user.id,
                module_id=module_id,
                score=score,
                max_score=max_score,
            )
            db.add(attempt)
            db.commit()

    return QuizSubmitResponse(
        module_id=module_id,
        score=score,
        max_score=max_score,
        percentage=percentage,
        passed=passed,
        feedback=feedback,
        new_user_awareness_score=new_awareness,
    )
