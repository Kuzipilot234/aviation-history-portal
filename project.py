import random

import base64
from pathlib import Path
import feedparser
import pandas as pd
import pydeck as pdk
import streamlit as st
from google import genai
import streamlit.components.v1 as components
import json



st.set_page_config(
    page_title="Kuzey's Aviation and History Portal",
    page_icon="✈️",
    layout="wide",
)
image_path = Path(__file__).parent / "assets" / "aviation_background.jpg"

image_bytes = image_path.read_bytes()
image_base64 = base64.b64encode(image_bytes).decode()

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(
                rgba(7, 20, 38, 0.78),
                rgba(7, 20, 38, 0.88)
            ),
            url("data:image/jpeg;base64,{image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    p,
    label,
    .stMarkdown {{
        color: #f1f5f9 !important;
    }}

    [data-testid="stTabs"] button {{
        color: #dbeafe !important;
        font-weight: 600;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: #ff6b4a !important;
        border-bottom-color: #ff6b4a !important;
    }}

    h1, h2, h3, h4 {{
        color: #ff6b4a !important;
    }}

        /* Normal st.button controls */
    .stButton > button,
    .stButton > button p,
    [data-testid="stBaseButton-secondary"] {{
        background-color: #ff6b4a !important;
        color: #071426 !important;
        border: 1px solid #ff6b4a !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}

    /* RSS st.link_button controls */
    .stLinkButton a,
    .stLinkButton a p,
    [data-testid="stLinkButton"] a {{
        background-color: #ff6b4a !important;
        color: #071426 !important;
        border: 1px solid #ff6b4a !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
    }}

    .stButton > button:hover,
    .stLinkButton a:hover,
    [data-testid="stBaseButton-secondary"]:hover {{
        background-color: #ff8568 !important;
        color: #071426 !important;
        border-color: #ff8568 !important;
    }}

    .stButton > button:hover p,
    .stLinkButton a:hover p {{
        color: #071426 !important;
    }}

    /* About the Creator expander title */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {{
        color: #ff6b4a !important;
        font-weight: 700 !important;
    }}


    [data-testid="stExpander"] summary:hover {{
        color: #ff8568 !important;
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


@st.cache_data(ttl=900)
def load_news_from_rss():
    articles = []


    for category, feed_url in RSS_FEEDS.items():
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

    return articles
ANNOUNCEMENTS = [
    {
        "date": "September 14, 2026",
        "title": "AI quizzes are now available",
        "message": (
            "You can now choose a topic and the number of questions "
            "for a customized AI-generated quiz."
        ),
    },
    {
        "date": "September 14, 2026",
        "title": "New feedback form",
        "message": (
            "Please share your ideas and report problems through the "
            "new Feedback tab."
        ),
    },
]
ANNOUNCEMENTS = [
    {
        "date": "September 14, 2026",
        "title": "AI quizzes are now available",
        "message": (
            "You can now choose a topic and the number of questions "
            "for a customized AI-generated quiz."
        ),
    },
    {
        "date": "September 14, 2026",
        "title": "New feedback form",
        "message": (
            "Please share your ideas and report problems through the "
            "new Feedback tab."
        ),
    },
]

rss_articles = load_news_from_rss()

st.markdown(
    "<h1 style='text-align: center; color: #FF4B4B; font-size: 42px;'>✈️ Kuzey's"
    " Aviation & History Portal 📜</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 16px; color: #888;'>Welcome to the Kuzey's Aviation and History portal! In this website you can see breaking news about Aviation and History. Also you can solve daily quizes, see a timeline of a random war or check the weather and airport radars. Enjoy the website!!</p>",
    unsafe_allow_html=True,
)
st.divider()



tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Global News Feed",
    "🤖 AI Chatbot",
    "📜 History mini games",
    "🏆 AI generated quiz",
    "💬 Feedback",
    "✈️Global Aviation radars"
])

with tab1:
    quotes = [
        (
            '"The engine is the heart of an airplane, but the pilot is its'
            ' soul." - Unknown'
        ),
        (
            '"If you can walk away from a landing, it\'s a good landing." -'
            " Chuck Yeager"
        ),
        (
            '"History is a gallery of pictures in which there are few originals'
            ' and many copies." - Alexis de Tocqueville'
        ),
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


    def display_news_section(section_title, articles, empty_message):
        st.markdown(f"### {section_title}")

        if not articles:
            st.info(empty_message)
            return

        news_cols = st.columns(3)

        for index, article in enumerate(articles):
            col_target = news_cols[index % 3]

            with col_target:
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

    st.divider()

with tab2:
    st.header("🤖 Kuzeys Aviation & History Portal AI Chatbot")
    st.markdown(
        "This custom-trained Google GenAI intelligence specializes in General aviation"
        ", military aviation and world history."
    )

    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    user_query = st.text_area(
        "Ask anything to the portal AI Chatbot:",
        max_chars = 300,
    )

    if st.button("Please press the button to get your answer!", key="chat_button_unique"):
        if user_query.strip() != "":
            with st.spinner("Analyzing tactical databanks..."):
                try:
                    prompt = (
                        "You are the AI of the Kuzeys Aviation And The History"
                        " portal. Answer the users questions about aviation and"
                        " history with rich technical data and fun trivia:"
                        f" {user_query}"
                    )
                    response = client.models.generate_content(
                        model="gemini-3.6-flash", contents=prompt
                    )
                    st.markdown(
                        "<h4 style='color: #FF4B4B;'>Strategic Intelligence"
                        " Report:</h4>",
                        unsafe_allow_html=True,
                    )
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error connecting to AI mainframe: {e}")
        else:
            st.warning("Mainframe requires a valid input question.")

with tab3:
    st.header("📜 Interactive Chronology & Strategy Games")

    st.subheader("⚔️ World War II Timeline")
    t1, t2, t3, t4, t5 = st.tabs(["1939", "1940", "1941", "1944", "1945"])
    with t1:
        st.markdown(
            "**September 1, 1939 - Invasion of Poland:** Germany invades Poland"
            " using Blitzkrieg tactics, starting WWII."
        )
    with t2:
        st.markdown(
            "**May 1940 - Fall of France & Dunkirk:** Allied troops make a"
            " dramatic escape from Dunkirk beaches."
        )
    with t3:
        st.markdown(
            "**December 7, 1941 - Attack on Pearl Harbor:** USA joins the"
            " Allies after a massive surprise attack."
        )
    with t4:
        st.markdown(
            "**June 6, 1944 - D-Day:** The largest naval invasion in history"
            " establishes the Western Front in Normandy."
        )
    with t5:
        st.markdown(
            "**1945 - Total Victory:** Germany and Japan surrender"
            " unconditionally. Peace is restored."
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
                    "I am a British Prime Minister during WWII.",
                    (
                        "I am famous for my 'We shall fight on the beaches'"
                        " speech."
                    ),
                    "I am often pictured with a cigar.",
                ],
                "answer": "Winston Churchill",
            },
        ]
        st.session_state.secret_figure = random.choice(figures)

    for i, clue in enumerate(st.session_state.secret_figure["clues"], 1):
        st.markdown(f"• Clue {i}: {clue}")

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
                "🏆 Correct! It was"
                f" {st.session_state.secret_figure['answer']}!"
            )
        else:
            st.error(
                "❌ Wrong answer! Try reviewing the operational intelligence"
                " clues."
            )

    if st.button("🔄 Next Target / Figure", key="game_reset"):
        del st.session_state.secret_figure
        st.rerun()

with tab4:
    st.header("🤖 AI-Generated Knowledge Quiz")
    st.markdown(
        "Choose a topic and the number of questions. The AI will create "
        "a multiple-choice quiz for you."
    )

    quiz_topic = st.text_input(
        "What should the quiz be about?",
        value="Aviation and world history",
        max_chars=100,
        key="quiz_topic_input",
    )

    question_count = st.slider(
        "How many questions do you want?",
        min_value=1,
        max_value=10,
        value=5,
        key="quiz_question_count",
    )

    if st.button("Generate AI Quiz", key="generate_ai_quiz"):
        topic = quiz_topic.strip()

        if topic == "":
            st.warning("Please enter a quiz topic first.")
        else:
            with st.spinner("Creating your quiz..."):
                try:
                    quiz_client = genai.Client(
                        api_key=st.secrets["GEMINI_API_KEY"]
                    )

                    quiz_prompt = f"""
Create a multiple-choice quiz about: {topic}

Create exactly {question_count} questions.
Each question must have exactly four answer options.
Only one answer may be correct.

Return ONLY valid JSON in this exact format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer_index": 0,
    "explanation": "Short explanation of the correct answer"
  }}
]

The answer_index must be a number from 0 to 3.
Do not include Markdown, commentary, or code fences.
"""

                    response = quiz_client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=quiz_prompt,
                    )

                    response_text = response.text.strip()

                    # Remove code fences if the AI adds them anyway.
                    if response_text.startswith("```"):
                        response_text = response_text.replace(
                            "```json", "", 1
                        )
                        response_text = response_text.replace(
                            "```", ""
                        ).strip()

                    generated_quiz = json.loads(response_text)

                    # Basic validation before displaying AI-generated data.
                    if not isinstance(generated_quiz, list):
                        raise ValueError("Quiz response was not a list.")

                    if len(generated_quiz) != question_count:
                        raise ValueError(
                            "The AI returned the wrong number of questions."
                        )

                    for question in generated_quiz:
                        if not isinstance(question, dict):
                            raise ValueError("Invalid question format.")

                        if not isinstance(
                            question.get("question"), str
                        ):
                            raise ValueError("Invalid question text.")

                        if not isinstance(
                            question.get("options"), list
                        ) or len(question["options"]) != 4:
                            raise ValueError(
                                "Each question must have four options."
                            )

                        answer_index = question.get("answer_index")
                        if answer_index not in [0, 1, 2, 3]:
                            raise ValueError(
                                "Invalid correct-answer index."
                            )

                    st.session_state.ai_quiz = generated_quiz
                    st.session_state.ai_quiz_version = (
                        st.session_state.get("ai_quiz_version", 0) + 1
                    )
                    st.success("Your AI quiz is ready!")

                except Exception:
                    st.error(
                        "The AI could not create the quiz right now. "
                        "Please try again with another topic."
                    )

    if "ai_quiz" in st.session_state:
        st.divider()
        st.subheader("Your Quiz")

        quiz_version = st.session_state.get("ai_quiz_version", 0)
        selected_answers = []

        for index, question in enumerate(st.session_state.ai_quiz):
            selected_answer = st.radio(
                f"{index + 1}. {question['question']}",
                question["options"],
                index=None,
                key=f"ai_answer_{quiz_version}_{index}",
            )
            selected_answers.append(selected_answer)

            if index < len(st.session_state.ai_quiz) - 1:
                st.divider()

        if st.button("Check My Answers", key="check_ai_quiz"):
            unanswered_questions = [
                index + 1
                for index, answer in enumerate(selected_answers)
                if answer is None
            ]

            if unanswered_questions:
                missing = ", ".join(
                    str(number) for number in unanswered_questions
                )
                st.warning(
                    f"Please answer question(s) {missing} before checking your quiz."
                )
            else:
                score = 0

                for index, question in enumerate(st.session_state.ai_quiz):
                    correct_answer = question["options"][
                        question["answer_index"]
                    ]

                    if selected_answers[index] == correct_answer:
                        score += 1

                st.subheader(
                    f"Your Score: {score}/{len(st.session_state.ai_quiz)}"
                )

                for index, question in enumerate(st.session_state.ai_quiz):
                    correct_answer = question["options"][
                        question["answer_index"]
                    ]

                    if selected_answers[index] == correct_answer:
                        st.success(
                            f"✅ Question {index + 1}: Correct!"
                        )
                    else:
                        st.error(
                            f"❌ Question {index + 1}: Incorrect. "
                            f"Correct answer: **{correct_answer}**"
                        )

                    explanation = question.get("explanation", "")
                    if explanation:
                        st.caption(f"Explanation: {explanation}")

                if score == len(st.session_state.ai_quiz):
                    st.balloons()
                    st.success("Perfect score!")

with tab6:
    st.subheader("🌐 Global Radars")
    rad1, rad2 = st.columns(2)

    with rad1:
        st.markdown("**🌍 Live Aviation Weather & Wind Radar**")
        weather_radar_html = '<iframe src="https://ventusky.com" width="100%" height="500px" style="border:none; border-radius: 10px;"></iframe>'
        st.markdown(weather_radar_html, unsafe_allow_html=True)

    with rad2:
        st.markdown("**📍 Kuzey's Global Aviation & Strategy Atlas**")
        map_data = {
            "lat": [
                41.2753,
                40.0786,
                38.3492,
                39.9494,
                34.9154,
                54.4920,
                33.6407,
                35.6528,
            ],
            "lon": [
                28.7519,
                32.5694,
                34.0536,
                32.6889,
                -117.8853,
                -3.4219,
                -84.4277,
                139.7594,
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
                (
                    "Aerospace test center where the sound barrier was"
                    " broken."
                ),
                "Historic Royal Air Force base.",
                "The busiest passenger airport in the world.",
                "Major Asian aviation hub.",
            ],
        }
        df = pd.DataFrame(map_data)
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color=[255, 75, 75, 200],
            get_radius=90000,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=35.0, longitude=25.0, zoom=3)
        tooltip_style = {
            "html": "<b>{name}</b><br/>ℹ️ {details}",
            "style": {
                "backgroundColor": "#1a1a1a",
                "color": "white",
                "borderRadius": "5px",
                "border": "1px solid #FF4B4B",
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

with tab5:
    st.header("💬 Help Improve the Portal")
    st.markdown(
        "Tell us what you like, what is confusing, and what you would like "
        "to see in a future update. Your feedback will help improve the beta."
    )

    components.iframe(
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
        ,
        height=950,
        scrolling=True,
    )

    st.link_button(
        "Open the feedback form in a new tab",
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform",

    )

st.divider()

with st.expander("👤 About the Creator / Portal", expanded=True):
    st.markdown("""
       Hello there! I am Kuzey, the creator of this Aviation and History Portal. I am a passionate aviation enthusiast and history buff. This portal is designed to provide you with the latest news in aviation, historical insights, interactive quizzes, and more. I hope you enjoy exploring the world of aviation and history through this platform! ✈️📜
        """)