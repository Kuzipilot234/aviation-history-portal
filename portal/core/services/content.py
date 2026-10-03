"""Fixed portal content: announcements, history games and map points.

Visible text is wrapped in gettext_lazy (as _) so it is translated into the
visitor's language when shown. Translations live in portal/locale.
"""

from datetime import date

from django.utils.translation import gettext_lazy as _

ANNOUNCEMENT_TAGS = {
    "feature": _("New feature"),
    "update": _("Update"),
    "fix": _("Fix"),
}

# Newest first. "tag" is a key of ANNOUNCEMENT_TAGS.
ANNOUNCEMENTS = [
    {
        "date": date(2026, 10, 3),
        "tag": "feature",
        "title": _("A fresh look, plus new features"),
        "message": _(
            "The portal has a cleaner design with dark and light themes, and is "
            "now available in English, Turkish, French and Spanish. Also new: "
            "\"On this day\" on the home page, a live flight tracker on the "
            "Radars page, and search and filters on the News page."
        ),
    },
    {
        "date": date(2026, 9, 26),
        "tag": "fix",
        "title": _("AI features are working again"),
        "message": _("The issue is now fixed. You can use the AI features freely!"),
    },
    {
        "date": date(2026, 9, 18),
        "tag": "feature",
        "title": _("AI daily news briefing"),
        "message": _(
            "You can now see a short summarized briefing of the latest "
            "aviation and history news."
        ),
    },
]

FEEDBACK_FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfR56-Q64jFBLxihSTV5jeyDfbWxxUaPo27zcd79FVeXbtlHA/viewform"
)

WW2_TIMELINE = {
    "1939": (
        _("September 1, 1939 - Invasion of Poland"),
        _("Germany invades Poland using Blitzkrieg tactics, starting WWII."),
    ),
    "1940": (
        _("May 1940 - Fall of France & Dunkirk"),
        _("Allied troops make a dramatic escape from Dunkirk beaches."),
    ),
    "1941": (
        _("December 7, 1941 - Attack on Pearl Harbor"),
        _("USA joins the Allies after a massive surprise attack."),
    ),
    "1944": (
        _("June 6, 1944 - D-Day"),
        _(
            "The largest naval invasion in history establishes the Western "
            "Front in Normandy."
        ),
    ),
    "1945": (
        _("1945 - Total Victory"),
        _("Germany and Japan surrender unconditionally."),
    ),
}

# The answers are names and stay the same in every language.
HISTORICAL_FIGURES = [
    {
        "answer": "Mustafa Kemal Atatürk",
        "clues": [
            _("I am the founder of the Republic of Türkiye."),
            _("I was born in Salonica in 1881."),
            _("My military genius was proven at Gallipoli."),
        ],
    },
    {
        "answer": "Julius Caesar",
        "clues": [
            _("I am a Roman general and dictator."),
            _("I famously crossed the Rubicon river."),
            _("My last words were allegedly addressed to Brutus."),
        ],
    },
    {
        "answer": "Napoleon Bonaparte",
        "clues": [
            _("I crowned myself Emperor of the French."),
            _("I dominated European affairs for over a decade."),
            _("My final military defeat occurred at Waterloo."),
        ],
    },
    {
        "answer": "Winston Churchill",
        "clues": [
            _("I was a British Prime Minister during WWII."),
            _("I am famous for my 'We shall fight on the beaches' speech."),
            _("I am often pictured with a cigar."),
        ],
    },
]

MAP_POINTS = [
    {"name": "Istanbul Airport (IST)", "lat": 41.2753, "lon": 28.7519,
     "details": _("Europe's modern megahub.")},
    {"name": "Mürted Air Base (Ankara)", "lat": 40.0786, "lon": 32.5694,
     "details": _("Historically significant Turkish jet base.")},
    {"name": "Incirlik Air Base (Adana)", "lat": 38.3492, "lon": 34.0536,
     "details": _("Strategic NATO aviation hub.")},
    {"name": "Eskişehir Air Base", "lat": 39.9494, "lon": 32.6889,
     "details": _("Birthplace of Turkish aviation.")},
    {"name": "Edwards Air Force Base (USA)", "lat": 34.9154, "lon": -117.8853,
     "details": _("Aerospace test center where the sound barrier was broken.")},
    {"name": "RAF Lossiemouth (UK)", "lat": 54.4920, "lon": -3.4219,
     "details": _("Historic Royal Air Force base.")},
    {"name": "Hartsfield-Jackson Atlanta (USA)", "lat": 33.6407, "lon": -84.4277,
     "details": _("The busiest passenger airport in the world.")},
    {"name": "Tokyo Haneda (Japan)", "lat": 35.6528, "lon": 139.7594,
     "details": _("Major Asian aviation hub.")},
]
