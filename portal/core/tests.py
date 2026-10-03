import json
from datetime import datetime, timezone
from io import StringIO
from unittest import mock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings

from core.services import ai, flights, news, onthisday
from core.templatetags.portal import markdownify

LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

SAMPLE_ARTICLES = [
    {
        "id": "a350",
        "category": "Aviation",
        "title": "A350 milestone",
        "summary": "Airbus delivers its 700th A350.",
        "preview": "Airbus delivers its 700th A350.",
        "url": "https://example.com/a350",
        "published_at": datetime(2026, 10, 2, 9, 5, tzinfo=timezone.utc),
        "published": "Fri, 02 Oct 2026",
    },
    {
        "id": "hastings",
        "category": "History",
        "title": "Battle of Hastings",
        "summary": "A look back at 1066.",
        "preview": "A look back at 1066.",
        "url": "",
        "published_at": None,
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

    def test_published_at(self):
        import time

        entry = {"published_parsed": time.strptime("2026-10-03 09:05", "%Y-%m-%d %H:%M")}
        self.assertEqual(news.published_at(entry), datetime(2026, 10, 3, 9, 5, tzinfo=timezone.utc))
        self.assertIsNone(news.published_at({"published": "Yesterday"}))

    def test_article_id_is_stable(self):
        self.assertEqual(news.article_id("https://x.com/a", "A"), news.article_id("https://x.com/a", "B"))
        self.assertNotEqual(news.article_id("https://x.com/a", ""), news.article_id("https://x.com/b", ""))

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
        for url in ["/", "/news/", "/chatbot/", "/quiz/", "/history/", "/feedback/", "/radars/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_home_is_simple(self):
        response = self.client.get("/")
        self.assertContains(response, "Announcements")
        self.assertContains(response, "A fresh look")
        self.assertNotContains(response, "A350 milestone")
        self.assertContains(response, 'id="theme-toggle"')

    def test_news_page_lists_articles(self):
        response = self.client.get("/news/")
        self.assertContains(response, "A350 milestone")
        self.assertContains(response, "Battle of Hastings")

    def test_news_filters(self):
        response = self.client.get("/news/results/", {"category": "History"})
        self.assertContains(response, "Battle of Hastings")
        self.assertNotContains(response, "A350 milestone")

        response = self.client.get("/news/results/", {"q": "airbus"})
        self.assertContains(response, "A350 milestone")
        self.assertNotContains(response, "Battle of Hastings")

        response = self.client.get("/news/results/", {"q": "zeppelin"})
        self.assertContains(response, "No stories match")

    @mock.patch("core.services.onthisday.httpx.get")
    def test_on_this_day(self, get):
        get.return_value = mock.Mock(
            json=lambda: {
                "selected": [
                    {"year": 1990, "text": "German reunification.", "pages": [
                        {"content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/German_reunification"}}}
                    ]},
                    {"year": 1952, "text": "Operation Hurricane.", "pages": []},
                ]
            },
            raise_for_status=lambda: None,
        )
        response = self.client.get("/on-this-day/")
        self.assertContains(response, "1952")
        self.assertContains(response, "German reunification.")
        self.assertLess(response.content.index(b"1952"), response.content.index(b"1990"))

    @mock.patch("core.services.onthisday.httpx.get", side_effect=RuntimeError("offline"))
    def test_on_this_day_failure(self, get):
        self.assertContains(self.client.get("/on-this-day/"), "couldn")

    @mock.patch("core.services.ai._complete", return_value="**Today** in aviation.")
    def test_briefing_is_cached(self, complete):
        self.assertContains(self.client.get("/news/briefing/"), "<strong>Today</strong>")
        self.client.get("/news/briefing/")
        complete.assert_called_once()

    @mock.patch("core.services.ai._complete", side_effect=RuntimeError("down"))
    def test_briefing_failure_shows_message(self, complete):
        self.assertContains(self.client.get("/news/briefing/"), "temporarily unavailable")

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


STATE = {"hex": "4bc8c5", "flight": "PGT980R ", "lat": 40.6799, "lon": 30.2471, "alt_baro": 21000,
         "alt_geom": 21654, "gs": 362.4, "track": 109.2, "t": "A20N", "r": "TC-NBA"}
GROUNDED = {"hex": "abc123", "flight": "", "lat": 41.0, "lon": 29.0, "alt_baro": "ground"}


@override_settings(CACHES=LOCMEM)
class FlightTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_parse_skips_planes_on_the_ground(self):
        aircraft = flights._parse([STATE, GROUNDED, STATE])
        self.assertEqual(len(aircraft), 1)  # grounded skipped, duplicate merged
        plane = aircraft[0]
        self.assertEqual(plane["callsign"], "PGT980R")
        self.assertEqual(plane["altitude_ft"], 21654)
        self.assertEqual(plane["speed_kt"], 362)
        self.assertEqual(plane["type"], "A20N")

    @mock.patch("core.services.flights._fetch")
    def test_falls_back_to_last_good_result(self, fetch):
        fetch.return_value = flights._parse([STATE])
        first = self.client.get("/radars/flights.json").json()
        self.assertFalse(first["stale"])
        self.assertEqual(len(first["aircraft"]), 1)

        # Make the cached result old, then let adsb.lol fail.
        cached = cache.get(flights.CACHE_KEY)
        cache.set(flights.CACHE_KEY, {**cached, "updated": cached["updated"] - 3600})
        fetch.side_effect = RuntimeError("429")
        second = self.client.get("/radars/flights.json").json()
        self.assertTrue(second["stale"])
        self.assertEqual(len(second["aircraft"]), 1)

    @mock.patch("core.services.flights._fetch", side_effect=RuntimeError("down"))
    def test_no_data_at_all(self, fetch):
        data = self.client.get("/radars/flights.json").json()
        self.assertEqual(data, {"aircraft": [], "updated": None, "stale": True})


@override_settings(CACHES=LOCMEM, SESSION_ENGINE="django.contrib.sessions.backends.cache")
class TranslationTests(TestCase):
    def setUp(self):
        cache.clear()
        patcher = mock.patch("core.services.news.fetch_articles", return_value=SAMPLE_ARTICLES)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_every_message_is_translated(self):
        # Fails when visible text was added without translations.
        call_command("update_translations", "--check", stdout=StringIO())

    def test_browser_language_is_used(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="tr")
        self.assertContains(response, '<html lang="tr"')
        self.assertContains(response, "Duyurular")  # Announcements

    def test_switching_language(self):
        response = self.client.post("/i18n/setlang/", {"language": "fr", "next": "/news/"})
        self.assertRedirects(response, "/news/", fetch_redirect_response=False)
        response = self.client.get("/news/")
        self.assertContains(response, "Actualités")
        self.assertContains(response, "2 articles")
        self.assertContains(response, "Traduire")  # translate buttons appear outside English

    def test_every_page_loads_in_every_language(self):
        for language in ["en", "tr", "fr", "es"]:
            for url in ["/", "/news/", "/chatbot/", "/quiz/", "/history/", "/feedback/", "/radars/"]:
                with self.subTest(language=language, url=url):
                    response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=language)
                    self.assertEqual(response.status_code, 200)

    def test_english_has_no_translate_button(self):
        self.assertNotContains(self.client.get("/news/", HTTP_ACCEPT_LANGUAGE="en"), "Translate")

    @mock.patch("core.services.ai._complete", return_value="Cevap.")
    def test_ai_answers_in_the_visitor_language(self, complete):
        self.client.post("/chatbot/ask/", {"question": "Merhaba"}, HTTP_ACCEPT_LANGUAGE="tr")
        self.assertIn("in Turkish", complete.call_args[0][0])

    @mock.patch("core.services.ai._complete", return_value=json.dumps({"title": "A350 dönüm noktası", "summary": "Airbus 700. A350'yi teslim etti."}))
    def test_article_translation_is_cached(self, complete):
        response = self.client.post("/news/a350/translate/", HTTP_ACCEPT_LANGUAGE="tr")
        self.assertContains(response, "A350 dönüm noktası")
        self.assertContains(response, "orijinali göster")
        self.client.post("/news/a350/translate/", HTTP_ACCEPT_LANGUAGE="tr")
        complete.assert_called_once()

    @mock.patch("core.services.ai._complete", side_effect=RuntimeError("down"))
    def test_article_translation_failure_keeps_original(self, complete):
        response = self.client.post("/news/a350/translate/", HTTP_ACCEPT_LANGUAGE="es")
        self.assertContains(response, "A350 milestone")
        self.assertContains(response, "La traducción no está disponible")

    def test_unknown_article_or_english_returns_404(self):
        self.assertEqual(self.client.post("/news/nope/translate/", HTTP_ACCEPT_LANGUAGE="tr").status_code, 404)
        self.assertEqual(self.client.post("/news/a350/translate/", HTTP_ACCEPT_LANGUAGE="en").status_code, 404)
