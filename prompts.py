def get_pre_quiz_prompt(topic, language="EN"):
    """Ask for ALL 3 pre-quiz questions in one shot, structured block format."""
    if language == "HI":
        return f"""आप एक शिक्षक हैं। "{topic}" पर 3 MCQ प्रश्न बनाएं।
नीचे दिए गए फॉर्मेट में बिल्कुल 3 प्रश्न दें। कोई अतिरिक्त टेक्स्ट नहीं।
सही उत्तर को अलग-अलग स्थानों पर रखें (A, B, C, या D)।

###Q1###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य में कारण]
###END###

###Q2###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य में कारण]
###END###

###Q3###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य में कारण]
###END###"""

    return f"""You are a quiz generator. Create exactly 3 MCQ questions about "{topic}".
Output ONLY the 3 question blocks below. No intro, no extra text, no commentary.
Place the correct answer at DIFFERENT letter positions across questions.

###Q1###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why this is correct]
###END###

###Q2###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why this is correct]
###END###

###Q3###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why this is correct]
###END###"""


def get_post_quiz_prompt(topic, level, attempt, language="EN"):
    """Ask for ALL 5 post-quiz questions in one shot."""
    difficulty = (
        "easy to medium difficulty"
        if attempt == 1
        else "simple foundational questions to rebuild confidence"
    )

    if language == "HI":
        return f"""आप एक शिक्षक हैं। "{topic}" पर 5 MCQ प्रश्न बनाएं। स्तर: {level}।
नीचे दिए गए फॉर्मेट में बिल्कुल 5 प्रश्न दें। कोई अतिरिक्त टेक्स्ट नहीं।
सही उत्तर को अलग-अलग स्थानों पर रखें।

###Q1###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य]
###END###

###Q2###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य]
###END###

###Q3###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य]
###END###

###Q4###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य]
###END###

###Q5###
QUESTION: [प्रश्न]
A) [विकल्प]
B) [विकल्प]
C) [विकल्प]
D) [विकल्प]
CORRECT: [सही अक्षर]
EXPLAIN: [एक वाक्य]
###END###"""

    return f"""You are a quiz generator. Create exactly 5 MCQ questions about "{topic}".
Level: {level}. Use {difficulty}.
Output ONLY the 5 question blocks. No intro, no commentary, nothing else.
Place the correct answer at DIFFERENT letter positions (vary A, B, C, D across questions).

###Q1###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why]
###END###

###Q2###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why]
###END###

###Q3###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why]
###END###

###Q4###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why]
###END###

###Q5###
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A or B or C or D]
EXPLAIN: [one sentence why]
###END###"""


def get_teaching_prompt(topic, level, language="EN"):
    level_instructions = {
        "BEGINNER": (
            "Assume zero prior knowledge. Use very simple language, "
            "relatable analogies, and build up from scratch."
        ),
        "INTERMEDIATE": (
            "The student has some foundation. "
            "Connect new ideas to what they likely already know."
        ),
        "ADVANCED": (
            "The student is comfortable with fundamentals. "
            "Dive into nuance, edge cases, and deeper mechanisms."
        ),
    }
    instruction = level_instructions.get(level, level_instructions["BEGINNER"])

    if language == "HI":
        return f"""आप विद्यापथ AI ट्यूटर हैं — उत्साही, धैर्यवान।
विषय: "{topic}" | स्तर: {level}
{instruction}
गर्मजोशी से स्वागत करें, बातचीत के तरीके से समझाएं, रोज़ के उदाहरण दें।
अंत में पूछें: "कोई सवाल?"
MCQ प्रश्न बिल्कुल न पूछें।"""

    return f"""You are VidyaPath AI Tutor — enthusiastic, patient, conversational.
Topic: "{topic}" | Level: {level}
{instruction}
Greet the student warmly, explain the topic conversationally with relatable examples.
End with: "Any questions? Want me to go deeper on anything?"
DO NOT ask MCQ questions. This is a teaching conversation."""


def get_roadmap_prompt(topic, level, language="EN"):
    return f"""Generate a learning roadmap for "{topic}" at {level} level.
ROADMAP_START
SUMMARY: [one sentence]
PHASE 1: [title] - [step1] / [step2] / [step3]
PHASE 2: [title] - [step1] / [step2] / [step3]
PHASE 3: [title] - [step1] / [step2] / [step3]
MOTIVATION: [encouraging message]
ROADMAP_END"""


def get_revision_prompt(topic, language="EN"):
    if language == "HI":
        return f""""{topic}" का त्वरित revision करें।
गर्मजोशी से स्वागत करें, मुख्य बिंदु bullet points में दें।
अंत में पूछें: "सब याद आया?"
ऊर्जावान रहें।"""

    return f"""Provide a quick revision of "{topic}".
Welcome the student back warmly, summarise key concepts in bullet points,
highlight the trickiest ideas, then ask: "Did it all come back? Want to go deeper?"
Be energetic and encouraging."""