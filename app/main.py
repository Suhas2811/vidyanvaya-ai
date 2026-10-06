import sys
import time
import json
import html
from datetime import datetime
from io import BytesIO
from pathlib import Path

import streamlit as st


# ==================================================
# PROJECT PATH
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==================================================
# DOCUMENT PROCESSING
# ==================================================

from document_processing.pdf_processor import (
    extract_text_from_pdf
)

from document_processing.docx_processor import (
    extract_text_from_docx
)

from document_processing.pptx_processor import (
    extract_text_from_pptx
)


# ==================================================
# RAG
# ==================================================

from rag.chunking import chunk_text

from rag.embeddings import create_embeddings

from rag.vector_store import (
    store_embeddings,
    get_collection_count,
    get_document_names,
    create_file_id
)

from rag.retrieval import (
    retrieve_relevant_chunks
)


# ==================================================
# AI / SERVICES
# ==================================================

from services.ai_provider import (
    generate_with_fallback
)

from services.question_bank_service import (
    extract_questions
)

from services.exam_prep_service import (
    generate_practice_test,
    evaluate_answer
)

from services.performance_service import (
    get_performance_summary
)


# ==================================================
# UI THEME + DASHBOARD (presentation layer only)
# ==================================================

# ==================================================
# DESIGN TOKENS (taken from the Stitch prototype)
# ==================================================

NAVY = "#1e1b4b"
INDIGO = "#4f46e5"
INDIGO_SOFT = "#eef0ff"
INK = "#14142b"
MUTED = "#6b7280"
LINE = "#e6e8f0"
PAGE_BG = "#f6f7fb"


# ==================================================
# HELPERS
# ==================================================

def _html(markup: str) -> None:
    """
    Render raw HTML. Leading whitespace and blank lines are removed so
    Streamlit's markdown parser never treats the HTML as a code block.
    """
    cleaned = "\n".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )
    st.markdown(cleaned, unsafe_allow_html=True)


def _esc(value) -> str:
    return html.escape(str(value))


def _greeting() -> str:
    hour = datetime.now().hour

    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


# ==================================================
# GLOBAL THEME
# ==================================================

def inject_theme() -> None:
    """Call once, right after st.set_page_config()."""

    _html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}}

.stApp {{ background: {PAGE_BG}; }}

#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

.block-container {{
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1240px;
}}

h1, h2, h3 {{
    color: {INK};
    letter-spacing: -0.02em;
    font-weight: 650;
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: #ffffff;
    border-right: 1px solid {LINE};
}}

section[data-testid="stSidebar"] h1 {{
    font-size: 1.15rem;
    margin-bottom: 0;
}}

/* Navigation radio -> vertical menu */
section[data-testid="stSidebar"] div[role="radiogroup"] {{
    gap: 4px;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
    width: 100%;
    padding: 9px 12px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    cursor: pointer;
    transition: background .15s ease;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
    display: none;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
    background: #f1f2f9;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
    background: {NAVY};
}}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {{
    color: #ffffff;
    font-weight: 600;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] p {{
    font-size: 0.9rem;
    color: #374151;
}}

/* ---------- Mode switches inside pages (horizontal radios) ---------- */
.stApp section.main div[role="radiogroup"][aria-orientation="horizontal"] > label,
.stApp [data-testid="stMain"] div[role="radiogroup"][aria-orientation="horizontal"] > label {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 999px;
    padding: 6px 16px;
}}

.stApp [data-testid="stMain"] div[role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) {{
    background: {INDIGO_SOFT};
    border-color: {INDIGO};
}}

.stApp [data-testid="stMain"] div[role="radiogroup"][aria-orientation="horizontal"] > label > div:first-child {{
    display: none;
}}

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 14px;
    padding: 14px 18px;
}}

div[data-testid="stMetricLabel"] p {{
    color: {MUTED};
    font-size: 0.8rem;
}}

div[data-testid="stMetricValue"] {{
    color: {INK};
    font-weight: 650;
}}

/* ---------- Buttons ---------- */
.stButton > button {{
    border-radius: 10px;
    border: 1px solid {LINE};
    font-weight: 550;
    transition: border-color .15s ease, background .15s ease;
}}

.stButton > button:hover {{
    border-color: {INDIGO};
    color: {INDIGO};
}}

.stButton > button[kind="primary"] {{
    background: {INDIGO};
    border-color: {INDIGO};
    color: #ffffff;
}}

.stButton > button[kind="primary"]:hover {{
    background: #4338ca;
    border-color: #4338ca;
    color: #ffffff;
}}

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{
    border-radius: 10px;
}}

div[data-testid="stFileUploader"] section {{
    border-radius: 14px;
    border: 1.5px dashed #c7cbe6;
    background: #ffffff;
}}

div[data-testid="stExpander"] {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 12px;
}}

/* ---------- Dashboard components ---------- */
.vv-mono {{
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: 0.68rem;
    letter-spacing: .04em;
}}

.vv-eyebrow {{ color: {INDIGO}; margin-bottom: 2px; }}

.vv-page-title {{
    font-size: 1.7rem;
    font-weight: 650;
    color: {INK};
    letter-spacing: -0.02em;
    margin: 0;
}}

.vv-page-sub {{ color: {MUTED}; font-size: .88rem; margin: 2px 0 18px 0; }}

.vv-hero {{
    background: linear-gradient(135deg, #1b1846 0%, #2b2877 55%, #3a2f9c 100%);
    border-radius: 20px;
    padding: 30px 34px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 24px;
    color: #ffffff;
    margin-bottom: 14px;
}}

.vv-hero h2 {{
    color: #ffffff;
    font-size: 2rem;
    margin: 12px 0 8px 0;
}}

.vv-hero p {{
    color: #c7c9ee;
    font-size: .9rem;
    max-width: 520px;
    margin: 0;
    line-height: 1.55;
}}

.vv-pill {{
    display: inline-block;
    padding: 4px 11px;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    color: #dcdcff;
}}

.vv-hero-side {{
    min-width: 240px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 14px;
    padding: 16px 18px;
}}

.vv-hero-side .vv-big {{ font-size: 1.5rem; font-weight: 650; margin: 4px 0; }}
.vv-hero-side .vv-note {{ color: #a7f3d0; }}

.vv-panel {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 14px;
}}

.vv-flow {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-top: 10px;
}}

.vv-step {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f5f6fb;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: .78rem;
    font-weight: 600;
    color: {INK};
}}

.vv-step i {{
    font-style: normal;
    width: 20px;
    height: 20px;
    flex: 0 0 20px;
    border-radius: 50%;
    background: {INDIGO};
    color: #ffffff;
    font-size: .68rem;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.vv-stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 14px;
}}

.vv-stat {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 16px;
    padding: 18px 20px;
}}

.vv-stat .vv-num {{
    font-size: 1.9rem;
    font-weight: 650;
    color: {INK};
    letter-spacing: -0.02em;
    line-height: 1.1;
}}

.vv-stat .vv-label {{ color: {MUTED}; font-size: .84rem; margin-top: 2px; }}

.vv-bar {{
    height: 5px;
    border-radius: 99px;
    background: #e9ebf5;
    margin-top: 12px;
    overflow: hidden;
}}

.vv-bar > span {{
    display: block;
    height: 100%;
    background: {INDIGO};
    border-radius: 99px;
}}

.vv-rec {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-left: 4px solid #dc2626;
    border-radius: 16px;
    padding: 18px 22px;
}}

.vv-rec h3 {{ margin: 6px 0 6px 0; font-size: 1.15rem; }}
.vv-rec p {{ color: #4b5563; margin: 0; font-size: .9rem; line-height: 1.55; }}

/* ---------- Advanced additions ---------- */
/* In-page mode switches are driven by the sidebar now */
.st-key-learn_mode, .st-key-practice_mode {{ display: none; }}

.vv-chips {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 14px 0; }}

.vv-chip {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-radius: 999px;
    padding: 4px 12px;
    color: #374151;
}}

.vv-dot {{
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #16a34a;
    margin-right: 6px;
}}

.vv-step.done i {{ background: #16a34a; }}
.vv-step.todo i {{ background: #c7cbe6; }}

.vv-step.active {{
    background: {INDIGO_SOFT};
    box-shadow: inset 0 0 0 1.5px {INDIGO};
}}

.vv-next {{
    background: #ffffff;
    border: 1px solid {LINE};
    border-left: 4px solid {INDIGO};
    border-radius: 16px;
    padding: 16px 20px;
}}

.vv-next h4 {{ margin: 4px 0 4px 0; font-size: 1.05rem; color: {INK}; }}
.vv-next p {{ margin: 0; color: #4b5563; font-size: .88rem; line-height: 1.5; }}

.vv-two {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}}

.vv-two .vv-panel {{ margin-bottom: 0; }}
.vv-panel h4 {{ margin: 0 0 6px 0; font-size: 1rem; color: {INK}; }}

.vv-mrow {{
    display: grid;
    grid-template-columns: 1.3fr 2fr 44px;
    align-items: center;
    gap: 12px;
    margin: 12px 0;
}}

.vv-mrow .vv-bar {{ margin-top: 0; }}

.vv-mname {{
    font-size: .85rem;
    font-weight: 550;
    color: {INK};
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.vv-act {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f0f1f7;
}}

.vv-act:last-child {{ border-bottom: none; }}

.vv-badge {{
    border-radius: 999px;
    padding: 3px 10px;
    font-size: .74rem;
    font-weight: 650;
}}

.vv-empty {{ color: {MUTED}; font-size: .88rem; margin: 8px 0 0 0; }}

@media (max-width: 900px) {{
    .vv-two {{ grid-template-columns: 1fr; }}
}}

@media (max-width: 900px) {{
    .vv-hero {{ flex-direction: column; }}
    .vv-flow {{ grid-template-columns: repeat(2, 1fr); }}
    .vv-stats {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
""")


# ==================================================
# NAVIGATION (flat menu that drives the existing pages)
# ==================================================

NAV_ITEMS = [
    "🏠 Dashboard",
    "📚 Materials",
    "🔍 Subject Guide",
    "📝 Question Bank",
    "🧠 Question Solver",
    "🎯 Exam Prep",
    "📊 Performance",
]

# menu item -> (existing page, learn mode, practice mode)
NAV_MAP = {
    "🏠 Dashboard": ("🏠 Dashboard", None, None),
    "📚 Materials": ("📚 Materials", None, None),
    "🔍 Subject Guide": ("🧠 Learn", "🔍 Subject Guide", None),
    "📝 Question Bank": ("📝 Practice", None, "📝 Question Bank"),
    "🧠 Question Solver": ("🧠 Learn", "🧠 Question Solver", None),
    "🎯 Exam Prep": ("📝 Practice", None, "🎯 Exam Preparation"),
    "📊 Performance": ("📊 Performance", None, None),
}


def _nav_label(option) -> str:
    """Sidebar label with a live count where it is useful."""
    try:
        document_total = len(get_document_names())
    except Exception:
        document_total = 0

    counts = {
        "📚 Materials": document_total,
        "📝 Question Bank": len(
            st.session_state.get("extracted_questions", [])
        ),
        "📊 Performance": len(
            st.session_state.get("performance_history", [])
        ),
    }

    count = counts.get(option, 0)

    return f"{option}   ·   {count}" if count else option


def resolve_navigation(nav_item) -> str:
    """
    Translate the sidebar choice into the existing page + mode,
    so the original page code runs exactly as before.
    """
    page, learn_mode, practice_mode = NAV_MAP.get(
        nav_item,
        NAV_MAP["🏠 Dashboard"]
    )

    if learn_mode:
        st.session_state["learn_mode"] = learn_mode

    if practice_mode:
        st.session_state["practice_mode"] = practice_mode

    return page


def _go(nav_item) -> None:
    st.session_state["main_navigation"] = nav_item


# ==================================================
# SMALL VISUAL HELPERS
# ==================================================

def _record_pct(record) -> float:
    """Percentage for one saved practice-test record."""
    try:
        if "percentage" in record:
            return float(record["percentage"])

        total = float(record.get("total_marks", 0))

        if total > 0:
            return float(record.get("score", 0)) / total * 100
    except (TypeError, ValueError):
        pass

    return 0.0


def _pct_color(pct) -> str:
    if pct >= 75:
        return "#16a34a"
    if pct >= 50:
        return "#d97706"
    return "#dc2626"


def _ring(pct, label, size=104) -> str:
    """SVG progress ring."""
    circumference = 2 * 3.14159 * 40
    offset = circumference * (1 - max(0, min(100, pct)) / 100)

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="40" fill="none" '
        f'stroke="rgba(255,255,255,.16)" stroke-width="9"/>'
        f'<circle cx="50" cy="50" r="40" fill="none" stroke="#a5b4fc" '
        f'stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{circumference:.1f}" '
        f'stroke-dashoffset="{offset:.1f}" '
        f'transform="rotate(-90 50 50)"/>'
        f'<text x="50" y="57" text-anchor="middle" fill="#ffffff" '
        f'font-size="21" font-weight="650" '
        f'font-family="Inter, sans-serif">{_esc(label)}</text>'
        f'</svg>'
    )


def _sparkline(values, width=150, height=38) -> str:
    """SVG trend line (needs at least two points)."""
    if len(values) < 2:
        return ""

    low, high = min(values), max(values)
    span = (high - low) or 1
    step = width / (len(values) - 1)

    points = " ".join(
        f"{index * step:.1f},"
        f"{height - 4 - ((value - low) / span) * (height - 8):.1f}"
        for index, value in enumerate(values)
    )

    return (
        f'<svg width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<polyline points="{points}" fill="none" stroke="{INDIGO}" '
        f'stroke-width="2.2" stroke-linecap="round" '
        f'stroke-linejoin="round"/></svg>'
    )


def _stage(doc_count, tests, recommendations) -> int:
    """Which step of the mastery lifecycle the learner is on (1-7)."""
    if doc_count == 0:
        return 1
    if tests == 0:
        return 2
    if recommendations:
        return 6
    return 7


def _next_action(doc_count, question_count, tests, recommendations):
    """Rule-based 'what should I do next' suggestion."""
    if doc_count == 0:
        return (
            "Upload your first study material",
            "Add notes, a textbook or a question paper so the AI has "
            "something to learn from.",
            "📚 Materials",
            "Upload material",
        )

    if tests == 0:
        return (
            "Take your first practice test",
            "A short test on any topic gives you a baseline and unlocks "
            "weak-area tracking.",
            "🎯 Exam Prep",
            "Start a test",
        )

    if recommendations:
        top = recommendations[0]
        topic = top.get("topic", "your weakest topic")
        pct = float(top.get("percentage", 0) or 0)

        return (
            f"Revise {topic}",
            f"You are scoring {pct:.0f}% here. A focused practice test "
            f"is the fastest way to move it up.",
            "🎯 Exam Prep",
            "Practice this topic",
        )

    if question_count == 0:
        return (
            "Extract a past question paper",
            "Turn a previous-year paper into a question bank you can "
            "solve with the AI.",
            "📝 Question Bank",
            "Open question bank",
        )

    return (
        "Raise the difficulty",
        "Your results look strong. Try a Hard practice test to keep "
        "improving.",
        "🎯 Exam Prep",
        "Start a harder test",
    )


# ==================================================
# DASHBOARD PAGE
# ==================================================

def render_dashboard(
    user_name,
    documents,
    chunk_count,
    questions,
    history,
    get_performance_summary,
) -> None:
    """
    Dashboard built only from data your app already has.

    documents               -> get_document_names()
    chunk_count             -> get_collection_count()
    questions               -> st.session_state["extracted_questions"]
    history                 -> st.session_state["performance_history"]
    get_performance_summary -> your existing function
    """

    summary = None

    if history:
        try:
            summary = get_performance_summary(history)
        except Exception:
            summary = None

    overall = (summary or {}).get("overall", {})
    topics = (summary or {}).get("topic_performance", {})
    recommendations = (summary or {}).get("recommendations", [])

    tests = overall.get("tests_attempted", 0)
    percentage = float(overall.get("percentage", 0) or 0)

    doc_count = len(documents)
    question_count = len(questions)

    user_name = str(user_name or "").strip()
    welcome_text = (
        f"Welcome back, {_esc(user_name)}."
        if user_name else "Welcome back."
    )
    greeting_text = (
        f"{_greeting()}, {_esc(user_name)}"
        if user_name else _greeting()
    )

    provider = ""

    for key in ("exam_prep_provider", "question_bank_provider"):
        value = str(st.session_state.get(key, "unknown") or "unknown")

        if value.lower() not in ("unknown", "none", ""):
            provider = value.capitalize()
            break

    provider_chip = (
        f'<span class="vv-chip vv-mono">AI · {_esc(provider)}</span>'
        if provider else ""
    )

    # ---------- Page heading + status chips ----------
    _html(f"""
<div class="vv-mono vv-eyebrow">KNOWLEDGE BASE · {chunk_count:,} CHUNKS INDEXED</div>
<h1 class="vv-page-title">Dashboard</h1>
<div class="vv-page-sub">{welcome_text} Continue learning from your academic knowledge base.</div>
<div class="vv-chips">
<span class="vv-chip vv-mono"><span class="vv-dot"></span>RAG ENGINE ONLINE</span>
<span class="vv-chip vv-mono">{doc_count} DOC{'S' if doc_count != 1 else ''}</span>
<span class="vv-chip vv-mono">{question_count} QUESTION{'S' if question_count != 1 else ''}</span>
{provider_chip}
</div>
""")

    # ---------- Hero ----------
    if doc_count:
        hero_text = (
            f"VidyānVaya AI has indexed <b>{doc_count} "
            f"academic material{'s' if doc_count != 1 else ''}</b> "
            f"into {chunk_count:,} searchable chunks. "
            f"Ask a question, solve a past paper, or take a practice test."
        )
    else:
        hero_text = (
            "Your knowledge base is empty. Upload notes, textbooks or "
            "question papers to start learning."
        )

    ring_label = f"{percentage:.0f}%" if tests else "—"
    side_note = (
        f"Across {tests} practice test{'s' if tests != 1 else ''}"
        if tests
        else "Take a practice test to start tracking"
    )

    _html(f"""
<div class="vv-hero">
<div>
<span class="vv-pill vv-mono">SEMANTIC RAG ENGINE ONLINE</span>
<h2>{greeting_text}</h2>
<p>{hero_text}</p>
</div>
<div class="vv-hero-side">
<div class="vv-mono" style="color:#c7c9ee">PRACTICE ACCURACY</div>
<div class="vv-hero-ring">
{_ring(percentage if tests else 0, ring_label)}
<div class="vv-mono vv-note">{_esc(side_note)}</div>
</div>
</div>
</div>
""")

    # ---------- Quick actions ----------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.button(
            "Upload material",
            type="primary",
            use_container_width=True,
            key="dash_upload",
            on_click=_go,
            args=("📚 Materials",),
        )

    with c2:
        st.button(
            "Explain a topic",
            use_container_width=True,
            key="dash_explain",
            on_click=_go,
            args=("🔍 Subject Guide",),
        )

    with c3:
        st.button(
            "Solve a question",
            use_container_width=True,
            key="dash_solve",
            on_click=_go,
            args=("🧠 Question Solver",),
        )

    with c4:
        st.button(
            "Generate practice test",
            use_container_width=True,
            key="dash_practice",
            on_click=_go,
            args=("🎯 Exam Prep",),
        )

    st.write("")

    # ---------- Next best action ----------
    (
        next_title,
        next_text,
        next_target,
        next_button,
    ) = _next_action(
        doc_count,
        question_count,
        tests,
        recommendations
    )

    left, right = st.columns([4, 1])

    with left:
        _html(f"""
<div class="vv-next">
<div class="vv-mono vv-eyebrow">RECOMMENDED NEXT STEP</div>
<h4>{_esc(next_title)}</h4>
<p>{_esc(next_text)}</p>
</div>
""")

    with right:
        st.write("")
        st.button(
            next_button,
            type="primary",
            use_container_width=True,
            key="dash_next_action",
            on_click=_go,
            args=(next_target,),
        )

    st.write("")

    # ---------- Workflow strip (reflects real progress) ----------
    steps = [
        "Learn", "Practice", "Answer", "Evaluate",
        "Analyze", "Revise", "Improve",
    ]

    current = _stage(doc_count, tests, recommendations)

    step_parts = []

    for number, name in enumerate(steps, start=1):
        if number < current:
            state = "done"
            mark = "✓"
        elif number == current:
            state = "active"
            mark = str(number)
        else:
            state = "todo"
            mark = str(number)

        step_parts.append(
            f'<div class="vv-step {state}"><i>{mark}</i>{name}</div>'
        )

    _html(f"""
<div class="vv-panel">
<div class="vv-mono" style="color:{MUTED}">MASTERY LIFECYCLE WORKFLOW</div>
<div class="vv-flow">{"".join(step_parts)}</div>
</div>
""")

    # ---------- Stat cards ----------
    scores = [_record_pct(record) for record in history][-10:]
    trend = _sparkline(scores)
    trend_html = (
        f'<div style="margin-top:10px">{trend}</div>'
        if trend
        else f'<div class="vv-mono" style="color:{MUTED};margin-top:10px">trend appears after 2 tests</div>'
    )

    _html(f"""
<div class="vv-stats">
<div class="vv-stat">
<div class="vv-num">{doc_count}</div>
<div class="vv-label">Academic documents</div>
<div class="vv-mono" style="color:{MUTED};margin-top:8px">{chunk_count:,} indexed chunks</div>
</div>
<div class="vv-stat">
<div class="vv-num">{question_count}</div>
<div class="vv-label">Extracted questions</div>
<div class="vv-mono" style="color:{MUTED};margin-top:8px">from the current question bank</div>
</div>
<div class="vv-stat">
<div class="vv-num">{percentage:.0f}%</div>
<div class="vv-label">Practice accuracy</div>
{trend_html}
</div>
<div class="vv-stat">
<div class="vv-num">{len(topics)}</div>
<div class="vv-label">Topics tracked</div>
<div class="vv-mono" style="color:{MUTED};margin-top:8px">{tests} test{'s' if tests != 1 else ''} attempted</div>
</div>
</div>
""")

    # ---------- Topic mastery + recent activity ----------
    if topics:
        ordered = sorted(
            topics.items(),
            key=lambda item: float(item[1].get("percentage", 0) or 0)
        )[:6]

        mastery_rows = ""

        for topic_name, topic_data in ordered:
            topic_pct = float(topic_data.get("percentage", 0) or 0)
            color = _pct_color(topic_pct)

            mastery_rows += (
                f'<div class="vv-mrow">'
                f'<div class="vv-mname">{_esc(topic_name)}</div>'
                f'<div class="vv-bar"><span style="width:{max(0, min(100, topic_pct)):.0f}%;background:{color}"></span></div>'
                f'<div class="vv-mono" style="text-align:right">{topic_pct:.0f}%</div>'
                f'</div>'
            )
    else:
        mastery_rows = (
            '<p class="vv-empty">Topic mastery appears after your '
            'first practice test.</p>'
        )

    if history:
        activity_rows = ""

        for record in list(reversed(history))[:5]:
            record_pct = _record_pct(record)
            color = _pct_color(record_pct)

            try:
                score_text = (
                    f"{float(record.get('score', 0)):g}/"
                    f"{float(record.get('total_marks', 0)):g}"
                )
            except (TypeError, ValueError):
                score_text = "—"

            topic_text = _esc(record.get("topic", "Unknown"))
            difficulty_text = _esc(record.get("difficulty", "—"))

            activity_rows += (
                f'<div class="vv-act"><div>'
                f'<div style="font-weight:600;font-size:.88rem;color:{INK}">{topic_text}</div>'
                f'<div class="vv-mono" style="color:{MUTED}">{difficulty_text} · {score_text}</div>'
                f'</div>'
                f'<span class="vv-badge" style="background:{color}1a;color:{color}">{record_pct:.0f}%</span>'
                f'</div>'
            )
    else:
        activity_rows = (
            '<p class="vv-empty">No practice tests yet. Your last five '
            'results will be listed here.</p>'
        )

    _html(f"""
<div class="vv-two">
<div class="vv-panel">
<h4>Topic mastery</h4>
<div class="vv-mono" style="color:{MUTED}">WEAKEST FIRST</div>
{mastery_rows}
</div>
<div class="vv-panel">
<h4>Recent practice</h4>
<div class="vv-mono" style="color:{MUTED}">LAST 5 TESTS</div>
{activity_rows}
</div>
</div>
""")

    # ---------- Top recommendation ----------
    if recommendations:
        top = recommendations[0]

        _html(f"""
<div class="vv-rec">
<div class="vv-mono" style="color:#dc2626">{_esc(str(top.get('priority', 'High')).upper())} PRIORITY RECOMMENDATION</div>
<h3>{_esc(top.get('topic', 'Topic'))} needs more attention</h3>
<p>Current performance: <b>{float(top.get('percentage', 0)):.1f}%</b>. {_esc(top.get('recommendation', ''))}</p>
</div>
""")

    else:
        _html("""
<div class="vv-panel">
<h3 style="margin:0 0 6px 0">No recommendations yet</h3>
<p style="margin:0;color:#6b7280;font-size:.9rem">
Complete a practice test and your weak areas and study
recommendations will appear here.
</p>
</div>
""")


# ==================================================
# PERFORMANCE INSIGHTS (shown above your existing dashboard)
# ==================================================

def render_performance_insights(history) -> None:
    """Trend, improvement and difficulty analysis. Adds to, not replaces,
    display_performance_dashboard()."""

    if not history:
        return

    percentages = [_record_pct(record) for record in history]
    count = len(percentages)

    average = sum(percentages) / count
    best = max(percentages)

    window = max(1, min(3, count // 2))

    if count >= 2:
        delta = (
            sum(percentages[-window:]) / window
            - sum(percentages[:window]) / window
        )
    else:
        delta = 0.0

    by_topic = {}
    by_difficulty = {}

    for record, value in zip(history, percentages):
        by_topic.setdefault(
            str(record.get("topic", "Unknown")), []
        ).append(value)

        by_difficulty.setdefault(
            str(record.get("difficulty", "Unknown")), []
        ).append(value)

    topic_means = {
        topic: sum(values) / len(values)
        for topic, values in by_topic.items()
    }

    weakest = min(topic_means, key=topic_means.get)

    delta_color = "#16a34a" if delta >= 0 else "#dc2626"
    delta_text = f"{delta:+.1f} pts" if count >= 2 else "—"

    st.subheader("🚀 Insights")

    _html(f"""
<div class="vv-stats">
<div class="vv-stat">
<div class="vv-num">{average:.0f}%</div>
<div class="vv-label">Average score</div>
</div>
<div class="vv-stat">
<div class="vv-num">{best:.0f}%</div>
<div class="vv-label">Best test</div>
</div>
<div class="vv-stat">
<div class="vv-num" style="color:{delta_color}">{delta_text}</div>
<div class="vv-label">Improvement (early vs recent)</div>
</div>
<div class="vv-stat">
<div class="vv-num" style="font-size:1.25rem;line-height:1.5">{_esc(weakest)}</div>
<div class="vv-label">Weakest topic · {topic_means[weakest]:.0f}%</div>
</div>
</div>
""")

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Score trend across tests (%)")
        st.line_chart({"Score %": percentages})

    with col2:
        st.caption("Average score by difficulty (%)")
        st.bar_chart({
            difficulty: sum(values) / len(values)
            for difficulty, values in by_difficulty.items()
        })

    st.divider()


# ==================================================
# STREAMLIT CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="VidyānVaya AI",
    page_icon="📚",
    layout="wide"
)

inject_theme()


# ==================================================
# SESSION STATE INITIALIZATION
# ==================================================

if "uploaded_files_data" not in st.session_state:
    st.session_state["uploaded_files_data"] = []

if "extracted_questions" not in st.session_state:
    st.session_state["extracted_questions"] = []

if "question_bank_provider" not in st.session_state:
    st.session_state["question_bank_provider"] = "unknown"

if "question_bank_source" not in st.session_state:
    st.session_state["question_bank_source"] = ""

if "exam_prep_questions" not in st.session_state:
    st.session_state["exam_prep_questions"] = []

if "exam_prep_provider" not in st.session_state:
    st.session_state["exam_prep_provider"] = "unknown"

if "exam_prep_document" not in st.session_state:
    st.session_state["exam_prep_document"] = ""

if "exam_prep_topic" not in st.session_state:
    st.session_state["exam_prep_topic"] = ""

if "exam_prep_difficulty" not in st.session_state:
    st.session_state["exam_prep_difficulty"] = "Medium"

if "exam_prep_context" not in st.session_state:
    st.session_state["exam_prep_context"] = ""

if "exam_prep_source_chunks" not in st.session_state:
    st.session_state["exam_prep_source_chunks"] = []

if "exam_prep_results" not in st.session_state:
    st.session_state["exam_prep_results"] = []

if "exam_prep_total_score" not in st.session_state:
    st.session_state["exam_prep_total_score"] = 0

if "performance_history" not in st.session_state:
    st.session_state["performance_history"] = []


# ==================================================
# PERFORMANCE HISTORY PERSISTENCE
# ==================================================

PERFORMANCE_HISTORY_FILE = PROJECT_ROOT / "data" / "performance_history.json"


def load_performance_history():
    """Load saved practice-test history from disk."""
    try:
        if PERFORMANCE_HISTORY_FILE.exists():
            with PERFORMANCE_HISTORY_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data
    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_performance_history(history):
    """Save practice-test history to disk."""
    try:
        PERFORMANCE_HISTORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with PERFORMANCE_HISTORY_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                history,
                file,
                indent=2,
                ensure_ascii=False
            )
    except OSError:
        pass


# Restore previous performance data when the app starts.
if not st.session_state["performance_history"]:
    st.session_state["performance_history"] = load_performance_history()


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def save_uploaded_files(uploaded_files):
    """
    Store uploaded file bytes in session state so that
    the files remain available across navigation sections.
    """

    stored_files = []

    for file in uploaded_files:
        stored_files.append(
            {
                "name": file.name,
                "bytes": file.getvalue(),
            }
        )

    st.session_state["uploaded_files_data"] = stored_files


def get_uploaded_file_names():
    """
    Return names of files currently stored in session state.
    """

    return [
        file["name"]
        for file in st.session_state["uploaded_files_data"]
    ]


def get_uploaded_pdf_names():
    """
    Return uploaded PDF file names.
    """

    return [
        file["name"]
        for file in st.session_state["uploaded_files_data"]
        if file["name"].lower().endswith(".pdf")
    ]


def get_uploaded_file_bytes(file_name):
    """
    Return bytes for a stored uploaded file.
    """

    for file in st.session_state["uploaded_files_data"]:
        if file["name"] == file_name:
            return file["bytes"]

    return None


def create_file_object(file_name):
    """
    Create a BytesIO object from a stored uploaded file.
    """

    file_bytes = get_uploaded_file_bytes(file_name)

    if file_bytes is None:
        return None

    file_object = BytesIO(file_bytes)
    file_object.name = file_name

    return file_object


def process_single_document(file_name, file_bytes):
    """
    Process one academic document and store its embeddings.
    """

    file = BytesIO(file_bytes)
    file.name = file_name

    extracted_text = ""

    if file_name.lower().endswith(".pdf"):

        file.seek(0)

        pages = extract_text_from_pdf(file)

        extracted_text = "\n".join(
            page["text"]
            for page in pages
            if page.get("text")
        )

        extraction_message = (
            f"PDF processed — {len(pages)} pages extracted."
        )

    elif file_name.lower().endswith(".docx"):

        file.seek(0)

        paragraphs = extract_text_from_docx(file)

        extracted_text = "\n".join(
            paragraph["text"]
            for paragraph in paragraphs
            if paragraph.get("text")
        )

        extraction_message = (
            f"DOCX processed — "
            f"{len(paragraphs)} paragraphs extracted."
        )

    elif file_name.lower().endswith(".pptx"):

        file.seek(0)

        slides = extract_text_from_pptx(file)

        extracted_text = "\n".join(
            slide["text"]
            for slide in slides
            if slide.get("text")
        )

        extraction_message = (
            f"PPTX processed — "
            f"{len(slides)} slides extracted."
        )

    else:

        raise ValueError(
            f"Unsupported file type: {file_name}"
        )

    if not extracted_text.strip():
        raise ValueError(
            f"No text could be extracted from {file_name}."
        )

    chunks = chunk_text(extracted_text)

    if not chunks:
        raise ValueError(
            f"No usable text chunks were created for {file_name}."
        )

    embeddings = create_embeddings(chunks)

    file_id = create_file_id(file_bytes)

    store_embeddings(
        chunks,
        embeddings,
        file_name,
        file_id
    )

    return {
        "message": extraction_message,
        "chunks": len(chunks),
        "embeddings": len(embeddings),
    }


def build_context(documents, heading="ACADEMIC SOURCE"):
    """
    Build a formatted academic context from retrieved chunks.
    """

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(
            f"""
{heading} {index}
========================

{document}
"""
        )

    return "\n".join(context_parts)


def extract_questions_with_progress(pages):
    """
    Extract questions from a question paper with visible progress.

    Small papers are sent as one request. Larger papers are split into
    overlapping page-based chunks so that very large prompts do not have
    to be processed in a single AI request.
    """

    page_texts = [
        str(page.get("text", "")).strip()
        for page in pages
        if page.get("text")
    ]

    page_texts = [
        page_text
        for page_text in page_texts
        if page_text
    ]

    if not page_texts:
        return [], "unknown"

    full_text = "\n\n".join(page_texts)

    # Keep ordinary question papers as a single AI request.
    # This avoids unnecessary extra API calls for small papers.
    max_single_request_chars = 18000

    if len(full_text) <= max_single_request_chars:
        st.info(
            f"📄 Extracted {len(page_texts)} page(s) "
            f"({len(full_text):,} characters)."
        )

        with st.status(
            "🤖 Extracting questions with AI...",
            expanded=True
        ) as status:

            start_time = time.perf_counter()

            questions, provider_used = extract_questions(
                full_text
            )

            elapsed = time.perf_counter() - start_time

            status.update(
                label=(
                    f"✅ Question extraction completed "
                    f"in {elapsed:.1f} seconds."
                ),
                state="complete",
                expanded=False
            )

        return questions, provider_used

    # Large papers are split by pages rather than arbitrary character
    # positions so that a question is less likely to be cut in half.
    max_chunk_chars = 12000
    overlap_pages = 1

    chunks = []
    current_pages = []
    current_length = 0

    for page_text in page_texts:

        additional_length = len(page_text) + (
            2 if current_pages else 0
        )

        if (
            current_pages
            and current_length + additional_length > max_chunk_chars
        ):
            chunks.append(current_pages.copy())

            overlap = current_pages[-overlap_pages:]
            current_pages = overlap.copy()
            current_length = sum(
                len(page) for page in current_pages
            ) + max(0, len(current_pages) - 1) * 2

        current_pages.append(page_text)

        current_length = sum(
            len(page) for page in current_pages
        ) + max(0, len(current_pages) - 1) * 2

    if current_pages:
        chunks.append(current_pages.copy())

    all_questions = []
    providers = []

    st.info(
        f"📄 Extracted {len(page_texts)} page(s) "
        f"({len(full_text):,} characters). "
        f"Large paper detected — processing "
        f"{len(chunks)} AI extraction parts."
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    extraction_start = time.perf_counter()

    for index, chunk_pages in enumerate(
        chunks,
        start=1
    ):

        chunk_text = "\n\n".join(chunk_pages)

        status_text.info(
            f"🤖 Extracting questions — "
            f"part {index}/{len(chunks)} "
            f"({len(chunk_text):,} characters)"
        )

        questions, provider_used = extract_questions(
            chunk_text
        )

        if questions:
            all_questions.extend(questions)

        providers.append(provider_used)

        progress_bar.progress(
            index / len(chunks)
        )

    elapsed = time.perf_counter() - extraction_start

    status_text.success(
        f"✅ All extraction parts completed in "
        f"{elapsed:.1f} seconds."
    )

    # Remove duplicate questions caused by the overlapping page.
    unique_questions = []
    seen_questions = set()

    for question in all_questions:

        question_text = str(
            question.get("question_text", "")
        ).strip()

        normalized_text = " ".join(
            question_text.lower().split()
        )

        if not normalized_text:
            continue

        if normalized_text in seen_questions:
            continue

        seen_questions.add(normalized_text)
        unique_questions.append(question)

    # Give the final list stable numbering if the model returned
    # duplicated or inconsistent numbering across chunks.
    for index, question in enumerate(
        unique_questions,
        start=1
    ):
        question["question_number"] = str(index)

    provider_names = [
        str(provider)
        for provider in providers
        if provider
    ]

    if not provider_names:
        final_provider = "unknown"
    elif len(set(provider_names)) == 1:
        final_provider = provider_names[0]
    else:
        final_provider = "multiple providers"

    return unique_questions, final_provider


def evaluate_practice_test_batch(practice_questions, academic_context):
    """
    Evaluate all answered practice-test questions in one LLM request.

    This replaces one LLM call per question with a single structured
    evaluation request, which is substantially faster for multi-question
    tests.
    """

    evaluation_items = []

    for index, practice_question in enumerate(
        practice_questions,
        start=1
    ):

        question_number = practice_question.get(
            "question_number",
            index
        )

        question_text = practice_question.get(
            "question",
            practice_question.get(
                "question_text",
                ""
            )
        )

        student_answer = st.session_state.get(
            f"exam_answer_{index}",
            ""
        )

        evaluation_items.append(
            {
                "question_number": question_number,
                "question": question_text,
                "student_answer": student_answer,
            }
        )

    answered_items = [
        item
        for item in evaluation_items
        if str(item["student_answer"]).strip()
    ]

    results_by_number = {}

    # Do not spend an LLM request on unanswered questions.
    for item in evaluation_items:

        if not str(item["student_answer"]).strip():

            results_by_number[str(item["question_number"])] = {
                "result": "Not Attempted",
                "score": 0,
                "feedback": "No answer was provided.",
                "missing_points": [],
                "ideal_answer": "",
            }

    if not answered_items:
        return [
            (
                item,
                results_by_number[
                    str(item["question_number"])
                ],
                "none"
            )
            for item in evaluation_items
        ]

    compact_items = []

    for item in answered_items:

        compact_items.append(
            {
                "question_number": item["question_number"],
                "question": item["question"],
                "student_answer": item["student_answer"],
            }
        )

    prompt = f"""
You are an academic examiner evaluating a student's practice test.

Evaluate ALL answered questions below in ONE response.

Use the academic context as the primary reference.

ACADEMIC CONTEXT:
{academic_context}

QUESTIONS AND STUDENT ANSWERS:
{json.dumps(compact_items, ensure_ascii=False, indent=2)}

For every answered question:
- Score it from 0 to 10.
- Decide whether it is Correct, Partially Correct, or Incorrect.
- Give concise, useful feedback.
- List important missing points.
- Provide a concise ideal answer.
- Do not invent facts that are unsupported by the academic context.

Return ONLY a valid JSON array.
Use exactly this structure:

[
  {{
    "question_number": 1,
    "result": "Correct",
    "score": 8,
    "feedback": "Concise feedback.",
    "missing_points": ["Important missing point"],
    "ideal_answer": "Concise ideal answer."
  }}
]

Return one object for every answered question.
"""

    start_time = time.perf_counter()

    response_text, provider_used = generate_with_fallback(
        prompt,
        academic_context
    )

    elapsed = time.perf_counter() - start_time

    # Normalize the different response shapes that LangChain/Gemini may return.
    if isinstance(response_text, list):
        parts = []
        for part in response_text:
            if isinstance(part, dict):
                if part.get("text"):
                    parts.append(str(part["text"]))
            elif isinstance(part, str):
                parts.append(part)
        cleaned = "\n".join(parts).strip()
    elif isinstance(response_text, dict):
        cleaned = str(response_text.get("text", response_text.get("content", response_text))).strip()
    else:
        cleaned = str(response_text).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "", 1).strip()

    evaluation_data = None

    # First try parsing the entire response.
    try:
        evaluation_data = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        pass

    # Then locate JSON embedded inside explanatory text.
    if evaluation_data is None:
        decoder = json.JSONDecoder()
        positions = [p for p in (cleaned.find("["), cleaned.find("{")) if p >= 0]
        for position in sorted(positions):
            try:
                candidate, _ = decoder.raw_decode(cleaned[position:])
                evaluation_data = candidate
                break
            except json.JSONDecodeError:
                continue

    # Accept common wrapper formats such as {"results": [...]}.
    if isinstance(evaluation_data, dict):
        for key in ("results", "evaluations", "evaluation", "answers"):
            if isinstance(evaluation_data.get(key), list):
                evaluation_data = evaluation_data[key]
                break

    if not isinstance(evaluation_data, list):
        preview = cleaned[:500].replace("\n", " ")
        raise ValueError(
            "AI evaluation did not return a valid JSON array. "
            f"Response preview: {preview}"
        )

    for item in evaluation_data:

        question_number = str(
            item.get("question_number", "")
        )

        results_by_number[question_number] = {
            "result": str(
                item.get("result", "N/A")
            ),
            "score": item.get("score", 0),
            "feedback": str(
                item.get(
                    "feedback",
                    "No feedback available."
                )
            ),
            "missing_points": item.get(
                "missing_points",
                []
            ),
            "ideal_answer": str(
                item.get(
                    "ideal_answer",
                    ""
                )
            ),
        }

    final_results = []

    for item in evaluation_items:

        question_number = str(
            item["question_number"]
        )

        evaluation = results_by_number.get(
            question_number,
            {
                "result": "Evaluation Unavailable",
                "score": 0,
                "feedback": (
                    "No evaluation was returned "
                    "for this question."
                ),
                "missing_points": [],
                "ideal_answer": "",
            }
        )

        final_results.append(
            (
                item,
                evaluation,
                provider_used
            )
        )

    return final_results


def display_performance_dashboard():
    """
    Display the Week 6/7 performance dashboard.
    """

    history = st.session_state.get(
        "performance_history",
        []
    )

    if not history:

        st.info(
            "No performance data is available yet. "
            "Complete a practice test to start tracking performance."
        )

        return

    summary = get_performance_summary(history)

    overall = summary["overall"]
    topic_performance = summary["topic_performance"]
    weak_areas = summary["weak_areas"]
    strong_areas = summary["strong_areas"]
    recommendations = summary["recommendations"]

    # ----------------------------------------------
    # Overall metrics
    # ----------------------------------------------

    st.subheader("📈 Overall Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tests Attempted",
            overall["tests_attempted"]
        )

    with col2:
        st.metric(
            "Total Score",
            f"{overall['total_score']:g}/{overall['total_marks']:g}"
        )

    with col3:
        st.metric(
            "Overall Percentage",
            f"{overall['percentage']:.1f}%"
        )

    with col4:
        st.metric(
            "Topics Tracked",
            len(topic_performance)
        )

    st.divider()

    # ----------------------------------------------
    # Topic-wise performance
    # ----------------------------------------------

    st.subheader("📚 Topic-Wise Performance")

    if topic_performance:

        topic_rows = []

        for topic, data in topic_performance.items():

            topic_rows.append(
                {
                    "Topic": topic,
                    "Tests": data["tests"],
                    "Score": (
                        f"{data['score']:g}/"
                        f"{data['total_marks']:g}"
                    ),
                    "Percentage": (
                        f"{data['percentage']:.1f}%"
                    ),
                }
            )

        st.table(topic_rows)

        # Native Streamlit chart
        chart_data = {
            topic: data["percentage"]
            for topic, data in topic_performance.items()
        }

        st.caption("Topic performance")

        st.bar_chart(chart_data)

    else:

        st.info(
            "Topic-wise performance is not available yet."
        )

    st.divider()

    # ----------------------------------------------
    # Weak and strong areas
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔎 Weak Areas")

        if weak_areas:

            for area in weak_areas:

                st.warning(
                    f"**{area['topic']}** — "
                    f"{area['percentage']:.1f}%"
                )

        else:

            st.success(
                "No weak areas identified using the current threshold."
            )

    with col2:

        st.subheader("⭐ Strong Areas")

        if strong_areas:

            for area in strong_areas:

                st.success(
                    f"**{area['topic']}** — "
                    f"{area['percentage']:.1f}%"
                )

        else:

            st.info(
                "No strong areas identified yet."
            )

    st.divider()

    # ----------------------------------------------
    # Recommendations
    # ----------------------------------------------

    st.subheader("💡 Personalized Recommendations")

    if recommendations:

        for recommendation in recommendations:

            priority = recommendation["priority"]
            topic = recommendation["topic"]
            percentage = recommendation["percentage"]
            action = recommendation["recommendation"]

            with st.container():

                st.markdown(
                    f"### {topic}"
                )

                st.write(
                    f"Current performance: "
                    f"**{percentage:.1f}%**"
                )

                st.write(
                    f"Priority: **{priority}**"
                )

                st.info(action)

    else:

        st.success(
            "No additional recommendations are required "
            "based on the current performance data."
        )

    st.divider()

    # ----------------------------------------------
    # Performance history
    # ----------------------------------------------

    st.subheader("🕒 Practice Test History")

    history_rows = []

    for index, record in enumerate(
        history,
        start=1
    ):

        history_rows.append(
            {
                "Test": index,
                "Topic": record.get(
                    "topic",
                    "Unknown"
                ),
                "Difficulty": record.get(
                    "difficulty",
                    "Unknown"
                ),
                "Score": (
                    f"{float(record.get('score', 0)):g}/"
                    f"{float(record.get('total_marks', 0)):g}"
                ),
                "Percentage": (
                    f"{float(record.get('percentage', 0)):.1f}%"
                    if "percentage" in record
                    else (
                        f"{(float(record.get('score', 0)) / float(record.get('total_marks', 1)) * 100):.1f}%"
                        if float(record.get("total_marks", 0)) > 0
                        else "0.0%"
                    )
                ),
            }
        )

    st.table(history_rows)


# ==================================================
# HEADER
# ==================================================

if st.session_state.get("main_navigation", "🏠 Dashboard") != "🏠 Dashboard":

    st.title("📚 VidyānVaya AI")

    st.subheader(
        "A Subject-Agnostic Academic Learning Assistant"
    )

    st.write(
        "Upload your academic materials and use AI to "
        "learn, solve questions, practice, analyze performance, "
        "and improve."
    )


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("📚 VidyānVaya AI")

st.sidebar.caption(
    "Academic Learning Assistant"
)

st.sidebar.text_input(
    "Your name",
    key="user_name",
    placeholder="Optional"
)

nav_item = st.sidebar.radio(
    "Navigate",
    NAV_ITEMS,
    key="main_navigation",
    format_func=_nav_label,
    label_visibility="collapsed"
)

page = resolve_navigation(nav_item)

st.sidebar.divider()

# Database status in sidebar

total_embeddings = get_collection_count()

st.sidebar.metric(
    "Stored Text Chunks",
    total_embeddings
)

documents_available = get_document_names()

st.sidebar.metric(
    "Processed Documents",
    len(documents_available)
)


# ==================================================
# PAGE 0 — DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    render_dashboard(
        user_name=st.session_state.get("user_name", ""),
        documents=get_document_names(),
        chunk_count=get_collection_count(),
        questions=st.session_state["extracted_questions"],
        history=st.session_state["performance_history"],
        get_performance_summary=get_performance_summary,
    )


# ==================================================
# PAGE 1 — MATERIALS
# ==================================================

elif page == "📚 Materials":

    st.header("📚 Academic Materials")

    st.write(
        "Upload your notes, textbooks, question papers, "
        "or presentations and add them to the academic knowledge base."
    )

    st.divider()

    uploaded_files = st.file_uploader(
        "Upload academic materials",
        type=[
            "pdf",
            "docx",
            "pptx"
        ],
        accept_multiple_files=True,
        key="academic_file_uploader"
    )

    if uploaded_files:

        save_uploaded_files(uploaded_files)

        st.success(
            f"{len(uploaded_files)} file(s) selected."
        )

        st.subheader("📄 Selected Files")

        for file in uploaded_files:

            st.write(
                f"• {file.name}"
            )

        st.divider()

        if st.button(
            "⚙️ Process / Update Documents",
            type="primary",
            key="process_documents_button"
        ):

            progress_container = st.container()

            with progress_container:

                for file in uploaded_files:

                    st.write(
                        f"📄 Processing: **{file.name}**"
                    )

                    try:

                        result = process_single_document(
                            file.name,
                            file.getvalue()
                        )

                        st.success(
                            f"✅ {file.name} processed successfully."
                        )

                        st.caption(
                            result["message"]
                        )

                        st.caption(
                            f"Created {result['chunks']} "
                            f"chunks and {result['embeddings']} "
                            f"embeddings."
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not process "
                            f"{file.name}: {e}"
                        )

    else:

        if st.session_state["uploaded_files_data"]:

            st.info(
                "Previously selected files are stored for this session."
            )

        else:

            st.info(
                "Upload academic materials to get started."
            )

    st.divider()

    # ----------------------------------------------
    # Processed documents
    # ----------------------------------------------

    st.subheader("📚 Processed Academic Materials")

    processed_documents = get_document_names()

    if processed_documents:

        for document in processed_documents:

            st.success(
                f"📖 {document}"
            )

    else:

        st.info(
            "No documents have been processed yet."
        )

    st.divider()

    # ----------------------------------------------
    # Database information
    # ----------------------------------------------

    st.subheader("🗄️ Knowledge Base Status")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Processed Documents",
            len(processed_documents)
        )

    with col2:

        st.metric(
            "Stored Text Chunks",
            get_collection_count()
        )


# ==================================================
# PAGE 2 — LEARN
# ==================================================

elif page == "🧠 Learn":

    st.header("🧠 Learn")

    st.write(
        "Learn from your uploaded academic material "
        "using grounded AI responses."
    )

    learn_mode = st.radio(
        "Choose a learning mode",
        [
            "🔍 Subject Guide",
            "🧠 Question Solver",
        ],
        horizontal=True,
        key="learn_mode"
    )

    st.divider()

    documents = get_document_names()

    if not documents:

        st.warning(
            "No academic material is available. "
            "Go to **📚 Materials** and process a document first."
        )

    else:

        # ==================================================
        # SUBJECT GUIDE
        # ==================================================

        if learn_mode == "🔍 Subject Guide":

            st.subheader("🔍 Ask VidyānVaya AI")

            selected_document = st.selectbox(
                "📚 Select academic material",
                documents,
                key="subject_guide_document"
            )

            st.success(
                f"📖 Currently using: **{selected_document}**"
            )

            query = st.text_area(
                "Enter your question",
                placeholder=(
                    "Example: Explain the OSI model "
                    "with its seven layers."
                ),
                height=100,
                key="subject_guide_query"
            )

            if st.button(
                "🤖 Ask VidyānVaya AI",
                type="primary",
                key="subject_guide_button"
            ):

                if not query.strip():

                    st.warning(
                        "Please enter a question."
                    )

                else:

                    try:

                        with st.spinner(
                            "🔎 Searching the selected document..."
                        ):

                            results = retrieve_relevant_chunks(
                                query=query,
                                source_name=selected_document,
                                n_results=5
                            )

                        documents_found = results.get(
                            "documents",
                            [[]]
                        )[0]

                        distances = results.get(
                            "distances",
                            [[]]
                        )[0]

                        if not documents_found:

                            st.warning(
                                "No relevant information was "
                                "found in this document."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(documents_found)} "
                                f"relevant text chunks."
                            )

                            context = build_context(
                                documents_found,
                                heading="SOURCE CHUNK"
                            )

                            with st.spinner(
                                "🤖 Generating answer..."
                            ):

                                answer, provider_used = (
                                    generate_with_fallback(
                                        query,
                                        context
                                    )
                                )

                            st.divider()

                            st.subheader("💡 Answer")

                            st.markdown(answer)

                            st.caption(
                                f"🤖 Generated by: "
                                f"{provider_used.capitalize()}"
                            )

                            with st.expander(
                                "📚 View retrieved source information"
                            ):

                                st.caption(
                                    f"Source document: "
                                    f"{selected_document}"
                                )

                                for index, document in enumerate(
                                    documents_found,
                                    start=1
                                ):

                                    st.markdown(
                                        f"### Source {index}"
                                    )

                                    st.write(document)

                                    if index <= len(distances):

                                        st.caption(
                                            f"Distance: "
                                            f"{distances[index - 1]:.4f}"
                                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not retrieve or "
                            f"generate answer: {e}"
                        )

        # ==================================================
        # QUESTION SOLVER
        # ==================================================

        else:

            st.subheader("🧠 Question Solver")

            questions = st.session_state.get(
                "extracted_questions",
                []
            )

            if not questions:

                st.info(
                    "No extracted questions are available yet. "
                    "Go to **📝 Practice → Question Bank** "
                    "to extract questions from a question paper."
                )

            else:

                selected_solver_document = st.selectbox(
                    "📚 Select study material",
                    documents,
                    key="solver_document_selector"
                )

                question_options = [
                    (
                        question.get(
                            "question_number",
                            ""
                        ),
                        question.get(
                            "question_text",
                            ""
                        )
                    )
                    for question in questions
                ]

                selected_question = st.selectbox(
                    "❓ Select a question to solve",
                    question_options,
                    format_func=lambda q: (
                        f"{q[0]} — "
                        f"{q[1][:120]}"
                        + (
                            "..."
                            if len(q[1]) > 120
                            else ""
                        )
                    ),
                    key="solver_question_selector"
                )

                question_number = selected_question[0]
                question_text = selected_question[1]

                st.markdown(
                    "### ❓ Selected Question"
                )

                st.info(
                    f"**{question_number}**\n\n"
                    f"{question_text}"
                )

                if st.button(
                    "🧠 Solve Question",
                    type="primary",
                    key="solve_question_button"
                ):

                    try:

                        with st.spinner(
                            "🔎 Searching your academic material..."
                        ):

                            results = retrieve_relevant_chunks(
                                query=question_text,
                                source_name=selected_solver_document,
                                n_results=5
                            )

                        documents_found = results.get(
                            "documents",
                            [[]]
                        )[0]

                        distances = results.get(
                            "distances",
                            [[]]
                        )[0]

                        if not documents_found:

                            st.warning(
                                "No relevant information was found "
                                "in the selected academic material."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(documents_found)} "
                                f"relevant academic chunks."
                            )

                            academic_context = build_context(
                                documents_found,
                                heading="ACADEMIC SOURCE"
                            )

                            solver_context = f"""
You are VidyānVaya AI's Question Solver.

Answer the student's examination question using ONLY the
retrieved academic material below as the primary source.

Requirements:
- Answer every sub-part.
- Use clear exam-oriented headings and bullet points.
- Include definitions, explanations, formulas, examples, or
  calculation steps when supported by the material.
- Keep the answer complete but concise.
- Do not introduce unrelated information.
- Do not invent unsupported facts or formulas.
- If the material is insufficient, say:
  "I could not find enough information in the uploaded materials
  to answer this question."

RETRIEVED ACADEMIC MATERIAL
===========================
{academic_context}

STUDENT QUESTION
================
{question_text}

Now provide the final exam-oriented answer.
"""

                            generation_start = time.perf_counter()

                            with st.spinner(
                                "🤖 Generating exam-ready solution..."
                            ):

                                answer, provider_used = (
                                    generate_with_fallback(
                                        question_text,
                                        solver_context
                                    )
                                )

                            generation_elapsed = (
                                time.perf_counter() - generation_start
                            )

                            st.success(
                                f"✅ Solution generated in "
                                f"{generation_elapsed:.1f} seconds "
                                f"using {provider_used.capitalize()}."
                            )

                            st.divider()

                            st.header("💡 Solution")

                            st.markdown(answer)

                            st.caption(
                                f"🤖 Generated by: "
                                f"{provider_used.capitalize()}"
                            )

                            with st.expander(
                                "📚 View academic sources used"
                            ):

                                st.caption(
                                    f"Study material: "
                                    f"{selected_solver_document}"
                                )

                                for index, document in enumerate(
                                    documents_found,
                                    start=1
                                ):

                                    st.markdown(
                                        f"### Source {index}"
                                    )

                                    st.write(document)

                                    if index <= len(distances):

                                        st.caption(
                                            f"Distance: "
                                            f"{distances[index - 1]:.4f}"
                                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not solve the question: {e}"
                        )


# ==================================================
# PAGE 3 — PRACTICE
# ==================================================

elif page == "📝 Practice":

    st.header("📝 Practice")

    st.write(
        "Practice with previous-year questions and "
        "AI-generated examination tests."
    )

    practice_mode = st.radio(
        "Choose a practice mode",
        [
            "📝 Question Bank",
            "🎯 Exam Preparation",
        ],
        horizontal=True,
        key="practice_mode"
    )

    st.divider()

    # ==================================================
    # QUESTION BANK
    # ==================================================

    if practice_mode == "📝 Question Bank":

        st.subheader("📝 Question Bank")

        st.write(
            "Upload or select a question paper. "
            "VidyānVaya AI first extracts the PDF text and then "
            "identifies the individual questions."
        )

        pdf_names = get_uploaded_pdf_names()

        if not pdf_names:

            st.warning(
                "No PDF question paper is available in the "
                "current session. Go to **📚 Materials** "
                "and upload a PDF question paper."
            )

        else:

            selected_question_paper = st.selectbox(
                "Select a question paper",
                pdf_names,
                key="question_paper_selector"
            )

            if st.button(
                "📝 Extract Questions",
                type="primary",
                key="extract_questions_button"
            ):

                try:

                    question_paper_file = create_file_object(
                        selected_question_paper
                    )

                    if question_paper_file is None:

                        st.error(
                            "Could not load the selected question paper."
                        )

                    else:

                        with st.status(
                            "🔎 Reading question paper...",
                            expanded=True
                        ) as pdf_status:

                            pdf_start = time.perf_counter()

                            st.write(
                                "📄 Extracting text from the PDF..."
                            )

                            pages = extract_text_from_pdf(
                                question_paper_file
                            )

                            page_count = len(pages)

                            question_paper_text = "\n".join(
                                page["text"]
                                for page in pages
                                if page.get("text")
                            )

                            pdf_elapsed = (
                                time.perf_counter() - pdf_start
                            )

                            if not question_paper_text.strip():

                                pdf_status.update(
                                    label=(
                                        "❌ No text could be extracted "
                                        "from the question paper."
                                    ),
                                    state="error",
                                    expanded=True
                                )

                                st.warning(
                                    "No text could be extracted "
                                    "from the selected question paper."
                                )

                            else:

                                pdf_status.update(
                                    label=(
                                        f"✅ PDF text extracted — "
                                        f"{page_count} page(s) in "
                                        f"{pdf_elapsed:.1f} seconds."
                                    ),
                                    state="complete",
                                    expanded=False
                                )

                                questions, provider_used = (
                                    extract_questions_with_progress(
                                        pages
                                    )
                                )

                                st.session_state[
                                    "extracted_questions"
                                ] = questions

                                st.session_state[
                                    "question_bank_provider"
                                ] = provider_used

                                st.session_state[
                                    "question_bank_source"
                                ] = selected_question_paper

                                if questions:

                                    st.success(
                                        f"✅ Extracted "
                                        f"{len(questions)} questions "
                                        f"from "
                                        f"{selected_question_paper}"
                                    )

                                else:

                                    st.warning(
                                        "No questions could be identified "
                                        "in the selected question paper."
                                    )

                except Exception as e:

                    st.error(
                        f"❌ Could not extract questions: {e}"
                    )

        # ----------------------------------------------
        # Display extracted questions
        # ----------------------------------------------

        questions = st.session_state.get(
            "extracted_questions",
            []
        )

        if questions:

            provider_used = st.session_state.get(
                "question_bank_provider",
                "unknown"
            )

            source_name = st.session_state.get(
                "question_bank_source",
                "Unknown"
            )

            st.divider()

            st.success(
                f"✅ {len(questions)} questions available "
                f"from {source_name}"
            )

            st.caption(
                f"🤖 Generated by: "
                f"{provider_used.capitalize()}"
            )

            st.subheader("📋 Extracted Questions")

            for question in questions:

                question_number = question.get(
                    "question_number",
                    ""
                )

                question_text = question.get(
                    "question_text",
                    ""
                )

                with st.container():

                    st.markdown(
                        f"### {question_number}"
                    )

                    st.write(
                        question_text
                    )

                    st.divider()

        else:

            st.info(
                "No questions have been extracted yet."
            )

    # ==================================================
    # EXAM PREPARATION
    # ==================================================

    else:

        st.subheader("🎯 Exam Preparation")

        st.write(
            "Generate AI-powered practice questions from "
            "your uploaded academic material and evaluate your answers."
        )

        exam_documents = get_document_names()

        if not exam_documents:

            st.info(
                "Upload and process academic material first "
                "to start exam preparation."
            )

        else:

            st.subheader("📚 Practice Test Setup")

            selected_exam_document = st.selectbox(
                "Select study material",
                exam_documents,
                key="exam_prep_document_selector"
            )

            col1, col2 = st.columns(2)

            with col1:

                exam_topic = st.text_input(
                    "Topic",
                    placeholder=(
                        "Example: Computer Organization"
                    ),
                    key="exam_prep_topic_input"
                )

            with col2:

                exam_difficulty = st.selectbox(
                    "Difficulty",
                    [
                        "Easy",
                        "Medium",
                        "Hard"
                    ],
                    index=1,
                    key="exam_prep_difficulty_selector"
                )

            exam_question_count = st.slider(
                "Number of questions",
                min_value=1,
                max_value=10,
                value=3,
                key="exam_prep_question_count"
            )

            if st.button(
                "🎯 Generate Practice Test",
                type="primary",
                key="generate_practice_test_button"
            ):

                if not exam_topic.strip():

                    st.warning(
                        "Please enter a topic before generating "
                        "the practice test."
                    )

                else:

                    try:

                        with st.spinner(
                            "🔎 Searching your academic material..."
                        ):

                            exam_results = (
                                retrieve_relevant_chunks(
                                    query=exam_topic,
                                    source_name=selected_exam_document,
                                    n_results=8
                                )
                            )

                        exam_documents_found = (
                            exam_results.get(
                                "documents",
                                [[]]
                            )[0]
                        )

                        if not exam_documents_found:

                            st.warning(
                                "No relevant academic material was found "
                                "for this topic."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(exam_documents_found)} "
                                f"relevant academic chunks."
                            )

                            exam_context = build_context(
                                exam_documents_found,
                                heading="ACADEMIC SOURCE"
                            )

                            with st.spinner(
                                "🤖 Generating practice questions..."
                            ):

                                (
                                    practice_questions,
                                    provider_used
                                ) = generate_practice_test(
                                    academic_context=exam_context,
                                    number_of_questions=(
                                        exam_question_count
                                    ),
                                    difficulty=exam_difficulty,
                                    topic=exam_topic
                                )

                            if not practice_questions:

                                st.warning(
                                    "The AI could not generate practice "
                                    "questions from the selected material."
                                )

                            else:

                                st.session_state[
                                    "exam_prep_questions"
                                ] = practice_questions

                                st.session_state[
                                    "exam_prep_provider"
                                ] = provider_used

                                st.session_state[
                                    "exam_prep_document"
                                ] = selected_exam_document

                                st.session_state[
                                    "exam_prep_topic"
                                ] = exam_topic

                                st.session_state[
                                    "exam_prep_difficulty"
                                ] = exam_difficulty

                                st.session_state[
                                    "exam_prep_context"
                                ] = exam_context

                                st.session_state[
                                    "exam_prep_source_chunks"
                                ] = exam_documents_found

                                st.session_state.pop(
                                    "exam_prep_results",
                                    None
                                )

                                st.session_state[
                                    "exam_prep_total_score"
                                ] = 0

                                st.success(
                                    f"✅ Generated "
                                    f"{len(practice_questions)} "
                                    f"practice questions."
                                )

                                st.caption(
                                    f"🤖 Generated by: "
                                    f"{provider_used.capitalize()}"
                                )

                    except Exception as e:

                        st.error(
                            f"❌ Could not generate practice test: {e}"
                        )

            # ------------------------------------------
            # Display generated practice test
            # ------------------------------------------

            practice_questions = st.session_state.get(
                "exam_prep_questions",
                []
            )

            if practice_questions:

                st.divider()

                st.subheader("📋 Practice Test")

                st.caption(
                    f"Study material: "
                    f"{st.session_state.get('exam_prep_document', 'Unknown')}"
                )

                st.caption(
                    f"Topic: "
                    f"{st.session_state.get('exam_prep_topic', 'Unknown')}"
                    f" | Difficulty: "
                    f"{st.session_state.get('exam_prep_difficulty', 'Medium')}"
                )

                for index, practice_question in enumerate(
                    practice_questions,
                    start=1
                ):

                    question_number = (
                        practice_question.get(
                            "question_number",
                            index
                        )
                    )

                    question_text = (
                        practice_question.get(
                            "question",
                            practice_question.get(
                                "question_text",
                                ""
                            )
                        )
                    )

                    question_difficulty = (
                        practice_question.get(
                            "difficulty",
                            st.session_state.get(
                                "exam_prep_difficulty",
                                "Medium"
                            )
                        )
                    )

                    st.markdown(
                        f"### Question {question_number}"
                    )

                    st.write(question_text)

                    st.caption(
                        f"Difficulty: {question_difficulty}"
                    )

                    st.text_area(
                        "Your answer",
                        key=f"exam_answer_{index}",
                        height=160
                    )

                    st.divider()

                if st.button(
                    "✅ Submit Practice Test",
                    type="primary",
                    key="submit_exam_prep_button"
                ):

                    evaluation_results = []
                    total_score = 0

                    with st.status(
                        "🤖 Evaluating your practice test...",
                        expanded=True
                    ) as evaluation_status:

                        evaluation_start = time.perf_counter()

                        st.write(
                            "📚 Preparing all answered questions "
                            "for one AI evaluation request..."
                        )

                        batch_results = (
                            evaluate_practice_test_batch(
                                practice_questions,
                                st.session_state[
                                    "exam_prep_context"
                                ]
                            )
                        )

                        for (
                            item,
                            evaluation,
                            evaluation_provider
                        ) in batch_results:

                            score = evaluation.get(
                                "score",
                                0
                            )

                            try:
                                score = float(score)
                            except (
                                TypeError,
                                ValueError
                            ):
                                score = 0

                            score = max(
                                0,
                                min(10, score)
                            )

                            total_score += score

                            evaluation_results.append(
                                {
                                    "question_number":
                                        item[
                                            "question_number"
                                        ],
                                    "question":
                                        item[
                                            "question"
                                        ],
                                    "student_answer":
                                        item[
                                            "student_answer"
                                        ],
                                    "evaluation":
                                        evaluation,
                                    "provider":
                                        evaluation_provider
                                }
                            )

                        evaluation_elapsed = (
                            time.perf_counter()
                            - evaluation_start
                        )

                        evaluation_status.update(
                            label=(
                                f"✅ Practice test evaluated in "
                                f"{evaluation_elapsed:.1f} seconds."
                            ),
                            state="complete",
                            expanded=False
                        )

                    st.session_state[
                        "exam_prep_results"
                    ] = evaluation_results

                    st.session_state[
                        "exam_prep_total_score"
                    ] = total_score

                    # ------------------------------------------
                    # Week 6 performance tracking
                    # ------------------------------------------

                    practice_record = {
                        "topic": (
                            st.session_state.get(
                                "exam_prep_topic",
                                "Unknown"
                            )
                        ),
                        "difficulty": (
                            st.session_state.get(
                                "exam_prep_difficulty",
                                "Medium"
                            )
                        ),
                        "score": total_score,
                        "total_marks": (
                            len(evaluation_results) * 10
                        ),
                        "questions_attempted": (
                            len(evaluation_results)
                        ),
                    }

                    st.session_state[
                        "performance_history"
                    ].append(
                        practice_record
                    )

                    save_performance_history(
                        st.session_state["performance_history"]
                    )

                    st.success(
                        "✅ Practice test evaluated successfully."
                    )

                # ------------------------------------------
                # Display evaluation results
                # ------------------------------------------

                evaluation_results = st.session_state.get(
                    "exam_prep_results",
                    []
                )

                if evaluation_results:

                    st.divider()

                    st.subheader(
                        "📊 Your Performance"
                    )

                    total_score = st.session_state.get(
                        "exam_prep_total_score",
                        0
                    )

                    max_score = (
                        len(evaluation_results) * 10
                    )

                    percentage = (
                        (total_score / max_score) * 100
                        if max_score > 0
                        else 0
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Score",
                            f"{total_score:g}/{max_score}"
                        )

                    with col2:

                        st.metric(
                            "Percentage",
                            f"{percentage:.1f}%"
                        )

                    with col3:

                        st.metric(
                            "Questions",
                            len(evaluation_results)
                        )

                    for result in evaluation_results:

                        evaluation = result[
                            "evaluation"
                        ]

                        st.markdown(
                            f"### Question "
                            f"{result['question_number']}"
                        )

                        st.write(
                            result["question"]
                        )

                        st.markdown(
                            "**Your Answer:**"
                        )

                        if result[
                            "student_answer"
                        ].strip():

                            st.write(
                                result["student_answer"]
                            )

                        else:

                            st.write(
                                "*Not attempted*"
                            )

                        st.markdown(
                            f"**Result:** "
                            f"{evaluation.get('result', 'N/A')}"
                        )

                        st.markdown(
                            f"**Score:** "
                            f"{evaluation.get('score', 0)}/10"
                        )

                        st.markdown(
                            "**Feedback:**"
                        )

                        st.write(
                            evaluation.get(
                                "feedback",
                                "No feedback available."
                            )
                        )

                        missing_points = (
                            evaluation.get(
                                "missing_points",
                                []
                            )
                        )

                        if missing_points:

                            st.markdown(
                                "**Points to Improve:**"
                            )

                            for point in missing_points:

                                st.write(
                                    f"- {point}"
                                )

                        ideal_answer = (
                            evaluation.get(
                                "ideal_answer",
                                ""
                            )
                        )

                        if ideal_answer:

                            with st.expander(
                                "💡 View Ideal Answer"
                            ):

                                st.write(
                                    ideal_answer
                                )

                        st.divider()


# ==================================================
# PAGE 4 — PERFORMANCE
# ==================================================

elif page == "📊 Performance":

    st.header("📊 Performance Dashboard")

    st.write(
        "Analyze your practice-test performance, "
        "identify weak and strong areas, and view "
        "personalized study recommendations."
    )

    st.divider()

    render_performance_insights(
        st.session_state["performance_history"]
    )

    display_performance_dashboard()


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "VidyānVaya AI — AI-powered academic learning assistant"
)