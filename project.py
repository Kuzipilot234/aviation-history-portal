import random

import base64
from pathlib import Path
import feedparser
import pandas as pd
import pydeck as pdk
import streamlit as st
from google import genai
import streamlit.components.v1 as components




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


@st.cache_data(ttl=900)
def load_news_from_rss():
    articles = []
    FEEDBACK_FORM_URL = (
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
    )

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

wikipedia_databank = {
    "sabiha gokcen": (
        "Sabiha Gökçen is the first female military pilot in the world. She"
        " graduated from Üsküdar American College and trained at the Eskişehir"
        " Aviation School. As the adopted daughter of Mustafa Kemal Atatürk,"
        " her legacy continues to inspire generations of aviators globally."
    ),
    "b-52 stratofortress": (
        "The B-52 Stratofortress remains one of the longest-serving heavy"
        " bombers in military history. First flying in 1952, this strategic"
        " aircraft is projected to receive engineering upgrades allowing it to"
        " sustain operations for nearly another quarter-century."
    ),
    "global air traffic": (
        "Global aviation infrastructure orchestrates over 200,000 aircraft"
        " movements daily. Currently, Hartsfield-Jackson Atlanta holds the"
        " record for absolute passenger volume, closely followed by Istanbul"
        " Airport as Europe's premier strategic transit hub."
    ),
    "lightning protection": (
        "Modern aerospace engineering guarantees that commercial flights are"
        " immune to lightning strikes. High-tech composite frames, like those"
        " found on the Boeing 787 and 777, feature integrated aluminum mesh"
        " shields to instantly dissipate high-voltage currents."
    ),
    "messerschmitt me 262": (
        "The Messerschmitt Me 262 was the world's first operational jet-powered"
        " fighter aircraft, introduced by Germany during WWII. Its extreme"
        " speed initially baffled Allied commanders, fundamentally rewriting"
        " tactical air combat doctrines."
    ),
    "fastest war in history": (
        "The Anglo-Zanzibar War of August 27, 1896, stands as the shortest"
        " recorded conflict in human history. Lasting exactly 38 minutes, the"
        " conflict concluded swiftly following decisive naval artillery"
        " bombardment by British warships."
    ),
    "emu war": (
        "The Great Emu War of 1932 was a bizarre military operation where the"
        " Australian military deployed soldiers armed with Lewis guns to cull"
        " an overpopulation of emu birds destroying crops. The highly agile"
        " birds successfully evaded the tactical deployments."
    ),
}
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Global News Feed",
    "🤖 AI Chatbot",
    "📜 History mini games",
    "🏆 Daily Updated Quick Quiz",
    "💬 Feedback",
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

    st.divider()

    st.markdown("### 🔍 Global Aviation & History Database ")
    wiki_query = st.text_input(
        "Search our database!",
        placeholder=(
            "Type an entity (e.g., Sabiha, B-52, Emu, Me 262, Lightning)..."
        ),
        key="wiki_search_input",
    )

    if wiki_query.strip() != "":
        match_found = False
        for key, value in wikipedia_databank.items():
            if wiki_query.lower() in key:
                st.markdown(f"#### 📖 Encyclopedia Entry: {key.upper()}")
                st.success(value)
                match_found = True
        if not match_found:
            st.warning(
                "No official encyclopedia record found. However, you can"
                " instantly ask our AI Chatbot below for full details!"
            )
        st.divider()

    st.subheader("📰 Live Global News Feed")
    st.markdown(
        "Stay informed with direct journalistic updates covering global"
        " aviation milestones, defense strategies, and archival historical"
        " findings."
    )

    if rss_articles:
        news_cols = st.columns(3)

        for idx, article in enumerate(rss_articles):
            col_target = news_cols[idx % 3]

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
    else:
        st.info("No news articles are available right now.")

    st.divider()

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
    st.header("🏆 Operational Knowledge Quiz")
    st.markdown(
        "Complete the fields below to verify your strategic clearance score."
    )

    q1 = st.radio(
        "1. What is the largest plane in the world?",
        ["Boeing 777", "Boeing 787", "Airbus A380"],
    )
    st.divider()
    q2 = st.radio(
        "2. What is the most sold passenger jet in the history?",
        ["Boeing 737", "Airbus A330", "Airbus A320"],
    )
    st.divider()
    q3 = st.radio(
        "3. What is the start date of the World war 2?",
        ["1945", "1939", "1914"],
    )
    st.divider()
    q4 = st.radio(
        "4. What is the Soviet Unions Founder?",
        ["Vladimir Lenin", "Stalin", "Brezhnev"],
    )
    st.divider()
    q5 = st.radio(
        "5. Who was the leader of Vichy France during WW2",
        ["Charles De Gaulle", "Petain", "Churchill"],
    )
    st.divider()
    q6 = st.radio(
        "6. Lauda Airlines belongs to which country?",
        ["Ireland", "Russia", "Austria"],
    )
    st.divider()
    q7 = st.radio(
        "7. What was the tactics name Germans used in WW2?",
        ["Blitzkrieg", "German", "Great Tactic"],
    )
    st.divider()
    q8 = st.radio(
        "8. What is the Russias Flag Carrier Airline?",
        ["S7 Air.", "Aeroflot", "Rossiya"],
    )
    st.divider()
    q9 = st.radio(
        "9. What is the attacks name that japans did to Americans during"
        " WW2?",
        ["Pearl Harbor", "Operation Market Garden", "Operation Great Sun"],
    )

    if st.button("Calculate Final Score", key="quiz_submit"):
        score = 0
        if q1 == "Airbus A380":
            score += 1
        if q2 == "Airbus A320":
            score += 1
        if q3 == "1939":
            score += 1
        if q4 == "Vladimir Lenin":
            score += 1
        if q5 == "Petain":
            score += 1
        if q6 == "Austria":
            score += 1
        if q7 == "Blitzkrieg":
            score += 1
        if q8 == "Aeroflot":
            score += 1
        if q9 == "Pearl Harbor":
            score += 1

        st.subheader(f"Your Verified Score: {score}/9")
        if score == 9:
            st.balloons()
            st.success(
                "Perfect Score! You are a validated Master Historian and Flight"
                " Enthusiast! 🎖️"
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
        "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
        ,
    )

st.divider()

with st.expander("👤 About the Creator / Portal", expanded=True):
    st.markdown("""
       Hello there! I am Kuzey, the creator of this Aviation and History Portal. I am a passionate aviation enthusiast and history buff. This portal is designed to provide you with the latest news in aviation, historical insights, interactive quizzes, and more. I hope you enjoy exploring the world of aviation and history through this platform! ✈️📜
        """)