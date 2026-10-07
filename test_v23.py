import base64
import io
import json
import tempfile
import threading
import unittest
import wave
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import content_packs
import narration_catalog
import server
import voice_worker


def page_reply(payload):
    spec = json.loads(payload["input"])
    return {"output": [{"type": "message", "content": json.dumps({
        "heading": f"Page {spec['page']}", "body": "A calm bird crossed the quiet garden today.",
        "imagePrompt": "A garden path"})}]}


def wav_bytes(seconds=10.0, rate=16000):
    sound = io.BytesIO()
    with wave.open(sound, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(b"\0\0" * int(seconds * rate))
    return sound.getvalue()


class V23StoryTests(unittest.TestCase):
    def generate(self, data, seen=None):
        def answer(url, payload, **kwargs):
            if seen is not None:
                seen.append(json.loads(payload["input"]))
            return page_reply(payload)
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", side_effect=answer), \
             patch.object(server, "release_image_memory"):
            return server.generate_story({"language": "English", "length": "5–7 minutes",
                                          "profile": {"name": "Emma", "avoidTopics": []}, **data})

    def test_sixteen_languages_each_have_a_reflection_and_locale(self):
        self.assertEqual(len(content_packs.LANGUAGES), 16)
        for name, info in content_packs.LANGUAGES.items():
            self.assertIn(name, content_packs.REFLECTIONS)
            self.assertRegex(info["locale"], r"^[a-z]{2}-[A-Z]{2}$")
        for name in ("Russian", "German", "French", "Japanese", "Arabic", "Hebrew"):
            self.assertIn(name, content_packs.LANGUAGES)

    def test_every_voiced_locale_belongs_to_a_story_language(self):
        locales = {info["locale"] for info in content_packs.LANGUAGES.values()}
        for preset in narration_catalog.VOICE_PRESETS:
            self.assertIn(preset["locale"], locales)
        voiced = {preset["locale"] for preset in narration_catalog.VOICE_PRESETS}
        self.assertEqual(locales - voiced, set(narration_catalog.LOCALES_WITHOUT_VOICE))

    def test_day_event_and_siblings_reach_every_page(self):
        seen = []
        story = self.generate({"dayEvent": "Emma lost her first tooth",
                               "coHeroes": [{"name": "Leo", "age": 7, "appearance": "short black hair"}]}, seen)
        self.assertTrue(all(spec["dayEvent"] == "Emma lost her first tooth" for spec in seen))
        self.assertEqual(seen[0]["coHeroes"][0]["name"], "Leo")
        self.assertTrue(story["usedDayEvent"])

    def test_day_event_cannot_smuggle_an_excluded_topic(self):
        with patch.object(server, "models", return_value=["m"]):
            with self.assertRaisesRegex(server.StoryError, "excluded topic"):
                server.generate_story({"dayEvent": "We saw a big spider", "language": "English",
                                       "profile": {"avoidTopics": ["Spiders"]}})

    def test_reading_stage_is_independent_from_age(self):
        young, older = [], []
        self.generate({"readingStage": 7, "hero": {"birthDate": "2021-01-01"}}, young)
        self.generate({"readingStage": 2, "hero": {"birthDate": "2016-01-01"}}, older)
        self.assertEqual(young[0]["readingStage"], "Independent reader")
        self.assertEqual(older[0]["readingStage"], "Sound explorer")
        self.assertNotEqual(young[0]["readingRule"], older[0]["readingRule"])

    def test_legacy_reading_level_maps_to_a_stage(self):
        self.assertEqual(content_packs.reading_stage(None, "Beginning reader"), 4)
        self.assertEqual(content_packs.reading_stage(11, "Read together"), 2)
        self.assertEqual(content_packs.reading_stage(True, ""), 3)

    def test_first_and_key_scenes_show_the_child_others_follow_the_page(self):
        story = self.generate({})
        flags = [page["heroScene"] for page in story["pages"]]
        self.assertEqual(flags, [True, False, False, True, False, True])
        self.assertEqual(content_packs.hero_scene_plan(3), [True, False, True])

    def test_series_keeps_the_same_companion(self):
        memory = {"id": "s", "episodes": [], "companion": {"key": "owl"}}
        with patch.object(server, "episode_recap", return_value={"seriesId": "s", "episodeNumber": 1}):
            story = self.generate({"seriesMemory": memory})
        self.assertEqual(story["companion"]["key"], "owl")
        self.assertEqual(story["seriesMeta"]["companion"]["name"], "Luma")
        self.assertIn("grey owl", story["companion"]["visual"])

    def test_review_words_and_character_sheet_are_passed(self):
        seen = []
        self.generate({"reviewWords": ["lantern", "meadow", 5], "characterSheet": "curly red hair, round glasses"}, seen)
        self.assertEqual(seen[0]["reviewWords"], ["lantern", "meadow"])
        self.assertIn("round glasses", seen[0]["hero"]["appearance"])

    def test_science_money_groa_support_profession_packs(self):
        seen = []
        self.generate({"contentPack": "science", "theme": "Oceans"}, seen)
        self.assertIn("Whales are mammals", seen[-1]["contentRules"])
        story = self.generate({"contentPack": "money", "theme": "Saving for a goal"}, seen)
        self.assertIn("Saving means keeping", seen[-1]["contentRules"])
        self.assertEqual(story["contentPack"], "money")
        story = self.generate({"contentPack": "groa", "journey": "Little Scientist", "journeyStep": 2}, seen)
        self.assertEqual(story["learningObjective"], "Make a guess about what will happen")
        self.assertEqual(story["domain"], "science")
        story = self.generate({"contentPack": "support", "theme": "Visiting the doctor"}, seen)
        self.assertTrue(story["sensitive"])
        self.assertIn("Do not promise it never hurts", seen[-1]["contentRules"])
        story = self.generate({"contentPack": "profession", "profession": "drone pilot", "theme": "Discovery"}, seen)
        self.assertEqual(story["profession"], "drone pilot")

    def test_money_topic_respects_minimum_age(self):
        with patch.object(server, "models", return_value=["m"]):
            with self.assertRaisesRegex(server.StoryError, "age 12"):
                server.generate_story({"contentPack": "money", "theme": "First steps in investing",
                                       "hero": {"birthDate": f"{__import__('datetime').date.today().year - 7}-01-01"},
                                       "profile": {"avoidTopics": []}})

    def test_support_scenario_cannot_override_exclusion(self):
        with patch.object(server, "models", return_value=["m"]):
            with self.assertRaisesRegex(server.StoryError, "cannot override"):
                server.generate_story({"contentPack": "support", "theme": "Darkness",
                                       "profile": {"avoidTopics": ["Darkness"]}})

    def test_faith_story_returns_references_and_never_a_quotation_rule_gap(self):
        seen = []
        story = self.generate({"contentPack": "faith", "tradition": "Buddhism", "theme": "Kindness and gratitude"}, seen)
        self.assertEqual(story["tradition"], "Buddhism")
        self.assertTrue(any(source["ref"] == "Dhammapada 5" for source in story["sources"]))
        for policy in content_packs.FAITH_POLICIES.values():
            for source in policy["references"]:
                self.assertEqual(set(source), {"ref", "about"})

    def test_vocabulary_keeps_only_words_that_occur_in_the_story(self):
        def answer(url, payload, **kwargs):
            if "Pick up to four words" in payload.get("system_prompt", ""):
                return {"output": [{"type": "message", "content": json.dumps({"words": [
                    {"word": "garden", "meaning": "a place where plants grow"},
                    {"word": "volcano", "meaning": "a mountain with fire"},
                    {"word": "quiet garden", "meaning": "two words"}]})}]}
            return page_reply(payload)
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", side_effect=answer), \
             patch.object(server, "release_image_memory"):
            story = server.generate_story({"language": "English", "length": "3–5 minutes",
                                           "extractVocabulary": True, "profile": {"avoidTopics": []}})
        self.assertEqual(story["vocabulary"], [{"word": "garden", "meaning": "a place where plants grow"}])

    def test_vocabulary_failure_never_discards_the_story(self):
        def answer(url, payload, **kwargs):
            if "Pick up to four words" in payload.get("system_prompt", ""):
                raise server.ProviderTimeoutError("slow")
            return page_reply(payload)
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", side_effect=answer), \
             patch.object(server, "release_image_memory"):
            story = server.generate_story({"language": "English", "length": "3–5 minutes",
                                           "extractVocabulary": True, "profile": {"avoidTopics": []}})
        self.assertEqual(story["vocabulary"], [])
        self.assertEqual(len(story["pages"]), 3)

    def test_word_meaning_uses_the_sentence_and_rejects_phrases(self):
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", return_value={"output": [{"type": "message", "content": json.dumps(
                 {"meaning": "a small light you can carry", "example": "The lantern glowed."})}]}) as mocked:
            result = server.define_word({"word": "lantern", "sentence": "Pip held a lantern.", "language": "English"})
            self.assertEqual(result["meaning"], "a small light you can carry")
            self.assertIn("Pip held a lantern.", mocked.call_args.args[1]["input"])
            with self.assertRaisesRegex(server.StoryError, "single word"):
                server.define_word({"word": "two words"})

    def test_translation_keeps_pages_images_and_blocks_excluded_topics(self):
        story = {"id": "abc", "language": "English", "title": "The garden", "pages": [
            {"heading": f"H{n}", "body": "A bird sang.", "imagePrompt": "bird", "heroScene": n == 0,
             "imageBase64": "aGVsbG8="} for n in range(3)]}

        def answer(url, payload, **kwargs):
            if "title" in payload["system_prompt"]:
                return {"output": [{"type": "message", "content": '{"title":"Сад"}'}]}
            return {"output": [{"type": "message", "content": json.dumps(
                {"heading": "Глава", "body": "Птица пела."}, ensure_ascii=False)}]}
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", side_effect=answer), patch.object(server, "release_image_memory"):
            result = server.translate_story({"story": story, "to": "Russian"})
            self.assertEqual(result["language"], "Russian")
            self.assertEqual(result["title"], "Сад")
            self.assertEqual(result["translationOf"], "abc")
            self.assertEqual([p["imageBase64"] for p in result["pages"]], ["aGVsbG8="] * 3)
            self.assertEqual(result["pages"][0]["heroScene"], True)
            self.assertNotEqual(result["id"], "abc")
            with self.assertRaisesRegex(server.StoryError, "Unknown target language"):
                server.translate_story({"story": story, "to": "Klingon"})

        def spider(url, payload, **kwargs):
            return {"output": [{"type": "message", "content": json.dumps(
                {"heading": "Глава", "body": "Пришёл паук."}, ensure_ascii=False)}]}
        with patch.object(server, "models", return_value=["m"]), \
             patch.object(server, "request_json", side_effect=spider), patch.object(server, "release_image_memory"):
            with self.assertRaisesRegex(server.StoryError, "excluded topic"):
                server.translate_story({"story": story, "to": "Russian", "avoidTopics": ["Spiders"]})


class V23ImageTests(unittest.TestCase):
    def test_character_sheet_only_enters_scenes_that_show_the_child(self):
        sheet = "curly red hair, round glasses, hearing aid"
        hero = server.comfy_workflow("forest", "c.safetensors", "Watercolor", None, False,
                                     {"heroScene": True, "characterSheet": sheet})["2"]["inputs"]["text"]
        scene = server.comfy_workflow("forest", "c.safetensors", "Watercolor", None, False,
                                      {"characterSheet": sheet})["2"]["inputs"]["text"]
        self.assertIn(sheet, hero)
        self.assertNotIn(sheet, scene)
        self.assertIn("Do not force the child hero", scene)

    def test_recurring_cast_look_and_fixed_seed_are_applied(self):
        workflow = server.comfy_workflow("forest", "c.safetensors", "Watercolor", None, False,
                                         {"castVisuals": "a small orange fox with a green satchel", "seed": 1234})
        self.assertIn("orange fox", workflow["2"]["inputs"]["text"])
        self.assertEqual(workflow["5"]["inputs"]["seed"], 1234)

    def test_drawing_becomes_the_starting_image(self):
        workflow = server.comfy_workflow("a purple dragon with three eyes", "c.safetensors", "Watercolor",
                                         "drawing.jpg", False, {"drawing": True})
        self.assertEqual(workflow["10"]["class_type"], "VAEEncode")
        self.assertEqual(workflow["5"]["inputs"]["latent_image"], ["10", 0])
        self.assertLess(workflow["5"]["inputs"]["denoise"], 0.8)
        self.assertNotIn("12", workflow)
        self.assertIn("child's own drawing", workflow["2"]["inputs"]["text"])

    def test_drawing_endpoint_requires_name_description_and_jpeg(self):
        with self.assertRaisesRegex(server.StoryError, "name and a short description"):
            server.character_from_drawing({"drawingBase64": "x"})
        with self.assertRaisesRegex(server.StoryError, "JPEG"):
            server.character_from_drawing({"name": "Zog", "description": "purple dragon",
                                           "drawingBase64": base64.b64encode(b"PNG").decode()})
        jpeg = base64.b64encode(b"\xff\xd8\xffdata").decode()
        with patch.object(server, "comfy_checkpoint", return_value="c"), \
             patch.object(server, "comfy_image", return_value=b"\x89PNG\r\n\x1a\nx") as image:
            result = server.character_from_drawing({"name": "Zog", "description": "purple dragon", "drawingBase64": jpeg})
        self.assertEqual(result["visual"], "purple dragon")
        self.assertEqual(image.call_args.args[5], {"drawing": True})


class V23VoiceTests(unittest.TestCase):
    def test_book_reports_sentence_segments_in_order(self):
        def fake(data, _root):
            return base64.b64encode(wav_bytes(1.0, 8000)).decode()
        with patch.object(voice_worker, "synthesize", side_effect=fake):
            book = voice_worker.synthesize_book(
                {"locale": "en-US", "pages": ["One. Two! Three?", "Four."]}, Path("."))
        self.assertEqual([s["text"] for s in book["segments"]], ["One.", "Two!", "Three?", "Four."])
        self.assertEqual([s["page"] for s in book["segments"]], [0, 0, 0, 1])
        self.assertEqual(book["pageOffsets"][0], 0)
        self.assertAlmostEqual(book["segments"][1]["start"], 1.25, places=2)
        self.assertAlmostEqual(book["pageOffsets"][1], book["segments"][3]["start"], places=3)
        starts = [s["start"] for s in book["segments"]]
        self.assertEqual(starts, sorted(starts))
        self.assertTrue(all(s["end"] > s["start"] for s in book["segments"]))

    def test_family_voice_needs_consent_valid_sample_and_three_at_most(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(server, "FAMILY_VOICE_DIR", Path(directory)), \
             patch.object(server, "clone_engine", return_value=None):
            sample = base64.b64encode(wav_bytes(12)).decode()
            with self.assertRaisesRegex(server.StoryError, "explicit consent"):
                server.register_family_voice({"id": "mom", "name": "Mom", "sampleBase64": sample})
            with self.assertRaisesRegex(server.StoryError, "between 8 and 90"):
                server.register_family_voice({"id": "mom", "name": "Mom", "consent": True,
                                              "sampleBase64": base64.b64encode(wav_bytes(2)).decode()})
            with self.assertRaisesRegex(server.StoryError, "16-bit WAV"):
                server.register_family_voice({"id": "mom", "name": "Mom", "consent": True,
                                              "sampleBase64": base64.b64encode(b"nope").decode()})
            for voice in ("mom", "dad", "gran"):
                listed = server.register_family_voice({"id": voice, "name": voice.title(), "consent": True,
                                                       "consentText": "I agree", "sampleBase64": sample})
            self.assertEqual(len(listed["voices"]), 3)
            self.assertNotIn("consentText", listed["voices"][0])
            with self.assertRaisesRegex(server.StoryError, "up to three"):
                server.register_family_voice({"id": "uncle", "name": "Uncle", "consent": True, "sampleBase64": sample})
            # Re-recording an existing voice is allowed.
            server.register_family_voice({"id": "mom", "name": "Mum", "consent": True, "sampleBase64": sample})
            remaining = server.delete_family_voice({"id": "dad"})
            self.assertEqual([v["id"] for v in remaining["voices"]], ["gran", "mom"])
            self.assertFalse(Path(directory, "dad.wav").exists())
            self.assertFalse(Path(directory, "dad.json").exists())
            with self.assertRaisesRegex(server.StoryError, "Invalid family voice id"):
                server.delete_family_voice({"id": "../etc"})

    def test_deleted_or_uninstalled_family_voice_is_never_substituted(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(server, "FAMILY_VOICE_DIR", Path(directory)):
            with self.assertRaisesRegex(server.StoryError, "deleted or never recorded"):
                server.synthesize_book({"locale": "en-US", "voiceId": "family-mom", "pages": ["Hi"]})
            with patch.object(server, "clone_engine", return_value=None):
                server.register_family_voice({"id": "mom", "name": "Mom", "consent": True,
                                              "sampleBase64": base64.b64encode(wav_bytes(12)).decode()})
            with patch.object(server, "CLONE_PYTHON", ""):
                with self.assertRaisesRegex(server.StoryError, "not installed"):
                    server.synthesize_book({"locale": "en-US", "voiceId": "family-mom", "pages": ["Hi"]})


class V23HttpTests(unittest.TestCase):
    def serve(self):
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (httpd.shutdown(), httpd.server_close(), thread.join(timeout=3)))
        return f"http://127.0.0.1:{httpd.server_port}"

    def test_catalog_and_new_routes_exist(self):
        root = self.serve()
        with urlopen(f"{root}/catalog", timeout=3) as response:
            data = json.load(response)
        self.assertEqual(len(data["languages"]), 16)
        self.assertIn("Oceans", data["science"])
        self.assertEqual(data["money"]["First steps in investing"], 12)
        self.assertIn("Starting school", data["support"])
        for path in ("/stories/translate", "/characters/from-drawing", "/words/define",
                     "/family-voices", "/family-voices/delete"):
            self.assertIn(path, server.POST_ROUTES)
        request = Request(f"{root}/words/define", data=b'{"word":"two words"}',
                          headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as failure:
            urlopen(request, timeout=3)
        self.assertEqual(failure.exception.code, 422)

    def test_pairing_token_protects_every_route_when_set(self):
        root = self.serve()
        with patch.object(server, "TOKEN", "secret"):
            with self.assertRaises(HTTPError) as failure:
                urlopen(f"{root}/catalog", timeout=3)
            self.assertEqual(failure.exception.code, 401)
            with urlopen(Request(f"{root}/catalog", headers={"X-Storyworld-Token": "secret"}), timeout=3) as ok:
                self.assertEqual(ok.status, 200)

    def test_bridge_reports_version_23(self):
        self.assertEqual(server.BRIDGE_VERSION, 23)


class GeneratedFilesTests(unittest.TestCase):
    """The Dart catalog and the UI catalogs must match the Python source of truth."""

    ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]

    def run_script(self, *args):
        import subprocess
        import sys
        return subprocess.run([sys.executable, *args], cwd=self.ROOT, capture_output=True, text=True)

    def test_dart_catalog_matches_content_packs(self):
        done = self.run_script("scripts/gen_catalog.py", "--check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_every_interface_language_is_complete(self):
        done = self.run_script("scripts/check_localization.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
