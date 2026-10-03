import logging

from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.services import ai
from core.services.ratelimit import seconds_to_wait

logger = logging.getLogger(__name__)

CHAT_COOLDOWN_SECONDS = 15
CHAT_MAX_CHARS = 300
QUIZ_COOLDOWN_SECONDS = 20
QUIZ_TOPIC_MAX_CHARS = 100
DEFAULT_TOPIC = "Aviation and world history"
CHAT_SUGGESTIONS = [
    "How did the Concorde fly faster than sound?",
    "What happened at the Battle of Gallipoli?",
    "Why do planes leave contrails?",
    "Who were the Tuskegee Airmen?",
]


def chatbot(request):
    return render(
        request,
        "ai/chatbot.html",
        {"max_chars": CHAT_MAX_CHARS, "suggestions": CHAT_SUGGESTIONS},
    )


@require_POST
def chatbot_ask(request):
    question = request.POST.get("question", "").strip()[:CHAT_MAX_CHARS]
    context = {"question": question}
    if not question:
        context["warning"] = "Please enter a question first."
    elif wait := seconds_to_wait(request, "chat", CHAT_COOLDOWN_SECONDS):
        context["warning"] = f"Please wait {wait} more second(s) before asking again."
    else:
        try:
            context["answer"] = ai.ask_chatbot(question)
        except Exception:
            logger.exception("Chatbot request failed")
            context["error"] = (
                "The AI chatbot couldn't answer right now. Please try again in a minute."
            )
    return render(request, "ai/_chat_answer.html", context)


def quiz(request):
    return render(
        request,
        "ai/quiz.html",
        {
            "difficulties": ai.DIFFICULTIES,
            "min_questions": ai.MIN_QUESTIONS,
            "max_questions": ai.MAX_QUESTIONS,
            "default_topic": DEFAULT_TOPIC,
            "topic_max_chars": QUIZ_TOPIC_MAX_CHARS,
            "questions": _questions(request.session.get("quiz")),
        },
    )


def _questions(quiz, answers=None):
    """Shape a stored quiz for the _quiz_area template."""
    if not quiz:
        return []
    answers = answers or [None] * len(quiz)
    return [
        {
            "number": index + 1,
            "name": f"q{index}",
            "text": question["question"],
            "options": list(enumerate(question["options"])),
            "chosen": chosen,
        }
        for index, (question, chosen) in enumerate(zip(quiz, answers))
    ]


def _read_settings(post):
    topic = post.get("topic", "").strip()[:QUIZ_TOPIC_MAX_CHARS]
    difficulty = post.get("difficulty")
    if difficulty not in ai.DIFFICULTIES:
        difficulty = "Medium"
    try:
        count = int(post.get("count", ai.MIN_QUESTIONS))
    except ValueError:
        count = ai.MIN_QUESTIONS
    count = min(max(count, ai.MIN_QUESTIONS), ai.MAX_QUESTIONS)
    return topic, difficulty, count


@require_POST
def quiz_generate(request):
    topic, difficulty, count = _read_settings(request.POST)
    context = {"questions": _questions(request.session.get("quiz"))}
    if not topic:
        context["warning"] = "Please enter a quiz topic first."
    elif wait := seconds_to_wait(request, "quiz", QUIZ_COOLDOWN_SECONDS):
        context["warning"] = (
            f"Please wait {wait} more second(s) before generating another quiz."
        )
    else:
        try:
            new_quiz = ai.generate_quiz(topic, difficulty, count)
        except ai.QuizFormatError:
            logger.warning("Quiz came back in the wrong format", exc_info=True)
            context["error"] = (
                "The AI returned a quiz in the wrong format. Please select "
                "Generate New Quiz again."
            )
        except Exception:
            logger.exception("Quiz generation failed")
            context["error"] = (
                "The quiz couldn't be created right now. Please try again in a minute."
            )
        else:
            request.session["quiz"] = new_quiz
            context = {
                "questions": _questions(new_quiz),
                "success": "Your personalized quiz is ready. Good luck!",
            }
    return render(request, "ai/_quiz_area.html", context)


@require_POST
def quiz_check(request):
    quiz = request.session.get("quiz")
    if not quiz:
        return render(
            request,
            "ai/_quiz_area.html",
            {"warning": "That quiz has expired. Please generate a new one."},
        )

    answers = []
    for index in range(len(quiz)):
        value = request.POST.get(f"q{index}")
        answers.append(int(value) if value in ("0", "1", "2", "3") else None)

    unanswered = [str(i + 1) for i, answer in enumerate(answers) if answer is None]
    if unanswered:
        return render(
            request,
            "ai/_quiz_area.html",
            {
                "questions": _questions(quiz, answers),
                "warning": (
                    f"Please answer question(s) {', '.join(unanswered)} before "
                    "checking your quiz."
                ),
            },
        )

    score, results = ai.score_quiz(quiz, answers)
    total = len(quiz)
    return render(
        request,
        "ai/_quiz_results.html",
        {
            "score": score,
            "total": total,
            "percentage": round(score / total * 100),
            "results": results,
        },
    )
