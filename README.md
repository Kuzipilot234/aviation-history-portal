# Kuzey's Aviation & History Portal

Aviation and history news, an AI chatbot and quiz, history games and radar
tools. Built with Django and HTMX; the AI features use Groq.

## Run it locally

```bash
cd portal
pip install -r requirements.txt
cp .env.example .env        # then put your Groq key in .env
python manage.py runserver
```

Open http://127.0.0.1:8000.

Run the tests with `python manage.py test`.

## Layout

| Path | What it holds |
| --- | --- |
| `portal/core/services/` | Plain Python logic: RSS (`news.py`), Groq calls (`ai.py`), fixed content (`content.py`), rate limits |
| `portal/news/` | News page, search, the AI summary and article translation |
| `portal/ai/` | Chatbot and quiz |
| `portal/games/` | WW2 timeline and Who Am I |
| `portal/core/` | Home page, shared layout, CSS, radars, feedback, translation command |

To post an announcement, edit `ANNOUNCEMENTS` in `portal/core/services/content.py`.

## Languages

The site is in English, Turkish, French and Spanish. Visitors get their
browser's language and can switch with the globe menu. The AI features answer
in the chosen language, and news articles have an AI "Translate" button.

After adding or changing visible text (`{% translate %}` in templates or
`_("...")` in Python):

```bash
cd portal
python manage.py update_translations
```

Then fill in the new empty `msgstr ""` lines in
`locale/tr|fr|es/LC_MESSAGES/django.po` and run the command again to compile
them. The tests fail while anything is untranslated.

## Deploying on Render

`render.yaml` describes the web service. Render redeploys on every push to `main`.

First-time setup: in the Render dashboard choose **New → Blueprint**, pick this
repository, and enter `GROQ_API_KEY` when asked. Render generates `SECRET_KEY`.
