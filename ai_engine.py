"""
AI / NLP Engine Module
Provides:
1. Multi-provider AI Integration (Google Gemini, OpenAI/Groq compatible)
2. Built-in Offline Intelligent NLP Engine with domain-specific knowledge banks
3. Dynamic question selection & context-aware follow-up question generation
4. In-depth response evaluation (Communication, STAR method, Technical accuracy)
5. Comprehensive final performance report synthesis
"""

import os
import json
import re
import urllib.request
import urllib.error

# Domain Technical Knowledge Profiles for offline evaluation & question generation
TECHNICAL_DOMAINS = {
    "Python & Backend": {
        "topics": ["Data Structures", "OOP", "Decorators & Generators", "Concurrency", "Frameworks & APIs"],
        "questions": [
            {
                "id": "py_1",
                "question": "Can you explain the difference between Python lists and tuples, and describe a real-world scenario where a tuple is strictly preferred?",
                "key_concepts": ["mutable", "immutable", "memory efficiency", "hashable", "dictionary keys", "performance"],
                "sample_ideal": "Lists are mutable and consume more memory for dynamic sizing. Tuples are immutable and fixed-size, making them memory-efficient and hashable as dictionary keys."
            },
            {
                "id": "py_2",
                "question": "How do Python's GIL (Global Interpreter Lock) and multiprocessing affect multi-threaded CPU-bound versus I/O-bound tasks?",
                "key_concepts": ["gil", "threads", "multiprocessing", "cpu-bound", "i/o-bound", "concurrency", "asyncio"],
                "sample_ideal": "GIL allows only one thread to execute Python bytecode at once. Multi-threading benefits I/O bound tasks, whereas CPU bound tasks need multiprocessing to utilize multiple cores."
            },
            {
                "id": "py_3",
                "question": "Explain how Python decorators work under the hood and provide an example of how you would implement an execution-time logger decorator.",
                "key_concepts": ["closure", "wrapper", "first-class functions", "functools.wraps", "time.time", "arguments *args **kwargs"],
                "sample_ideal": "A decorator is a callable that takes a function as argument and returns an augmented wrapper function using closure principles."
            },
            {
                "id": "py_4",
                "question": "What is the difference between shallow copy and deep copy in Python? How does mutable nesting affect them?",
                "key_concepts": ["copy", "deepcopy", "nested objects", "reference", "memory address", "mutability"],
                "sample_ideal": "Shallow copy copies references of nested compound objects, whereas deep copy recursively duplicates nested objects completely."
            }
        ]
    },
    "Full Stack Web Development": {
        "topics": ["RESTful APIs", "State Management", "Authentication & Security", "Performance", "DOM & Rendering"],
        "questions": [
            {
                "id": "fs_1",
                "question": "Explain the difference between client-side rendering (CSR) and server-side rendering (SSR). What are the SEO and performance trade-offs?",
                "key_concepts": ["seo", "initial load", "hydration", "time to interactive", "crawler", "single page application"],
                "sample_ideal": "SSR renders HTML on the server giving fast first contentful paint and good SEO, while CSR offloads rendering to the browser after downloading JS bundles."
            },
            {
                "id": "fs_2",
                "question": "How do JWT (JSON Web Tokens) work for user authentication, and where should tokens be stored securely in the frontend?",
                "key_concepts": ["jwt", "header", "payload", "signature", "httponly cookie", "localstorage", "xss", "csrf"],
                "sample_ideal": "JWT consists of Header, Payload, and Signature. Storing in httpOnly secure cookies protects against XSS attacks compared to localStorage."
            },
            {
                "id": "fs_3",
                "question": "Describe the event loop in JavaScript. How do the Call Stack, Microtask Queue (Promises), and Macrotask Queue (setTimeout) interact?",
                "key_concepts": ["event loop", "call stack", "microtask queue", "macrotask queue", "promises", "settimeout", "async"],
                "sample_ideal": "Call stack executes synchronous code. When empty, microtask queue (promises) is processed completely before the event loop pulls from the macrotask queue."
            },
            {
                "id": "fs_4",
                "question": "What are CORS (Cross-Origin Resource Sharing) errors, and how do you resolve them properly on the backend server?",
                "key_concepts": ["cors", "origin", "headers", "access-control-allow-origin", "preflight", "options request"],
                "sample_ideal": "CORS is a browser security mechanism restricting cross-domain requests. It is fixed on the backend by returning appropriate Access-Control-Allow-Origin headers."
            }
        ]
    },
    "Data Science & AI": {
        "topics": ["Machine Learning Lifecycle", "Model Evaluation", "Overfitting & Regularization", "Data Preprocessing", "Neural Networks"],
        "questions": [
            {
                "id": "ds_1",
                "question": "What is the Bias-Variance tradeoff in Machine Learning, and what concrete techniques do you use to detect and mitigate overfitting?",
                "key_concepts": ["bias", "variance", "overfitting", "underfitting", "regularization", "l1 l2", "cross-validation", "dropout"],
                "sample_ideal": "High bias leads to underfitting; high variance causes overfitting. Overfitting is resolved via L1/L2 regularization, cross-validation, and pruning/dropout."
            },
            {
                "id": "ds_2",
                "question": "When would you prefer Precision over Recall, or Recall over Precision? Provide an example domain for each case.",
                "key_concepts": ["precision", "recall", "false positive", "false negative", "f1-score", "cancer detection", "spam filter"],
                "sample_ideal": "Recall is critical when False Negatives are costly (medical diagnosis, cancer detection). Precision is preferred when False Positives are harmful (spam filters, fraud flagging)."
            },
            {
                "id": "ds_3",
                "question": "How do Tree-based ensemble methods like Random Forest differ from Gradient Boosting (like XGBoost)?",
                "key_concepts": ["bagging", "boosting", "parallel trees", "sequential errors", "residuals", "variance reduction", "learning rate"],
                "sample_ideal": "Random Forest uses bagging to build independent trees in parallel to reduce variance. Boosting trains trees sequentially to correct prior errors."
            },
            {
                "id": "ds_4",
                "question": "Explain feature scaling (Normalization vs Standardization). Why do distance-based algorithms require it while Decision Trees do not?",
                "key_concepts": ["min-max normalization", "standardization z-score", "distance metrics", "knn", "svm", "decision trees monotonic split"],
                "sample_ideal": "Distance algorithms like KNN and SVM rely on Euclidean distances which get skewed by scale. Decision Trees use monotonic threshold splits and are scale-invariant."
            }
        ]
    },
    "Databases & SQL": {
        "topics": ["Indexing", "ACID Properties", "Normalization", "Query Optimization", "NoSQL vs SQL"],
        "questions": [
            {
                "id": "db_1",
                "question": "What are ACID properties in relational database transactions, and how does a database engine ensure Atomicity and Durability?",
                "key_concepts": ["atomicity", "consistency", "isolation", "durability", "wal write ahead log", "commit", "rollback", "transaction"],
                "sample_ideal": "ACID ensures reliability. Atomicity (all or nothing) and Durability are achieved through Write-Ahead Logging (WAL) and redo/undo transaction logs."
            },
            {
                "id": "db_2",
                "question": "Explain how B-Tree indexes improve SELECT query performance, and what trade-offs they introduce for INSERT and UPDATE operations.",
                "key_concepts": ["b-tree", "index", "logarithmic lookup", "disk i/o", "write overhead", "rebalancing", "table scan"],
                "sample_ideal": "B-Tree indexes reduce lookup time from O(N) full table scan to O(log N). However, writes, updates, and deletes become slower due to index maintenance."
            },
            {
                "id": "db_3",
                "question": "What is the difference between Clustered and Non-Clustered indexes? Can a database table have multiple clustered indexes?",
                "key_concepts": ["clustered index", "non-clustered index", "physical order", "pointer", "leaf node", "primary key"],
                "sample_ideal": "A clustered index determines the physical order of data on disk (only one allowed per table). Non-clustered indexes store separate pointers to data rows."
            },
            {
                "id": "db_4",
                "question": "Explain database normalization up to Third Normal Form (3NF). Why might an enterprise system intentionally denormalize?",
                "key_concepts": ["1nf", "2nf", "3nf", "functional dependency", "transitive dependency", "denormalization", "read performance", "joins"],
                "sample_ideal": "3NF removes transitive dependencies to eliminate data redundancy. Systems denormalize in read-heavy reporting systems (OLAP) to avoid expensive multi-table JOINs."
            }
        ]
    },
    "Java & Object-Oriented Design": {
        "topics": ["OOP Principles", "JVM Architecture", "Collections Framework", "Concurrency", "Spring & Microservices"],
        "questions": [
            {
                "id": "java_1",
                "question": "Explain the four core principles of Object-Oriented Programming (OOP) and give an example of Polymorphism in Java.",
                "key_concepts": ["encapsulation", "inheritance", "polymorphism", "abstraction", "method overloading", "method overriding", "interface"],
                "sample_ideal": "OOP pillars are Encapsulation, Inheritance, Polymorphism, and Abstraction. Polymorphism manifests as compile-time overloading or runtime overriding via interfaces."
            },
            {
                "id": "java_2",
                "question": "How does the JVM Garbage Collector work, and what is the difference between Young Generation and Old Generation memory?",
                "key_concepts": ["jvm", "garbage collection", "heap", "young generation", "eden", "survivor", "old generation", "tenured", "stop the world"],
                "sample_ideal": "JVM organizes heap into Young (Eden, Survivor) and Old (Tenured) generation. Minor GC cleans short-lived objects; objects surviving multiple cycles are promoted."
            },
            {
                "id": "java_3",
                "question": "What is the difference between HashMap and ConcurrentHashMap in Java? Why should Hashtable not be used in modern applications?",
                "key_concepts": ["hashmap", "concurrenthashmap", "thread safety", "bucket locking", "synchronized", "performance"],
                "sample_ideal": "HashMap is not thread-safe. ConcurrentHashMap uses segment/bucket level locking for high concurrent throughput without locking the entire table."
            },
            {
                "id": "java_4",
                "question": "Explain the difference between an Abstract Class and an Interface in Java 8 and beyond.",
                "key_concepts": ["abstract class", "interface", "multiple inheritance", "default methods", "state", "instance variables"],
                "sample_ideal": "Interfaces specify behavior (and default methods since Java 8) supporting multiple inheritance, while abstract classes can hold state (constructors, fields)."
            }
        ]
    },
    "Cloud, DevOps & Fundamentals": {
        "topics": ["Containerization", "CI/CD", "OS Process vs Thread", "Networking & TCP/IP", "Cloud Architecture"],
        "questions": [
            {
                "id": "ops_1",
                "question": "How does Docker containerization differ from traditional virtual machines (VMs) in terms of architecture and resource efficiency?",
                "key_concepts": ["docker", "container", "virtual machine", "hypervisor", "shared kernel", "cgroups", "namespaces", "lightweight"],
                "sample_ideal": "VMs run full guest operating systems on top of a hypervisor. Containers share the host OS kernel using Linux namespaces and cgroups, making them lightweight."
            },
            {
                "id": "ops_2",
                "question": "Explain the TCP 3-way handshake process and what occurs during connection termination.",
                "key_concepts": ["syn", "syn-ack", "ack", "fin", "sequence number", "reliable transport", "connection oriented"],
                "sample_ideal": "Client sends SYN, server responds with SYN-ACK, client sends ACK. Termination requires a 4-way FIN/ACK handshake to close both directions."
            },
            {
                "id": "ops_3",
                "question": "What is the difference between horizontal scaling and vertical scaling? How do load balancers distribute traffic across instances?",
                "key_concepts": ["horizontal scaling", "vertical scaling", "scale out", "scale up", "load balancer", "round robin", "least connections", "stateless"],
                "sample_ideal": "Vertical scaling upgrades CPU/RAM on a single machine; horizontal scaling adds more nodes. Load balancers distribute requests using round-robin, least connections, or IP hash."
            },
            {
                "id": "ops_4",
                "question": "Explain the concept of CI/CD pipeline. What are the distinct stages from git commit to production deployment?",
                "key_concepts": ["ci/cd", "continuous integration", "continuous deployment", "automated testing", "linting", "build artifact", "staging", "rollback"],
                "sample_ideal": "CI/CD automates software delivery: Commit -> Lint & Build -> Unit/Integration Tests -> Containerization -> Staging Deploy -> Smoke Test -> Production Deploy."
            }
        ]
    }
}

# =========================================================================
# DYNAMIC AI-GENERATED HR INTERVIEW QUESTION ENGINE
# =========================================================================

HR_CATEGORY_BLUEPRINTS = [
    {
        "num": 1,
        "category": "Self Introduction",
        "focus": "Academic background, career interests, passion for technology, and personal introduction.",
        "eval_criteria": "Structured introduction, academic background, career motivation, and relevance to the target role."
    },
    {
        "num": 2,
        "category": "Career Goals",
        "focus": "Short-term and long-term milestones, motivation for choosing the IT industry, and role aspirations.",
        "eval_criteria": "Clear ambition, realistic progression timeline, enthusiasm for the IT sector, and commitment to growth."
    },
    {
        "num": 3,
        "category": "Strengths and Weaknesses",
        "focus": "Personal and technical strengths, areas for growth/improvement, and handling challenges or pressure.",
        "eval_criteria": "Self-awareness, actionable steps for improvement, resilience under pressure, and honesty."
    },
    {
        "num": 4,
        "category": "Teamwork and Problem Solving",
        "focus": "Collaborative experience, resolving conflicts or disagreements, and problem-solving under deadlines.",
        "eval_criteria": "Diplomacy, empathy, active listening, structured STAR method, and focus on collective team success."
    },
    {
        "num": 5,
        "category": "Company and Job Role",
        "focus": "Value proposition (why we should hire you), company fit, and interest in this specific job role.",
        "eval_criteria": "Alignment with target role responsibilities, unique strengths, organizational culture fit, and mutual value."
    }
]

def generate_procedural_hr_question(question_num: int, candidate_profile: dict, previous_transcripts: list = None, seed_salt: int = 0) -> dict:
    """
    Intelligent procedural question generator.
    Synthesizes diverse, context-aware, role-specific HR questions based on the candidate's
    target role, academic tier, skills, and previous responses.
    """
    import random
    import hashlib
    import time

    role = (candidate_profile.get("target_role") or "Software Engineer").strip()
    exp = (candidate_profile.get("experience_level") or "Fresher").strip()
    skills = (candidate_profile.get("primary_skills") or "Python, SQL").strip()
    name = (candidate_profile.get("full_name") or candidate_profile.get("username") or "Candidate").strip()
    is_fresher = "fresher" in exp.lower() or "graduate" in exp.lower() or "student" in exp.lower()

    # Create a deterministic yet session-variant seed
    seed_str = f"{name}_{role}_{exp}_{question_num}_{seed_salt}_{int(time.time())}"
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    # Reference to previous answer if available
    prev_bridge = ""
    if previous_transcripts and len(previous_transcripts) > 0:
        last_item = previous_transcripts[-1]
        last_ans = last_item.get("candidate_answer", "").strip()
        if last_ans and len(last_ans) > 20:
            bridge_options = [
                "Thank you for sharing that context.",
                "I appreciate your perspective on that.",
                "That gives me good insight into your thinking.",
                "Thank you for walking me through that experience."
            ]
            prev_bridge = rng.choice(bridge_options) + " "

    # 1. Self Introduction
    if question_num == 1:
        category = "Self Introduction"
        criteria = "Structured introduction, academic background, career motivation, and relevance to the target role."
        if is_fresher:
            templates = [
                f"Welcome to the interview, {name}! To start off, could you tell me about yourself, your academic background in college, and what sparked your interest in pursuing a career as a {role} in the IT industry?",
                f"Hello {name}, it's great to connect with you today. Please introduce yourself, highlighting your educational journey, the core technical projects you enjoyed working on, and why you are excited about the {role} position.",
                f"Could you walk me through your personal journey, {name}? Tell me about your academic studies, the technical areas like {skills} you have explored, and what motivated you to specialize as a {role}?",
                f"To begin our conversation today, please tell me about yourself, your academic background, and the key experiences that led you to pursue a career in technology as a {role}.",
                f"Please introduce yourself, {name}. Share an overview of your college background, your favorite engineering subjects, and what drives your passion to join our team as a {role}."
            ]
        else:
            templates = [
                f"Welcome to the interview, {name}. Could you please walk me through your professional background, your key projects involving {skills}, and what brings you to seek this {role} opportunity at this stage in your career?",
                f"To get started, please tell me about yourself, your technical trajectory so far, and the core domain experiences that make you passionate about taking on this {role} role.",
                f"Could you summarize your professional journey, {name}? Highlight your hands-on background with {skills} and why you feel ready to excel as our next {role}.",
                f"Please introduce yourself, focusing on your career progression, your technical specializations, and what specifically motivated you to apply for our {role} position."
            ]
        q_text = rng.choice(templates)

    # 2. Career Goals
    elif question_num == 2:
        category = "Career Goals"
        criteria = "Clear ambition, realistic progression timeline, enthusiasm for the IT sector, and commitment to growth."
        templates = [
            f"{prev_bridge}Where do you see yourself professionally over the next 2 to 5 years, and what specifically drew you to build a career in the IT industry as a {role}?",
            f"{prev_bridge}Could you outline your short-term and long-term career aspirations? How does working as a {role} align with your long-term vision in the software industry?",
            f"{prev_bridge}The tech industry evolves at a rapid pace. What are your primary technical and professional milestones for the next few years, and why did you choose the IT sector over other fields?",
            f"{prev_bridge}Looking ahead, what skills or leadership responsibilities do you hope to master in your first two years as a {role}, and where do you envision your career five years down the road?",
            f"{prev_bridge}What motivated you to choose the information technology sector, and how do you plan to steer your growth to become a subject matter expert in {role} responsibilities?"
        ]
        q_text = rng.choice(templates)

    # 3. Strengths and Weaknesses
    elif question_num == 3:
        category = "Strengths and Weaknesses"
        criteria = "Self-awareness, actionable steps for improvement, resilience under pressure, and honesty."
        templates = [
            f"{prev_bridge}What do you consider your greatest personal or professional strength when working on technical tasks, and conversely, what is an area or weakness you are actively working to improve?",
            f"{prev_bridge}In a fast-paced {role} role, challenges and tight deadlines are inevitable. What is one technical or behavioral area you consider your biggest weakness, and how do you maintain composure when unexpected obstacles arise?",
            f"{prev_bridge}Self-awareness is critical in our engineering culture. Could you share one key strength that sets you apart as a {role}, along with an area of development where you have sought feedback to grow?",
            f"{prev_bridge}Describe a personal strength that has helped you succeed in demanding technical situations, and walk me through a weakness you identified and the concrete steps you took to overcome it.",
            f"{prev_bridge}We all have areas where we excel and areas where we need improvement. How would your peers describe your greatest asset as a {role}, and what is one skill or habit you are currently refining?"
        ]
        q_text = rng.choice(templates)

    # 4. Teamwork and Problem Solving
    elif question_num == 4:
        category = "Teamwork and Problem Solving"
        criteria = "Diplomacy, empathy, active listening, structured STAR method, and focus on collective team success."
        templates = [
            f"{prev_bridge}Software development is heavily collaborative. Can you describe a situation where you had a disagreement with a peer or teammate on a project? How did you resolve the conflict and reach a productive outcome?",
            f"{prev_bridge}Tell me about a time you worked in a group to tackle a difficult technical problem under a strict deadline. What was your role, and how did you keep the team aligned toward success?",
            f"{prev_bridge}Have you ever worked with someone whose communication or work style was very different from yours? How did you adapt your approach to ensure the team delivered quality work as a cohesive unit?",
            f"{prev_bridge}Describe a scenario where a team project ran into an unexpected hurdle or bottleneck. How did you contribute to solving the problem, and what did you learn about team dynamics from that experience?",
            f"{prev_bridge}In your experience working on collaborative projects involving {skills}, how do you handle constructive criticism from teammates, and how do you build consensus when opinions differ?"
        ]
        q_text = rng.choice(templates)

    # 5. Company and Job Role
    else:
        category = "Company and Job Role"
        criteria = "Alignment with target role responsibilities, unique strengths, organizational culture fit, and mutual value."
        templates = [
            f"{prev_bridge}With many candidates applying, why should we choose to hire you for this {role} position? What unique blend of technical ability, passion, and work ethic do you bring to our team?",
            f"{prev_bridge}What specifically makes you enthusiastic about joining our organization as a {role}, and how do your background and core skills in {skills} align with our engineering standards?",
            f"{prev_bridge}Considering our team's focus on high-impact technology delivery, why are you interested in this particular {role} position, and what value can you add from day one?",
            f"{prev_bridge}As we conclude our interview, give me your pitch: why are you the best fit for our {role} opening, and how will hiring you make our engineering organization stronger?",
            f"{prev_bridge}Why do you want to work with us specifically as a {role}, and what makes you confident that you will thrive in our dynamic team environment?"
        ]
        q_text = rng.choice(templates)

    return {
        "question_num": question_num,
        "category": category,
        "question_text": q_text,
        "eval_criteria": criteria
    }

def generate_dynamic_hr_question(question_num: int, candidate_profile: dict, previous_transcripts: list = None, api_key: str = None, session_seed: int = 0) -> dict:
    """
    Generates an authentic, role-aligned, conversational HR interview question.
    Uses Google Gemini API if key is available; otherwise utilizes the advanced procedural generator.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    role = (candidate_profile.get("target_role") or "Software Engineer").strip()
    exp = (candidate_profile.get("experience_level") or "Fresher").strip()
    skills = (candidate_profile.get("primary_skills") or "Python, SQL").strip()
    name = (candidate_profile.get("full_name") or candidate_profile.get("username") or "Candidate").strip()
    bio = (candidate_profile.get("bio") or "").strip()

    blueprint = next((b for b in HR_CATEGORY_BLUEPRINTS if b["num"] == question_num), HR_CATEGORY_BLUEPRINTS[0])
    category_name = blueprint["category"]
    category_focus = blueprint["focus"]

    if key:
        try:
            transcript_summary = ""
            if previous_transcripts:
                transcript_summary = "\n".join([
                    f"- Previous Q{t['question_num']}: \"{t.get('question_text', '')}\"\n  Candidate Answer: \"{t.get('candidate_answer', '')[:200]}\""
                    for t in previous_transcripts[-2:]
                ])

            prompt = f"""
You are a Senior Technical HR Director conducting a placement interview for an IT company.

Candidate Profile:
- Name: {name}
- Target Job Role: {role}
- Experience Level: {exp}
- Key Skills: {skills}
- Academic Background & Bio: {bio}

Interview Round: Round 2 - HR & Behavioral Interview
Question Number: {question_num} of 5
Category Target: {category_name}
Category Objectives: {category_focus}

Recent Conversation Context in this Session:
{transcript_summary if transcript_summary else "This is the start of the interview."}

Instructions:
1. Generate ONE realistic, professional, conversational interview question suited for a candidate applying for the role of '{role}' with experience level '{exp}'.
2. If previous answers exist, craft a natural conversational bridge that acknowledges what the candidate discussed before pivoting into the question.
3. The question must strictly belong to the category '{category_name}'.
4. Avoid generic repetitive questions; make the phrasing engaging and natural.
5. Return strictly valid JSON with this exact schema (no markdown fences, no extra text):
{{
  "question_num": {question_num},
  "category": "{category_name}",
  "question_text": "your generated question here",
  "eval_criteria": "{blueprint['eval_criteria']}"
}}
"""
            raw_output = call_gemini_api(key, prompt)
            match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if data.get("question_text"):
                    return {
                        "question_num": question_num,
                        "category": category_name,
                        "question_text": data["question_text"].strip(),
                        "eval_criteria": data.get("eval_criteria", blueprint["eval_criteria"])
                    }
        except Exception:
            pass

    return generate_procedural_hr_question(
        question_num=question_num,
        candidate_profile=candidate_profile,
        previous_transcripts=previous_transcripts,
        seed_salt=session_seed
    )

def generate_hr_session_plan(candidate_profile: dict, api_key: str = None, session_seed: int = 0) -> list:
    """
    Generates a complete 5-question dynamic interview plan for a new HR interview session.
    Guarantees no repeated questions and strict compliance with the 5 required categories.
    """
    plan = []
    for q_num in range(1, 6):
        q = generate_dynamic_hr_question(
            question_num=q_num,
            candidate_profile=candidate_profile,
            previous_transcripts=None,
            api_key=api_key,
            session_seed=session_seed + q_num * 17
        )
        plan.append(q)
    return plan


# =========================================================================
# TECHNICAL INTERVIEW BANKS: FUNDAMENTALS, CODING, DSA, SQL, & PROJECTS
# =========================================================================

PROGRAMMING_FUNDAMENTALS_QUESTIONS = [
    {
        "id": "fund_1",
        "topic": "OOP Concepts",
        "category": "OOP Concepts",
        "difficulty": "Easy - Medium",
        "question": "Explain the four core pillars of Object-Oriented Programming (OOP)—Encapsulation, Inheritance, Polymorphism, and Abstraction. How do they improve software maintainability, and what is an example of runtime polymorphism in Python or Java?",
        "key_concepts": ["encapsulation", "inheritance", "polymorphism", "abstraction", "method overriding", "interface", "maintainability", "class"],
        "expected_answer": "Encapsulation bundles data and methods while restricting direct access. Inheritance promotes code reuse. Polymorphism allows methods to take multiple forms (overloading/overriding). Abstraction hides implementation complexity behind interfaces.",
        "sample_ideal": "Encapsulation bundles data and methods while restricting direct access. Inheritance promotes code reuse. Polymorphism allows methods to take multiple forms (overloading/overriding). Abstraction hides implementation complexity behind interfaces."
    },
    {
        "id": "fund_2",
        "topic": "Data Types & Mutability",
        "category": "Data Types & Mutability",
        "difficulty": "Easy",
        "question": "Explain the fundamental difference between mutable and immutable data types in Python and Java. Why can a tuple or string serve as a dictionary key or hash set element, while a list cannot?",
        "key_concepts": ["mutable", "immutable", "hashable", "tuple", "list", "dictionary key", "memory address", "hash collision"],
        "expected_answer": "Immutable objects cannot change their state after creation, guaranteeing a fixed hash value necessary for dictionary hash tables. Mutable objects can change dynamically, which would invalidate hash lookups.",
        "sample_ideal": "Immutable objects cannot change their state after creation, guaranteeing a fixed hash value necessary for dictionary hash tables. Mutable objects can change dynamically, which would invalidate hash lookups."
    },
    {
        "id": "fund_3",
        "topic": "Exception Handling",
        "category": "Exception Handling",
        "difficulty": "Medium",
        "question": "How does robust exception handling work in enterprise applications? Explain the purpose of try, except/catch, else, and finally blocks, and explain why catching bare generic exceptions (e.g. 'except:') is considered an anti-pattern.",
        "key_concepts": ["try", "except", "catch", "finally", "cleanup", "resource leak", "bare except", "custom exceptions", "fail fast"],
        "expected_answer": "The try block encapsulates risky operations. Catch/except handles specific expected error types. Finally guarantees resource cleanup like closing files/connections. Bare exceptions mask keyboard interrupts and system errors.",
        "sample_ideal": "The try block encapsulates risky operations. Catch/except handles specific expected error types. Finally guarantees resource cleanup like closing files/connections. Bare exceptions mask keyboard interrupts and system errors."
    },
    {
        "id": "fund_4",
        "topic": "Functions & Scope",
        "category": "Functions & Scope",
        "difficulty": "Medium",
        "question": "Describe variable scope resolution (the LEGB rule in Python: Local, Enclosing, Global, Built-in). How do closures and lambda expressions interact with outer variables, and what are the trade-offs of using global variables?",
        "key_concepts": ["legb", "local", "enclosing", "global", "built-in", "closure", "lambda", "side effects", "thread safety"],
        "expected_answer": "Python resolves variables inside-out: Local -> Enclosing -> Global -> Built-in. Closures retain access to enclosing scope even after outer function returns. Globals introduce hidden dependencies and race conditions.",
        "sample_ideal": "Python resolves variables inside-out: Local -> Enclosing -> Global -> Built-in. Closures retain access to enclosing scope even after outer function returns. Globals introduce hidden dependencies and race conditions."
    }
]

LIVE_CODING_QUESTIONS = [
    {
        "id": "code_reverse_str",
        "title": "Reverse a String",
        "topic": "Strings & In-Place Algorithms",
        "category": "Live Coding Assessment",
        "difficulty": "Easy",
        "question": "Given a string `s`, reverse the order of its characters without using built-in reversal functions (e.g., avoid `[::-1]` or `StringBuilder.reverse`). Read from standard input and print the reversed string to standard output.",
        "description": "Given a string `s`, reverse the order of its characters without using built-in reversal functions (e.g., avoid `[::-1]` or `StringBuilder.reverse`). Read from standard input and print the reversed string to standard output.",
        "sample_input": "hello",
        "sample_output": "olleh",
        "expected_answer": "olleh",
        "time_complexity": "O(N)",
        "space_complexity": "O(N) for string representation",
        "starter_codes": {
            "Python": "# Write a program to reverse a given string\ndef reverse_string(s: str) -> str:\n    chars = list(s)\n    left, right = 0, len(chars) - 1\n    while left < right:\n        chars[left], chars[right] = chars[right], chars[left]\n        left += 1\n        right -= 1\n    return ''.join(chars)\n\nimport sys\nraw = sys.stdin.read().strip()\nif raw:\n    print(reverse_string(raw))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static String reverseString(String s) {\n        char[] chars = s.toCharArray();\n        int left = 0, right = chars.length - 1;\n        while (left < right) {\n            char temp = chars[left];\n            chars[left] = chars[right];\n            chars[right] = temp;\n            left++;\n            right--;\n        }\n        return new String(chars);\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            System.out.println(reverseString(sc.nextLine().trim()));\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n#include <string.h>\n\nvoid reverseString(char* s) {\n    int left = 0, right = strlen(s) - 1;\n    while (left < right) {\n        char temp = s[left];\n        s[left] = s[right];\n        s[right] = temp;\n        left++;\n        right--;\n    }\n}\n\nint main() {\n    char str[1000];\n    if (fgets(str, sizeof(str), stdin)) {\n        str[strcspn(str, \"\\r\\n\")] = 0;\n        reverseString(str);\n        printf(\"%s\\n\", str);\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\n#include <string>\nusing namespace std;\n\nstring reverseString(string s) {\n    int left = 0, right = s.length() - 1;\n    while (left < right) {\n        swap(s[left], s[right]);\n        left++;\n        right--;\n    }\n    return s;\n}\n\nint main() {\n    string s;\n    if (getline(cin, s)) {\n        cout << reverseString(s) << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "hello", "expected": "olleh"},
            {"input": "placement", "expected": "tnemecalp"},
            {"input": "interview", "expected": "weivretni"},
            {"input": "algorithm", "expected": "mhtirogla"}
        ]
    },
    {
        "id": "code_largest_three",
        "title": "Find the Largest of Three Numbers",
        "topic": "Conditional Logic & Basic Math",
        "category": "Live Coding Assessment",
        "difficulty": "Easy",
        "question": "Given three space-separated integers `a`, `b`, and `c`, determine and print the largest of the three numbers using conditional statements.",
        "description": "Given three space-separated integers `a`, `b`, and `c`, determine and print the largest of the three numbers using conditional statements.",
        "sample_input": "12 45 32",
        "sample_output": "45",
        "expected_answer": "45",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "starter_codes": {
            "Python": "import sys\ndef find_largest(a: int, b: int, c: int) -> int:\n    if a >= b and a >= c:\n        return a\n    elif b >= a and b >= c:\n        return b\n    else:\n        return c\n\nraw = sys.stdin.read().strip()\nif raw:\n    parts = [int(x) for x in raw.split()]\n    print(find_largest(parts[0], parts[1], parts[2]))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static int findLargest(int a, int b, int c) {\n        if (a >= b && a >= c) return a;\n        if (b >= a && b >= c) return b;\n        return c;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            int a = sc.nextInt();\n            int b = sc.nextInt();\n            int c = sc.nextInt();\n            System.out.println(findLargest(a, b, c));\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n\nint findLargest(int a, int b, int c) {\n    if (a >= b && a >= c) return a;\n    if (b >= a && b >= c) return b;\n    return c;\n}\n\nint main() {\n    int a, b, c;\n    if (scanf(\"%d %d %d\", &a, &b, &c) == 3) {\n        printf(\"%d\\n\", findLargest(a, b, c));\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\nusing namespace std;\n\nint findLargest(int a, int b, int c) {\n    if (a >= b && a >= c) return a;\n    if (b >= a && b >= c) return b;\n    return c;\n}\n\nint main() {\n    int a, b, c;\n    if (cin >> a >> b >> c) {\n        cout << findLargest(a, b, c) << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "12 45 32", "expected": "45"},
            {"input": "-5 -20 -1", "expected": "-1"},
            {"input": "100 100 50", "expected": "100"},
            {"input": "7 89 89", "expected": "89"}
        ]
    },
    {
        "id": "code_is_prime",
        "title": "Check Whether a Number is Prime",
        "topic": "Mathematics & Number Theory",
        "category": "Live Coding Assessment",
        "difficulty": "Easy - Medium",
        "question": "Given a positive integer `n`, print 'Prime' if it is a prime number, or 'Not Prime' if it is composite or less than or equal to 1. Check divisors up to sqrt(n).",
        "description": "Given a positive integer `n`, print 'Prime' if it is a prime number, or 'Not Prime' if it is composite or less than or equal to 1. Check divisors up to sqrt(n).",
        "sample_input": "17",
        "sample_output": "Prime",
        "expected_answer": "Prime",
        "time_complexity": "O(sqrt(N))",
        "space_complexity": "O(1)",
        "starter_codes": {
            "Python": "import sys\ndef is_prime(n: int) -> str:\n    if n <= 1:\n        return 'Not Prime'\n    if n <= 3:\n        return 'Prime'\n    if n % 2 == 0 or n % 3 == 0:\n        return 'Not Prime'\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0:\n            return 'Not Prime'\n        i += 6\n    return 'Prime'\n\nraw = sys.stdin.read().strip()\nif raw:\n    print(is_prime(int(raw)))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static String isPrime(int n) {\n        if (n <= 1) return \"Not Prime\";\n        if (n <= 3) return \"Prime\";\n        if (n % 2 == 0 || n % 3 == 0) return \"Not Prime\";\n        for (int i = 5; i * i <= n; i += 6) {\n            if (n % i == 0 || n % (i + 2) == 0) return \"Not Prime\";\n        }\n        return \"Prime\";\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            System.out.println(isPrime(sc.nextInt()));\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n\nconst char* isPrime(int n) {\n    if (n <= 1) return \"Not Prime\";\n    if (n <= 3) return \"Prime\";\n    if (n % 2 == 0 || n % 3 == 0) return \"Not Prime\";\n    for (int i = 5; i * i <= n; i += 6) {\n        if (n % i == 0 || n % (i + 2) == 0) return \"Not Prime\";\n    }\n    return \"Prime\";\n}\n\nint main() {\n    int n;\n    if (scanf(\"%d\", &n) == 1) {\n        printf(\"%s\\n\", isPrime(n));\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\nusing namespace std;\n\nstring isPrime(int n) {\n    if (n <= 1) return \"Not Prime\";\n    if (n <= 3) return \"Prime\";\n    if (n % 2 == 0 || n % 3 == 0) return \"Not Prime\";\n    for (int i = 5; i * i <= n; i += 6) {\n        if (n % i == 0 || n % (i + 2) == 0) return \"Not Prime\";\n    }\n    return \"Prime\";\n}\n\nint main() {\n    int n;\n    if (cin >> n) {\n        cout << isPrime(n) << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "17", "expected": "Prime"},
            {"input": "4", "expected": "Not Prime"},
            {"input": "1", "expected": "Not Prime"},
            {"input": "97", "expected": "Prime"},
            {"input": "100", "expected": "Not Prime"}
        ]
    },
    {
        "id": "code_factorial",
        "title": "Find Factorial of a Number",
        "topic": "Recursion & Iteration",
        "category": "Live Coding Assessment",
        "difficulty": "Easy",
        "question": "Given a non-negative integer `n`, compute and print its factorial (n!). Remember that 0! = 1.",
        "description": "Given a non-negative integer `n`, compute and print its factorial (n!). Remember that 0! = 1.",
        "sample_input": "5",
        "sample_output": "120",
        "expected_answer": "120",
        "time_complexity": "O(N)",
        "space_complexity": "O(1)",
        "starter_codes": {
            "Python": "import sys\ndef factorial(n: int) -> int:\n    ans = 1\n    for i in range(2, n + 1):\n        ans *= i\n    return ans\n\nraw = sys.stdin.read().strip()\nif raw:\n    print(factorial(int(raw)))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static long factorial(int n) {\n        long ans = 1;\n        for (int i = 2; i <= n; i++) {\n            ans *= i;\n        }\n        return ans;\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            System.out.println(factorial(sc.nextInt()));\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n\nlong long factorial(int n) {\n    long long ans = 1;\n    for (int i = 2; i <= n; i++) ans *= i;\n    return ans;\n}\n\nint main() {\n    int n;\n    if (scanf(\"%d\", &n) == 1) {\n        printf(\"%lld\\n\", factorial(n));\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\nusing namespace std;\n\nlong long factorial(int n) {\n    long long ans = 1;\n    for (int i = 2; i <= n; i++) ans *= i;\n    return ans;\n}\n\nint main() {\n    int n;\n    if (cin >> n) {\n        cout << factorial(n) << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "5", "expected": "120"},
            {"input": "0", "expected": "1"},
            {"input": "1", "expected": "1"},
            {"input": "7", "expected": "5040"}
        ]
    },
    {
        "id": "code_is_palindrome",
        "title": "Check Whether a String is a Palindrome",
        "topic": "Two-Pointer Technique",
        "category": "Live Coding Assessment",
        "difficulty": "Easy",
        "question": "Given an input string `s`, check if it reads the same forwards and backwards. Print 'Palindrome' or 'Not Palindrome'.",
        "description": "Given an input string `s`, check if it reads the same forwards and backwards. Print 'Palindrome' or 'Not Palindrome'.",
        "sample_input": "racecar",
        "sample_output": "Palindrome",
        "expected_answer": "Palindrome",
        "time_complexity": "O(N)",
        "space_complexity": "O(1)",
        "starter_codes": {
            "Python": "import sys\ndef is_palindrome(s: str) -> str:\n    left, right = 0, len(s) - 1\n    while left < right:\n        if s[left] != s[right]:\n            return 'Not Palindrome'\n        left += 1\n        right -= 1\n    return 'Palindrome'\n\nraw = sys.stdin.read().strip()\nif raw:\n    print(is_palindrome(raw))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static String isPalindrome(String s) {\n        int left = 0, right = s.length() - 1;\n        while (left < right) {\n            if (s.charAt(left) != s.charAt(right)) return \"Not Palindrome\";\n            left++;\n            right--;\n        }\n        return \"Palindrome\";\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            System.out.println(isPalindrome(sc.nextLine().trim()));\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n#include <string.h>\n\nconst char* isPalindrome(const char* s) {\n    int left = 0, right = strlen(s) - 1;\n    while (left < right) {\n        if (s[left] != s[right]) return \"Not Palindrome\";\n        left++;\n        right--;\n    }\n    return \"Palindrome\";\n}\n\nint main() {\n    char str[1000];\n    if (fgets(str, sizeof(str), stdin)) {\n        str[strcspn(str, \"\\r\\n\")] = 0;\n        printf(\"%s\\n\", isPalindrome(str));\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\n#include <string>\nusing namespace std;\n\nstring isPalindrome(string s) {\n    int left = 0, right = s.length() - 1;\n    while (left < right) {\n        if (s[left] != s[right]) return \"Not Palindrome\";\n        left++;\n        right--;\n    }\n    return \"Palindrome\";\n}\n\nint main() {\n    string s;\n    if (getline(cin, s)) {\n        cout << isPalindrome(s) << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "racecar", "expected": "Palindrome"},
            {"input": "hello", "expected": "Not Palindrome"},
            {"input": "madam", "expected": "Palindrome"},
            {"input": "level", "expected": "Palindrome"}
        ]
    },
    {
        "id": "code_find_duplicates",
        "title": "Find Duplicate Elements in an Array",
        "topic": "Hash Maps & Frequency Counting",
        "category": "Live Coding Assessment",
        "difficulty": "Medium",
        "question": "Given a space-separated sequence of integers, find and print all elements that appear more than once, sorted in ascending order with a single space separator. If no duplicates exist, print 'None'.",
        "description": "Given a space-separated sequence of integers, find and print all elements that appear more than once, sorted in ascending order with a single space separator. If no duplicates exist, print 'None'.",
        "sample_input": "1 2 3 2 4 1",
        "sample_output": "1 2",
        "expected_answer": "1 2",
        "time_complexity": "O(N log N)",
        "space_complexity": "O(N)",
        "starter_codes": {
            "Python": "import sys\ndef find_duplicates(nums: list) -> str:\n    counts = {}\n    for n in nums:\n        counts[n] = counts.get(n, 0) + 1\n    dups = sorted([k for k, v in counts.items() if v > 1])\n    return ' '.join(str(x) for x in dups) if dups else 'None'\n\nraw = sys.stdin.read().strip()\nif raw:\n    nums = [int(x) for x in raw.split()]\n    print(find_duplicates(nums))\n",
            "Java": "import java.util.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n            Map<Integer, Integer> map = new HashMap<>();\n            for (String p : parts) {\n                if (!p.isEmpty()) {\n                    int val = Integer.parseInt(p);\n                    map.put(val, map.getOrDefault(val, 0) + 1);\n                }\n            }\n            List<Integer> dups = new ArrayList<>();\n            for (Map.Entry<Integer, Integer> entry : map.entrySet()) {\n                if (entry.getValue() > 1) dups.add(entry.getKey());\n            }\n            Collections.sort(dups);\n            if (dups.isEmpty()) {\n                System.out.println(\"None\");\n            } else {\n                StringBuilder sb = new StringBuilder();\n                for (int i = 0; i < dups.size(); i++) {\n                    if (i > 0) sb.append(\" \");\n                    sb.append(dups.get(i));\n                }\n                System.out.println(sb.toString());\n            }\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n#include <stdlib.h>\n\nint cmp(const void* a, const void* b) {\n    return (*(int*)a - *(int*)b);\n}\n\nint main() {\n    int arr[1000], n = 0, val;\n    while (scanf(\"%d\", &val) == 1) {\n        arr[n++] = val;\n    }\n    qsort(arr, n, sizeof(int), cmp);\n    int dups[1000], d_count = 0;\n    for (int i = 0; i < n - 1; i++) {\n        if (arr[i] == arr[i + 1]) {\n            if (d_count == 0 || dups[d_count - 1] != arr[i]) {\n                dups[d_count++] = arr[i];\n            }\n        }\n    }\n    if (d_count == 0) {\n        printf(\"None\\n\");\n    } else {\n        for (int i = 0; i < d_count; i++) {\n            printf(\"%d%c\", dups[i], (i == d_count - 1 ? '\\n' : ' '));\n        }\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\n#include <vector>\n#include <map>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    int val;\n    map<int, int> counts;\n    while (cin >> val) {\n        counts[val]++;\n    }\n    vector<int> dups;\n    for (auto& p : counts) {\n        if (p.second > 1) dups.push_back(p.first);\n    }\n    if (dups.empty()) {\n        cout << \"None\" << endl;\n    } else {\n        for (size_t i = 0; i < dups.size(); i++) {\n            cout << dups[i] << (i + 1 == dups.size() ? \"\" : \" \");\n        }\n        cout << endl;\n    }\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "1 2 3 2 4 1", "expected": "1 2"},
            {"input": "5 10 15 20", "expected": "None"},
            {"input": "4 4 4 2 2", "expected": "2 4"},
            {"input": "9 8 7 8 9 10", "expected": "8 9"}
        ]
    },
    {
        "id": "code_custom_sort",
        "title": "Sort an Array Without Built-in Functions",
        "topic": "Sorting Algorithms",
        "category": "Live Coding Assessment",
        "difficulty": "Medium",
        "question": "Given a space-separated sequence of integers, sort the array in ascending order by implementing a sorting algorithm (e.g. Bubble Sort or Selection Sort). Do not use built-in sort functions like `.sort()` or `qsort()`.",
        "description": "Given a space-separated sequence of integers, sort the array in ascending order by implementing a sorting algorithm (e.g. Bubble Sort or Selection Sort). Do not use built-in sort functions like `.sort()` or `qsort()`.",
        "sample_input": "64 25 12 22 11",
        "sample_output": "11 12 22 25 64",
        "expected_answer": "11 12 22 25 64",
        "time_complexity": "O(N^2) or O(N log N)",
        "space_complexity": "O(1) auxiliary",
        "starter_codes": {
            "Python": "import sys\ndef bubble_sort(nums: list) -> str:\n    n = len(nums)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if nums[j] > nums[j + 1]:\n                nums[j], nums[j + 1] = nums[j + 1], nums[j]\n    return ' '.join(str(x) for x in nums)\n\nraw = sys.stdin.read().strip()\nif raw:\n    nums = [int(x) for x in raw.split()]\n    print(bubble_sort(nums))\n",
            "Java": "import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n            int[] arr = new int[parts.length];\n            for (int i = 0; i < parts.length; i++) arr[i] = Integer.parseInt(parts[i]);\n            // Implement Bubble Sort\n            for (int i = 0; i < arr.length; i++) {\n                for (int j = 0; j < arr.length - i - 1; j++) {\n                    if (arr[j] > arr[j + 1]) {\n                        int temp = arr[j];\n                        arr[j] = arr[j + 1];\n                        arr[j + 1] = temp;\n                    }\n                }\n            }\n            StringBuilder sb = new StringBuilder();\n            for (int i = 0; i < arr.length; i++) {\n                if (i > 0) sb.append(\" \");\n                sb.append(arr[i]);\n            }\n            System.out.println(sb.toString());\n        }\n    }\n}\n",
            "C": "#include <stdio.h>\n\nint main() {\n    int arr[1000], n = 0, val;\n    while (scanf(\"%d\", &val) == 1) {\n        arr[n++] = val;\n    }\n    for (int i = 0; i < n; i++) {\n        for (int j = 0; j < n - i - 1; j++) {\n            if (arr[j] > arr[j + 1]) {\n                int temp = arr[j];\n                arr[j] = arr[j + 1];\n                arr[j + 1] = temp;\n            }\n        }\n    }\n    for (int i = 0; i < n; i++) {\n        printf(\"%d%c\", arr[i], (i == n - 1 ? '\\n' : ' '));\n    }\n    return 0;\n}\n",
            "C++": "#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    vector<int> arr;\n    int val;\n    while (cin >> val) {\n        arr.push_back(val);\n    }\n    for (size_t i = 0; i < arr.size(); i++) {\n        for (size_t j = 0; j + 1 < arr.size() - i; j++) {\n            if (arr[j] > arr[j + 1]) {\n                swap(arr[j], arr[j + 1]);\n            }\n        }\n    }\n    for (size_t i = 0; i < arr.size(); i++) {\n        cout << arr[i] << (i + 1 == arr.size() ? \"\" : \" \");\n    }\n    cout << endl;\n    return 0;\n}\n"
        },
        "test_cases": [
            {"input": "64 25 12 22 11", "expected": "11 12 22 25 64"},
            {"input": "5 4 3 2 1", "expected": "1 2 3 4 5"},
            {"input": "42", "expected": "42"},
            {"input": "3 1 4 1 5 9 2 6", "expected": "1 1 2 3 4 5 6 9"}
        ]
    }
]

DATA_STRUCTURES_QUESTIONS = [
    {
        "id": "dsa_1",
        "topic": "Arrays vs Linked Lists",
        "category": "Arrays vs Linked Lists",
        "difficulty": "Medium",
        "question": "Compare dynamic Arrays and Singly Linked Lists in terms of memory contiguousness, cache locality, random access, and element insertion/deletion. When is a Linked List strictly preferred over an array?",
        "key_concepts": ["contiguous memory", "cache locality", "random access o(1)", "pointer overhead", "insertion at head o(1)", "memory reallocation"],
        "expected_answer": "Arrays provide O(1) random access and superior CPU cache locality due to contiguous memory. Linked lists avoid reallocation overhead and offer O(1) insertion at head/tail without shifting elements.",
        "sample_ideal": "Arrays provide O(1) random access and superior CPU cache locality due to contiguous memory. Linked lists avoid reallocation overhead and offer O(1) insertion at head/tail without shifting elements."
    },
    {
        "id": "dsa_2",
        "topic": "Stacks & Queues",
        "category": "Stacks & Queues",
        "difficulty": "Medium",
        "question": "Explain the mechanics of Stacks (LIFO) and Queues (FIFO). How would you use a Stack to validate balanced parentheses in a code parser, and what are the time and space complexities of that approach?",
        "key_concepts": ["stack", "queue", "lifo", "fifo", "balanced parentheses", "push", "pop", "o(n) time", "o(n) space"],
        "expected_answer": "A Stack operates LIFO while a Queue operates FIFO. In parentheses matching, push open brackets onto the stack; when encountering a close bracket, pop and ensure matching type. Time and space are O(N).",
        "sample_ideal": "A Stack operates LIFO while a Queue operates FIFO. In parentheses matching, push open brackets onto the stack; when encountering a close bracket, pop and ensure matching type. Time and space are O(N)."
    },
    {
        "id": "dsa_3",
        "topic": "Searching Algorithms",
        "category": "Searching Algorithms",
        "difficulty": "Medium",
        "question": "How does Binary Search achieve O(log N) time complexity? What strict prerequisite must be met, and how do you calculate the middle index in languages like Java or C++ to avoid 32-bit integer overflow?",
        "key_concepts": ["binary search", "sorted array", "o(log n)", "divide and conquer", "mid = low + (high - low) / 2", "integer overflow"],
        "expected_answer": "Binary search halves the search space each step on a pre-sorted array. To prevent integer overflow when (low + high) exceeds 2^31 - 1, calculate mid as low + (high - low) / 2.",
        "sample_ideal": "Binary search halves the search space each step on a pre-sorted array. To prevent integer overflow when (low + high) exceeds 2^31 - 1, calculate mid as low + (high - low) / 2."
    },
    {
        "id": "dsa_4",
        "topic": "Sorting & Complexity",
        "category": "Sorting & Complexity",
        "difficulty": "Medium",
        "question": "Compare QuickSort and MergeSort. Explain their Divide and Conquer strategies, their average and worst-case time complexities, auxiliary space requirements, and why MergeSort is preferred for sorting Linked Lists.",
        "key_concepts": ["quicksort", "mergesort", "divide and conquer", "pivot", "o(n log n)", "o(n^2) worst case", "stable sort", "o(n) auxiliary space"],
        "expected_answer": "MergeSort divides into halves, sorts recursively, and merges in O(N log N) worst-case time with O(N) space. QuickSort partitions in-place around a pivot with O(1) auxiliary space, but degrades to O(N^2) if pivot selection is poor.",
        "sample_ideal": "MergeSort divides into halves, sorts recursively, and merges in O(N log N) worst-case time with O(N) space. QuickSort partitions in-place around a pivot with O(1) auxiliary space, but degrades to O(N^2) if pivot selection is poor."
    }
]

DATABASE_SQL_QUESTIONS = [
    {
        "id": "sql_1",
        "title": "SELECT & Filter High-Earning Engineers",
        "topic": "Filtering & Sorting",
        "category": "Database & SQL",
        "difficulty": "Easy - Medium",
        "question": "Write a query to retrieve the `name`, `role`, and `salary` of all employees in the Engineering department (`department_id = 1`) who earn more than 70,000, ordered by `salary` descending.",
        "description": "Write a query to retrieve the `name`, `role`, and `salary` of all employees in the Engineering department (`department_id = 1`) who earn more than 70,000, ordered by `salary` descending.",
        "starter_code": "SELECT name, role, salary\nFROM employees\nWHERE department_id = 1 AND salary > 70000\nORDER BY salary DESC;",
        "expected_query": "SELECT name, role, salary FROM employees WHERE department_id = 1 AND salary > 70000 ORDER BY salary DESC;",
        "expected_answer": "SELECT name, role, salary FROM employees WHERE department_id = 1 AND salary > 70000 ORDER BY salary DESC;"
    },
    {
        "id": "sql_2",
        "title": "INNER JOIN Employees and Departments",
        "topic": "Relational Joins",
        "category": "Database & SQL",
        "difficulty": "Medium",
        "question": "Perform an INNER JOIN between `employees` and `departments` to list each employee's `name`, `role`, department `name` (aliased as `department`), and `location`.",
        "description": "Perform an INNER JOIN between `employees` and `departments` to list each employee's `name`, `role`, department `name` (aliased as `department`), and `location`.",
        "starter_code": "SELECT e.name, e.role, d.name AS department, d.location\nFROM employees e\nJOIN departments d ON e.department_id = d.id;",
        "expected_query": "SELECT e.name, e.role, d.name AS department, d.location FROM employees e JOIN departments d ON e.department_id = d.id;",
        "expected_answer": "SELECT e.name, e.role, d.name AS department, d.location FROM employees e JOIN departments d ON e.department_id = d.id;"
    },
    {
        "id": "sql_3",
        "title": "GROUP BY Department Analytics",
        "topic": "Aggregation & HAVING",
        "category": "Database & SQL",
        "difficulty": "Medium",
        "question": "Calculate the total employee count (`total_employees`) and average salary (`avg_salary` rounded) for each department that has more than 1 employee.",
        "description": "Calculate the total employee count (`total_employees`) and average salary (`avg_salary` rounded) for each department that has more than 1 employee.",
        "starter_code": "SELECT d.name AS department, COUNT(e.id) AS total_employees, ROUND(AVG(e.salary)) AS avg_salary\nFROM departments d\nJOIN employees e ON d.id = e.department_id\nGROUP BY d.id\nHAVING COUNT(e.id) > 1;",
        "expected_query": "SELECT d.name AS department, COUNT(e.id) AS total_employees, ROUND(AVG(e.salary)) AS avg_salary FROM departments d JOIN employees e ON d.id = e.department_id GROUP BY d.id HAVING COUNT(e.id) > 1;",
        "expected_answer": "SELECT d.name AS department, COUNT(e.id) AS total_employees, ROUND(AVG(e.salary)) AS avg_salary FROM departments d JOIN employees e ON d.id = e.department_id GROUP BY d.id HAVING COUNT(e.id) > 1;"
    },
    {
        "id": "sql_4",
        "title": "Find Second Highest Salary (Subquery)",
        "topic": "Nested Subqueries",
        "category": "Database & SQL",
        "difficulty": "Medium",
        "question": "Write a SQL query using a nested subquery to find the second highest salary among all employees in the `employees` table.",
        "description": "Write a SQL query using a nested subquery to find the second highest salary among all employees in the `employees` table.",
        "starter_code": "SELECT MAX(salary) AS second_highest_salary\nFROM employees\nWHERE salary < (SELECT MAX(salary) FROM employees);",
        "expected_query": "SELECT MAX(salary) AS second_highest_salary FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);",
        "expected_answer": "SELECT MAX(salary) AS second_highest_salary FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);"
    }
]

PROJECT_ARCHITECTURE_QUESTIONS = [
    {
        "id": "proj_1",
        "topic": "Project Architecture & Tech Stack",
        "category": "Project Architecture & Tech Stack",
        "difficulty": "Medium",
        "question": "Describe your primary academic, capstone, or personal software project. What was the core problem statement, and what technical criteria drove your choice of programming language, backend framework, and database?",
        "key_concepts": ["problem statement", "architecture", "tech stack", "framework", "database", "rationale", "trade-offs", "scalability"],
        "expected_answer": "A candidate should clearly state the user problem, justify tech choices (e.g. Python/Django for rapid ORM prototyping or Node.js for high-concurrency event loops), and discuss architecture modularity.",
        "sample_ideal": "A candidate should clearly state the user problem, justify tech choices (e.g. Python/Django for rapid ORM prototyping or Node.js for high-concurrency event loops), and discuss architecture modularity."
    },
    {
        "id": "proj_2",
        "topic": "Database Design & Normalization",
        "category": "Database Design & Normalization",
        "difficulty": "Medium",
        "question": "Walk through the database schema design of your project. How did you normalize tables, establish primary/foreign key relationships, and ensure data integrity under concurrent user writes?",
        "key_concepts": ["schema design", "normalization", "primary key", "foreign key", "referential integrity", "indexing", "transactions"],
        "expected_answer": "Demonstrate understanding of entity relationships (1:N, N:M), foreign key cascading, index placement on frequently queried columns, and transactional boundaries to prevent race conditions.",
        "sample_ideal": "Demonstrate understanding of entity relationships (1:N, N:M), foreign key cascading, index placement on frequently queried columns, and transactional boundaries to prevent race conditions."
    },
    {
        "id": "proj_3",
        "topic": "API Integration & End-to-End Flow",
        "category": "API Integration & End-to-End Flow",
        "difficulty": "Medium - Hard",
        "question": "Explain the end-to-end data flow in your project when a user submits a form or triggers an action. How are requests authenticated, validated, processed by backend controllers, and stored?",
        "key_concepts": ["data flow", "rest api", "jwt", "authentication", "middleware", "validation", "controller", "serialization"],
        "expected_answer": "Detail frontend state management, HTTP payload formatting, JWT bearer token verification in backend middleware, schema sanitization, ORM persistence, and clean JSON response codes.",
        "sample_ideal": "Detail frontend state management, HTTP payload formatting, JWT bearer token verification in backend middleware, schema sanitization, ORM persistence, and clean JSON response codes."
    },
    {
        "id": "proj_4",
        "topic": "Technical Challenges & Debugging",
        "category": "Technical Challenges & Debugging",
        "difficulty": "Medium - Hard",
        "question": "What was the most challenging technical bug, performance bottleneck, or architecture limitation you encountered in your project? Walk through your diagnostic steps, profiling tools, and final resolution.",
        "key_concepts": ["debugging", "root cause", "bottleneck", "profiling", "logs", "resolution", "edge cases", "refactoring"],
        "expected_answer": "Structure the answer using an engineering diagnostic workflow: problem symptom, isolating root cause through logging/profiling, evaluating alternative fixes, and verifying resolution.",
        "sample_ideal": "Structure the answer using an engineering diagnostic workflow: problem symptom, isolating root cause through logging/profiling, evaluating alternative fixes, and verifying resolution."
    }
]

# Backward compatibility aliases
CODING_CHALLENGES = LIVE_CODING_QUESTIONS
DSA_QUESTIONS = DATA_STRUCTURES_QUESTIONS
SQL_CHALLENGES = DATABASE_SQL_QUESTIONS
PROJECT_QUESTIONS = PROJECT_ARCHITECTURE_QUESTIONS


# --- AI Core Logic ---

def call_gemini_api(api_key: str, prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Call Google Gemini REST API without third-party dependencies."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"]

def evaluate_response(question: str, answer: str, round_type: str, domain: str = "General", api_key: str = None) -> dict:
    """
    Evaluates a candidate's answer.
    Uses LLM API if key provided; otherwise runs the high-fidelity offline NLP evaluator.
    """
    clean_ans = answer.strip()
    if not clean_ans or len(clean_ans) < 10:
        return {
            "score": 2.0,
            "strengths": ["Submitted a brief attempt."],
            "weaknesses": ["Response is too terse or incomplete to evaluate effectively."],
            "feedback": "Your response was very brief. In interviews, elaborate with structured explanations, concrete examples, or technical reasoning.",
            "follow_up": "Could you expand on this and walk me through a specific example or application?",
            "metrics": {"Clarity": 25, "Depth": 20, "Relevance": 30, "Structure": 25}
        }

    # If external API key provided, try calling LLM
    if api_key:
        try:
            prompt = f"""
You are an expert IT Placement Interviewer evaluating a candidate response.
Round: {round_type}
Domain: {domain}
Question: {question}
Candidate Answer: {clean_ans}

Evaluate thoroughly and return strictly valid JSON matching this schema:
{{
  "score": (float between 1.0 and 10.0),
  "strengths": ["point 1", "point 2"],
  "weaknesses": ["point 1", "point 2"],
  "feedback": "detailed constructive feedback paragraph",
  "follow_up": "one intelligent follow-up question digging deeper into what the candidate answered",
  "metrics": {{
    "Clarity": (integer 0-100),
    "Depth": (integer 0-100),
    "Relevance": (integer 0-100),
    "Structure": (integer 0-100)
  }}
}}
Do not include markdown fences or other text outside the JSON.
"""
            raw_text = call_gemini_api(api_key, prompt)
            # Parse json
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            # Fall back to offline engine on network/key error
            pass

    # Built-in Intelligent Offline NLP Engine
    return offline_evaluate(question, clean_ans, round_type, domain)

def offline_evaluate(question: str, answer: str, round_type: str, domain: str) -> dict:
    """
    High-fidelity heuristic NLP evaluation engine.
    Analyzes word count, vocabulary sophistication, concept density, STAR elements, and sentiment.
    """
    words = [w.lower() for w in re.findall(r"\b\w+\b", answer)]
    word_count = len(words)
    answer_lower = answer.lower()

    score = 5.0
    strengths = []
    weaknesses = []
    metrics = {"Clarity": 60, "Depth": 55, "Relevance": 65, "Structure": 60}

    # 1. Volume & Depth Analysis
    if word_count < 25:
        score -= 1.5
        weaknesses.append("Response is brief and lacks supporting depth.")
        metrics["Depth"] -= 25
    elif word_count > 70:
        score += 1.0
        strengths.append("Provided a detailed and well-elaborated response.")
        metrics["Depth"] += 20
        metrics["Clarity"] += 10
    else:
        strengths.append("Communicated the main thought directly.")

    # 2. Round-Specific Evaluation
    if round_type == "HR":
        # Check for STAR method markers (Situation, Task, Action, Result)
        star_markers = {
            "situation": ["when i was", "during my", "in our team", "project", "scenario", "problem was"],
            "action": ["i decided", "i implemented", "i took responsibility", "i communicated", "my role was", "i resolved"],
            "result": ["as a result", "outcome", "finally", "we achieved", "successfully", "learned", "improved"]
        }
        found_star = []
        for phase, tokens in star_markers.items():
            if any(t in answer_lower for t in tokens):
                found_star.append(phase)

        if len(found_star) >= 2:
            score += 1.5
            strengths.append(f"Demonstrated behavioral structure by mentioning {', '.join(found_star)}.")
            metrics["Structure"] += 25
        else:
            weaknesses.append("Could benefit from applying the STAR method (Situation, Task, Action, Result).")
            metrics["Structure"] -= 15

        # Check professionalism & positive tone
        positive_vocab = ["collaborate", "learned", "initiative", "solution", "deliver", "responsibility", "feedback", "growth"]
        matched_pos = [w for w in positive_vocab if w in answer_lower]
        if matched_pos:
            score += 0.8
            strengths.append(f"Used strong professional action verbs ({', '.join(matched_pos[:3])}).")
            metrics["Clarity"] += 15

        # Formulate contextual follow-up
        if "project" in answer_lower or "team" in answer_lower:
            follow_up = "What was the single most difficult technical or collaborative hurdle you faced in that experience, and how did you measure your success?"
        elif "learn" in answer_lower or "improve" in answer_lower:
            follow_up = "Could you walk me through a specific resource or feedback session that helped you realize you needed that improvement?"
        else:
            follow_up = "If you were to face a similar situation today with higher stakes, what would you do differently?"

    else:
        # Technical Round Evaluation
        key_concepts = []
        # Search domain knowledge for matching concepts
        if domain in TECHNICAL_DOMAINS:
            for q in TECHNICAL_DOMAINS[domain]["questions"]:
                if any(w in question.lower() for w in q["question"].lower().split()[:4]):
                    key_concepts = q["key_concepts"]
                    break

        matched_concepts = [c for c in key_concepts if c in answer_lower]
        if matched_concepts:
            score += min(len(matched_concepts) * 0.9, 2.5)
            strengths.append(f"Accurately addressed key technical terms: {', '.join(matched_concepts)}.")
            metrics["Relevance"] += 25
            metrics["Depth"] += 20
        else:
            weaknesses.append("Missed mentioning essential architectural/system-level terms associated with this concept.")
            metrics["Relevance"] -= 15

        # Technical reasoning phrases
        reasoning_phrases = ["because", "therefore", "in contrast", "performance", "complexity", "trade-off", "latency", "memory"]
        matched_reasoning = [p for p in reasoning_phrases if p in answer_lower]
        if matched_reasoning:
            score += 0.7
            strengths.append("Articulated trade-offs and underlying mechanics effectively.")
            metrics["Clarity"] += 15
        else:
            weaknesses.append("Try explaining the trade-offs (e.g. time complexity vs space complexity or efficiency).")

        # Formulate contextual follow-up
        if any(c in answer_lower for c in ["memory", "performance", "fast", "speed", "scale"]):
            follow_up = f"You touched on efficiency—how does this behave under high concurrency or extremely large datasets?"
        elif any(c in answer_lower for c in ["error", "exception", "fail", "null"]):
            follow_up = "How would you handle edge cases and fault recovery in a production-grade deployment for this?"
        else:
            follow_up = "Can you describe a scenario where using this approach would actually be considered an anti-pattern or suboptimal choice?"

    # Clamp scores
    score = round(max(2.5, min(9.8, score)), 1)
    for k in metrics:
        metrics[k] = max(20, min(100, metrics[k]))

    # Construct constructive feedback narrative
    strength_text = " ".join(strengths)
    weakness_text = " ".join(weaknesses) if weaknesses else "Overall solid response."
    feedback = f"{strength_text} {weakness_text}"

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "follow_up": follow_up,
        "metrics": metrics
    }

def evaluate_technical_round(stage: str, question: str, answer: str, api_key: str = None) -> dict:
    """
    Evaluates candidate responses across the 7 technical criteria:
    1. Technical accuracy
    2. Coding correctness
    3. Logical thinking
    4. Time and space complexity
    5. Problem-solving ability
    6. Database knowledge
    7. Project understanding
    """
    clean_ans = answer.strip()
    if not clean_ans or len(clean_ans) < 10:
        return {
            "score": 2.0,
            "strengths": ["Attempted response."],
            "weaknesses": ["Response is too brief to demonstrate technical competence."],
            "feedback": "Please provide a complete explanation covering technical mechanics, syntax, edge cases, and reasoning.",
            "metrics": {
                "Technical Accuracy": 25,
                "Logical Thinking": 20,
                "Problem Solving": 25,
                "Complexity Awareness": 20
            }
        }

    answer_lower = clean_ans.lower()
    words = [w.lower() for w in re.findall(r"\b\w+\b", clean_ans)]
    word_count = len(words)

    score = 6.0
    strengths = []
    weaknesses = []

    # Criteria tracking
    crit_accuracy = 65
    crit_logic = 65
    crit_problem_solving = 65
    crit_complexity = 60
    crit_db = 65
    crit_project = 65

    # Depth & explanation check
    if word_count < 25:
        score -= 1.5
        crit_accuracy -= 20
        weaknesses.append("Response is terse; elaborate more on underlying mechanics.")
    elif word_count > 60:
        score += 1.0
        crit_accuracy += 15
        crit_logic += 15
        strengths.append("Provided a comprehensive and structured technical explanation.")

    # Search for technical terminology and reasoning
    tech_terms = [
        "memory", "pointer", "reference", "stack", "heap", "interface", "class", "object",
        "complexity", "o(n)", "o(1)", "o(log n)", "o(n^2)", "runtime", "space", "time",
        "thread", "lock", "immutable", "mutable", "hash", "table", "index", "b-tree",
        "sql", "join", "group by", "foreign key", "primary key", "acid", "transaction",
        "exception", "try", "catch", "finally", "closure", "scope", "recursion", "divide and conquer"
    ]
    found_terms = [t for t in tech_terms if t in answer_lower]
    if len(found_terms) >= 3:
        score += min(1.5, len(found_terms) * 0.3)
        crit_accuracy += 15
        crit_problem_solving += 10
        strengths.append(f"Demonstrated technical fluency with key terms: {', '.join(found_terms[:4])}.")
    else:
        weaknesses.append("Incorporate more industry-standard terminology and runtime/memory considerations.")

    # Stage-specific criteria evaluation
    if stage == "Fundamentals":
        if any(c in answer_lower for c in ["encapsulation", "inheritance", "polymorphism", "abstraction", "immutable", "try", "finally"]):
            score += 1.0
            crit_accuracy += 15
            strengths.append("Clear grasp of language fundamentals and object-oriented principles.")
    elif stage == "DSA":
        if any(c in answer_lower for c in ["o(n)", "o(1)", "o(log n)", "time complexity", "space complexity", "worst case", "divide and conquer"]):
            score += 1.2
            crit_complexity += 25
            crit_logic += 15
            strengths.append("Accurately evaluated algorithmic time and space complexity trade-offs.")
        else:
            weaknesses.append("Consider explicitly stating the Big-O time and space complexity.")
            crit_complexity -= 15
    elif stage == "SQL":
        crit_db = 75
        if any(c in answer_lower for c in ["select", "join", "group by", "having", "foreign key", "index", "subquery", "where"]):
            score += 1.2
            crit_db += 20
            strengths.append("Strong understanding of relational database operations and query optimization.")
    elif stage == "Project":
        crit_project = 75
        if any(c in answer_lower for c in ["architecture", "api", "database", "schema", "rest", "jwt", "debug", "frontend", "backend"]):
            score += 1.2
            crit_project += 20
            strengths.append("Articulated project architectural decisions, data flow, and trade-offs effectively.")

    score = round(max(3.0, min(9.9, score)), 1)
    metrics = {
        "Technical Accuracy": max(20, min(100, crit_accuracy)),
        "Logical Thinking": max(20, min(100, crit_logic)),
        "Problem Solving": max(20, min(100, crit_problem_solving)),
        "Complexity Awareness": max(20, min(100, crit_complexity))
    }
    if stage == "SQL":
        metrics["Database Knowledge"] = max(20, min(100, crit_db))
    if stage == "Project":
        metrics["Project Understanding"] = max(20, min(100, crit_project))

    strength_text = " ".join(strengths)
    weakness_text = " ".join(weaknesses) if weaknesses else "Strong, articulate response."
    feedback = f"{strength_text} {weakness_text}"

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "metrics": metrics
    }

def generate_comprehensive_report(candidate_name: str, target_role: str, domain: str,
                                  aptitude_score: float, hr_score: float, technical_score: float,
                                  coding_score: float, transcripts: list) -> dict:
    """
    Synthesizes round-wise evaluations into an overall placement readiness analysis report.
    """
    overall_score = round(
        (aptitude_score * 0.25) +
        (hr_score * 0.35) +
        (technical_score * 0.30) +
        (coding_score * 0.10),
        1
    )

    if overall_score >= 80:
        readiness = "Placement Ready (Tier-1 Ready)"
        summary_verdict = "Outstanding performance across all assessment rounds. Demonstrates solid analytical reasoning, articulate communication, and strong core technical fundamentals."
    elif overall_score >= 65:
        readiness = "Interview Ready (Minor Polish Recommended)"
        summary_verdict = "Competent candidate with good problem-solving foundation. Recommended to polish technical edge cases and structure behavioral answers tighter."
    elif overall_score >= 50:
        readiness = "Emerging Potential (Targeted Preparation Required)"
        summary_verdict = "Demonstrates foundational aptitude, but requires focused revision on core domain depth and behavioral STAR methodology."
    else:
        readiness = "Needs Foundational Preparation"
        summary_verdict = "Candidate needs structured practice in aptitude problem solving and foundational computer science topics before upcoming placement drives."

    # Identify overarching strengths and improvement areas
    strengths_pool = []
    improvements_pool = []

    if aptitude_score >= 70:
        strengths_pool.append("Strong quantitative and analytical problem-solving speed.")
    else:
        improvements_pool.append("Practice time management and formula drills for Quantitative Aptitude.")

    if hr_score >= 70:
        strengths_pool.append("High interpersonal articulation and professional behavioral responses.")
    else:
        improvements_pool.append("Structure behavioral questions using the STAR format (Situation, Task, Action, Result).")

    if technical_score >= 70:
        strengths_pool.append(f"Clear conceptual grasp of {domain} architectures and principles.")
    else:
        improvements_pool.append(f"Deepen knowledge in {domain} internals, time/space complexity, and trade-offs.")

    if coding_score >= 70:
        strengths_pool.append("Clean algorithmic code implementation and passing test suites.")
    else:
        improvements_pool.append("Work on edge-case testing and dry-running code before execution.")

    roadmap = [
        {"week": "Week 1", "goal": "Aptitude Drills", "tasks": "Solve 20 daily problems in percentages, time & work, syllogisms, and coding-decoding."},
        {"week": "Week 2", "goal": f"{domain} Mastery", "tasks": "Revise core theoretical concepts, internals, design patterns, and system interactions."},
        {"week": "Week 3", "goal": "Mock HR & STAR Stories", "tasks": "Draft 5 personal project stories using the STAR method for behavioral interviews."},
        {"week": "Week 4", "goal": "Simulated Live Tests", "tasks": "Take timed mock assessments and practice speaking answers aloud using speech synthesis."}
    ]

    return {
        "candidate_name": candidate_name,
        "target_role": target_role,
        "target_domain": domain,
        "aptitude_score": aptitude_score,
        "hr_score": hr_score,
        "technical_score": technical_score,
        "coding_score": coding_score,
        "overall_score": overall_score,
        "readiness_status": readiness,
        "summary_verdict": summary_verdict,
        "top_strengths": strengths_pool if strengths_pool else ["Eager to learn and attempt all rounds."],
        "priority_improvements": improvements_pool if improvements_pool else ["Continue maintaining consistency."],
        "preparation_roadmap": roadmap
    }
