"""
Performance Report & Analytics Generator Module
Builds Plotly charts, competence radar diagrams, and downloadable report summaries.
"""

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def create_radar_chart(aptitude_score: float, hr_score: float, technical_score: float, coding_score: float):
    """
    Creates an interactive Plotly radar chart displaying candidate strengths across core pillars.
    """
    categories = [
        'Analytical Aptitude',
        'HR & Behavioral',
        'Technical Depth',
        'Coding & Logic',
        'Communication Tone',
        'Problem Solving'
    ]

    # Normalize values out of 100
    apt = min(100, max(10, aptitude_score))
    hr = min(100, max(10, hr_score))
    tech = min(100, max(10, technical_score))
    code = min(100, max(10, coding_score))
    comm = min(100, max(10, (hr * 0.6 + tech * 0.4)))
    prob = min(100, max(10, (apt * 0.5 + code * 0.3 + tech * 0.2)))

    values = [apt, hr, tech, code, comm, prob]
    benchmark = [75, 75, 75, 70, 75, 75]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Candidate Score',
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=benchmark + [benchmark[0]],
        theta=categories + [categories[0]],
        name='IT Industry Benchmark',
        line=dict(color='#10b981', dash='dash', width=1.5),
        fill='none'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color='#94a3b8')
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#f8fafc')
            )
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#cbd5e1")
        )
    )
    return fig

def create_round_comparison_bar(aptitude_score: float, hr_score: float, technical_score: float, coding_score: float):
    """
    Creates a bar chart comparing performance across the 4 rounds against minimum qualification standards.
    """
    rounds = ['Round 1: Aptitude', 'Round 2: HR', 'Round 3: Technical', 'Round 4: Coding']
    scores = [aptitude_score, hr_score, technical_score, coding_score]
    cutoff = [60, 65, 65, 60]

    colors = ['#10b981' if s >= c else '#f59e0b' if s >= 40 else '#ef4444' for s, c in zip(scores, cutoff)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rounds,
        y=scores,
        name='Your Score',
        marker_color=colors,
        text=[f"{s}%" for s in scores],
        textposition='auto',
    ))

    fig.add_trace(go.Scatter(
        x=rounds,
        y=cutoff,
        mode='lines+markers',
        name='Cutoff Threshold',
        line=dict(color='#ef4444', width=2, dash='dot')
    ))

    fig.update_layout(
        yaxis=dict(range=[0, 105], title="Score (%)", tickfont=dict(color='#cbd5e1'), title_font=dict(color='#cbd5e1')),
        xaxis=dict(tickfont=dict(color='#cbd5e1')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="#cbd5e1")
        )
    )
    return fig

def generate_exportable_html_report(report_data: dict, transcripts: list = None) -> str:
    """
    Generates a self-contained, clean printable HTML document for saving or printing as PDF.
    """
    cand = report_data.get("candidate_name", "Candidate")
    role = report_data.get("target_role", "Software Engineer")
    domain = report_data.get("target_domain", "IT Systems")
    overall = report_data.get("overall_score", 0.0)
    verdict = report_data.get("summary_verdict", "")
    readiness = report_data.get("readiness_status", "Evaluated")
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")

    strengths_html = "".join([f"<li>✅ {s}</li>" for s in report_data.get("top_strengths", [])])
    improvements_html = "".join([f"<li>⚠️ {i}</li>" for i in report_data.get("priority_improvements", [])])

    roadmap_rows = ""
    for r in report_data.get("preparation_roadmap", []):
        roadmap_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">{r.get('week')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; color: #2563eb;">{r.get('goal')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{r.get('tasks')}</td>
        </tr>
        """

    transcript_sections = ""
    if transcripts:
        transcript_sections = "<h3>Detailed Interview Transcripts & AI Feedback</h3>"
        for t in transcripts:
            transcript_sections += f"""
            <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 12px 16px; margin-bottom: 12px; border-radius: 4px;">
                <div style="font-weight: bold; color: #1e293b;">[{t.get('round_type')}] Q{t.get('question_num')}: {t.get('question_text')}</div>
                <div style="margin: 8px 0; color: #334155;"><strong>Answer:</strong> {t.get('candidate_answer')}</div>
                <div style="color: #047857; font-size: 13px;"><strong>AI Assessment (Score: {t.get('score')}/10):</strong> {t.get('feedback')}</div>
            </div>
            """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Interview Assessment Report - {cand}</title>
        <style>
            body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #0f172a; margin: 40px auto; max-width: 850px; line-height: 1.6; }}
            .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-end; }}
            .title {{ font-size: 24px; font-weight: bold; color: #1e3a8a; margin: 0; }}
            .meta {{ color: #64748b; font-size: 13px; }}
            .score-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 25px 0; }}
            .score-card {{ background: #f1f5f9; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }}
            .score-val {{ font-size: 28px; font-weight: bold; color: #2563eb; }}
            .score-lbl {{ font-size: 12px; color: #475569; text-transform: uppercase; font-weight: 600; }}
            .overall-banner {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .verdict {{ font-size: 18px; font-weight: bold; margin-bottom: 6px; }}
            .section {{ margin-top: 25px; }}
            h3 {{ color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }}
            ul {{ padding-left: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            @media print {{
                body {{ margin: 20px; }}
                button {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div style="text-align: right; margin-bottom: 10px;">
            <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                🖨️ Print / Save as PDF
            </button>
        </div>
        <div class="header">
            <div>
                <h1 class="title">Virtual Interview Performance Report</h1>
                <div style="font-size: 14px; color: #475569;">AI-Driven Virtual Interview and Skill Assessment Platform</div>
            </div>
            <div class="meta">
                Date: {now_str}<br>
                Candidate: <strong>{cand}</strong><br>
                Target Role: <strong>{role}</strong>
            </div>
        </div>

        <div class="overall-banner">
            <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Readiness Status</div>
            <div class="verdict">{readiness} (Overall Score: {overall}%)</div>
            <div style="font-size: 14px; opacity: 0.95;">{verdict}</div>
        </div>

        <div class="score-grid">
            <div class="score-card">
                <div class="score-val">{report_data.get('aptitude_score', 0)}%</div>
                <div class="score-lbl">Round 1: Aptitude</div>
            </div>
            <div class="score-card">
                <div class="score-val">{report_data.get('hr_score', 0)}%</div>
                <div class="score-lbl">Round 2: HR Interview</div>
            </div>
            <div class="score-card">
                <div class="score-val">{report_data.get('technical_score', 0)}%</div>
                <div class="score-lbl">Round 3: Technical ({domain})</div>
            </div>
            <div class="score-card">
                <div class="score-val">{report_data.get('coding_score', 0)}%</div>
                <div class="score-lbl">Optional: Coding</div>
            </div>
        </div>

        <div class="section" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h3>Key Strengths Identified</h3>
                <ul>{strengths_html}</ul>
            </div>
            <div>
                <h3>Priority Improvement Areas</h3>
                <ul>{improvements_html}</ul>
            </div>
        </div>

        <div class="section">
            <h3>4-Week Placement Readiness Roadmap</h3>
            <table>
                <thead>
                    <tr style="background: #f1f5f9; text-align: left;">
                        <th style="padding: 10px; border-bottom: 2px solid #cbd5e1;">Timeline</th>
                        <th style="padding: 10px; border-bottom: 2px solid #cbd5e1;">Milestone</th>
                        <th style="padding: 10px; border-bottom: 2px solid #cbd5e1;">Target Action</th>
                    </tr>
                </thead>
                <tbody>
                    {roadmap_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            {transcript_sections}
        </div>

        <div style="margin-top: 40px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
            Generated automatically by AI-Driven Virtual Interview & Skill Assessment Platform • Final-Year BCA Project
        </div>
    </body>
    </html>
    """
    return html
