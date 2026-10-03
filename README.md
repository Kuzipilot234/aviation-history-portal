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
| `portal/news/` | Home page and the daily briefing |
| `portal/ai/` | Chatbot and quiz |
| `portal/games/` | WW2 timeline and Who Am I |
| `portal/core/` | Shared layout, CSS, feedback and radar pages |

To post an announcement, edit `ANNOUNCEMENTS` in `portal/core/services/content.py`.

## Deploying on Render

`render.yaml` describes the web service. Render redeploys on every push to `main`.

First-time setup: in the Render dashboard choose **New → Blueprint**, pick this
repository, and enter `GROQ_API_KEY` when asked. Render generates `SECRET_KEY`.
