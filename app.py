import streamlit as st
import ollama
import hashlib
import json
import re
import random

from database import (
    init_db, get_user, create_user,
    get_user_sessions, create_session, update_session,
)
from prompts import (
    get_pre_quiz_prompt, get_teaching_prompt,
    get_post_quiz_prompt, get_roadmap_prompt, get_revision_prompt,
)

# ──────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────
init_db()
st.set_page_config(page_title="VidyaPath", page_icon="🎓", layout="wide")

# ──────────────────────────────────────────────
# LANGUAGE
# ──────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

LANGUAGES = {
    "EN": {
        "app_name":      "VidyaPath",
        "tagline":       "Your personal AI tutor — adaptive, patient, always there for you.",
        "welcome":       "What do you want to learn today",
        "placeholder":   "e.g., Photosynthesis, Python loops, Newton's Laws…",
        "start_learning": "Start Learning 🚀",
    },
    "HI": {
        "app_name":      "विद्यापथ",
        "tagline":       "आपका व्यक्तिगत AI शिक्षक — अनुकूलनीय, धैर्यवान, हमेशा आपके साथ।",
        "welcome":       "आज क्या सीखना चाहते हैं",
        "placeholder":   "जैसे, प्रकाश संश्लेषण, Python लूप, न्यूटन के नियम…",
        "start_learning": "सीखना शुरू करें 🚀",
    },
}


def t(key):
    return LANGUAGES[st.session_state.lang].get(key, key)


# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;800&family=DM+Sans:wght@400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a, #0f1422); color: #e8eaf6; }
[data-testid="stSidebar"] {
    background: rgba(10,14,26,0.98) !important;
    border-right: 1px solid #1e2540;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem !important; max-width: 960px; margin: auto; }

/* HERO */
.hero { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb, #4fc3f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .3rem;
}
.hero p { color: #5c6bc0; font-size: 1.1rem; }

/* CARDS */
.auth-card {
    background: rgba(17,24,39,0.97);
    border: 1px solid #1e2d4a;
    border-radius: 20px;
    padding: 2.2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,.4);
}
.topic-card {
    background: rgba(17,24,39,0.8);
    border: 1px solid #1e2d4a;
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    transition: all .2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102,126,234,.45) !important;
}

/* MCQ */
.mcq-box {
    background: rgba(17,24,39,.65);
    border: 1px solid #2d3a5e;
    border-radius: 20px;
    padding: 1.8rem;
    margin: 1.5rem 0;
}
.mcq-q {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 1.2rem;
    padding-bottom: .7rem;
    border-bottom: 2px solid #667eea;
    color: #e8eaf6;
}

/* FEEDBACK */
.fb-ok {
    background: rgba(76,175,80,.15);
    border-left: 4px solid #4caf50;
    padding: .9rem 1.2rem;
    border-radius: 10px;
    margin: .8rem 0;
    color: #a5d6a7;
}
.fb-bad {
    background: rgba(244,67,54,.15);
    border-left: 4px solid #f44336;
    padding: .9rem 1.2rem;
    border-radius: 10px;
    margin: .8rem 0;
    color: #ef9a9a;
}

/* LEVEL BADGES */
.level-badge {
    display: inline-block;
    padding: 5px 20px;
    border-radius: 25px;
    font-size: .85rem;
    font-weight: bold;
    margin-bottom: 1rem;
}
.lvl-b { background: rgba(76,175,80,.2);  border: 1px solid #4caf50; color: #a5d6a7; }
.lvl-i { background: rgba(255,193,7,.2);  border: 1px solid #ffc107; color: #fff59d; }
.lvl-a { background: rgba(244,67,54,.2);  border: 1px solid #f44336; color: #ef9a9a; }

/* PROGRESS DOTS */
.dots { display: flex; gap: 12px; justify-content: center; margin: 1.2rem 0; }
.dot  { width: 13px; height: 13px; border-radius: 50%; background: #2d3a5e; transition: all .3s; }
.dot.active { background: #667eea; transform: scale(1.3); box-shadow: 0 0 8px #667eea; }
.dot.done   { background: #4caf50; }

/* HEADINGS */
.sec-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    margin-bottom: .3rem;
    background: linear-gradient(135deg, #e8eaf6, #9fa8da);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sec-sub   { color: #5c6bc0; margin-bottom: 1.2rem; font-size: .95rem; }
.chip {
    display: inline-block;
    background: rgba(102,126,234,.2);
    border: 1px solid #667eea;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: .85rem;
    color: #9fa8da;
    margin-bottom: .8rem;
}

/* WIN BOX */
.win-box {
    background: linear-gradient(135deg, rgba(76,175,80,.2), rgba(0,150,136,.2));
    border: 2px solid #4caf50;
    border-radius: 24px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}
.win-box h2 { color: #a5d6a7; font-size: 2rem; margin-bottom: .4rem; }

/* INPUT */
.stTextInput > div > input {
    background: rgba(17,24,39,.8) !important;
    border: 1px solid #2d3a5e !important;
    border-radius: 10px !important;
    color: #e8eaf6 !important;
    padding: .7rem 1rem !important;
}
.stTextInput > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102,126,234,.25) !important;
}

/* CHAT */
[data-testid="stChatMessage"] {
    background: rgba(17,24,39,.6) !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 14px !important;
    margin-bottom: .8rem !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# LLM HELPERS
# ──────────────────────────────────────────────
def llm(messages, spinner_text="Thinking…"):
    """Call phi3 via Ollama; return full response string."""
    try:
        stream = ollama.chat(model="phi3", messages=messages, stream=True)
        full = ""
        for chunk in stream:
            full += chunk["message"]["content"]
        return full
    except Exception as e:
        st.error(f"Ollama error: {e}")
        return ""


def llm_stream(messages):
    """Streaming generator for teaching chat."""
    try:
        stream = ollama.chat(model="phi3", messages=messages, stream=True)
        for chunk in stream:
            yield chunk["message"]["content"]
    except Exception as e:
        st.error(f"Ollama error: {e}")
        yield ""


# ──────────────────────────────────────────────
# QUESTION PARSING
# ──────────────────────────────────────────────
def parse_all_questions(raw_text):
    """
    Parse all ###Qn### ... ###END### blocks from a single LLM response.

    Returns a list of dicts:
      {
        "question":      str,
        "options":       {"A": str, "B": str, "C": str, "D": str},
        "correct_text":  str,   # text of the correct option (immune to re-labelling)
        "explanation":   str,
      }
    Options are shuffled randomly to neutralise phi3's D-always-correct bias.
    """
    questions = []
    blocks = re.split(r"###Q\d+###", raw_text, flags=re.IGNORECASE)

    for block in blocks:
        end_idx = re.search(r"###END###", block, re.IGNORECASE)
        if end_idx:
            block = block[: end_idx.start()]
        block = block.strip()
        if not block:
            continue

        # QUESTION
        q_match = re.search(
            r"QUESTION:\s*(.+?)(?=\nA\)|\nA \.|\Z)", block, re.DOTALL | re.IGNORECASE
        )
        if not q_match:
            continue
        question = re.sub(r"\s+", " ", q_match.group(1).strip())

        # OPTIONS A-D
        raw_options = {}
        for letter in ["A", "B", "C", "D"]:
            pat = rf"(?:^|\n)\s*{letter}[)\.]\s*(.+?)(?=\n\s*[A-D][)\.]|\nCORRECT|\nEXPLAIN|\Z)"
            m = re.search(pat, block, re.DOTALL | re.IGNORECASE)
            if m:
                raw_options[letter] = re.sub(r"\s+", " ", m.group(1).strip())

        if len(raw_options) < 2:
            continue

        # CORRECT letter → correct text
        correct_text = None
        c_match = re.search(r"CORRECT:\s*([A-D])", block, re.IGNORECASE)
        if c_match:
            cl = c_match.group(1).upper()
            correct_text = raw_options.get(cl)

        # Fallback patterns
        if not correct_text:
            for pat in [
                r"(?:correct answer is|the answer is)\s*[\"']?([A-D])[\"']?",
                r"\b([A-D])\s+is\s+(?:correct|right)\b",
            ]:
                m2 = re.search(pat, block, re.IGNORECASE)
                if m2:
                    correct_text = raw_options.get(m2.group(1).upper())
                    if correct_text:
                        break

        # Last resort: last option
        if not correct_text:
            correct_text = list(raw_options.values())[-1]

        # EXPLANATION
        explanation = ""
        e_match = re.search(
            r"EXPLAIN:\s*(.+?)(?=\n\n|\Z)", block, re.DOTALL | re.IGNORECASE
        )
        if e_match:
            explanation = re.sub(r"\s+", " ", e_match.group(1).strip())

        # Shuffle options so correct answer position is random
        option_texts = list(raw_options.values())
        random.shuffle(option_texts)
        letters = ["A", "B", "C", "D"]
        shuffled = {letters[i]: option_texts[i] for i in range(len(option_texts))}

        questions.append(
            {
                "question":     question,
                "options":      shuffled,
                "correct_text": correct_text,
                "explanation":  explanation,
            }
        )

    return questions


def score_answer(chosen_letter, mcq):
    """Compare chosen option text against stored correct_text (normalised)."""
    chosen_text = mcq["options"].get(chosen_letter, "")

    def norm(s):
        s = s.lower().strip()
        s = re.sub(r"[^\w\s]", "", s)
        return re.sub(r"\s+", " ", s)

    return norm(chosen_text) == norm(mcq["correct_text"])


# ──────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def render_dots(current, total):
    html = '<div class="dots">'
    for i in range(total):
        if i < current:
            html += '<div class="dot done"></div>'
        elif i == current:
            html += '<div class="dot active"></div>'
        else:
            html += '<div class="dot"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_level(level):
    cls  = {"BEGINNER": "lvl-b", "INTERMEDIATE": "lvl-i", "ADVANCED": "lvl-a"}.get(level, "lvl-b")
    icon = {"BEGINNER": "🌱",    "INTERMEDIATE": "📘",    "ADVANCED": "🎯"}.get(level, "📚")
    st.markdown(
        f'<div class="level-badge {cls}">{icon} {level}</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ──────────────────────────────────────────────
_defaults = {
    "phase":            "login",
    "user":             None,
    "topic":            None,
    "session_id":       None,
    "level":            None,
    "quiz_attempt":     1,
    "reteach_count":    0,
    # quiz state
    "quiz_questions":   [],
    "quiz_index":       0,
    "correct_answers":  0,
    "answered_this_q":  False,
    "last_correct":     False,
    "last_correct_text": "",
    "last_explanation": "",
    # teaching chat
    "messages":         [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_quiz_state():
    st.session_state.quiz_questions   = []
    st.session_state.quiz_index       = 0
    st.session_state.correct_answers  = 0
    st.session_state.answered_this_q  = False
    st.session_state.last_correct     = False
    st.session_state.last_correct_text = ""
    st.session_state.last_explanation  = ""


# ──────────────────────────────────────────────
# GENERIC QUIZ RENDERER
# *** MUST be defined BEFORE the phase if/elif chain ***
# ──────────────────────────────────────────────
def render_quiz(total, on_complete):
    """
    Renders a quiz of `total` questions from st.session_state.quiz_questions.
    Calls on_complete(score) when all questions are answered.
    """
    qs    = st.session_state.quiz_questions
    idx   = st.session_state.quiz_index
    score = st.session_state.correct_answers

    render_dots(idx, total)
    st.markdown(
        f'<div class="chip">✅ {score} correct so far</div>',
        unsafe_allow_html=True,
    )

    # All questions done
    if idx >= total:
        on_complete(score)
        return

    mcq = qs[idx]

    # Show question & options
    if not st.session_state.answered_this_q:
        st.markdown('<div class="mcq-box">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="mcq-q">❓ Q{idx+1}/{total} &nbsp; {mcq["question"]}</div>',
            unsafe_allow_html=True,
        )
        for letter, text in mcq["options"].items():
            if st.button(
                f"{letter})  {text}", key=f"opt_{idx}_{letter}", use_container_width=True
            ):
                correct = score_answer(letter, mcq)
                if correct:
                    st.session_state.correct_answers += 1
                st.session_state.answered_this_q   = True
                st.session_state.last_correct      = correct
                st.session_state.last_correct_text = mcq["correct_text"]
                st.session_state.last_explanation  = mcq["explanation"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Show feedback
    else:
        ok  = st.session_state.last_correct
        ct  = st.session_state.last_correct_text
        exp = st.session_state.last_explanation

        if ok:
            st.markdown(
                f'<div class="fb-ok">✅ <b>Correct!</b> {exp}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="fb-bad">❌ <b>Incorrect.</b> '
                f'Correct answer: <b>{ct}</b><br>{exp}</div>',
                unsafe_allow_html=True,
            )

        next_label = "Next Question →" if idx + 1 < total else "See Results →"
        if st.button(next_label, type="primary", key=f"next_{idx}"):
            st.session_state.quiz_index       += 1
            st.session_state.answered_this_q   = False
            st.session_state.last_correct      = False
            st.session_state.last_correct_text = ""
            st.session_state.last_explanation  = ""
            st.rerun()


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"# 🎓 {t('app_name')}")
    st.caption(t("tagline"))

    if st.session_state.user:
        st.markdown(f"### 👋 {st.session_state.user[1]}")

        sessions = get_user_sessions(st.session_state.user[0])
        in_prog  = [s for s in sessions if s[5] == 0]
        done     = [s for s in sessions if s[5] == 1]

        if in_prog:
            st.markdown("**📖 In Progress**")
            for s in in_prog[:3]:
                label = s[2][:25] + "…" if len(s[2]) > 25 else s[2]
                if st.button(f"📚 {label}", key=f"ip_{s[0]}"):
                    st.session_state.update(
                        {
                            "session_id": s[0],
                            "topic":      s[2],
                            "level":      s[3],
                            "messages":   json.loads(s[4]) if s[4] else [],
                            "phase":      "teaching",
                        }
                    )
                    reset_quiz_state()
                    st.rerun()

        if done:
            st.markdown("**✅ Completed**")
            for s in done[:3]:
                label = s[2][:25] + "…" if len(s[2]) > 25 else s[2]
                if st.button(f"🔄 {label}", key=f"c_{s[0]}"):
                    st.session_state.update(
                        {"topic": s[2], "messages": [], "phase": "revision"}
                    )
                    reset_quiz_state()
                    st.rerun()

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🆕 New", use_container_width=True):
                st.session_state.update(
                    {"phase": "dashboard", "messages": [], "topic": None}
                )
                reset_quiz_state()
                st.rerun()
        with c2:
            if st.button("🚪 Logout", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

        st.divider()
        st.markdown("### 🌐 Language")
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.lang = "EN"
            st.rerun()
        if st.button("🇮🇳 हिंदी", use_container_width=True):
            st.session_state.lang = "HI"
            st.rerun()


# ══════════════════════════════════════════════
# PHASE: LOGIN
# ══════════════════════════════════════════════
if st.session_state.phase == "login":
    st.markdown(
        '<div class="hero"><h1>🎓 VidyaPath</h1>'
        "<p>Your personal AI tutor — adaptive, patient, always there for you.</p></div>",
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            u = st.text_input("Username", key="lu")
            p = st.text_input("Password", type="password", key="lp")
            if st.button("Login", type="primary", use_container_width=True):
                user = get_user(u)
                if user and user[2] == hash_pw(p):
                    st.session_state.user  = user
                    st.session_state.phase = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            nu = st.text_input("Username", key="ru")
            np = st.text_input("Password", type="password", key="rp")
            cp = st.text_input("Confirm Password", type="password", key="rc")
            if st.button("Create Account", type="primary", use_container_width=True):
                if np != cp:
                    st.error("Passwords don't match")
                elif len(nu) < 3:
                    st.error("Username too short (min 3 chars)")
                elif len(np) < 4:
                    st.error("Password too short (min 4 chars)")
                elif create_user(nu, hash_pw(np)):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PHASE: DASHBOARD
# ══════════════════════════════════════════════
elif st.session_state.phase == "dashboard":
    st.markdown(
        f'<div class="sec-title">{t("welcome")}, {st.session_state.user[1]}! 🚀</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sec-sub">Type any topic below to start your personalised learning journey.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="topic-card">', unsafe_allow_html=True)
    topic = st.text_input("", placeholder=t("placeholder"), label_visibility="collapsed")
    if st.button(t("start_learning"), type="primary", use_container_width=True):
        if topic.strip():
            sid = create_session(st.session_state.user[0], topic.strip())
            st.session_state.update(
                {
                    "topic":         topic.strip(),
                    "session_id":    sid,
                    "messages":      [],
                    "level":         None,
                    "quiz_attempt":  1,
                    "reteach_count": 0,
                    "phase":         "pre_quiz",
                }
            )
            reset_quiz_state()
            st.rerun()
        else:
            st.warning("Please enter a topic first.")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PHASE: PRE-QUIZ  (3 questions)
# ══════════════════════════════════════════════
elif st.session_state.phase == "pre_quiz":
    st.markdown(
        f'<div class="sec-title">📝 Pre-Assessment: {st.session_state.topic}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sec-sub">3 quick questions to personalise your lesson.</div>',
        unsafe_allow_html=True,
    )

    # Generate questions once per session
    if not st.session_state.quiz_questions:
        with st.spinner("Generating questions…"):
            prompt = get_pre_quiz_prompt(st.session_state.topic, st.session_state.lang)
            raw    = llm([{"role": "user", "content": prompt}])
            qs     = parse_all_questions(raw)

        if not qs:
            st.error("⚠️ Couldn't parse questions from the model's response. Raw output below:")
            st.code(raw)
            if st.button("🔄 Retry"):
                st.rerun()
            st.stop()

        # Pad to exactly 3 if model gave fewer (safety net)
        while len(qs) < 3:
            qs.append(qs[0])

        st.session_state.quiz_questions = qs[:3]
        st.rerun()

    # Completion callback
    def pre_complete(score):
        if score >= 2:
            level = "ADVANCED"
        elif score == 1:
            level = "INTERMEDIATE"
        else:
            level = "BEGINNER"

        st.session_state.level = level
        update_session(
            st.session_state.session_id,
            st.session_state.messages,
            knowledge_level=level,
        )

        st.markdown("---")
        st.success(f"✅ Assessment complete! You scored **{score}/3**")
        render_level(level)

        msgs = {
            "BEGINNER":     ("🌱", "No worries — everyone starts somewhere! I'll explain everything from scratch."),
            "INTERMEDIATE": ("📘", "Nice! You've got a solid base. I'll build on what you already know."),
            "ADVANCED":     ("🎯", "Impressive! Let's dive into the deeper concepts."),
        }
        icon, msg = msgs[level]
        st.info(f"{icon} {msg}")
        st.markdown("---")

        if st.button("📖 Begin Personalised Lesson", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.phase    = "teaching"
            reset_quiz_state()
            st.rerun()

    render_quiz(total=3, on_complete=pre_complete)


# ══════════════════════════════════════════════
# PHASE: TEACHING
# ══════════════════════════════════════════════
elif st.session_state.phase == "teaching":
    level = st.session_state.level or "BEGINNER"
    st.markdown(
        f'<div class="sec-title">📚 {st.session_state.topic}</div>',
        unsafe_allow_html=True,
    )
    render_level(level)

    # Initialise lesson on first visit
    if not st.session_state.messages:
        prompt = get_teaching_prompt(st.session_state.topic, level, st.session_state.lang)
        st.session_state.messages = [{"role": "system", "content": prompt}]
        with st.spinner("Preparing your personalised lesson…"):
            reply = llm(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            update_session(
                st.session_state.session_id,
                st.session_state.messages,
                knowledge_level=level,
            )
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        av = "🎓" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

    # Take quiz button
    _, mid, _ = st.columns([2, 1.5, 2])
    with mid:
        if st.button("✅ Take Final Quiz", type="primary", use_container_width=True):
            st.session_state.phase = "post_quiz"
            reset_quiz_state()
            st.rerun()

    # Chat input
    if q := st.chat_input("Ask a question about the topic…"):
        with st.chat_message("user", avatar="👤"):
            st.markdown(q)
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("assistant", avatar="🎓"):
            resp = st.write_stream(llm_stream(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": resp})
        update_session(
            st.session_state.session_id,
            st.session_state.messages,
            knowledge_level=level,
        )
        st.rerun()


# ══════════════════════════════════════════════
# PHASE: POST-QUIZ  (5 questions)
# ══════════════════════════════════════════════
elif st.session_state.phase == "post_quiz":
    attempt = st.session_state.quiz_attempt
    st.markdown(
        f'<div class="sec-title">🎯 Final Quiz — Attempt {attempt}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sec-sub">5 questions to test your understanding.</div>',
        unsafe_allow_html=True,
    )

    # Generate questions once
    if not st.session_state.quiz_questions:
        with st.spinner("Generating quiz questions…"):
            prompt = get_post_quiz_prompt(
                st.session_state.topic,
                st.session_state.level or "BEGINNER",
                attempt,
                st.session_state.lang,
            )
            raw = llm([{"role": "user", "content": prompt}])
            qs  = parse_all_questions(raw)

        if not qs:
            st.error("⚠️ Couldn't parse quiz questions. Raw output:")
            st.code(raw)
            if st.button("🔄 Retry"):
                st.rerun()
            st.stop()

        while len(qs) < 5:
            qs.append(qs[len(qs) % max(len(qs), 1)])

        st.session_state.quiz_questions = qs[:5]
        st.rerun()

    # Completion callback
    def post_complete(score):
        if score >= 3:
            st.balloons()
            st.markdown(
                f'<div class="win-box">'
                f"<h2>🏆 CONGRATULATIONS!</h2>"
                f"<p>You have mastered <b>{st.session_state.topic}</b>!</p>"
                f"<p><b>Score: {score}/5</b></p>"
                f"</div>",
                unsafe_allow_html=True,
            )
            update_session(
                st.session_state.session_id,
                st.session_state.messages,
                completed=1,
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔍 Go Deeper", type="primary", use_container_width=True):
                    sid = create_session(
                        st.session_state.user[0],
                        f"{st.session_state.topic} (Advanced)",
                    )
                    st.session_state.update(
                        {
                            "level":      "ADVANCED",
                            "phase":      "teaching",
                            "messages":   [],
                            "session_id": sid,
                        }
                    )
                    reset_quiz_state()
                    st.rerun()
            with c2:
                if st.button("📚 New Topic", use_container_width=True):
                    st.session_state.update({"phase": "dashboard", "messages": []})
                    reset_quiz_state()
                    st.rerun()
        else:
            st.session_state.reteach_count += 1
            st.warning(
                f"📚 You scored **{score}/5**. "
                f"Let's review together before trying again! "
                f"(Reteach #{st.session_state.reteach_count})"
            )
            if st.button("🔄 Review & Try Again", type="primary", use_container_width=True):
                st.session_state.update(
                    {
                        "phase":        "teaching",
                        "messages":     [],
                        "quiz_attempt": st.session_state.quiz_attempt + 1,
                    }
                )
                reset_quiz_state()
                st.rerun()

    render_quiz(total=5, on_complete=post_complete)


# ══════════════════════════════════════════════
# PHASE: REVISION
# ══════════════════════════════════════════════
elif st.session_state.phase == "revision":
    st.markdown(
        f'<div class="sec-title">🔄 Revision: {st.session_state.topic}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sec-sub'>Welcome back! Let's refresh your memory.</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        prompt = get_revision_prompt(st.session_state.topic, st.session_state.lang)
        st.session_state.messages = [{"role": "system", "content": prompt}]
        with st.spinner("Preparing revision…"):
            reply = llm(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        av = "🎓" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Go Deeper", type="primary", use_container_width=True):
            sid = create_session(
                st.session_state.user[0],
                f"{st.session_state.topic} (Deep Dive)",
            )
            st.session_state.update(
                {
                    "level":      "ADVANCED",
                    "phase":      "teaching",
                    "messages":   [],
                    "session_id": sid,
                }
            )
            reset_quiz_state()
            st.rerun()
    with c2:
        if st.button("📚 New Topic", use_container_width=True):
            st.session_state.update({"phase": "dashboard", "messages": []})
            reset_quiz_state()
            st.rerun()

    if q := st.chat_input("Ask a question…"):
        with st.chat_message("user", avatar="👤"):
            st.markdown(q)
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("assistant", avatar="🎓"):
            resp = st.write_stream(llm_stream(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.rerun()