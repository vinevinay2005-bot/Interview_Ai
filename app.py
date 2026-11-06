"""
AI-Driven Virtual Interview and Skill Assessment Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import database
import ai_engine
import speech_helper
import coding_runner
import report_generator
import hr_api

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Virtual Interview & Skill Assessment Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
database.init_db()

# --- Custom Styling ---
st.markdown("""
<style>
    /* Global Styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 24px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: white !important;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        opacity: 0.9;
        color: #e2e8f0 !important;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-card p {
        margin: 4px 0 0 0;
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }
    /* Chat Stream & Message Containers */
    .chat-msg-row-ai {
        display: flex;
        justify-content: flex-start;
        width: 100%;
        margin-bottom: 12px;
    }
    .chat-msg-row-candidate {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin-bottom: 12px;
    }
    .chat-bubble-ai {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 12px 12px 12px 2px;
        color: #f8fafc;
        max-width: 82%;
        text-align: left !important;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    .chat-bubble-ai * {
        text-align: left !important;
    }
    .chat-bubble-candidate {
        background: #0f2744;
        border: 1px solid #1e3a8a;
        border-right: 4px solid #10b981;
        padding: 16px 20px;
        border-radius: 12px 12px 2px 12px;
        color: #f1f5f9;
        max-width: 82%;
        text-align: left !important;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    .chat-bubble-candidate * {
        text-align: left !important;
    }
    .chat-speaker-label {
        font-weight: 700;
        font-size: 13.5px;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
        text-align: left !important;
    }
    .speaker-ai {
        color: #60a5fa;
    }
    .speaker-candidate {
        color: #34d399;
    }
    .chat-text-content {
        font-size: 15px;
        color: #f8fafc;
        text-align: left !important;
        white-space: pre-wrap;
    }
    .feedback-box {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 14px 18px;
        border-radius: 8px;
        margin: 4px 0 16px 0;
        text-align: left !important;
        max-width: 82%;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .feedback-box * {
        text-align: left !important;
    }
    @media (max-width: 768px) {
        .chat-bubble-ai, .chat-bubble-candidate, .feedback-box {
            max-width: 95% !important;
            padding: 12px 14px !important;
        }
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }

    /* Clean Modern SaaS Login & Form UI */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04) !important;
        padding: 36px 32px 30px 32px !important;
    }
    div[data-testid="stTextInput"] {
        margin-bottom: 16px !important;
    }
    div[data-testid="stTextInput"] label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1.5px solid #cbd5e1 !important;
        height: 52px !important;
        min-height: 52px !important;
        padding: 0 16px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 15.5px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        outline: none !important;
    }
    div[data-testid="stCheckbox"] {
        margin-top: -6px !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stCheckbox"] label {
        font-size: 13.5px !important;
        color: #64748b !important;
        font-weight: 500 !important;
    }

    /* Blue Professional Branding Buttons */
    div.st-key-btn_login_submit > button,
    div.st-key-btn_submit_reset > button,
    div.st-key-btn_execute_signup > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        height: 52px !important;
        min-height: 52px !important;
        font-size: 16.5px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        letter-spacing: 0.2px !important;
    }
    div.st-key-btn_login_submit > button:hover,
    div.st-key-btn_submit_reset > button:hover,
    div.st-key-btn_execute_signup > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    div.st-key-btn_login_submit > button:active,
    div.st-key-btn_submit_reset > button:active,
    div.st-key-btn_execute_signup > button:active {
        background-color: #1e3a8a !important;
        transform: translateY(0px) !important;
    }

    /* Blue Navigation Links for Forgot Password & Sign Up */
    div.st-key-btn_forgot_password_link button,
    div.st-key-btn_signup_link button,
    div.st-key-btn_return_login button,
    div.st-key-btn_cancel_reset button {
        background: transparent !important;
        border: none !important;
        padding: 4px 0 !important;
        color: #2563eb !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        text-decoration: none !important;
        box-shadow: none !important;
        text-align: left !important;
        cursor: pointer !important;
        min-height: auto !important;
        height: auto !important;
        transition: color 0.15s ease !important;
    }
    div.st-key-btn_forgot_password_link button:hover,
    div.st-key-btn_signup_link button:hover,
    div.st-key-btn_return_login button:hover,
    div.st-key-btn_cancel_reset button:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
        background: transparent !important;
    }

    /* Centered Responsive Layout for Auth Card */
    @media (max-width: 640px) {
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 24px 18px 20px 18px !important;
            border-radius: 12px !important;
        }
    }

    /* Single-Column Vertical Dashboard Cards */
    .dash-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.05);
    }
    .dash-card-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0 0 6px 0;
    }
    .dash-card-desc {
        font-size: 14px;
        color: #475569;
        margin: 0 0 14px 0;
        line-height: 1.5;
    }
    .dash-section-header {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Technical Interview Stage Stepper & Code Editor */
    .tech-step-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        background: #0f172a;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .tech-code-container {
        background: #0b1120;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
    }
    .tech-console-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1e293b;
        padding: 8px 14px;
        border-radius: 8px 8px 0 0;
        border: 1px solid #334155;
        border-bottom: none;
        font-size: 13px;
        font-weight: 600;
        color: #e2e8f0;
    }
    .tech-console-body {
        background: #090d16;
        border: 1px solid #334155;
        border-radius: 0 0 8px 8px;
        padding: 14px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        color: #38bdf8;
        min-height: 90px;
        max-height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-all;
    }
    .tech-schema-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 14px;
        font-size: 13px;
        color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "user" not in st.session_state:
    st.session_state.user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard & Overview"

if "nav_target" not in st.session_state:
    st.session_state.nav_target = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "remembered_user" not in st.session_state:
    st.session_state.remembered_user = ""

if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "target_domain" not in st.session_state:
    st.session_state.target_domain = "Python & Backend"

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

# Aptitude State
if "aptitude_questions" not in st.session_state:
    st.session_state.aptitude_questions = []
if "aptitude_answers" not in st.session_state:
    st.session_state.aptitude_answers = {}
if "aptitude_submitted" not in st.session_state:
    st.session_state.aptitude_submitted = False
if "aptitude_score" not in st.session_state:
    st.session_state.aptitude_score = 0.0

# HR Interview State
if "hr_question_idx" not in st.session_state:
    st.session_state.hr_question_idx = 0
if "hr_scores" not in st.session_state:
    st.session_state.hr_scores = []
if "hr_completed" not in st.session_state:
    st.session_state.hr_completed = False

# Technical Interview State
if "tech_question_idx" not in st.session_state:
    st.session_state.tech_question_idx = 0
if "tech_scores" not in st.session_state:
    st.session_state.tech_scores = []
if "tech_completed" not in st.session_state:
    st.session_state.tech_completed = False

# Technical Interview Modular Stages State
if "tech_active_stage" not in st.session_state:
    st.session_state.tech_active_stage = "1. Programming Fundamentals"
if "tech_fund_idx" not in st.session_state:
    st.session_state.tech_fund_idx = 0
if "tech_code_idx" not in st.session_state:
    st.session_state.tech_code_idx = 0
if "tech_code_lang" not in st.session_state:
    st.session_state.tech_code_lang = "Python"
if "tech_dsa_idx" not in st.session_state:
    st.session_state.tech_dsa_idx = 0
if "tech_sql_idx" not in st.session_state:
    st.session_state.tech_sql_idx = 0
if "tech_proj_idx" not in st.session_state:
    st.session_state.tech_proj_idx = 0
if "tech_run_result" not in st.session_state:
    st.session_state.tech_run_result = None
if "sql_run_result" not in st.session_state:
    st.session_state.sql_run_result = None

# Coding Challenge State
if "coding_score" not in st.session_state:
    st.session_state.coding_score = 0.0
if "coding_completed" not in st.session_state:
    st.session_state.coding_completed = False

# --- Helper Functions ---
def navigate_to(page_name):
    """Safely queue a navigation target to apply before the radio widget is instantiated."""
    st.session_state.nav_target = page_name

def login_user(identifier, password, remember_me=False):
    if not identifier or not password:
        st.warning("⚠️ Please provide both your username/email and password.")
        return False
    user = database.authenticate_user(identifier, password)
    if user:
        st.session_state.user = user
        if remember_me:
            st.session_state.remembered_user = identifier.strip()
        else:
            st.session_state.remembered_user = ""
        st.success(f"Welcome back, {user['full_name']}! Redirecting to Dashboard...")
        time.sleep(0.4)
        st.rerun()
        return True
    else:
        st.error("Invalid username/email or password. Please verify your credentials.")
        return False

def logout_user():
    st.session_state.user = None
    st.session_state.current_session_id = None
    st.session_state.nav_target = None
    st.session_state.current_page = "Dashboard & Overview"
    if "sidebar_nav_radio" in st.session_state:
        st.session_state.sidebar_nav_radio = "Dashboard & Overview"
    st.rerun()

def get_or_create_session():
    if not st.session_state.current_session_id and st.session_state.user:
        sid = database.create_assessment_session(
            st.session_state.user["id"],
            st.session_state.target_domain
        )
        st.session_state.current_session_id = sid
    return st.session_state.current_session_id

# --- Navigation & Sidebar ---
if st.session_state.user:
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="margin: 0; color: #38bdf8;">🎯 AI Interviewer</h2>
        <span style="font-size: 12px; color: #94a3b8;">Skill Assessment Platform</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    logged_in_name = (st.session_state.user.get("full_name") or st.session_state.user.get("username") or "").strip()
    st.sidebar.markdown(f"**Logged in as:** `{logged_in_name}`")
    st.sidebar.caption(f"Role: {st.session_state.user['target_role']}")
    
    nav_options = [
        "Dashboard & Overview",
        "Round 1: Aptitude Test",
        "Round 2: HR Interview",
        "Round 3: Technical Interview",
        "Optional: Coding Sandbox",
        "Final Performance Report",
        "Candidate Profile & Settings"
    ]

    # Process any queued programmatic navigation target BEFORE widget instantiation
    if st.session_state.get("nav_target"):
        target = st.session_state.nav_target
        if target in nav_options:
            st.session_state.current_page = target
            st.session_state.sidebar_nav_radio = target
        st.session_state.nav_target = None

    # Ensure widget state is initialized before instantiation
    if "sidebar_nav_radio" not in st.session_state or st.session_state.sidebar_nav_radio not in nav_options:
        st.session_state.sidebar_nav_radio = st.session_state.get("current_page", "Dashboard & Overview")

    def on_sidebar_nav_change():
        st.session_state.current_page = st.session_state.sidebar_nav_radio

    nav_selection = st.sidebar.radio(
        "Navigation Menu",
        nav_options,
        key="sidebar_nav_radio",
        on_change=on_sidebar_nav_change
    )
    st.session_state.current_page = nav_selection

    st.sidebar.markdown("---")
    # Quick Status Summary in Sidebar
    sid = st.session_state.current_session_id
    st.sidebar.markdown("### Current Assessment")
    st.sidebar.caption(f"Domain: **{st.session_state.target_domain}**")
    st.sidebar.write(f"- Aptitude: {'Completed (' + str(st.session_state.aptitude_score) + '%)' if st.session_state.aptitude_submitted else 'Pending'}")
    st.sidebar.write(f"- HR Round: {'Completed' if st.session_state.hr_completed else 'In Progress'}")
    st.sidebar.write(f"- Technical: {'Completed' if st.session_state.tech_completed else 'In Progress'}")
    st.sidebar.write(f"- Coding: {'Completed (' + str(st.session_state.coding_score) + '%)' if st.session_state.coding_completed else 'Optional'}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out", use_container_width=True):
        logout_user()
else:
    nav_selection = "Authentication"

# =========================================================================
# PAGE 0: AUTHENTICATION (SINGLE-SCREEN CENTERED CARD)
# =========================================================================
if not st.session_state.user:
    # Hide sidebar completely on unauthenticated login view
    st.markdown("""
    <style>
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        @media (min-width: 768px) {
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
                max-width: 480px !important;
                min-width: 440px !important;
            }
        }
        @media (max-width: 767px) {
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
                display: none !important;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
                width: 100% !important;
                max-width: 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    col_spacer_l, col_center, col_spacer_r = st.columns([1, 1.4, 1])

    with col_center:
        with st.container(border=True):
            # -------------------------------------------------------------
            # 1. LOGIN INTERFACE
            # -------------------------------------------------------------
            if st.session_state.auth_mode == "login":
                if st.session_state.show_forgot_password:
                    # Top Section
                    st.markdown("""
                    <div style="text-align: center; margin-bottom: 22px;">
                        <div style="display: inline-flex; width: 54px; height: 54px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); border-radius: 14px; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37, 99, 235, 0.28); margin-bottom: 12px;">
                            <span style="font-size: 26px;">🎯</span>
                        </div>
                        <h1 style="font-size: 24px; font-weight: 700; color: #E53935; margin: 0 0 2px 0; letter-spacing: -0.4px;">AI Interviewer</h1>
                        <p style="font-size: 13px; font-weight: 600; color: #E53935; margin: 0 0 16px 0; letter-spacing: 0.6px; text-transform: uppercase;">Skill Assessment Platform</p>
                        <div style="height: 1px; background: #e2e8f0; margin: 0 auto 16px auto; width: 85%;"></div>
                        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 6px 0;">Reset your password</h2>
                        <p style="font-size: 14px; color: #64748b; margin: 0 0 4px 0;">Enter your registered email address along with your new password.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    reset_ident = st.text_input(
                        "Email Address *",
                        placeholder="Enter your email address",
                        key="reset_user_ident"
                    )

                    show_reset_pwd = st.checkbox("Show password", key="chk_show_reset_pwd")

                    reset_new_pwd = st.text_input(
                        "New Password *",
                        type="text" if show_reset_pwd else "password",
                        placeholder="Enter new password (min. 6 characters)",
                        key="reset_new_pwd"
                    )
                    reset_confirm_pwd = st.text_input(
                        "Confirm New Password *",
                        type="text" if show_reset_pwd else "password",
                        placeholder="Confirm new password",
                        key="reset_confirm_pwd"
                    )

                    if st.button("Reset Password", type="primary", use_container_width=True, key="btn_submit_reset"):
                        clean_ident = reset_ident.strip()
                        if not clean_ident or not reset_new_pwd or not reset_confirm_pwd:
                            st.warning("Please fill in all fields.")
                        elif "@" in clean_ident and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_ident):
                            st.warning("Please enter a valid email address.")
                        elif len(reset_new_pwd) < 6:
                            st.warning("Password must be at least 6 characters long.")
                        elif reset_new_pwd != reset_confirm_pwd:
                            st.error("Passwords do not match.")
                        else:
                            success, msg = database.reset_password(clean_ident, reset_new_pwd)
                            if success:
                                st.success(msg)
                                time.sleep(1.0)
                                st.session_state.show_forgot_password = False
                                st.rerun()
                            else:
                                st.error(msg)

                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                    if st.button("← Cancel & Return to Log In", key="btn_cancel_reset"):
                        st.session_state.show_forgot_password = False
                        st.rerun()

                else:
                    # Top Section
                    st.markdown("""
                    <div style="text-align: center; margin-bottom: 22px;">
                        <div style="display: inline-flex; width: 54px; height: 54px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); border-radius: 14px; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37, 99, 235, 0.28); margin-bottom: 12px;">
                            <span style="font-size: 26px;">🎯</span>
                        </div>
                        <h1 style="font-size: 24px; font-weight: 700; color: #E53935; margin: 0 0 2px 0; letter-spacing: -0.4px;">AI Interviewer</h1>
                        <p style="font-size: 13px; font-weight: 600; color: #E53935; margin: 0 0 16px 0; letter-spacing: 0.6px; text-transform: uppercase;">Skill Assessment Platform</p>
                        <div style="height: 1px; background: #e2e8f0; margin: 0 auto 12px auto; width: 85%;"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 1. Email Address label & input field
                    login_email = st.text_input(
                        "Email Address *",
                        placeholder="Enter your email address",
                        key="login_email_input"
                    )

                    # 2. Show/Hide Password eye toggle & Password input
                    show_pwd = st.checkbox("Show password", key="chk_login_show_pwd")
                    login_password = st.text_input(
                        "Password *",
                        type="text" if show_pwd else "password",
                        placeholder="Enter your password",
                        key="login_password_input"
                    )

                    # 3. Log In button
                    if st.button("Log In", type="primary", use_container_width=True, key="btn_login_submit"):
                        clean_email = login_email.strip()
                        if not clean_email or not login_password:
                            st.warning("Please enter both email address and password.")
                        elif "@" in clean_email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_email):
                            st.warning("Please enter a valid email address.")
                        else:
                            login_user(clean_email, login_password)

                    # 4. Spacing between Log in button and options
                    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

                    # 5. Forgot Password Section
                    col_fp1, col_fp2 = st.columns([1.15, 1])
                    with col_fp1:
                        st.markdown("<p style='text-align: right; color: #64748b; font-size: 14px; margin: 0; padding-top: 4px;'>Forgot your password?</p>", unsafe_allow_html=True)
                    with col_fp2:
                        if st.button("Reset your password", key="btn_forgot_password_link"):
                            st.session_state.show_forgot_password = True
                            st.rerun()

                    # 6. Spacing between Forgot Password and Sign Up
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                    # 7. Sign Up Section
                    col_su1, col_su2 = st.columns([1.15, 1])
                    with col_su1:
                        st.markdown("<p style='text-align: right; color: #64748b; font-size: 14px; margin: 0; padding-top: 4px;'>Don't have an account?</p>", unsafe_allow_html=True)
                    with col_su2:
                        if st.button("Sign Up", key="btn_signup_link"):
                            st.session_state.auth_mode = "signup"
                            st.rerun()

            # -------------------------------------------------------------
            # 2. SIGN UP INTERFACE
            # -------------------------------------------------------------
            elif st.session_state.auth_mode == "signup":
                # Top Section
                st.markdown("""
                <div style="text-align: center; margin-bottom: 22px;">
                    <div style="display: inline-flex; width: 54px; height: 54px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); border-radius: 14px; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37, 99, 235, 0.28); margin-bottom: 12px;">
                        <span style="font-size: 26px;">🎯</span>
                    </div>
                    <h1 style="font-size: 24px; font-weight: 700; color: #E53935; margin: 0 0 2px 0; letter-spacing: -0.4px;">AI Interviewer</h1>
                    <p style="font-size: 13px; font-weight: 600; color: #E53935; margin: 0 0 16px 0; letter-spacing: 0.6px; text-transform: uppercase;">Skill Assessment Platform</p>
                    <div style="height: 1px; background: #e2e8f0; margin: 0 auto 16px auto; width: 85%;"></div>
                    <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 6px 0;">Create an Account</h2>
                    <p style="font-size: 14px; color: #64748b; margin: 0 0 4px 0;">Sign up to begin your virtual AI interview assessment.</p>
                </div>
                """, unsafe_allow_html=True)

                su_full_name = st.text_input("Full Name *", placeholder="Enter your full name", key="su_fullname")
                su_email = st.text_input("Email Address *", placeholder="Enter your email address", key="su_email")
                su_username = st.text_input("Username *", placeholder="Choose a username", key="su_username")
                
                show_su_pwd = st.checkbox("Show password", key="chk_show_su_pwd")
                su_password = st.text_input(
                    "Password *",
                    type="text" if show_su_pwd else "password",
                    placeholder="Enter password (min. 6 characters)",
                    key="su_pwd"
                )
                su_confirm_password = st.text_input(
                    "Confirm Password *",
                    type="text" if show_su_pwd else "password",
                    placeholder="Confirm password",
                    key="su_confirm_pwd"
                )

                if st.button("Sign Up", type="primary", use_container_width=True, key="btn_execute_signup"):
                    clean_su_name = su_full_name.strip()
                    clean_su_email = su_email.strip()
                    clean_su_user = su_username.strip()

                    if not clean_su_name or not clean_su_email or not clean_su_user or not su_password or not su_confirm_password:
                        st.warning("All fields are required. Please fill in all fields.")
                    elif len(clean_su_name) < 2:
                        st.warning("Full Name must be at least 2 characters.")
                    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_su_email):
                        st.warning("Please enter a valid email address.")
                    elif len(clean_su_user) < 3:
                        st.warning("Username must be at least 3 characters long.")
                    elif len(su_password) < 6:
                        st.warning("Password must be at least 6 characters long.")
                    elif su_password != su_confirm_password:
                        st.error("Password and Confirm Password do not match.")
                    else:
                        exists, err_msg = database.check_user_exists(clean_su_user, clean_su_email)
                        if exists:
                            st.error(err_msg)
                        else:
                            success, uid, reg_msg = database.register_user(
                                username=clean_su_user,
                                password=su_password,
                                full_name=clean_su_name,
                                email=clean_su_email
                            )
                            if success:
                                st.success("Account registered successfully! Redirecting to dashboard...")
                                auto_user = database.authenticate_user(clean_su_user, su_password)
                                if auto_user:
                                    st.session_state.user = auto_user
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.session_state.auth_mode = "login"
                                    st.rerun()
                            else:
                                st.error(reg_msg)

                st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                col_r_login1, col_r_login2 = st.columns([1.15, 1])
                with col_r_login1:
                    st.markdown("<p style='text-align: right; color: #64748b; font-size: 14px; margin: 0; padding-top: 4px;'>Already have an account?</p>", unsafe_allow_html=True)
                with col_r_login2:
                    if st.button("Log In", key="btn_return_login"):
                        st.session_state.auth_mode = "login"
                        st.rerun()

    st.stop()

# =========================================================================
# PAGE 1: CANDIDATE DASHBOARD
# =========================================================================
elif nav_selection == "Dashboard & Overview":
    # 1. Welcome Section
    logged_in_name = (st.session_state.user.get("full_name") or st.session_state.user.get("username") or "").strip()
    welcome_message = f"Welcome Back, {logged_in_name}!" if logged_in_name else "Welcome Back!"
    st.markdown(f"<h2 style='font-size: 26px; font-weight: 700; color: #1e3a8a; margin: 0 0 24px 0;'>{welcome_message}</h2>", unsafe_allow_html=True)

    # 2. Configure Domain for This Session
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Configure Domain for This Session</div>
    </div>
    """, unsafe_allow_html=True)

    domain_options = list(ai_engine.TECHNICAL_DOMAINS.keys())
    current_domain_index = domain_options.index(st.session_state.target_domain) if st.session_state.target_domain in domain_options else 0

    selected_dom = st.selectbox(
        "Select Technical Domain for Round 3",
        domain_options,
        index=current_domain_index,
        key="select_domain_step2"
    )

    if st.button("Confirm Domain Selection", type="secondary", key="btn_confirm_domain_step2"):
        st.session_state.target_domain = selected_dom
        get_or_create_session()
        st.success(f"Domain set to: {selected_dom}")
    elif selected_dom != st.session_state.target_domain:
        st.session_state.target_domain = selected_dom
        get_or_create_session()

    # 3. Start Your Assessment
    st.markdown("<div class='dash-section-header'>Start Your Assessment</div>", unsafe_allow_html=True)

    # 4. Round 1: Aptitude Test
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Round 1: Aptitude Test</div>
        <div class='dash-card-desc'>
            Comprehensive quantitative ability, logical reasoning, and verbal comprehension test with automated objective evaluation.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Aptitude Test", type="primary", use_container_width=True, key="btn_start_round1"):
        st.session_state.target_domain = selected_dom
        get_or_create_session()
        navigate_to("Round 1: Aptitude Test")
        st.rerun()

    # 5. Round 2: HR Interview
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Round 2: HR Interview</div>
        <div class='dash-card-desc'>
            AI-driven behavioral assessment evaluating situational judgment, communication, STAR response methodology, and professional readiness.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start HR Interview", type="primary", use_container_width=True, key="btn_start_round2"):
        st.session_state.target_domain = selected_dom
        get_or_create_session()
        navigate_to("Round 2: HR Interview")
        st.rerun()

    # 6. Round 3: Technical Interview
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Round 3: Technical Interview</div>
        <div class='dash-card-desc'>
            In-depth domain examination featuring conceptual questions, architectural insights, and scenario troubleshooting tailored to your chosen technical domain.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Technical Interview", type="primary", use_container_width=True, key="btn_start_round3"):
        st.session_state.target_domain = selected_dom
        get_or_create_session()
        navigate_to("Round 3: Technical Interview")
        st.rerun()

    # 7. Optional Coding Sandbox
    st.markdown("<div class='dash-section-header'>Additional Features</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Optional Coding Sandbox</div>
        <div class='dash-card-desc'>
            Live interactive Python coding environment to solve algorithmic challenges against unit test suites.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Optional Coding Sandbox", type="secondary", use_container_width=True, key="btn_open_coding"):
        get_or_create_session()
        navigate_to("Optional: Coding Sandbox")
        st.rerun()

    # 8. Final Performance Report
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Final Performance Report</div>
        <div class='dash-card-desc'>
            Multi-round performance analytics, competence radar visualizations, identified candidate strengths, and structured 4-week study roadmap.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Final Performance Report", type="secondary", use_container_width=True, key="btn_open_report"):
        get_or_create_session()
        navigate_to("Final Performance Report")
        st.rerun()

    # 9. Candidate Profile & Settings
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-title'>Candidate Profile & Settings</div>
        <div class='dash-card-desc'>
            Manage personal profile information, target engineering roles, experience qualifications, and AI model configurations.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Candidate Profile & Settings", type="secondary", use_container_width=True, key="btn_open_profile"):
        navigate_to("Candidate Profile & Settings")
        st.rerun()

    # 10. Reset Current Assessment Session
    st.markdown("<div class='dash-section-header'>Reset Assessment Session</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='dash-card'>
        <div class='dash-card-desc'>
            Clear all active responses, round scores, and current interview progress to begin a fresh assessment session.
        </div>
    </div>
    """, unsafe_allow_html=True)

    confirm_reset = st.checkbox("Confirm resetting the current assessment session", key="chk_confirm_reset_dashboard")
    if st.button("Reset Current Assessment Session", type="secondary", use_container_width=True, key="btn_reset_session_dash"):
        if not confirm_reset:
            st.warning("Please check the confirmation box above before resetting the session.")
        else:
            st.session_state.current_session_id = None
            st.session_state.aptitude_questions = []
            st.session_state.aptitude_answers = {}
            st.session_state.aptitude_submitted = False
            st.session_state.aptitude_score = 0.0
            st.session_state.hr_question_idx = 0
            st.session_state.hr_scores = []
            st.session_state.hr_completed = False
            st.session_state.tech_question_idx = 0
            st.session_state.tech_scores = []
            st.session_state.tech_completed = False
            st.session_state.coding_score = 0.0
            st.session_state.coding_completed = False
            st.success("Assessment session has been reset successfully.")
            time.sleep(0.5)
            st.rerun()

# =========================================================================
# PAGE 2: ROUND 1 - APTITUDE TEST
# =========================================================================
elif nav_selection == "Round 1: Aptitude Test":
    st.markdown("""
    <div class="main-header">
        <h1>Round 1: General & Technical Aptitude Test</h1>
        <p>Evaluates Quantitative Aptitude, Logical Reasoning, and Verbal Ability through automated objective scoring.</p>
    </div>
    """, unsafe_allow_html=True)

    session_id = get_or_create_session()

    if not st.session_state.aptitude_questions:
        st.session_state.aptitude_questions = database.get_aptitude_questions(limit_per_category=4)

    questions = st.session_state.aptitude_questions

    if not st.session_state.aptitude_submitted:
        st.info("**Instructions:** Answer all 12 questions below covering Quantitative, Logical, and Verbal topics. Click **Submit Test** when finished to receive instant scoring and step-by-step explanations.")

        # Test Form
        with st.form("aptitude_exam_form"):
            for idx, q in enumerate(questions, 1):
                st.markdown(f"#### Q{idx}. [{q['category']} • {q['difficulty']}]")
                st.write(q["question_text"])

                options = [
                    f"A) {q['option_a']}",
                    f"B) {q['option_b']}",
                    f"C) {q['option_c']}",
                    f"D) {q['option_d']}"
                ]

                existing_choice = st.session_state.aptitude_answers.get(q["id"], None)
                def_index = None
                if existing_choice:
                    for i, opt in enumerate(["A", "B", "C", "D"]):
                        if existing_choice == opt:
                            def_index = i

                selected = st.radio(
                    f"Select Answer for Q{idx}:",
                    options,
                    index=def_index,
                    key=f"q_{q['id']}"
                )
                if selected:
                    chosen_opt = selected.split(")")[0]
                    st.session_state.aptitude_answers[q["id"]] = chosen_opt

                st.markdown("---")

            submit_test = st.form_submit_button("Submit Aptitude Test", type="primary")

        if submit_test:
            correct_count = 0
            for q in questions:
                user_ans = st.session_state.aptitude_answers.get(q["id"])
                if user_ans == q["correct_option"]:
                    correct_count += 1

            total = len(questions)
            pct = round((correct_count / total) * 100.0, 1)
            st.session_state.aptitude_score = pct
            st.session_state.aptitude_submitted = True

            # Update database
            database.update_session_scores(session_id, aptitude_score=pct)
            st.success(f"Assessment Submitted! Score: {correct_count}/{total} ({pct}%)")
            st.rerun()

    else:
        # Results & Review View
        total = len(questions)
        correct_count = sum(1 for q in questions if st.session_state.aptitude_answers.get(q["id"]) == q["correct_option"])
        score_pct = st.session_state.aptitude_score

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Questions", total)
        with col2:
            st.metric("Correct Answers", f"{correct_count} / {total}")
        with col3:
            st.metric("Aptitude Score", f"{score_pct}%")

        if score_pct >= 60:
            st.success(f"🎉 Congratulations! You have successfully cleared the Round 1 Aptitude Cutoff (Cutoff: 60%).")
        else:
            st.warning(f"⚠️ Your score of {score_pct}% is below the typical 60% campus placement cutoff. Review the explanations below to improve.")

        st.markdown("### 🔍 Answer Key & Detailed Mathematical Explanations")
        for idx, q in enumerate(questions, 1):
            user_ans = st.session_state.aptitude_answers.get(q["id"], "Not Answered")
            is_correct = user_ans == q["correct_option"]

            status_icon = "✅" if is_correct else "❌"
            color_border = "#10b981" if is_correct else "#ef4444"

            st.markdown(f"""
            <div style="background: #1e293b; border-left: 4px solid {color_border}; padding: 14px 18px; border-radius: 8px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #f8fafc;">{status_icon} Q{idx}. [{q['category']}] {q['question_text']}</div>
                <div style="margin: 6px 0; font-size: 13px; color: #cbd5e1;">
                    Your Answer: <strong>{user_ans}</strong> | Correct Answer: <strong style="color: #38bdf8;">{q['correct_option']}</strong>
                </div>
                <div style="background: #0f172a; padding: 10px 14px; border-radius: 6px; font-size: 13px; color: #94a3b8; margin-top: 8px;">
                    <strong>Explanation:</strong> {q['explanation']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Retake Aptitude Test"):
            st.session_state.aptitude_questions = database.get_aptitude_questions(limit_per_category=4)
            st.session_state.aptitude_answers = {}
            st.session_state.aptitude_submitted = False
            st.session_state.aptitude_score = 0.0
            st.rerun()

# =========================================================================
# PAGE 3: ROUND 2 - HR INTERVIEW
# =========================================================================
elif nav_selection == "Round 2: HR Interview":
    st.markdown("""
    <div class="main-header">
        <h1>Round 2: AI-Powered HR & Behavioral Interview</h1>
        <p>Interactive interview evaluating communication skills, STAR methodology, confidence, and culture fit with real-time audio playback & speech transcription.</p>
    </div>
    """, unsafe_allow_html=True)

    session_id = get_or_create_session()
    candidate_profile = {
        "id": st.session_state.user.get("id"),
        "full_name": (st.session_state.user.get("full_name") or st.session_state.user.get("username") or "Candidate").strip(),
        "username": st.session_state.user.get("username", "candidate"),
        "target_role": st.session_state.user.get("target_role", "Software Engineer"),
        "experience_level": st.session_state.user.get("experience_level", "Fresher"),
        "primary_skills": st.session_state.user.get("primary_skills", "Python, SQL"),
        "bio": st.session_state.user.get("bio", "")
    }

    # Synchronize answered question count from database transcripts
    transcripts = database.get_session_transcripts(session_id)
    hr_transcripts = [t for t in transcripts if t["round_type"] == "HR"]
    answered_count = len(hr_transcripts)
    st.session_state.hr_question_idx = answered_count

    # Load persistent questions for this session or dynamically generate 5 unique questions
    hr_questions = hr_api.get_or_load_hr_questions(
        session_id=session_id,
        candidate_profile=candidate_profile,
        api_key=st.session_state.gemini_api_key
    )
    total_hr = len(hr_questions) if hr_questions else 5

    # Show progress bar with clean indicators
    progress_val = min(1.0, answered_count / total_hr)
    st.progress(
        progress_val,
        text=f"Interview Round: HR Interview • Progress: Question {min(answered_count + 1, total_hr)} of {total_hr}"
    )

    # Display prior conversation transcripts
    if hr_transcripts:
        st.markdown("### 💬 Interview Transcript History")
        candidate_name = candidate_profile["full_name"]
        for item in hr_transcripts:
            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer (Question {item['question_num']})</div>
                    <div class="chat-text-content">{item['question_text']}</div>
                </div>
            </div>
            <div class="chat-msg-row-candidate">
                <div class="chat-bubble-candidate">
                    <div class="chat-speaker-label speaker-candidate">{candidate_name}</div>
                    <div class="chat-text-content">{item['candidate_answer']}</div>
                </div>
            </div>
            <div class="chat-msg-row-ai">
                <div class="feedback-box">
                    <div style="font-weight: 600; color: #10b981; margin-bottom: 4px; text-align: left;">AI Evaluation Score: {item['score']}/10</div>
                    <div style="font-size: 13.5px; color: #cbd5e1; line-height: 1.5; text-align: left;">{item['feedback']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # If all 5 HR questions completed
    if answered_count >= total_hr:
        st.session_state.hr_completed = True
        scores = [t["score"] for t in hr_transcripts if t.get("score") is not None]
        avg_score = round(sum(scores) / len(scores) * 10.0, 1) if scores else 75.0
        database.update_session_scores(session_id, hr_score=avg_score)

        st.success(f"🎉 HR Interview Round Completed! Your Average HR Score is {avg_score}%.")
        st.info("You can now proceed to **Round 3: Technical Interview** from the sidebar.")

        col_next_r, col_restart = st.columns([1, 1])
        with col_next_r:
            if st.button("Proceed to Round 3: Technical Interview", type="primary", use_container_width=True):
                navigate_to("Round 3: Technical Interview")
                st.rerun()

        with col_restart:
            if st.button("🔄 Start a New HR Interview Session", use_container_width=True):
                new_session_id = database.create_fresh_assessment_session(
                    st.session_state.user["id"],
                    st.session_state.target_domain
                )
                st.session_state.current_session_id = new_session_id
                st.session_state.hr_question_idx = 0
                st.session_state.hr_scores = []
                st.session_state.hr_completed = False

                # Generate fresh dynamic question set for the new session
                hr_api.start_hr_session(
                    user_id=st.session_state.user["id"],
                    target_domain=st.session_state.target_domain,
                    candidate_profile=candidate_profile,
                    api_key=st.session_state.gemini_api_key
                )
                st.rerun()

    else:
        curr_q = hr_questions[answered_count]

        st.markdown(f"### Current Question: Question {answered_count + 1} of {total_hr} • {curr_q['category']}")
        st.markdown(f"""
        <div class="chat-msg-row-ai">
            <div class="chat-bubble-ai" style="max-width: 100%; width: 100%; border-left: 5px solid #3b82f6;">
                <div class="chat-speaker-label speaker-ai">AI Interviewer • Question {answered_count + 1} ({curr_q['category']})</div>
                <div class="chat-text-content" style="font-size: 16px; font-weight: 500;">"{curr_q['question_text']}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TTS: Listen out loud
        speech_helper.render_tts_player(curr_q['question_text'], element_id=f"hr_q_{session_id}_{answered_count + 1}")

        # STT: Mic Voice Helper
        st.markdown("##### 🎙️ Voice Assistant (Optional Microphone Input)")
        speech_helper.render_stt_mic_helper()

        # Candidate Answer Input
        candidate_ans = st.text_area(
            "Your Spoken or Typed Response:",
            height=130,
            placeholder="Structure your answer using the STAR method: Situation, Task, Action you took, and final Result...",
            key=f"hr_input_{session_id}_{answered_count}"
        )

        col_sub, col_reset = st.columns([1, 4])
        with col_sub:
            if st.button("Submit & Next Question", type="primary", key=f"btn_sub_hr_{session_id}_{answered_count}"):
                if not candidate_ans or len(candidate_ans.strip()) < 10:
                    st.warning("Please provide a more descriptive answer before submitting.")
                else:
                    with st.spinner("AI evaluating communication, behavioral markers, and sentiment..."):
                        submit_res = hr_api.submit_hr_answer(
                            session_id=session_id,
                            question_num=answered_count + 1,
                            question_text=curr_q["question_text"],
                            candidate_answer=candidate_ans,
                            candidate_profile=candidate_profile,
                            api_key=st.session_state.gemini_api_key
                        )
                        st.session_state.hr_scores.append(submit_res["score"])
                        st.session_state.hr_question_idx += 1
                        st.rerun()

# =========================================================================
# PAGE 4: ROUND 3 - TECHNICAL INTERVIEW
# =========================================================================
elif nav_selection == "Round 3: Technical Interview":
    st.markdown("""
    <div class="main-header">
        <h1>Round 3: Technical & Practical Coding Interview</h1>
        <p>Enterprise technical evaluation combining programming fundamentals, live coding, data structures, SQL databases, and project architecture defense.</p>
    </div>
    """, unsafe_allow_html=True)

    session_id = get_or_create_session()
    candidate_name = (st.session_state.user.get("full_name") or st.session_state.user.get("username") or "Candidate").strip()

    # Define Technical Interview Sections
    tech_stages = [
        "1. Programming Fundamentals",
        "2. Live Coding Assessment",
        "3. Data Structures & Algorithms",
        "4. Database & SQL Practical",
        "5. Project Architecture & Defense"
    ]

    active_stage_idx = tech_stages.index(st.session_state.tech_active_stage) if st.session_state.tech_active_stage in tech_stages else 0
    selected_stage = st.radio(
        "Select Interview Stage",
        tech_stages,
        index=active_stage_idx,
        key="tech_stage_radio_selector",
        horizontal=True
    )
    st.session_state.tech_active_stage = selected_stage

    # Stage Progress Calculation
    transcripts = database.get_session_transcripts(session_id)
    tech_transcripts = [t for t in transcripts if t["round_type"] == "Technical"]
    
    fund_bank = getattr(ai_engine, "PROGRAMMING_FUNDAMENTALS_QUESTIONS", [])
    coding_bank = getattr(ai_engine, "LIVE_CODING_QUESTIONS", getattr(ai_engine, "CODING_CHALLENGES", []))
    dsa_bank = getattr(ai_engine, "DATA_STRUCTURES_QUESTIONS", getattr(ai_engine, "DSA_QUESTIONS", []))
    sql_bank = getattr(ai_engine, "DATABASE_SQL_QUESTIONS", getattr(ai_engine, "SQL_CHALLENGES", []))
    proj_bank = getattr(ai_engine, "PROJECT_ARCHITECTURE_QUESTIONS", getattr(ai_engine, "PROJECT_QUESTIONS", []))

    total_tech_steps = len(fund_bank) + len(coding_bank) + len(dsa_bank) + len(sql_bank) + len(proj_bank)
    completed_tech_count = min(total_tech_steps, len(tech_transcripts))
    st.progress(
        completed_tech_count / total_tech_steps if total_tech_steps > 0 else 0.0,
        text=f"Overall Technical Round Progress: {completed_tech_count} of {total_tech_steps} assessments completed ({int((completed_tech_count / total_tech_steps) * 100) if total_tech_steps > 0 else 0}%)"
    )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # STAGE 1: PROGRAMMING FUNDAMENTALS & OOP
    # -------------------------------------------------------------------------
    if selected_stage == "1. Programming Fundamentals":
        fund_questions = getattr(ai_engine, "PROGRAMMING_FUNDAMENTALS_QUESTIONS", [])
        total_fund = len(fund_questions)
        if total_fund == 0:
            st.info("No programming fundamentals questions currently configured.")
        else:
            curr_fund_idx = max(0, min(st.session_state.tech_fund_idx, total_fund - 1))
            curr_q = fund_questions[curr_fund_idx]

            col_nav_l, col_nav_mid, col_nav_r = st.columns([1, 2, 1])
            with col_nav_l:
                if st.button("Previous Question", key="fund_btn_prev", disabled=(curr_fund_idx == 0)):
                    st.session_state.tech_fund_idx = max(0, curr_fund_idx - 1)
                    st.rerun()
            with col_nav_mid:
                st.markdown(f"<p style='text-align: center; font-weight: 600; color: #94a3b8; margin: 6px 0;'>Question {curr_fund_idx + 1} of {total_fund} • {curr_q.get('topic') or curr_q.get('category', 'Fundamentals')}</p>", unsafe_allow_html=True)
            with col_nav_r:
                if st.button("Next Question", key="fund_btn_next", disabled=(curr_fund_idx == total_fund - 1)):
                    st.session_state.tech_fund_idx = min(total_fund - 1, curr_fund_idx + 1)
                    st.rerun()

            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai" style="max-width: 100%; width: 100%; border-left: 5px solid #3b82f6;">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer • Fundamentals Question {curr_fund_idx + 1} ({curr_q.get('topic') or curr_q.get('category', 'Fundamentals')})</div>
                    <div class="chat-text-content" style="font-size: 16px; font-weight: 500;">{curr_q['question']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            speech_helper.render_tts_player(curr_q['question'], element_id=f"fund_q_{curr_q['id']}")
            speech_helper.render_stt_mic_helper()

            fund_ans = st.text_area(
                "Your Technical Explanation:",
                height=140,
                placeholder="Explain the underlying mechanics, syntax differences, mutability/scope rules, and industry best practices...",
                key=f"fund_ans_input_{curr_q['id']}"
            )

            if st.button("Submit Explanation", type="primary", key=f"btn_sub_fund_{curr_q['id']}"):
                if not fund_ans or len(fund_ans.strip()) < 10:
                    st.warning("Please provide a thorough technical explanation.")
                else:
                    with st.spinner("AI evaluating technical precision, terminology, and concept depth..."):
                        eval_res = ai_engine.evaluate_technical_round(
                            stage="Fundamentals",
                            question=curr_q["question"],
                            answer=fund_ans,
                            api_key=st.session_state.gemini_api_key
                        )
                        category_name = curr_q.get('topic') or curr_q.get('category', 'Fundamentals')
                        database.record_transcript_entry(
                            session_id=session_id,
                            round_type="Technical",
                            question_num=curr_fund_idx + 1,
                            question_text=f"[Fundamentals: {category_name}] {curr_q['question']}",
                            candidate_answer=fund_ans,
                            feedback=eval_res["feedback"],
                            score=eval_res["score"]
                        )
                        st.session_state.tech_scores.append(eval_res["score"])
                        avg_score = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1)
                        database.update_session_scores(session_id, technical_score=avg_score)
                        st.success(f"Response evaluated! Score: {eval_res['score']}/10")
                        if curr_fund_idx < total_fund - 1:
                            st.session_state.tech_fund_idx += 1
                        st.rerun()

    # -------------------------------------------------------------------------
    # STAGE 2: LIVE CODING ASSESSMENT
    # -------------------------------------------------------------------------
    elif selected_stage == "2. Live Coding Assessment":
        coding_challenges = getattr(ai_engine, "LIVE_CODING_QUESTIONS", getattr(ai_engine, "CODING_CHALLENGES", []))
        total_challenges = len(coding_challenges)
        if total_challenges == 0:
            st.info("No live coding challenges currently configured.")
        else:
            curr_code_idx = max(0, min(st.session_state.tech_code_idx, total_challenges - 1))
            curr_challenge = coding_challenges[curr_code_idx]

            col_c_prev, col_c_mid, col_c_next = st.columns([1, 2, 1])
            with col_c_prev:
                if st.button("Previous Challenge", key="code_btn_prev", disabled=(curr_code_idx == 0)):
                    st.session_state.tech_code_idx = max(0, curr_code_idx - 1)
                    st.session_state.tech_run_result = None
                    st.rerun()
            with col_c_mid:
                selected_ch_title = st.selectbox(
                    "Select Problem",
                    [f"{i+1}. {c['title']} ({c['difficulty']})" for i, c in enumerate(coding_challenges)],
                    index=curr_code_idx,
                    key="code_ch_select",
                    label_visibility="collapsed"
                )
                new_idx = int(selected_ch_title.split(".")[0]) - 1
                if new_idx != curr_code_idx:
                    st.session_state.tech_code_idx = new_idx
                    st.session_state.tech_run_result = None
                    st.rerun()
            with col_c_next:
                if st.button("Next Challenge", key="code_btn_next", disabled=(curr_code_idx == total_challenges - 1)):
                    st.session_state.tech_code_idx = min(total_challenges - 1, curr_code_idx + 1)
                    st.session_state.tech_run_result = None
                    st.rerun()

            st.markdown(f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-left: 5px solid #10b981; border-radius: 10px; padding: 20px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 19px; font-weight: 700; color: #f8fafc;">{curr_challenge['title']}</span>
                    <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{curr_challenge['difficulty']}</span>
                </div>
                <p style="color: #cbd5e1; font-size: 14.5px; line-height: 1.6; margin: 8px 0 14px 0;">{curr_challenge['description']}</p>
                <div style="display: flex; gap: 20px; font-size: 13px; color: #94a3b8; margin-bottom: 12px;">
                    <span><strong>Target Time Complexity:</strong> <code>{curr_challenge.get('time_complexity', 'O(N)')}</code></span>
                    <span><strong>Target Space Complexity:</strong> <code>{curr_challenge.get('space_complexity', 'O(1)')}</code></span>
                </div>
                <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 220px; background: #0f172a; padding: 10px 14px; border-radius: 6px; font-size: 13px;">
                        <span style="color: #64748b; font-weight: 600;">Sample Input:</span><br>
                        <code style="color: #38bdf8;">{curr_challenge['sample_input']}</code>
                    </div>
                    <div style="flex: 1; min-width: 220px; background: #0f172a; padding: 10px 14px; border-radius: 6px; font-size: 13px;">
                        <span style="color: #64748b; font-weight: 600;">Expected Output:</span><br>
                        <code style="color: #34d399;">{curr_challenge['sample_output']}</code>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_lang, col_space = st.columns([1, 3])
            with col_lang:
                selected_lang = st.selectbox(
                    "Programming Language:",
                    ["Python", "Java", "C", "C++"],
                    index=["Python", "Java", "C", "C++"].index(st.session_state.tech_code_lang),
                    key=f"lang_select_{curr_challenge['id']}"
                )
                st.session_state.tech_code_lang = selected_lang

            starter_code = curr_challenge["starter_codes"].get(selected_lang, "")
            code_key = f"code_editor_{curr_challenge['id']}_{selected_lang}"
            if code_key not in st.session_state:
                st.session_state[code_key] = starter_code

            candidate_code = st.text_area(
                f"Code Editor ({selected_lang}):",
                value=st.session_state[code_key],
                height=260,
                key=code_key
            )

            col_btn_run, col_btn_sub = st.columns([1, 1])
            with col_btn_run:
                if st.button("Run Code", type="secondary", use_container_width=True, key=f"btn_run_{curr_challenge['id']}"):
                    with st.spinner(f"Compiling and running {selected_lang} code against sample test cases..."):
                        run_res = coding_runner.execute_candidate_solution(
                            challenge=curr_challenge,
                            code_str=candidate_code,
                            language=selected_lang,
                            run_only_samples=True
                        )
                        st.session_state.tech_run_result = run_res

            with col_btn_sub:
                if st.button("Submit Code", type="primary", use_container_width=True, key=f"btn_sub_{curr_challenge['id']}"):
                    with st.spinner(f"Evaluating {selected_lang} submission against comprehensive test suite in isolated runner..."):
                        eval_res = coding_runner.execute_candidate_solution(
                            challenge=curr_challenge,
                            code_str=candidate_code,
                            language=selected_lang,
                            run_only_samples=False
                        )
                        st.session_state.tech_run_result = eval_res
                        score = eval_res["score"]
                        st.session_state.coding_score = score
                        st.session_state.coding_completed = True

                        database.record_transcript_entry(
                            session_id=session_id,
                            round_type="Technical",
                            question_num=curr_code_idx + 1,
                            question_text=f"[Live Coding: {selected_lang}] {curr_challenge['title']}",
                            candidate_answer=f"```{selected_lang.lower()}\n{candidate_code}\n```",
                            feedback=f"Passed {eval_res['passed']} of {eval_res['total']} test cases ({score}%). Status: {eval_res['status']}.",
                            score=round(score / 10.0, 1)
                        )
                        st.session_state.tech_scores.append(round(score / 10.0, 1))
                        avg_score = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1)
                        database.update_session_scores(session_id, technical_score=avg_score, coding_score=score)
                        if score == 100.0:
                            st.success(f"All {eval_res['total']} Test Cases Passed! Submission recorded (100%).")
                        else:
                            st.warning(f"Submitted! Passed {eval_res['passed']} of {eval_res['total']} Test Cases. Score: {score}%.")

            if st.session_state.tech_run_result:
                res = st.session_state.tech_run_result
                status = res.get("status", "Unknown")
                status_color = "#10b981" if status == "Success" else ("#f59e0b" if status == "Wrong Answer" else "#ef4444")

                st.markdown(f"""
                <div style="margin-top: 18px;">
                    <div class="tech-console-header">
                        <span>Console Output & Test Suite</span>
                        <span style="color: {status_color}; font-weight: 700;">Status: {status.upper()} ({res.get('passed', 0)}/{res.get('total', 0)} Passed)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if res.get("error"):
                    st.error(f"Error Diagnostic:\n{res['error']}")

                if res.get("details"):
                    st.markdown("##### Test Case Breakdown:")
                    tc_data = []
                    for d in res["details"]:
                        tc_data.append({
                            "Test Case": f"Case {d['test_case']}",
                            "Input": d["input"],
                            "Expected Output": d["expected"],
                            "Actual Output": d["actual"],
                            "Result": "Passed" if d["passed"] else "Failed"
                        })
                    st.dataframe(pd.DataFrame(tc_data), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # STAGE 3: DATA STRUCTURES & ALGORITHMS
    # -------------------------------------------------------------------------
    elif selected_stage == "3. Data Structures & Algorithms":
        dsa_questions = getattr(ai_engine, "DATA_STRUCTURES_QUESTIONS", getattr(ai_engine, "DSA_QUESTIONS", []))
        total_dsa = len(dsa_questions)
        if total_dsa == 0:
            st.info("No data structures & algorithms questions currently configured.")
        else:
            curr_dsa_idx = max(0, min(st.session_state.tech_dsa_idx, total_dsa - 1))
            curr_q = dsa_questions[curr_dsa_idx]

            col_d_prev, col_d_mid, col_d_next = st.columns([1, 2, 1])
            with col_d_prev:
                if st.button("Previous Question", key="dsa_btn_prev", disabled=(curr_dsa_idx == 0)):
                    st.session_state.tech_dsa_idx = max(0, curr_dsa_idx - 1)
                    st.rerun()
            with col_d_mid:
                st.markdown(f"<p style='text-align: center; font-weight: 600; color: #94a3b8; margin: 6px 0;'>DSA Question {curr_dsa_idx + 1} of {total_dsa} • {curr_q.get('topic') or curr_q.get('category', 'DSA')}</p>", unsafe_allow_html=True)
            with col_d_next:
                if st.button("Next Question", key="dsa_btn_next", disabled=(curr_dsa_idx == total_dsa - 1)):
                    st.session_state.tech_dsa_idx = min(total_dsa - 1, curr_dsa_idx + 1)
                    st.rerun()

            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai" style="max-width: 100%; width: 100%; border-left: 5px solid #8b5cf6;">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer • DSA Question {curr_dsa_idx + 1} ({curr_q.get('topic') or curr_q.get('category', 'DSA')})</div>
                    <div class="chat-text-content" style="font-size: 16px; font-weight: 500;">{curr_q['question']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            speech_helper.render_tts_player(curr_q['question'], element_id=f"dsa_q_{curr_q['id']}")
            speech_helper.render_stt_mic_helper()

            dsa_ans = st.text_area(
                "Your Algorithmic & Complexity Analysis:",
                height=140,
                placeholder="Explain the data structure design, traversal/search mechanics, and state both Time and Space complexity in Big-O notation...",
                key=f"dsa_ans_input_{curr_q['id']}"
            )

            if st.button("Submit Algorithmic Answer", type="primary", key=f"btn_sub_dsa_{curr_q['id']}"):
                if not dsa_ans or len(dsa_ans.strip()) < 10:
                    st.warning("Please provide a thorough algorithmic explanation.")
                else:
                    with st.spinner("AI evaluating algorithmic correctness, time/space complexity, and logic..."):
                        eval_res = ai_engine.evaluate_technical_round(
                            stage="DSA",
                            question=curr_q["question"],
                            answer=dsa_ans,
                            api_key=st.session_state.gemini_api_key
                        )
                        category_name = curr_q.get('topic') or curr_q.get('category', 'DSA')
                        database.record_transcript_entry(
                            session_id=session_id,
                            round_type="Technical",
                            question_num=curr_dsa_idx + 1,
                            question_text=f"[DSA: {category_name}] {curr_q['question']}",
                            candidate_answer=dsa_ans,
                            feedback=eval_res["feedback"],
                            score=eval_res["score"]
                        )
                        st.session_state.tech_scores.append(eval_res["score"])
                        avg_score = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1)
                        database.update_session_scores(session_id, technical_score=avg_score)
                        st.success(f"Response evaluated! Score: {eval_res['score']}/10")
                        if curr_dsa_idx < total_dsa - 1:
                            st.session_state.tech_dsa_idx += 1
                        st.rerun()

    # -------------------------------------------------------------------------
    # STAGE 4: DATABASE & SQL PRACTICAL
    # -------------------------------------------------------------------------
    elif selected_stage == "4. Database & SQL Practical":
        sql_challenges = getattr(ai_engine, "DATABASE_SQL_QUESTIONS", getattr(ai_engine, "SQL_CHALLENGES", []))
        total_sql = len(sql_challenges)
        if total_sql == 0:
            st.info("No database & SQL challenges currently configured.")
        else:
            curr_sql_idx = max(0, min(st.session_state.tech_sql_idx, total_sql - 1))
            curr_sql = sql_challenges[curr_sql_idx]

            st.markdown("""
            <div class="tech-schema-box">
                <strong>Relational Database Schema Reference:</strong><br>
                • <code>departments (id INT PK, name TEXT, location TEXT)</code><br>
                • <code>employees (id INT PK, name TEXT, department_id INT FK, role TEXT, salary INT, hire_year INT)</code><br>
                • <code>projects (id INT PK, title TEXT, department_id INT FK, budget INT, status TEXT)</code>
            </div>
            """, unsafe_allow_html=True)

            col_s_prev, col_s_mid, col_s_next = st.columns([1, 2, 1])
            with col_s_prev:
                if st.button("Previous SQL Task", key="sql_btn_prev", disabled=(curr_sql_idx == 0)):
                    st.session_state.tech_sql_idx = max(0, curr_sql_idx - 1)
                    st.session_state.sql_run_result = None
                    st.rerun()
            with col_s_mid:
                st.markdown(f"<p style='text-align: center; font-weight: 600; color: #94a3b8; margin: 6px 0;'>SQL Challenge {curr_sql_idx + 1} of {total_sql}: {curr_sql['title']}</p>", unsafe_allow_html=True)
            with col_s_next:
                if st.button("Next SQL Task", key="sql_btn_next", disabled=(curr_sql_idx == total_sql - 1)):
                    st.session_state.tech_sql_idx = min(total_sql - 1, curr_sql_idx + 1)
                    st.session_state.sql_run_result = None
                    st.rerun()

            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai" style="max-width: 100%; width: 100%; border-left: 5px solid #06b6d4;">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer • SQL Task {curr_sql_idx + 1} ({curr_sql['title']})</div>
                    <div class="chat-text-content" style="font-size: 15.5px; font-weight: 500;">{curr_sql['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sql_key = f"sql_editor_{curr_sql['id']}"
            if sql_key not in st.session_state:
                st.session_state[sql_key] = curr_sql["starter_code"]

            candidate_sql = st.text_area(
                "SQL Query Editor:",
                value=st.session_state[sql_key],
                height=120,
                key=sql_key
            )

            col_s_run, col_s_sub = st.columns([1, 1])
            with col_s_run:
                if st.button("Execute Query", type="secondary", use_container_width=True, key=f"btn_run_sql_{curr_sql['id']}"):
                    with st.spinner("Executing query on isolated in-memory relational database..."):
                        sql_res = coding_runner.execute_sql_query(candidate_sql, curr_sql["expected_query"])
                        st.session_state.sql_run_result = sql_res

            with col_s_sub:
                if st.button("Submit SQL Answer", type="primary", use_container_width=True, key=f"btn_sub_sql_{curr_sql['id']}"):
                    with st.spinner("Validating SQL query and evaluating database competence..."):
                        sql_res = coding_runner.execute_sql_query(candidate_sql, curr_sql["expected_query"])
                        st.session_state.sql_run_result = sql_res
                        passed = sql_res["passed"]
                        score = 9.5 if passed else (5.0 if sql_res["status"] == "Success" else 2.0)

                        database.record_transcript_entry(
                            session_id=session_id,
                            round_type="Technical",
                            question_num=curr_sql_idx + 1,
                            question_text=f"[Database & SQL: {curr_sql['title']}] {curr_sql['description']}",
                            candidate_answer=f"```sql\n{candidate_sql}\n```",
                            feedback=sql_res["feedback"],
                            score=score
                        )
                        st.session_state.tech_scores.append(score)
                        avg_score = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1)
                        database.update_session_scores(session_id, technical_score=avg_score)
                        if passed:
                            st.success(f"Query matched expected dataset! Score: {score}/10")
                        else:
                            st.warning(f"Query executed with partial match. Score: {score}/10")

            if st.session_state.sql_run_result:
                res = st.session_state.sql_run_result
                if res.get("error"):
                    st.error(res["error"])
                else:
                    st.markdown(f"**Execution Output** ({res['row_count']} rows returned in {res.get('execution_time_ms', 0)} ms):")
                    df = pd.DataFrame(res["rows"], columns=res["columns"])
                    st.dataframe(df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # STAGE 5: PROJECT ARCHITECTURE & DEFENSE
    # -------------------------------------------------------------------------
    elif selected_stage == "5. Project Architecture & Defense":
        proj_questions = getattr(ai_engine, "PROJECT_ARCHITECTURE_QUESTIONS", getattr(ai_engine, "PROJECT_QUESTIONS", []))
        total_proj = len(proj_questions)
        if total_proj == 0:
            st.info("No project architecture questions currently configured.")
        else:
            curr_proj_idx = max(0, min(st.session_state.tech_proj_idx, total_proj - 1))
            curr_q = proj_questions[curr_proj_idx]

            col_p_prev, col_p_mid, col_p_next = st.columns([1, 2, 1])
            with col_p_prev:
                if st.button("Previous Question", key="proj_btn_prev", disabled=(curr_proj_idx == 0)):
                    st.session_state.tech_proj_idx = max(0, curr_proj_idx - 1)
                    st.rerun()
            with col_p_mid:
                st.markdown(f"<p style='text-align: center; font-weight: 600; color: #94a3b8; margin: 6px 0;'>Project Defense {curr_proj_idx + 1} of {total_proj} • {curr_q.get('topic') or curr_q.get('category', 'Project Defense')}</p>", unsafe_allow_html=True)
            with col_p_next:
                if st.button("Next Question", key="proj_btn_next", disabled=(curr_proj_idx == total_proj - 1)):
                    st.session_state.tech_proj_idx = min(total_proj - 1, curr_proj_idx + 1)
                    st.rerun()

            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai" style="max-width: 100%; width: 100%; border-left: 5px solid #f59e0b;">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer • Project Question {curr_proj_idx + 1} ({curr_q.get('topic') or curr_q.get('category', 'Project Defense')})</div>
                    <div class="chat-text-content" style="font-size: 16px; font-weight: 500;">{curr_q['question']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            speech_helper.render_tts_player(curr_q['question'], element_id=f"proj_q_{curr_q['id']}")
            speech_helper.render_stt_mic_helper()

            proj_ans = st.text_area(
                "Your Project Defense & Architectural Rationale:",
                height=140,
                placeholder="Describe your technical choices, schema design, API patterns, diagnostic debugging steps, and real-world trade-offs...",
                key=f"proj_ans_input_{curr_q['id']}"
            )

            if st.button("Submit Project Defense", type="primary", key=f"btn_sub_proj_{curr_q['id']}"):
                if not proj_ans or len(proj_ans.strip()) < 10:
                    st.warning("Please provide a thorough technical defense.")
                else:
                    with st.spinner("AI evaluating system architecture, database design, and project understanding..."):
                        eval_res = ai_engine.evaluate_technical_round(
                            stage="Project",
                            question=curr_q["question"],
                            answer=proj_ans,
                            api_key=st.session_state.gemini_api_key
                        )
                        category_name = curr_q.get('topic') or curr_q.get('category', 'Project Defense')
                        database.record_transcript_entry(
                            session_id=session_id,
                            round_type="Technical",
                            question_num=curr_proj_idx + 1,
                            question_text=f"[Project Defense: {category_name}] {curr_q['question']}",
                            candidate_answer=proj_ans,
                            feedback=eval_res["feedback"],
                            score=eval_res["score"]
                        )
                        st.session_state.tech_scores.append(eval_res["score"])
                        avg_score = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1)
                        database.update_session_scores(session_id, technical_score=avg_score)
                        st.success(f"Project defense evaluated! Score: {eval_res['score']}/10")
                    if curr_proj_idx < total_proj - 1:
                        st.session_state.tech_proj_idx += 1
                    st.rerun()

    # -------------------------------------------------------------------------
    # TRANSCRIPT HISTORY & ROUND SUMMARY
    # -------------------------------------------------------------------------
    if tech_transcripts:
        st.markdown("### Technical Interview Conversation History")
        for item in tech_transcripts:
            st.markdown(f"""
            <div class="chat-msg-row-ai">
                <div class="chat-bubble-ai">
                    <div class="chat-speaker-label speaker-ai">AI Interviewer (Question {item['question_num']})</div>
                    <div class="chat-text-content">{item['question_text']}</div>
                </div>
            </div>
            <div class="chat-msg-row-candidate">
                <div class="chat-bubble-candidate">
                    <div class="chat-speaker-label speaker-candidate">{candidate_name}</div>
                    <div class="chat-text-content">{item['candidate_answer']}</div>
                </div>
            </div>
            <div class="chat-msg-row-ai">
                <div class="feedback-box">
                    <div style="font-weight: 600; color: #3b82f6; margin-bottom: 4px; text-align: left;">Technical Accuracy Score: {item['score']}/10</div>
                    <div style="font-size: 13.5px; color: #cbd5e1; line-height: 1.5; text-align: left;">{item['feedback']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================================
# PAGE 5: OPTIONAL TECHNICAL COMPONENT - CODING SANDBOX
# =========================================================================
elif nav_selection == "Optional: Coding Sandbox":
    st.markdown("""
    <div class="main-header">
        <h1>Optional Technical Component: Live Coding Challenge</h1>
        <p>Interactive multi-language code editor and unit-testing sandbox evaluating algorithmic problem solving.</p>
    </div>
    """, unsafe_allow_html=True)

    session_id = get_or_create_session()
    challenges = getattr(ai_engine, "LIVE_CODING_QUESTIONS", getattr(ai_engine, "CODING_CHALLENGES", []))

    if not challenges:
        st.info("No coding challenges currently configured.")
    else:
        selected_challenge_title = st.selectbox("Select Challenge:", [c["title"] for c in challenges])
        active_challenge = next((c for c in challenges if c["title"] == selected_challenge_title), challenges[0])

        st.markdown(f"### {active_challenge['title']} `[{active_challenge['difficulty']}]`")
        st.markdown(f"""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #38bdf8;">
            {active_challenge['description']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Sample Test Cases:")
        for i, tc in enumerate(active_challenge["test_cases"][:2], 1):
            st.code(f"Input: {tc['input']}  -->  Expected Output: {tc['expected']}", language="python")

        starter_py = active_challenge.get("starter_codes", {}).get("Python", active_challenge.get("starter_code", ""))
        code_solution = st.text_area(
            "Python Solution Editor:",
            value=starter_py,
            height=200,
            key=f"sandbox_code_{active_challenge['id']}"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            run_code = st.button("Run & Evaluate Code", type="primary")

        if run_code:
            with st.spinner("Executing solution against test cases in sandbox..."):
                exec_res = coding_runner.execute_candidate_solution(active_challenge, code_solution, language="Python", run_only_samples=False)

                if exec_res.get("error"):
                    st.error(f"Execution Error: {exec_res['error']}")
                else:
                    score = exec_res["score"]
                    st.session_state.coding_score = score
                    st.session_state.coding_completed = True
                    database.update_session_scores(session_id, coding_score=score)

                    if score == 100.0:
                        st.success(f"All {exec_res['total']} Test Cases Passed! Score: 100%")
                    else:
                        st.warning(f"Passed {exec_res['passed']} of {exec_res['total']} Test Cases. Score: {score}%")

                    st.markdown("### Test Suite Breakdown:")
                    for d in exec_res["details"]:
                        t_icon = "Passed" if d["passed"] else "Failed"
                        st.write(f"- **Test Case {d['test_case']}**: {t_icon} | Input: `{d['input']}` | Expected: `{d['expected']}` | Output: `{d['actual']}`")
                    st.write(f"- **Test Case {d['test_case']}**: {t_icon} | Input: `{d['input']}` | Expected: `{d['expected']}` | Output: `{d['actual']}`")

# =========================================================================
# PAGE 6: FINAL PERFORMANCE REPORT & ANALYTICS
# =========================================================================
elif nav_selection == "Final Performance Report":
    st.markdown("""
    <div class="main-header">
        <h1>Comprehensive Interview Performance Report</h1>
        <p>Holistic multi-round analytics, competence radar visualizations, identified strengths, and 4-week placement preparation plan.</p>
    </div>
    """, unsafe_allow_html=True)

    session_id = get_or_create_session()
    transcripts = database.get_session_transcripts(session_id)

    # Calculate scores
    apt_sc = st.session_state.aptitude_score
    hr_sc = round(sum(st.session_state.hr_scores) / len(st.session_state.hr_scores) * 10.0, 1) if st.session_state.hr_scores else 70.0
    tech_sc = round(sum(st.session_state.tech_scores) / len(st.session_state.tech_scores) * 10.0, 1) if st.session_state.tech_scores else 75.0
    code_sc = st.session_state.coding_score

    report = ai_engine.generate_comprehensive_report(
        candidate_name=st.session_state.user["full_name"],
        target_role=st.session_state.user["target_role"],
        domain=st.session_state.target_domain,
        aptitude_score=apt_sc,
        hr_score=hr_sc,
        technical_score=tech_sc,
        coding_score=code_sc,
        transcripts=transcripts
    )

    # Save to database
    database.update_session_scores(
        session_id,
        aptitude_score=apt_sc,
        hr_score=hr_sc,
        technical_score=tech_sc,
        coding_score=code_sc,
        overall_score=report["overall_score"],
        status="Completed",
        report_data=report
    )

    # High-level Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card"><h3>{report['overall_score']}%</h3><p>Overall Score</p></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card"><h3>{apt_sc}%</h3><p>Round 1: Aptitude</p></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card"><h3>{hr_sc}%</h3><p>Round 2: HR</p></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card"><h3>{tech_sc}%</h3><p>Round 3: Tech</p></div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-card"><h3>{code_sc}%</h3><p>Coding Round</p></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Readiness Banner
    status_bg = "#065f46" if report["overall_score"] >= 75 else "#1e3a8a" if report["overall_score"] >= 60 else "#854d0e"
    st.markdown(f"""
    <div style="background: {status_bg}; padding: 18px 24px; border-radius: 10px; margin: 16px 0; color: white;">
        <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Placement Readiness Status</div>
        <div style="font-size: 22px; font-weight: bold; margin: 4px 0;">{report['readiness_status']}</div>
        <div style="font-size: 14px; opacity: 0.95;">{report['summary_verdict']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Visualizations Row
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("### 🕸️ Competency Radar Analysis")
        radar_fig = report_generator.create_radar_chart(apt_sc, hr_sc, tech_sc, code_sc)
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_chart2:
        st.markdown("### 📊 Round Performance vs Minimum Cutoff")
        bar_fig = report_generator.create_round_comparison_bar(apt_sc, hr_sc, tech_sc, code_sc)
        st.plotly_chart(bar_fig, use_container_width=True)

    # Strengths vs Improvements
    col_str, col_imp = st.columns(2)
    with col_str:
        st.markdown("### ✅ Key Candidate Strengths")
        for s in report["top_strengths"]:
            st.markdown(f"- **{s}**")
    with col_imp:
        st.markdown("### ⚠️ Priority Improvement Areas")
        for i in report["priority_improvements"]:
            st.markdown(f"- **{i}**")

    # 4-Week Roadmap
    st.markdown("---")
    st.markdown("### 📅 Personalized 4-Week Placement Readiness Roadmap")
    df_roadmap = pd.DataFrame(report["preparation_roadmap"])
    df_roadmap.columns = ["Timeline", "Target Objective", "Action Items"]
    st.table(df_roadmap)

    # HTML Download / Print Button
    st.markdown("---")
    st.markdown("### 📄 Export & Print Assessment Report")
    html_report = report_generator.generate_exportable_html_report(report, transcripts)

    col_d1, col_d2 = st.columns([1, 3])
    with col_d1:
        st.download_button(
            label="📥 Download Full Report (HTML / Printable)",
            data=html_report,
            file_name=f"Interview_Assessment_Report_{st.session_state.user['username']}.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )
    with col_d2:
        st.caption("You can open the downloaded report in any browser and use **File > Print (or Ctrl+P)** to save it as an official academic evaluation PDF.")

# =========================================================================
# PAGE 7: CANDIDATE PROFILE & AI SETTINGS
# =========================================================================
elif nav_selection == "Candidate Profile & Settings":
    st.markdown("""
    <div class="main-header">
        <h1>Candidate Profile & Platform Settings</h1>
        <p>Manage your profile, target role preferences, and configure optional AI model API keys.</p>
    </div>
    """, unsafe_allow_html=True)

    user = database.get_user_by_id(st.session_state.user["id"])

    tab_p, tab_ai = st.tabs(["👤 Profile Information", "🤖 AI Engine & Model Settings"])

    with tab_p:
        with st.form("update_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                u_name = st.text_input("Full Name", value=user["full_name"])
                u_email = st.text_input("Email", value=user["email"])
                u_role = st.text_input("Target Role", value=user["target_role"])
            with col2:
                u_exp = st.selectbox("Experience Tier", ["Fresher", "0-1 Years", "1-3 Years"], index=0)
                u_skills = st.text_input("Primary Technical Skills", value=user["primary_skills"])
                u_bio = st.text_area("Career Summary / Bio", value=user["bio"])

            if st.form_submit_button("Save Profile Changes", type="primary"):
                database.update_user_profile(user["id"], u_name, u_email, u_role, u_exp, u_skills, u_bio)
                st.session_state.user = database.get_user_by_id(user["id"])
                st.success("Profile updated successfully!")

    with tab_ai:
        st.markdown("### AI / NLP Engine Configuration")
        st.markdown("""
        The platform features a **Hybrid AI Architecture**:
        1. **Built-in Offline Heuristic NLP Engine (Default):** Evaluates depth, STAR structure, sentiment, and domain keyword density with zero API keys and zero internet dependencies.
        2. **Google Gemini Generative AI:** Uses an optional Gemini API Key to enable generative dynamic question generation and real-time deep NLP evaluations.
        """)

        key_input = st.text_input(
            "Google Gemini API Key (Optional):",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Leave blank to use the built-in offline NLP engine."
        )

        col_k1, col_k2 = st.columns([1, 3])
        with col_k1:
            if st.button("Apply AI Key", type="primary"):
                st.session_state.gemini_api_key = key_input.strip()
                st.success("AI Configuration updated!")
        with col_k2:
            if st.session_state.gemini_api_key:
                st.info("Status: Online Generative AI API is active.")
            else:
                st.info("Status: Built-in Offline Heuristic NLP Engine is active.")
