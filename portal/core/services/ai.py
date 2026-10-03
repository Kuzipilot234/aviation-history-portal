"""All Groq calls: the daily briefing, the chatbot, quizzes and translation."""

import json

from django.conf import settings
from django.core.cache import cache
from groq import Groq

# The language the model should write in, by site language code.
LANGUAGE_NAMES = {"en": "English", "tr": "Turkish", "fr": "French", "es": "Spanish"}

BRIEFING_CACHE_KEY = "daily_briefing:{language}"
BRIEFING_CACHE_SECONDS = 6 * 60 * 60
BRIEFING_STORIES_PER_CATEGORY = 6

DIFFICULTIES = ["Easy", "Medium", "Hard"]
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10


class QuizFormatError(ValueError):
    """The model returned a quiz that doesn't match the requested format."""


def _complete(prompt):
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set.")
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def _strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return text


def _write_in(language):
    """The prompt line that sets the answer language."""
    return f"Write your entire answer in {LANGUAGE_NAMES.get(language, 'English')}."


def daily_briefing(articles, language="en"):
    """Summarize the latest articles in the given language.

    Successful results are cached for six hours per language. Errors are
    raised, not cached, so the next visitor triggers a retry. Returns None
    when there are no articles to summarize.
    """
    key = BRIEFING_CACHE_KEY.format(language=language)
    briefing = cache.get(key)
    if briefing is not None:
        return briefing
    if not articles:
        return None

    selected = []
    for category in ("Aviation", "History"):
        in_category = [a for a in articles if a["category"] == category]
        selected += in_category[:BRIEFING_STORIES_PER_CATEGORY]
    source_text = "\n".join(
        f"[{item['category']}] {item['title']}: {item['summary']}" for item in selected
    )
    prompt = (
        "You are the editor of Kuzey's Aviation and History Portal. "
        "Write a concise daily briefing in 3 short paragraphs: one aviation "
        "update, one history update, and one overall takeaway. Use only the "
        "information supplied below. Do not invent facts, dates, or events. "
        f"Do not use Markdown headings. {_write_in(language)}\n\n" + source_text
    )
    briefing = _complete(prompt)
    cache.set(key, briefing, BRIEFING_CACHE_SECONDS)
    return briefing


def ask_chatbot(question, language="en"):
    prompt = (
        "You are the AI assistant for Kuzey's Aviation and History Portal. "
        "Answer questions about aviation and history clearly, accurately, and "
        f"engagingly. {_write_in(language)} User question: {question}"
    )
    return _complete(prompt)


def parse_quiz(response_text, question_count):
    """Parse and check the model's JSON quiz. Raises QuizFormatError."""
    try:
        quiz = json.loads(_strip_code_fences(response_text))
    except json.JSONDecodeError as error:
        raise QuizFormatError("The quiz was not valid JSON.") from error

    if not isinstance(quiz, list) or len(quiz) != question_count:
        raise QuizFormatError("The quiz has the wrong number of questions.")
    for question in quiz:
        if (
            not isinstance(question, dict)
            or not isinstance(question.get("question"), str)
            or not isinstance(question.get("options"), list)
            or len(question["options"]) != 4
            or not all(isinstance(option, str) for option in question["options"])
            or isinstance(question.get("answer_index"), bool)
            or question.get("answer_index") not in (0, 1, 2, 3)
        ):
            raise QuizFormatError("A question is in the wrong format.")

    return [
        {
            "question": q["question"],
            "options": q["options"],
            "answer_index": q["answer_index"],
            "explanation": q["explanation"] if isinstance(q.get("explanation"), str) else "",
        }
        for q in quiz
    ]


def generate_quiz(topic, difficulty, question_count, language="en"):
    prompt = f"""
Create a {difficulty.lower()} multiple-choice quiz about: {topic}
Write the questions, options and explanations in {LANGUAGE_NAMES.get(language, "English")}. Keep the JSON keys in English.

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
    return parse_quiz(_complete(prompt), question_count)


def translate_article(title, summary, language):
    """Translate a news article. Returns {"title": ..., "summary": ...}."""
    prompt = (
        f"Translate this news article into {LANGUAGE_NAMES[language]}. Keep names, "
        "aircraft models and numbers as they are. Return ONLY valid JSON in the form "
        '{"title": "...", "summary": "..."} with no Markdown or code fences.\n\n'
        + json.dumps({"title": title, "summary": summary}, ensure_ascii=False)
    )
    result = json.loads(_strip_code_fences(_complete(prompt)))
    if not isinstance(result, dict) or not all(
        isinstance(result.get(key), str) for key in ("title", "summary")
    ):
        raise ValueError("The translation was in the wrong format.")
    return {"title": result["title"], "summary": result["summary"]}


def score_quiz(quiz, answers):
    """answers holds the chosen option index (or None) for each question."""
    results = [
        {
            **question,
            "chosen": chosen,
            "correct_answer": question["options"][question["answer_index"]],
            "chosen_answer": question["options"][chosen] if chosen is not None else None,
            "is_correct": chosen == question["answer_index"],
        }
        for question, chosen in zip(quiz, answers)
    ]
    score = sum(result["is_correct"] for result in results)
    return score, results
