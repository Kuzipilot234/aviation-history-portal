import json
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings

from core.services import ai, news
from core.templatetags.portal import markdownify

LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

SAMPLE_ARTICLES = [
    {
        "category": "Aviation",
        "title": "A350 milestone",
        "summary": "Airbus delivers its 700th A350.",
        "preview": "Airbus delivers its 700th A350.",
        "url": "https://example.com/a350",
        "published": "Fri, 02 Oct 2026",
    },
    {
        "category": "History",
        "title": "Battle of Hastings",
        "summary": "A look back at 1066.",
        "preview": "A look back at 1066.",
        "url": "",
        "published": "Thu, 01 Oct 2026",
    },
]


def quiz_json(count=5, **overrides):
    question = {
        "question": "Who flew first at Kitty Hawk?",
        "options": ["Wright brothers", "Blériot", "Lindbergh", "Earhart"],
        "answer_index": 0,
        "explanation": "Orville Wright flew in 1903.",
    }
    question.update(overrides)
    return json.dumps([question] * count)


class NewsServiceTests(TestCase):
    def test_strip_html_removes_tags_and_entities(self):
        text = '<p>Hello&nbsp;<a href="x">world</a> &amp; more</p><script>bad()</script>'
        self.assertEqual(news.strip_html(text), "Hello world & more")

    def test_published_label(self):
        import time

        entry = {"published_parsed": time.strptime("2026-10-03 09:05", "%Y-%m-%d %H:%M")}
        self.assertEqual(news.published_label(entry), "3 Oct 2026, 09:05")
        self.assertEqual(news.published_label({"published": "Yesterday"}), "Yesterday")

    def test_preview_cuts_on_a_word(self):
        self.assertEqual(news.make_preview("one two three", length=9), "one two...")
        self.assertEqual(news.make_preview("short"), "short")


class QuizParsingTests(TestCase):
    def test_valid_quiz(self):
        quiz = ai.parse_quiz(quiz_json(5), 5)
        self.assertEqual(len(quiz), 5)
        self.assertEqual(quiz[0]["answer_index"], 0)

    def test_code_fences_are_removed(self):
        self.assertEqual(len(ai.parse_quiz("```json\n" + quiz_json(5) + "\n```", 5)), 5)

    def test_rejects_bad_quizzes(self):
        bad_inputs = [
            ("not json", 5),
            (quiz_json(4), 5),
            (quiz_json(5, answer_index=4), 5),
            (quiz_json(5, answer_index=True), 5),
            (quiz_json(5, options=["a", "b", "c"]), 5),
        ]
        for text, count in bad_inputs:
            with self.subTest(text=text[:40]), self.assertRaises(ai.QuizFormatError):
                ai.parse_quiz(text, count)

    def test_score(self):
        quiz = ai.parse_quiz(quiz_json(5), 5)
        score, results = ai.score_quiz(quiz, [0, 1, 0, None, 0])
        self.assertEqual(score, 3)
        self.assertFalse(results[1]["is_correct"])
        self.assertEqual(results[1]["correct_answer"], "Wright brothers")


class MarkdownTests(TestCase):
    def test_markdown_is_rendered_and_html_is_cleaned(self):
        html = markdownify("**bold** <script>alert(1)</script>")
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("<script>", html)


@override_settings(CACHES=LOCMEM, SESSION_ENGINE="django.contrib.sessions.backends.cache")
class PageTests(TestCase):
    def setUp(self):
        cache.clear()
        patcher = mock.patch("core.services.news.fetch_articles", return_value=SAMPLE_ARTICLES)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_every_page_loads(self):
        for url in ["/", "/chatbot/", "/quiz/", "/history/", "/feedback/", "/radars/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_home_lists_articles(self):
        response = self.client.get("/")
        self.assertContains(response, "A350 milestone")
        self.assertContains(response, "Battle of Hastings")

    @mock.patch("core.services.ai._complete", return_value="**Today** in aviation.")
    def test_briefing_is_cached(self, complete):
        self.assertContains(self.client.get("/briefing/"), "<strong>Today</strong>")
        self.client.get("/briefing/")
        complete.assert_called_once()

    @mock.patch("core.services.ai._complete", side_effect=RuntimeError("down"))
    def test_briefing_failure_shows_message(self, complete):
        self.assertContains(self.client.get("/briefing/"), "temporarily unavailable")

    @mock.patch("core.services.ai._complete", return_value="Mach 1 was first broken in 1947.")
    def test_chatbot_answers_then_enforces_cooldown(self, complete):
        response = self.client.post("/chatbot/ask/", {"question": "When was Mach 1 broken?"})
        self.assertContains(response, "1947")
        response = self.client.post("/chatbot/ask/", {"question": "Again?"})
        self.assertContains(response, "Please wait")

    @mock.patch("core.services.ai._complete", side_effect=RuntimeError("secret detail"))
    def test_chatbot_error_hides_details(self, complete):
        response = self.client.post("/chatbot/ask/", {"question": "Hi"})
        self.assertContains(response, "answer right now")
        self.assertNotContains(response, "secret detail")

    def test_chatbot_needs_a_question(self):
        self.assertContains(self.client.post("/chatbot/ask/", {"question": "  "}), "enter a question")

    @mock.patch("core.services.ai._complete", return_value=quiz_json(5))
    def test_quiz_flow(self, complete):
        response = self.client.post(
            "/quiz/generate/", {"topic": "Aviation", "difficulty": "Easy", "count": "5"}
        )
        self.assertContains(response, "Question 5 of 5")

        response = self.client.post("/quiz/check/", {"q0": "0", "q1": "0"})
        self.assertContains(response, "answer question(s) 3, 4, 5")
        self.assertContains(response, 'value="0" checked')

        answers = {f"q{i}": "0" for i in range(5)}
        answers["q4"] = "2"
        response = self.client.post("/quiz/check/", answers)
        self.assertContains(response, "Final Score: 4/5 (80%)")

    def test_quiz_check_without_quiz(self):
        self.assertContains(self.client.post("/quiz/check/", {}), "expired")

    def test_who_am_i(self):
        self.client.get("/history/")
        index = self.client.session["figure_index"]
        from core.services.content import HISTORICAL_FIGURES

        answer = HISTORICAL_FIGURES[index]["answer"]
        self.assertContains(self.client.post("/history/guess/", {"guess": answer}), "Correct")
        self.assertContains(self.client.post("/history/guess/", {"guess": "Nobody"}), "Not Nobody")

        self.client.post("/history/next/")
        self.assertNotEqual(self.client.session["figure_index"], index)

    def test_timeline_tabs(self):
        self.assertContains(self.client.get("/history/timeline/1944/"), "D-Day")
        self.assertEqual(self.client.get("/history/timeline/1999/").status_code, 404)
