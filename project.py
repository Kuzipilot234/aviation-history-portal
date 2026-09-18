import base64
import json
import random
import time
from pathlib import Path

import feedparser
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image

st.set_page_config(
    page_title="Kuzey's Aviation and History Portal",
    page_icon="✈️",
    layout="wide",
)

PROJECT_DIR = Path(__file__).parent
BACKGROUND_PATH = PROJECT_DIR / "assets" / "aviation_background.jpg"
LOGO_PATH = PROJECT_DIR / "assets" / "site_logo.png"

# Load the background image as Base64 so it works locally and on Streamlit Cloud.
background_base64 = ""
if BACKGROUND_PATH.exists():
    background_base64 = base64.b64encode(
        BACKGROUND_PATH.read_bytes()
    ).decode("utf-8")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(
                rgba(11, 31, 51, 0.82),
                rgba(11, 31, 51, 0.92)
            ),
            url("data:image/jpeg;base64,{background_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    p, label, .stMarkdown {{
        color: #f1f5f9 !important;
    }}

    h1, h2, h3, h4 {{
        color: #f97316 !important;
    }}

[data-testid="stSidebar"] {{
    background: #0b1f33 !important;
    border-right: 1px solid #163a5c !important;
}}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] .stMarkdown {{
        color: #f8fafc !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: #486581 !important;
    }}

    /* Sidebar navigation appears as flat clickable menu links. */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button p {{
        width: 100% !important;
        background-color: transparent !important;
        color: #f8fafc !important;
        border: none !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.65rem 0.75rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stButton > button:hover p {{
        background-color: #1e3a56 !important;
        color: #c2410c !important;
    }}

    /* Main-page action buttons. */
    .stButton > button {{
        background-color: #f97316 !important;
        color: #f8fafc !important;
        border: 1px solid #f97316 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}

    .stButton > button p {{
        color: #f8fafc !important;
    }}

    .stButton > button:hover {{
        background-color: #fb923c !important;
        color: #f8fafc !important;
        border-color: #fb923c !important;
    }}

    .stLinkButton a,
    .stLinkButton a p,
    [data-testid="stLinkButton"] a {{
        background-color: #f97316 !important;
        color: #f8fafc !important;
        border: 1px solid #f97316 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
    }}

    .stLinkButton a:hover,
    .stLinkButton a:hover p,
    [data-testid="stLinkButton"] a:hover {{
        background-color: #fb923c !important;
        color: #f8fafc !important;
        border-color: #fb923c !important;
    }}

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {{
        background-color: #f8fafc !important;
        color: #111827 !important;
        border: 2px solid #f97316 !important;
        border-radius: 8px !important;
    }}

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {{
        color: #cbd5e1 !important;
    }}

    [data-testid="stTabs"] button {{
        color: #ffedd5 !important;
        font-weight: 600 !important;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: #f97316 !important;
        border-bottom-color: #f97316 !important;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {{
        color: #f97316 !important;
        font-weight: 700 !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        color: #fb923c !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
    width: 100% !important;
    min-height: 48px !important;
    margin-bottom: 8px !important;
    padding: 0 14px !important;
    background: #f97316 !important;
    color: #f8fafc !important;
    border: 1px solid #fdba74 !important;
    border-radius: 8px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    text-align: left !important;
}}
    [data-testid="stSidebar"] h2 {{
    font-family: 'Lora', Georgia, serif !important;
    font-size: 1.65rem !important;
    color: #f8fafc !important;
    letter-spacing: 0.5px !important;
}}

    </style>
    """,
    unsafe_allow_html=True,
)

RSS_FEEDS = {
    "Aviation": "https://simpleflying.com/feed/",
    "History": "https://www.worldhistory.org/rss/",
}

FEEDBACK_FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
)

ANNOUNCEMENTS = [
    {
        "date": "September 18 2026",
        "title": "Major Update!! A new AI daily news briefing function is added",
        "message": (
            "You can now see a short summarized briefing of the latest aviation and history news!  "

        ),
    },
    {
        "date": "September 18, 2026",
        "title": "Updated AI generated quiz",
        "message": (
            "You can now select your quiz's difficulty"
        ),
    },
]


@st.cache_data(ttl=900)
def load_news_from_rss():
    articles = []

    for category, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append(
                    {
                        "category": category,
                        "title": entry.get("title", "Untitled"),
                        "summary": entry.get(
                            "summary", "No summary available."
                        ),
                        "url": entry.get("link", ""),
                        "published": entry.get(
                            "published", "Unknown date"
                        ),
                    }
                )
        except Exception:
            continue

    return articles


@st.cache_data(ttl=21600, show_spinner=False)
def generate_daily_briefing(article_payload):
    """Create one cached briefing from the latest RSS headlines and summaries."""
    if not article_payload:
        return "There is not enough recent news to prepare a briefing right now."

    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        source_text = "\n".join(
            f"[{item['category']}] {item['title']}: {item['summary']}"
            for item in article_payload[:12]
        )
        prompt = (
                "You are the editor of Kuzey's Aviation and History Portal. "
                "Write a concise daily briefing in 3 short paragraphs: one aviation "
                "update, one history update, and one overall takeaway. Use only the "
                "information supplied below. Do not invent facts, dates, or events. "
                "Do not use Markdown headings.\n\n" + source_text
        )
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return (
            "The AI daily briefing is temporarily unavailable. You can still "
            "browse the latest aviation and history stories below."
        )


def display_news_section(section_title, articles, empty_message):
    st.markdown(f"### {section_title}")

    if not articles:
        st.info(empty_message)
        return

    news_columns = st.columns(3)
    for index, article in enumerate(articles):
        with news_columns[index % 3]:
            st.markdown(f"##### {article['title']}")
            st.caption(
                f"{article['category']} · {article['published']}"
            )
            st.write(article["summary"])

            if article["url"]:
                st.link_button(
                    "Read original article",
                    article["url"],
                )


rss_articles = load_news_from_rss()

PAGE_LABELS = {
    "news": "🏠 Global News Feed",
    "chatbot": "🤖 AI Chatbot",
    "history": "📜 History Mini Games",
    "quiz": "🏆 AI Generated Quiz",
    "feedback": "💬 Feedback",
    "radars": "✈️ Aviation Radars",
}

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "news"

with st.sidebar:
    if LOGO_PATH.exists():
        try:
            logo_image = Image.open(LOGO_PATH)
            logo_image.load()
            st.image(logo_image, width=170)
        except Exception:
            st.info("Logo could not be displayed.")
    else:
        st.info("Add assets/site_logo.png to display the logo.")

    st.markdown(
        """
        <h2 style="color: #f8fafc; margin-bottom: 0;">
            Kuzey Aviation and History Portal
        </h2>
        <p style="color: #cbd5e1; margin-top: 0;">

        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    for page_id, page_label in PAGE_LABELS.items():
        if st.button(
                page_label,
                key=f"navigation_{page_id}",
                use_container_width=True,
        ):
            st.session_state.selected_page = page_id
            st.rerun()

    st.divider()
    st.caption("Explore aviation, history, and more.")

selected_page = st.session_state.selected_page

st.markdown(
    "<h1 style='text-align: center; color: #f97316; font-size: 42px;'>"
    "✈️ Kuzey's Aviation & History Portal 📜</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 16px;'>"
    "Explore aviation news, history, AI quizzes, games, and live radar tools."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

if selected_page == "news":
    quotes = [
        '"The engine is the heart of an airplane, but the pilot is its soul." - Unknown',
        '"If you can walk away from a landing, it\'s a good landing." - Chuck Yeager',
        '"History is a gallery of pictures in which there are few originals and many copies." - Alexis de Tocqueville',
    ]
    st.info(random.choice(quotes))

    st.subheader("📢 Announcements")
    for announcement in ANNOUNCEMENTS:
        st.info(
            f"**{announcement['title']}**\n\n"
            f"_{announcement['date']}_\n\n"
            f"{announcement['message']}"
        )

    st.divider()
    st.subheader("📰 Global News Feed")
    st.markdown(
        "Read the latest aviation and history stories from the selected RSS sources."
    )

    st.subheader("☀️ Daily Briefing")
    st.caption("A short AI summary based on the latest cached RSS articles. Refreshed every six hours.")
    briefing_payload = tuple(
        {
            "category": article["category"],
            "title": article["title"],
            "summary": article["summary"],
        }
        for article in rss_articles
    )
    with st.container(border=True):
        st.write(generate_daily_briefing(briefing_payload))

    aviation_articles = [
        article
        for article in rss_articles
        if article["category"] == "Aviation"
    ]
    history_articles = [
        article
        for article in rss_articles
        if article["category"] == "History"
    ]

    display_news_section(
        "✈️ Aviation News",
        aviation_articles,
        "No aviation news is available right now.",
    )
    st.divider()
    display_news_section(
        "📜 History News",
        history_articles,
        "No history news is available right now.",
    )


elif selected_page == "chatbot":
    st.header("🤖 Kuzey's Aviation & History Portal AI Chatbot")
    st.markdown(
        "Ask the portal AI about general aviation, military aviation, or history."
    )
    if "last_chat_time" not in st.session_state:
        st.session_state.last_chat_time = 0

    COOLDOWN_SECONDS = 15

    user_query = st.text_area(
        "Ask anything to the portal AI chatbot:",
        max_chars=300,
        key="chat_query",
    )

    if st.button("Get an answer", key="chat_button_unique"):
        seconds_since_last = time.time() - st.session_state.last_chat_time
        if seconds_since_last < COOLDOWN_SECONDS:
            wait_time = round(COOLDOWN_SECONDS - seconds_since_last)
            st.warning(f"Please wait {wait_time} more second(s) before asking again.")
        elif not user_query.strip():
            st.warning("Please enter a question first.")
        else:
            st.session_state.last_chat_time = time.time()
            with st.spinner("Preparing an answer..."):
                try:
                    client = genai.Client(
                        api_key=st.secrets["GEMINI_API_KEY"]
                    )
                    prompt = (
                        "You are the AI assistant for Kuzey's Aviation and "
                        "History Portal. Answer questions about aviation and "
                        "history clearly, accurately, and engagingly. "
                        f"User question: {user_query}"
                    )
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                    )
                    st.subheader("Strategic Intelligence Report")
                    st.write(response.text)
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        st.warning(
                            "The AI service is experiencing high demand right now. "
                            "Please try again in a few minutes."
                        )
                    else:
                        st.error(
                            "The chatbot could not connect right now. Please try again later."
                        )


elif selected_page == "history":
    st.header("📜 Interactive Chronology & Strategy Games")

    st.subheader("⚔️ World War II Timeline")
    timeline_tabs = st.tabs(["1939", "1940", "1941", "1944", "1945"])

    with timeline_tabs[0]:
        st.markdown(
            "**September 1, 1939 - Invasion of Poland:** Germany invades Poland using Blitzkrieg tactics, starting WWII."
        )
    with timeline_tabs[1]:
        st.markdown(
            "**May 1940 - Fall of France & Dunkirk:** Allied troops make a dramatic escape from Dunkirk beaches."
        )
    with timeline_tabs[2]:
        st.markdown(
            "**December 7, 1941 - Attack on Pearl Harbor:** USA joins the Allies after a massive surprise attack."
        )
    with timeline_tabs[3]:
        st.markdown(
            "**June 6, 1944 - D-Day:** The largest naval invasion in history establishes the Western Front in Normandy."
        )
    with timeline_tabs[4]:
        st.markdown(
            "**1945 - Total Victory:** Germany and Japan surrender unconditionally."
        )

    st.divider()
    st.subheader("🕵️ Historical 'Who Am I?' Challenge")

    if "secret_figure" not in st.session_state:
        figures = [
            {
                "clues": [
                    "I am the founder of the Republic of Türkiye.",
                    "I was born in Salonica in 1881.",
                    "My military genius was proven at Gallipoli.",
                ],
                "answer": "Mustafa Kemal Atatürk",
            },
            {
                "clues": [
                    "I am a Roman general and dictator.",
                    "I famously crossed the Rubicon river.",
                    "My last words were allegedly addressed to Brutus.",
                ],
                "answer": "Julius Caesar",
            },
            {
                "clues": [
                    "I crowned myself Emperor of the French.",
                    "I dominated European affairs for over a decade.",
                    "My final military defeat occurred at Waterloo.",
                ],
                "answer": "Napoleon Bonaparte",
            },
            {
                "clues": [
                    "I was a British Prime Minister during WWII.",
                    "I am famous for my 'We shall fight on the beaches' speech.",
                    "I am often pictured with a cigar.",
                ],
                "answer": "Winston Churchill",
            },
        ]
        st.session_state.secret_figure = random.choice(figures)

    for index, clue in enumerate(
            st.session_state.secret_figure["clues"],
            start=1,
    ):
        st.markdown(f"• Clue {index}: {clue}")

    guess = st.selectbox(
        "Identify the figure:",
        options=[
            "Select...",
            "Mustafa Kemal Atatürk",
            "Julius Caesar",
            "Napoleon Bonaparte",
            "Winston Churchill",
        ],
        key="game_select",
    )

    if guess != "Select...":
        if guess == st.session_state.secret_figure["answer"]:
            st.success(
                "🏆 Correct! It was "
                f"{st.session_state.secret_figure['answer']}!"
            )
        else:
            st.error("❌ Wrong answer! Review the clues and try again.")

    if st.button("🔄 Next Target / Figure", key="game_reset"):
        del st.session_state.secret_figure
        st.rerun()


elif selected_page == "quiz":
    st.header("🏆 AI-Generated Knowledge Quiz")
    st.markdown(
        "Build a quiz around any topic, then submit it to reveal your score, "
        "correct answers, and explanations."
    )

    setup_col, preview_col = st.columns([1.35, 1])
    with setup_col:
        quiz_topic = st.text_input(
            "What should the quiz be about?",
            value="Aviation and world history",
            max_chars=100,
            key="quiz_topic_input",
        )
        difficulty = st.selectbox(
            "Choose a difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
            key="quiz_difficulty",
        )
        question_count = st.slider(
            "How many questions do you want?",
            min_value=5,
            max_value=10,
            value=5,
            key="quiz_question_count",
        )
    with preview_col:
        st.info(
            f"Your quiz will contain **{question_count} questions** at "
            f"**{difficulty.lower()}** difficulty.\n\n"
            "Answer every question, then select **Check My Answers** to see "
            "the results."
        )

    if "last_quiz_time" not in st.session_state:
        st.session_state.last_quiz_time = 0

    QUIZ_COOLDOWN_SECONDS = 20
    if st.button("✨ Generate New Quiz", key="generate_ai_quiz", use_container_width=True):
        seconds_since_last = time.time() - st.session_state.last_quiz_time
        topic = quiz_topic.strip()

        if seconds_since_last < QUIZ_COOLDOWN_SECONDS:
            wait_time = round(QUIZ_COOLDOWN_SECONDS - seconds_since_last)
            st.warning(f"Please wait {wait_time} more second(s) before generating another quiz.")
        elif not topic:
            st.warning("Please enter a quiz topic first.")
        else:
            st.session_state.last_quiz_time = time.time()
            with st.spinner("Creating your personalized quiz..."):
                try:
                    quiz_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    quiz_prompt = f"""
Create a {difficulty.lower()} multiple-choice quiz about: {topic}

Create exactly {question_count} questions. Each question must have exactly four answer options and only one correct answer.
Return ONLY valid JSON in this exact format:
[{{
  "question": "Question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer_index": 0,
  "explanation": "Short explanation of the correct answer"
}}]
The answer_index must be a number from 0 to 3. Do not include Markdown or code fences.
"""
                    response = quiz_client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=quiz_prompt,
                    )
                    response_text = response.text.strip()
                    if response_text.startswith("```"):
                        response_text = response_text.replace("```json", "", 1).replace("```", "").strip()
                    generated_quiz = json.loads(response_text)
                    if not isinstance(generated_quiz, list) or len(generated_quiz) != question_count:
                        raise ValueError("Invalid quiz length")
                    for question in generated_quiz:
                        if (
                                not isinstance(question, dict)
                                or not isinstance(question.get("question"), str)
                                or not isinstance(question.get("options"), list)
                                or len(question["options"]) != 4
                                or question.get("answer_index") not in [0, 1, 2, 3]
                        ):
                            raise ValueError("Invalid question format")
                    st.session_state.ai_quiz = generated_quiz
                    st.session_state.ai_quiz_version = st.session_state.get("ai_quiz_version", 0) + 1
                    st.session_state.quiz_checked = False
                    st.success("Your personalized quiz is ready. Good luck!")
                except Exception:
                    st.error("The AI could not create the quiz right now. Please try again with another topic.")

    if "ai_quiz" in st.session_state:
        st.divider()
        st.subheader("Your Challenge")
        quiz_version = st.session_state.get("ai_quiz_version", 0)
        selected_answers = []
        total_questions = len(st.session_state.ai_quiz)
        for index, question in enumerate(st.session_state.ai_quiz):
            st.progress((index + 1) / total_questions, text=f"Question {index + 1} of {total_questions}")
            selected_answer = st.radio(
                question["question"],
                question["options"],
                index=None,
                key=f"ai_answer_{quiz_version}_{index}",
            )
            selected_answers.append(selected_answer)
            if index < total_questions - 1:
                st.divider()

        if st.button("✅ Check My Answers", key="check_ai_quiz", use_container_width=True):
            unanswered = [str(index + 1) for index, answer in enumerate(selected_answers) if answer is None]
            if unanswered:
                st.warning(f"Please answer question(s) {', '.join(unanswered)} before checking your quiz.")
            else:
                score = sum(
                    selected_answers[index] == question["options"][question["answer_index"]]
                    for index, question in enumerate(st.session_state.ai_quiz)
                )
                st.session_state.quiz_checked = True
                st.session_state.quiz_score = score
                st.rerun()

        if st.session_state.get("quiz_checked"):
            score = st.session_state.quiz_score
            percentage = round(score / total_questions * 100)
            st.divider()
            st.subheader(f"Final Score: {score}/{total_questions} ({percentage}%)")
            if score == total_questions:
                st.balloons()
                st.success("Perfect score! Outstanding work.")
            elif percentage >= 70:
                st.success("Great result! You have a strong grasp of the topic.")
            else:
                st.info("Good attempt. Review the explanations below and try another quiz.")

            st.subheader("Answer Review")
            for index, question in enumerate(st.session_state.ai_quiz):
                correct_answer = question["options"][question["answer_index"]]
                chosen = st.session_state.get(f"ai_answer_{quiz_version}_{index}")
                if chosen == correct_answer:
                    st.success(f"✅ Question {index + 1}: Correct")
                else:
                    st.error(f"❌ Question {index + 1}: Incorrect — correct answer: **{correct_answer}**")
                if question.get("explanation"):
                    st.caption(f"Explanation: {question['explanation']}")


elif selected_page == "feedback":
    st.header("💬 Help Improve the Portal")
    st.markdown(
        "Tell us what you like, what is confusing, and what you would like "
        "to see in a future update. Your feedback will help improve the beta."
    )
    components.iframe(
        FEEDBACK_FORM_URL,
        height=950,
        scrolling=True,
    )
    st.link_button(
        "Open the feedback form in a new tab",
        FEEDBACK_FORM_URL,
    )


elif selected_page == "radars":
    st.header("🌐 Global Aviation Radars")
    radar_col, map_col = st.columns(2)

    with radar_col:
        st.markdown("**🌍 Live Aviation Weather & Wind Radar**")
        st.markdown(
            '<iframe src="https://ventusky.com" width="100%" '
            'height="500px" style="border:none; border-radius:10px;">'
            "</iframe>",
            unsafe_allow_html=True,
        )

    with map_col:
        st.markdown("**📍 Kuzey's Global Aviation & Strategy Atlas**")
        map_data = {
            "lat": [
                41.2753, 40.0786, 38.3492, 39.9494,
                34.9154, 54.4920, 33.6407, 35.6528,
            ],
            "lon": [
                28.7519, 32.5694, 34.0536, 32.6889,
                -117.8853, -3.4219, -84.4277, 139.7594,
            ],
            "name": [
                "Istanbul Airport (IST)",
                "Mürted Air Base (Ankara)",
                "Incirlik Air Base (Adana)",
                "Eskişehir Air Base",
                "Edwards Air Force Base (USA)",
                "RAF Lossiemouth (UK)",
                "Hartsfield-Jackson Atlanta (USA)",
                "Tokyo Haneda (Japan)",
            ],
            "details": [
                "Europe's modern megahub.",
                "Historically significant Turkish jet base.",
                "Strategic NATO aviation hub.",
                "Birthplace of Turkish aviation.",
                "Aerospace test center where the sound barrier was broken.",
                "Historic Royal Air Force base.",
                "The busiest passenger airport in the world.",
                "Major Asian aviation hub.",
            ],
        }
        map_df = pd.DataFrame(map_data)
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position=["lon", "lat"],
            get_color=[249, 115, 22, 220],
            get_radius=90000,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=35.0,
            longitude=25.0,
            zoom=3,
        )
        tooltip_style = {
            "html": "<b>{name}</b><br/>ℹ️ {details}",
            "style": {
                "backgroundColor": "#102a43",
                "color": "white",
                "borderRadius": "5px",
                "border": "1px solid #f97316",
            },
        }
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip_style,
            ),
            use_container_width=True,
        )

st.divider()
with st.expander("👤 About the Creator / Portal", expanded=False):
    st.markdown(
        "Hello! I am Kuzey, the creator of this Aviation and History Portal. "
        "This portal brings together aviation news, historical insights, "
        "interactive quizzes, games, and radar tools. I hope you enjoy "
        "exploring it! ✈️📜"
    )
