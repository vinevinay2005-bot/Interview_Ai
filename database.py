"""
Database Management Module
SQLite database schema, connections, and initial data seeding for:
- Users & Profiles
- Aptitude Question Bank (Quantitative, Logical, Verbal)
- Assessment Sessions & Round Scores
- Interview Transcripts & AI Feedback
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "interview_platform.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        target_role TEXT DEFAULT 'Software Engineer',
        experience_level TEXT DEFAULT 'Fresher',
        primary_skills TEXT DEFAULT 'Python, SQL',
        bio TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Aptitude questions bank
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, -- 'Quantitative', 'Logical', 'Verbal'
        difficulty TEXT DEFAULT 'Medium', -- 'Easy', 'Medium', 'Hard'
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
        explanation TEXT NOT NULL
    )
    """)

    # Assessment Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        target_domain TEXT NOT NULL,
        aptitude_score REAL DEFAULT 0.0,
        hr_score REAL DEFAULT 0.0,
        technical_score REAL DEFAULT 0.0,
        coding_score REAL DEFAULT 0.0,
        overall_score REAL DEFAULT 0.0,
        status TEXT DEFAULT 'In Progress', -- 'In Progress', 'Completed'
        report_data TEXT, -- JSON blob of full analysis
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Interview Transcripts (for HR & Technical rounds)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        round_type TEXT NOT NULL, -- 'HR', 'Technical'
        question_num INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        candidate_answer TEXT NOT NULL,
        feedback TEXT NOT NULL,
        score REAL DEFAULT 0.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)
    )
    """)

    # Dynamic Session-Specific HR Questions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS session_hr_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_num INTEGER NOT NULL,
        category TEXT NOT NULL,
        question_text TEXT NOT NULL,
        eval_criteria TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES assessment_sessions(id),
        UNIQUE(session_id, question_num)
    )
    """)

    conn.commit()
    seed_default_data(conn)
    conn.close()

def seed_default_data(conn):
    cursor = conn.cursor()

    # Seed default demo user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'candidate'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, target_role, experience_level, primary_skills, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'candidate',
            hash_password('demo123'),
            'Alex Johnson',
            'alex.johnson@example.com',
            'Junior Software Engineer',
            'Fresher (2025 Graduate)',
            'Python, SQL, HTML/CSS, Git',
            'Aspiring full-stack engineer passionate about building scalable web applications.'
        ))

    # Seed aptitude questions if empty
    cursor.execute("SELECT COUNT(*) FROM aptitude_questions")
    if cursor.fetchone()[0] == 0:
        questions = [
            # Quantitative Aptitude
            (
                "Quantitative", "Medium",
                "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?",
                "120 metres", "150 metres", "180 metres", "324 metres",
                "B",
                "Speed = 60 * (5/18) m/sec = 50/3 m/sec. Distance (length) = Speed * Time = (50/3) * 9 = 150 metres."
            ),
            (
                "Quantitative", "Easy",
                "A person buys a product for $450 and sells it for $540. What is the profit percentage?",
                "15%", "18%", "20%", "25%",
                "C",
                "Profit = $540 - $450 = $90. Profit % = (90 / 450) * 100 = 20%."
            ),
            (
                "Quantitative", "Medium",
                "If A can do a piece of work in 10 days and B can do it in 15 days, in how many days can they complete it working together?",
                "5 days", "6 days", "7.5 days", "8 days",
                "B",
                "1/A + 1/B = 1/10 + 1/15 = 5/30 = 1/6. Thus, together they complete it in 6 days."
            ),
            (
                "Quantitative", "Medium",
                "What is the average of first 50 natural numbers?",
                "25.0", "25.5", "26.0", "50.0",
                "B",
                "Average of first n natural numbers is (n + 1) / 2 = 51 / 2 = 25.5."
            ),
            (
                "Quantitative", "Hard",
                "In how many different ways can the letters of the word 'LEADING' be arranged so that vowels always come together?",
                "360", "480", "720", "5040",
                "C",
                "Vowels are E, A, I (3 vowels). Treat (EAI) as one unit. Units = L, D, N, G, (EAI) = 5 items. 5! * 3! = 120 * 6 = 720."
            ),
            (
                "Quantitative", "Medium",
                "Two numbers are in the ratio 3 : 5. If 9 is subtracted from each, the new ratio is 12 : 23. What is the smaller number?",
                "27", "33", "49", "55",
                "B",
                "Let numbers be 3x and 5x. (3x - 9)/(5x - 9) = 12/23. 23*(3x - 9) = 12*(5x - 9) -> 69x - 207 = 60x - 108 -> 9x = 99 -> x = 11. Smaller number = 3 * 11 = 33."
            ),
            # Logical Reasoning
            (
                "Logical", "Easy",
                "Look at the series: 2, 1, (1/2), (1/4), ... What number should come next?",
                "(1/3)", "(1/8)", "(2/8)", "(1/16)",
                "B",
                "Each number is halved: 2 / 2 = 1, 1 / 2 = 1/2, (1/2)/2 = 1/4, (1/4)/2 = 1/8."
            ),
            (
                "Logical", "Medium",
                "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
                "Brother", "Uncle", "Father", "Cousin",
                "C",
                "The only son of Suresh's mother is Suresh himself. So the boy is the son of Suresh, making Suresh his Father."
            ),
            (
                "Logical", "Medium",
                "If 'ROSE' is coded as 6821, 'CHAIR' is coded as 73456, and 'PREACH' is coded as 961473, what is the code for 'SEARCH'?",
                "246173", "214673", "214763", "216473",
                "B",
                "From mapping: S=2, E=1, A=4, R=6, C=7, H=3. Therefore, SEARCH = 214673."
            ),
            (
                "Logical", "Medium",
                "Statement: All mangoes are golden in colour. No golden-coloured things are cheap. Conclusion I: All mangoes are cheap. Conclusion II: Golden-coloured mangoes are not cheap.",
                "Only Conclusion I follows", "Only Conclusion II follows", "Either I or II follows", "Neither follows",
                "B",
                "Since all mangoes are golden and no golden-coloured things are cheap, golden-coloured mangoes cannot be cheap. Conclusion II follows."
            ),
            (
                "Logical", "Hard",
                "Find the missing number in the sequence: 4, 18, 48, 100, 180, ?",
                "210", "280", "294", "310",
                "C",
                "Pattern is n^3 - n^2 or n^2 * (n-1): 2^2*(2-1)=4; 3^2*(3-1)=18; 4^2*(4-1)=48; 5^2*(5-1)=100; 6^2*(6-1)=180; 7^2*(7-1) = 49 * 6 = 294."
            ),
            (
                "Logical", "Easy",
                "Which word does NOT belong with the others? (Apple, Banana, Carrot, Orange)",
                "Apple", "Banana", "Carrot", "Orange",
                "C",
                "Carrot is a root vegetable, whereas Apple, Banana, and Orange are fruits."
            ),
            # Verbal Ability
            (
                "Verbal", "Easy",
                "Choose the synonym for 'CANDID':",
                "Secretive", "Frank", "Deceitful", "Shy",
                "B",
                "Candid means truthful, outspoken, and frank."
            ),
            (
                "Verbal", "Medium",
                "Choose the antonym for 'EPHEMERAL':",
                "Transitory", "Eternal", "Brief", "Fragile",
                "B",
                "Ephemeral means lasting for a very short time; its opposite is Eternal (everlasting)."
            ),
            (
                "Verbal", "Easy",
                "Complete the sentence: Neither of the two candidates ________ suitable for the job.",
                "are", "is", "were", "have been",
                "B",
                "'Neither' takes a singular verb when referring to two singular subjects individually: 'is suitable'."
            ),
            (
                "Verbal", "Medium",
                "Identify the grammatically correct sentence:",
                "One of the students have forgot their book.",
                "One of the students has forgotten his or her book.",
                "One of the students have forgotten his book.",
                "One of the student have forgot his book.",
                "B",
                "Subject is 'One' which is singular, requiring 'has forgotten', and singular agreement 'his or her'."
            ),
            (
                "Verbal", "Medium",
                "Select the idiom meaning: 'To face the music'",
                "To attend a concert", "To accept unpleasant consequences", "To create harmony", "To dance to tunes",
                "B",
                "'To face the music' means to confront and accept responsibility or unpleasant consequences of one's actions."
            ),
            (
                "Verbal", "Hard",
                "Choose the correctly spelled word:",
                "Acquiesce", "Aquiese", "Acquiesse", "Acqueisce",
                "A",
                "The correct spelling is 'Acquiesce', meaning to accept something reluctantly but without protest."
            )
        ]

        cursor.executemany("""
        INSERT INTO aptitude_questions (category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, questions)

    conn.commit()

# --- User Management Queries ---

def check_user_exists(username, email):
    """Check if either username or email already exists in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT username, email FROM users 
    WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
    """, (username.strip(), email.strip()))
    row = cursor.fetchone()
    conn.close()
    if row:
        if row["username"].lower() == username.strip().lower():
            return True, "This username is already taken. Please choose a different username."
        if row["email"].lower() == email.strip().lower():
            return True, "An account with this email address already exists. Please log in."
    return False, ""

def register_user(username, password, full_name, email, target_role="Software Engineer", experience_level="Fresher", primary_skills="Python, SQL", bio=""):
    # Pre-check for duplicate username or email
    exists, err_msg = check_user_exists(username, email)
    if exists:
        return False, None, err_msg

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, target_role, experience_level, primary_skills, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username.strip(),
            hash_password(password),
            full_name.strip(),
            email.strip(),
            target_role.strip(),
            experience_level.strip(),
            primary_skills.strip(),
            bio.strip()
        ))
        conn.commit()
        user_id = cursor.lastrowid
        return True, user_id, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, None, "Username already exists. Please choose another username."
    finally:
        conn.close()

def authenticate_user(identifier, password):
    """Authenticate user with either username or email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM users 
    WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
    """, (identifier.strip(), identifier.strip()))
    row = cursor.fetchone()
    conn.close()
    if row and row["password_hash"] == hash_password(password):
        return dict(row)
    return None

def reset_password(identifier, new_password):
    """Reset user password by username or email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, username FROM users 
    WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
    """, (identifier.strip(), identifier.strip()))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "No account found with that username or email address."
    
    cursor.execute("""
    UPDATE users SET password_hash = ? WHERE id = ?
    """, (hash_password(new_password), row["id"]))
    conn.commit()
    conn.close()
    return True, "Password has been successfully reset! You can now log in with your new password."

def update_user_profile(user_id, full_name, email, target_role, experience_level, primary_skills, bio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users
    SET full_name = ?, email = ?, target_role = ?, experience_level = ?, primary_skills = ?, bio = ?
    WHERE id = ?
    """, (full_name, email, target_role, experience_level, primary_skills, bio, user_id))
    conn.commit()
    conn.close()
    return True

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# --- Aptitude Questions Queries ---

def get_aptitude_questions(limit_per_category=4):
    conn = get_connection()
    cursor = conn.cursor()
    questions = []
    for cat in ["Quantitative", "Logical", "Verbal"]:
        cursor.execute("""
        SELECT * FROM aptitude_questions
        WHERE category = ?
        ORDER BY RANDOM()
        LIMIT ?
        """, (cat, limit_per_category))
        questions.extend([dict(r) for r in cursor.fetchall()])
    conn.close()
    return questions

# --- Assessment Sessions & Transcripts Queries ---

def create_assessment_session(user_id, target_domain):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO assessment_sessions (user_id, target_domain, status)
    VALUES (?, ?, 'In Progress')
    """, (user_id, target_domain))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def update_session_scores(session_id, aptitude_score=None, hr_score=None, technical_score=None, coding_score=None, overall_score=None, status=None, report_data=None):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if aptitude_score is not None:
        updates.append("aptitude_score = ?")
        params.append(aptitude_score)
    if hr_score is not None:
        updates.append("hr_score = ?")
        params.append(hr_score)
    if technical_score is not None:
        updates.append("technical_score = ?")
        params.append(technical_score)
    if coding_score is not None:
        updates.append("coding_score = ?")
        params.append(coding_score)
    if overall_score is not None:
        updates.append("overall_score = ?")
        params.append(overall_score)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if report_data is not None:
        updates.append("report_data = ?")
        params.append(json.dumps(report_data))

    if updates:
        params.append(session_id)
        sql = f"UPDATE assessment_sessions SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, params)
        conn.commit()
    conn.close()

def record_transcript_entry(session_id, round_type, question_num, question_text, candidate_answer, feedback, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO interview_transcripts (session_id, round_type, question_num, question_text, candidate_answer, feedback, score)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, round_type, question_num, question_text, candidate_answer, feedback, score))
    conn.commit()
    conn.close()

def get_user_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM assessment_sessions
    WHERE user_id = ?
    ORDER BY session_date DESC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_session_transcripts(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM interview_transcripts
    WHERE session_id = ?
    ORDER BY round_type, question_num ASC
    """, (session_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_session_details(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessment_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        if d.get("report_data"):
            try:
                d["report_data"] = json.loads(d["report_data"])
            except Exception:
                pass
        return d
    return None

# --- Dynamic HR Session Questions Storage ---

def store_session_hr_question(session_id, question_num, category, question_text, eval_criteria=""):
    """Saves or updates a dynamically generated HR question for a specific session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO session_hr_questions (session_id, question_num, category, question_text, eval_criteria)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(session_id, question_num) DO UPDATE SET
        category = excluded.category,
        question_text = excluded.question_text,
        eval_criteria = excluded.eval_criteria
    """, (session_id, question_num, category, question_text, eval_criteria))
    conn.commit()
    conn.close()

def get_session_hr_questions(session_id):
    """Retrieves all dynamically generated HR questions for an active session in order."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT question_num, category, question_text, eval_criteria
    FROM session_hr_questions
    WHERE session_id = ?
    ORDER BY question_num ASC
    """, (session_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def clear_session_hr_questions(session_id):
    """Clears generated questions and HR transcripts when resetting or restarting an interview."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session_hr_questions WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM interview_transcripts WHERE session_id = ? AND round_type = 'HR'", (session_id,))
    conn.commit()
    conn.close()

def create_fresh_assessment_session(user_id, target_domain):
    """Explicitly initializes a new assessment session for a fresh interview."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO assessment_sessions (user_id, target_domain, status)
    VALUES (?, ?, 'In Progress')
    """, (user_id, target_domain))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
