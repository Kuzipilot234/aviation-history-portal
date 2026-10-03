"""Fixed portal content: announcements, quotes, history games and map points."""

from datetime import date

# Newest first. "tag" is one of: New feature, Update, Fix.
ANNOUNCEMENTS = [
    {
        "date": date(2026, 10, 3),
        "tag": "New feature",
        "title": "A fresh look, plus three new features",
        "message": (
            "The portal has a cleaner design. New: \"On this day\" on the home "
            "page, a live flight tracker on the Radars page, and search and "
            "filters on the News page."
        ),
    },
    {
        "date": date(2026, 9, 26),
        "tag": "Fix",
        "title": "AI features are working again",
        "message": "The issue is now fixed. You can use the AI features freely!",
    },
    {
        "date": date(2026, 9, 18),
        "tag": "New feature",
        "title": "AI daily news briefing",
        "message": (
            "You can now see a short summarized briefing of the latest "
            "aviation and history news."
        ),
    },
]

QUOTES = [
    '"The engine is the heart of an airplane, but the pilot is its soul." - Unknown',
    '"If you can walk away from a landing, it\'s a good landing." - Chuck Yeager',
    '"History is a gallery of pictures in which there are few originals and '
    'many copies." - Alexis de Tocqueville',
]

FEEDBACK_FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
)

WW2_TIMELINE = {
    "1939": (
        "September 1, 1939 - Invasion of Poland",
        "Germany invades Poland using Blitzkrieg tactics, starting WWII.",
    ),
    "1940": (
        "May 1940 - Fall of France & Dunkirk",
        "Allied troops make a dramatic escape from Dunkirk beaches.",
    ),
    "1941": (
        "December 7, 1941 - Attack on Pearl Harbor",
        "USA joins the Allies after a massive surprise attack.",
    ),
    "1944": (
        "June 6, 1944 - D-Day",
        "The largest naval invasion in history establishes the Western Front "
        "in Normandy.",
    ),
    "1945": (
        "1945 - Total Victory",
        "Germany and Japan surrender unconditionally.",
    ),
}

HISTORICAL_FIGURES = [
    {
        "answer": "Mustafa Kemal Atatürk",
        "clues": [
            "I am the founder of the Republic of Türkiye.",
            "I was born in Salonica in 1881.",
            "My military genius was proven at Gallipoli.",
        ],
    },
    {
        "answer": "Julius Caesar",
        "clues": [
            "I am a Roman general and dictator.",
            "I famously crossed the Rubicon river.",
            "My last words were allegedly addressed to Brutus.",
        ],
    },
    {
        "answer": "Napoleon Bonaparte",
        "clues": [
            "I crowned myself Emperor of the French.",
            "I dominated European affairs for over a decade.",
            "My final military defeat occurred at Waterloo.",
        ],
    },
    {
        "answer": "Winston Churchill",
        "clues": [
            "I was a British Prime Minister during WWII.",
            "I am famous for my 'We shall fight on the beaches' speech.",
            "I am often pictured with a cigar.",
        ],
    },
]

MAP_POINTS = [
    {"name": "Istanbul Airport (IST)", "lat": 41.2753, "lon": 28.7519,
     "details": "Europe's modern megahub."},
    {"name": "Mürted Air Base (Ankara)", "lat": 40.0786, "lon": 32.5694,
     "details": "Historically significant Turkish jet base."},
    {"name": "Incirlik Air Base (Adana)", "lat": 38.3492, "lon": 34.0536,
     "details": "Strategic NATO aviation hub."},
    {"name": "Eskişehir Air Base", "lat": 39.9494, "lon": 32.6889,
     "details": "Birthplace of Turkish aviation."},
    {"name": "Edwards Air Force Base (USA)", "lat": 34.9154, "lon": -117.8853,
     "details": "Aerospace test center where the sound barrier was broken."},
    {"name": "RAF Lossiemouth (UK)", "lat": 54.4920, "lon": -3.4219,
     "details": "Historic Royal Air Force base."},
    {"name": "Hartsfield-Jackson Atlanta (USA)", "lat": 33.6407, "lon": -84.4277,
     "details": "The busiest passenger airport in the world."},
    {"name": "Tokyo Haneda (Japan)", "lat": 35.6528, "lon": 139.7594,
     "details": "Major Asian aviation hub."},
]
