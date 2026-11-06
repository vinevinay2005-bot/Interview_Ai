"""
HR Interview Server-Side Backend & REST API Module
Provides dedicated backend endpoints and services for dynamic AI question generation,
session persistence, and answer evaluation.
"""

import os
import json
import database
import ai_engine

def start_hr_session(user_id: int, target_domain: str, candidate_profile: dict, api_key: str = None) -> dict:
    """
    Initializes a new HR interview session, generates 5 unique dynamic questions
    tailored to the candidate profile, and stores them in the database.
    """
    session_id = database.create_fresh_assessment_session(user_id, target_domain)
    
    # Generate 5 dynamic, role-specific questions
    questions = ai_engine.generate_hr_session_plan(
        candidate_profile=candidate_profile,
        api_key=api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        session_seed=session_id
    )

    # Persist questions to database
    for q in questions:
        database.store_session_hr_question(
            session_id=session_id,
            question_num=q["question_num"],
            category=q["category"],
            question_text=q["question_text"],
            eval_criteria=q.get("eval_criteria", "")
        )

    return {
        "status": "success",
        "session_id": session_id,
        "total_questions": len(questions),
        "questions": questions
    }

def get_or_load_hr_questions(session_id: int, candidate_profile: dict, api_key: str = None) -> list:
    """
    Retrieves existing session questions from the database.
    If not yet generated for this session, dynamically generates and saves them.
    This guarantees that refreshing an active session never replaces questions randomly.
    """
    existing = database.get_session_hr_questions(session_id)
    if existing and len(existing) == 5:
        return existing

    # Generate fresh plan for this session
    plan = ai_engine.generate_hr_session_plan(
        candidate_profile=candidate_profile,
        api_key=api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        session_seed=session_id
    )

    for q in plan:
        database.store_session_hr_question(
            session_id=session_id,
            question_num=q["question_num"],
            category=q["category"],
            question_text=q["question_text"],
            eval_criteria=q.get("eval_criteria", "")
        )

    return plan

def get_current_question(session_id: int, question_num: int, candidate_profile: dict, api_key: str = None) -> dict:
    """
    Retrieves the specific question for the current question number (1 to 5).
    """
    questions = get_or_load_hr_questions(session_id, candidate_profile, api_key)
    for q in questions:
        if q["question_num"] == question_num:
            return q

    # Fallback generation for out-of-range index
    fallback = ai_engine.generate_dynamic_hr_question(
        question_num=question_num,
        candidate_profile=candidate_profile,
        api_key=api_key,
        session_seed=session_id + question_num
    )
    database.store_session_hr_question(
        session_id=session_id,
        question_num=question_num,
        category=fallback["category"],
        question_text=fallback["question_text"],
        eval_criteria=fallback.get("eval_criteria", "")
    )
    return fallback

def submit_hr_answer(session_id: int, question_num: int, question_text: str, candidate_answer: str,
                     candidate_profile: dict, api_key: str = None) -> dict:
    """
    Evaluates candidate's answer, records transcript entry, and prepares/refines the next question.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    # Evaluate answer
    eval_res = ai_engine.evaluate_response(
        question=question_text,
        answer=candidate_answer,
        round_type="HR",
        domain=candidate_profile.get("target_role", "General HR"),
        api_key=key
    )

    # Record in database
    database.record_transcript_entry(
        session_id=session_id,
        round_type="HR",
        question_num=question_num,
        question_text=question_text,
        candidate_answer=candidate_answer,
        feedback=eval_res["feedback"],
        score=eval_res["score"]
    )

    # If next question exists, contextually adapt it based on candidate's answer
    next_question_num = question_num + 1
    next_question = None
    if next_question_num <= 5:
        # Get transcripts up to now
        transcripts = database.get_session_transcripts(session_id)
        hr_transcripts = [t for t in transcripts if t["round_type"] == "HR"]
        
        # Generate follow-up contextualized next question
        next_question = ai_engine.generate_dynamic_hr_question(
            question_num=next_question_num,
            candidate_profile=candidate_profile,
            previous_transcripts=hr_transcripts,
            api_key=key,
            session_seed=session_id + next_question_num * 31
        )
        # Store refined question
        database.store_session_hr_question(
            session_id=session_id,
            question_num=next_question_num,
            category=next_question["category"],
            question_text=next_question["question_text"],
            eval_criteria=next_question.get("eval_criteria", "")
        )

    return {
        "status": "success",
        "question_num": question_num,
        "score": eval_res["score"],
        "feedback": eval_res["feedback"],
        "metrics": eval_res.get("metrics", {}),
        "next_question_num": next_question_num if next_question_num <= 5 else None,
        "next_question": next_question,
        "is_completed": next_question_num > 5
    }

def restart_hr_interview(session_id: int, user_id: int, target_domain: str, candidate_profile: dict, api_key: str = None) -> dict:
    """
    Clears existing HR questions and transcripts or creates a fresh session for a brand-new interview.
    """
    # Create fresh session for true independence
    new_session_id = database.create_fresh_assessment_session(user_id, target_domain)
    plan = ai_engine.generate_hr_session_plan(
        candidate_profile=candidate_profile,
        api_key=api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        session_seed=new_session_id
    )
    for q in plan:
        database.store_session_hr_question(
            session_id=new_session_id,
            question_num=q["question_num"],
            category=q["category"],
            question_text=q["question_text"],
            eval_criteria=q.get("eval_criteria", "")
        )
    return {
        "status": "success",
        "session_id": new_session_id,
        "questions": plan
    }

