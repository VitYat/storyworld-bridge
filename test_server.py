import json
import base64
import threading
import tempfile
import re
import sys
import types
import wave
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError
import unittest
from unittest.mock import patch

import server
import piper_voice
import model_preflight


def example_story():
    return {
        "language": "Russian",
        "title": "Тайна сада",
        "subtitle": "Спокойное приключение",
        "profession": "Садовник",
        "pages": [
            {"heading": f"Страница {n}", "body": "Герои ищут дорожку в саду.",
             "reflectionPrompt": "Что ты заметил?", "imagePrompt": "Garden scene"}
            for n in range(3)
        ],
    }


class ServerTests(unittest.TestCase):
    def test_preflight_requires_a_real_page_and_not_just_a_model_listing(self):
        with patch.object(model_preflight, "request", return_value={"output": [
            {"type": "message", "content": json.dumps({
                "heading": "Hello", "body": "Two words.", "imagePrompt": "An illustrated bird"})}
        ]}):
            self.assertFalse(model_preflight.probe("http://127.0.0.1:1234", "model"))

    def test_preflight_switches_bad_experimental_instance_to_downloaded_instruct(self):
        catalog = {"models": [
            {"type": "llm", "key": "bad/defiant-uncensored-9b", "display_name": "Defiant Uncensored",
             "loaded_instances": [{"id": "defiant"}], "size_bytes": 10_000_000_000},
            {"type": "llm", "key": "lmstudio-community/qwen3.5-9b", "display_name": "Qwen3.5 9B",
             "loaded_instances": [], "size_bytes": 10_000_000_000},
        ]}
        calls = []
        def answer(_base, path, payload=None, timeout=15):
            calls.append((path, payload))
            if path == "/api/v1/models":
                return catalog
            if path == "/api/v1/models/load":
                return {"instance_id": "standard-qwen"}
            return {}
        with patch.object(model_preflight, "request", side_effect=answer), \
             patch.object(model_preflight, "probe", return_value=True) as probe:
            result = model_preflight.select_model("http://127.0.0.1:1234", "defiant")
        self.assertEqual(result, {"model": "standard-qwen", "switched": True})
        self.assertEqual(probe.call_args.args[1], "standard-qwen")
        self.assertIn(("/api/v1/models/unload", {"instance_id": "defiant"}), calls)
        self.assertIn(("/api/v1/models/load", {"model": "lmstudio-community/qwen3.5-9b",
                                                "context_length": 4096, "flash_attention": True}), calls)

    def test_preflight_unloads_failed_candidate_before_next_model(self):
        catalog = {"models": [
            {"type": "llm", "key": "defiant-uncensored", "loaded_instances": [{"id": "bad"}]},
            {"type": "llm", "key": "qwen3.5-9b", "loaded_instances": [], "size_bytes": 10_000_000_000},
            {"type": "llm", "key": "qwen-7b-instruct", "loaded_instances": [], "size_bytes": 6_000_000_000},
        ]}
        calls = []
        def answer(_base, path, payload=None, timeout=15):
            calls.append((path, payload))
            if path == "/api/v1/models":
                return catalog
            if path == "/api/v1/models/load":
                return {"instance_id": payload["model"]}
            return {}
        with patch.object(model_preflight, "request", side_effect=answer), \
             patch.object(model_preflight, "probe", side_effect=[False, True]):
            result = model_preflight.select_model("http://127.0.0.1:1234", "bad")
        self.assertEqual(result["model"], "qwen-7b-instruct")
        self.assertIn(("/api/v1/models/unload", {"instance_id": "qwen3.5-9b"}), calls)

    def test_preflight_rejects_remote_server_and_no_ordinary_model(self):
        with self.assertRaisesRegex(ValueError, "local HTTP"):
            model_preflight.select_model("https://example.com", "bad")
        catalog = {"models": [{"type": "llm", "key": "bad/defiant-uncensored-9b",
                               "display_name": "Defiant", "loaded_instances": [{"id": "bad"}]}]}
        with patch.object(model_preflight, "request", return_value=catalog):
            with self.assertRaisesRegex(RuntimeError, "no ordinary instruct model"):
                model_preflight.select_model("http://127.0.0.1:1234", "bad")

    def test_compact_story_against_local_http_provider(self):
        seen = []

        class LocalProvider(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                assert self.path == "/v1/models"
                data = b'{"data":[{"id":"loaded-model"}]}'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                seen.append(self.path)
                if self.path == "/free":
                    self.send_response(200)
                    self.end_headers()
                    return
                number = json.loads(body["input"])["page"]
                page = {"heading": f"Page {number}", "body": "A gentle bird found a peaceful garden.",
                        "imagePrompt": "An illustrated garden"}
                data = json.dumps({"output": [{"type": "message", "content": json.dumps(page)}]}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)

        httpd = ThreadingHTTPServer(("127.0.0.1", 0), LocalProvider)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            root = f"http://127.0.0.1:{httpd.server_port}"
            with patch.object(server, "LM_URL", root + "/v1"), \
                 patch.object(server, "COMFY_URL", root), patch.object(server, "MODEL_ID", ""):
                story = server.generate_story({"language": "English", "length": "3–5 minutes",
                                               "profile": {"avoidTopics": []}})
            self.assertEqual([page["heading"] for page in story["pages"]],
                             ["Page 1", "Page 2", "Page 3"])
            self.assertEqual(seen, ["/free", "/api/v1/chat", "/api/v1/chat", "/api/v1/chat"])
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=3)

    @patch.object(server, "release_image_memory")
    @patch.object(server, "models", return_value=["qwen3.5-9b-local"])
    @patch.object(server, "request_json")
    def test_qwen35_short_pages_free_image_memory_and_finish(self, request, _models, freed):
        def answer(url, payload, **kwargs):
            self.assertTrue(url.endswith("/api/v1/chat"))
            self.assertEqual(payload["reasoning"], "off")
            self.assertLessEqual(payload["max_output_tokens"], 950)
            self.assertEqual(kwargs["timeout"], 120)
            page_number = json.loads(payload["input"])["page"]
            content = json.dumps({"heading": f"Part {page_number}",
                                  "body": f"Scene number {page_number}, a kind child meets a friendly bird.",
                                  "imagePrompt": "Cartoon bird in a bright garden"})
            return {"output": [{"type": "message", "content": content}]}
        request.side_effect = answer
        with patch.object(server, "MODEL_ID", ""):
            result = server.generate_story({"language": "English", "length": "5–7 minutes",
                                            "profile": {"avoidTopics": []}})
        self.assertEqual(len(result["pages"]), 6)
        self.assertEqual(request.call_count, 6)
        self.assertEqual(result["pages"][-1]["heading"], "Part 6")
        freed.assert_called_once()

    @patch.object(server, "release_image_memory")
    @patch.object(server, "models", return_value=["qwen3.5-9b-local"])
    @patch.object(server, "request_json", side_effect=server.ProviderTimeoutError("timed out"))
    def test_qwen35_short_page_timeout_is_explicit(self, _request, _models, freed):
        with patch.object(server, "MODEL_ID", ""):
            with self.assertRaisesRegex(server.StoryError, "short page in two minutes"):
                server.generate_story({"language": "English", "length": "3–5 minutes",
                                       "profile": {"avoidTopics": []}})
        freed.assert_called_once()

    @patch.object(server, "urlopen")
    def test_image_memory_release_posts_unload_request(self, opener):
        response = opener.return_value.__enter__.return_value
        response.read.return_value = b""
        server.release_image_memory()
        self.assertEqual(opener.call_args.args[0].full_url, server.COMFY_URL + "/free")
        self.assertIn(b'"unload_models":true', opener.call_args.args[0].data)

    def test_piper_voice_returns_wav_for_ukrainian_text(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory, "uk_UA-ukrainian_tts-medium.onnx")
            model.write_bytes(b"model placeholder")
            model.with_suffix(".onnx.json").write_text("{}")

            class FakeVoice:
                @staticmethod
                def load(_path):
                    return FakeVoice()

                def synthesize_wav(self, content, output):
                    self.assert_text = content
                    output.setnchannels(1)
                    output.setsampwidth(2)
                    output.setframerate(22050)
                    output.writeframes(b"\0" * 128)

            with patch.dict(sys.modules, {"piper": types.SimpleNamespace(PiperVoice=FakeVoice)}):
                encoded = piper_voice.synthesize({"locale": "uk-UA", "text": "Привіт"}, Path(directory))
            with wave.open(__import__("io").BytesIO(base64.b64decode(encoded))) as result:
                self.assertEqual(result.getframerate(), 22050)
    @patch.object(server, "urlopen", side_effect=URLError(TimeoutError("timed out")))
    def test_provider_timeout_is_not_reported_as_unavailable(self, _request):
        with self.assertRaises(server.ProviderTimeoutError):
            server.request_json("http://127.0.0.1:1234/v1/chat/completions", {}, timeout=90)

    @patch.object(server, "installed_voice_catalog", return_value=[{"id": "piper-uk", "locale": "uk-UA"}])
    @patch.object(server.subprocess, "run")
    def test_local_ukrainian_page_uses_piper_without_browser_voice(self, run, _voices):
        run.return_value.returncode = 0
        run.return_value.stdout = base64.b64encode(b"RIFF" + b"\0" * 60).decode()
        with patch.object(server, "VOICE_PYTHON", "C:/Storyworld/voice/python.exe"), \
             patch.object(server, "VOICE_DIR", Path("C:/Storyworld/voice/models")):
            result = server.synthesize_page({"locale": "uk-UA", "text": "Привіт, світе!"})
        self.assertEqual(result["mimeType"], "audio/wav")
        self.assertIn("Привіт", run.call_args.kwargs["input"])
        self.assertEqual(run.call_args.kwargs["timeout"], 120)

    @patch.object(server, "installed_voices", return_value=[])
    def test_missing_ukrainian_voice_is_not_silently_replaced(self, _voices):
        with self.assertRaisesRegex(server.StoryError, "No local narration voice"):
            server.synthesize_page({"locale": "uk-UA", "text": "Привіт"})

    def test_comfy_queue_history_and_image_download(self):
        png = b"\x89PNG\r\n\x1a\nmock"

        class FakeComfy(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                assert body["prompt"]["7"]["class_type"] == "SaveImage"
                data = json.dumps({"prompt_id": "one"}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if self.path.startswith("/history/"):
                    data = json.dumps({"one": {"outputs": {"7": {"images": [{"filename": "safe.png"}]}}}}).encode()
                else:
                    self.assert_path()
                    data = png
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)

            def assert_path(self):
                assert self.path.startswith("/view?filename=safe.png")

        httpd = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(server, "COMFY_URL", f"http://127.0.0.1:{httpd.server_port}"):
                self.assertEqual(server.comfy_image("garden", "model.safetensors"), png)
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=3)

    def test_temporary_child_photo_is_removed_after_comfy_job(self):
        with tempfile.TemporaryDirectory() as directory:
            class FakeComfy(BaseHTTPRequestHandler):
                def log_message(self, *_):
                    pass

                def do_POST(self):
                    body = self.rfile.read(int(self.headers["Content-Length"]))
                    if self.path == "/upload/image":
                        name = re.search(rb'filename="([^"]+)"', body).group(1).decode()
                        Path(directory, name).write_bytes(body)
                        data = json.dumps({"name": name, "subfolder": ""}).encode()
                    else:
                        assert json.loads(body)["prompt"]["8"]["class_type"] == "LoadImage"
                        data = b'{"prompt_id":"one"}'
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)

                def do_GET(self):
                    data = (b'{"one":{"outputs":{"7":{"images":[{"filename":"image.png"}]}}}}'
                            if self.path.startswith("/history/") else b"\x89PNG\r\n\x1a\nmock")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)

            httpd = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(server, "COMFY_URL", f"http://127.0.0.1:{httpd.server_port}"), \
                     patch.object(server, "COMFY_INPUT_DIR", directory), patch.object(server, "reference_ready", return_value=True):
                    server.comfy_image("garden", "checkpoint.safetensors", photo=b"\xff\xd8\xffJPEG")
                    self.assertEqual(list(Path(directory).iterdir()), [])
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=3)

    def test_valid_story_has_distinct_id(self):
        result = server.validate_story(example_story(), [], "Russian")
        self.assertTrue(result["id"])

    def test_excluded_topic_in_another_language_is_blocked(self):
        story = example_story()
        story["pages"][0]["body"] = "В саду появился паук."
        with self.assertRaisesRegex(server.StoryError, "excluded topic"):
            server.validate_story(story, ["Spiders"], "Russian")

    def test_wrong_language_marker_fails(self):
        with self.assertRaisesRegex(server.StoryError, "requested story language"):
            server.validate_story(example_story(), [], "Spanish")

    @patch.object(server, "MODEL_ID", "storyworld-qwen35-9b-q8")
    @patch.object(server, "models", return_value=["another-model", "storyworld-qwen35-9b-q8"])
    def test_explicit_model_selection_ignores_list_order(self, _models):
        self.assertEqual(server.selected_model(), "storyworld-qwen35-9b-q8")

    @patch.object(server, "MODEL_ID", "storyworld-qwen35-9b-q8")
    @patch.object(server, "models", return_value=["another-model"])
    def test_missing_selected_model_does_not_fall_back(self, _models):
        with self.assertRaisesRegex(server.StoryError, "unavailable"):
            server.selected_model()

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json")
    def test_text_generation_calls_local_chat(self, mocked, _models):
        mocked.return_value = {"output": [{"type": "message", "content": json.dumps({
            "heading": "Тайна сада", "body": "Герои ищут дорожку в саду.",
            "imagePrompt": "Cartoon garden"})}]}
        output = server.generate_story({"language": "Russian", "profile": {"ageBand": "4–6", "avoidTopics": []}})
        self.assertEqual(output["title"], "Тайна сада")
        self.assertIn("/api/v1/chat", mocked.call_args.args[0])

    @patch.object(server, "models", return_value=["test-model"])
    def test_support_cannot_override_avoid(self, _models):
        with self.assertRaisesRegex(server.StoryError, "cannot override"):
            server.generate_story({"supportTopic": "Darkness", "profile": {"avoidTopics": ["Darkness"]}})

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json")
    def test_custom_representation_passes_to_local_model(self, mocked, _models):
        mocked.return_value = {"output": [{"type": "message", "content": json.dumps({
            "heading": "Тайна сада", "body": "Герои ищут дорожку в саду.",
            "imagePrompt": "Cartoon garden"})}]}
        server.generate_story({"language": "Russian", "profile": {
            "customRepresentation": "a character with a unique prosthetic hand", "avoidTopics": []}})
        spec = json.loads(mocked.call_args.args[1]["input"])
        self.assertEqual(spec["customRepresentation"], "a character with a unique prosthetic hand")

    @patch.object(server, "request_json")
    def test_image_generation_calls_local_image_server(self, mocked):
        mocked.return_value = {"images": [base64.b64encode(b"PNG").decode()]}
        image = server.generate_image({"prompt": "garden"})
        self.assertEqual(image["imageBase64"], "UE5H")
        self.assertIn("/sdapi/v1/txt2img", mocked.call_args.args[0])

    @patch.object(server, "comfy_checkpoint", return_value="v1-5-pruned-emaonly.safetensors")
    @patch.object(server, "comfy_image", return_value=b"\x89PNG\r\n\x1a\nexample")
    def test_comfy_image_is_returned_as_png(self, image, _checkpoint):
        result = server.generate_image({"prompt": "gentle garden"})
        self.assertEqual(base64.b64decode(result["imageBase64"]), b"\x89PNG\r\n\x1a\nexample")
        image.assert_called_once_with("gentle garden", "v1-5-pruned-emaonly.safetensors", "Watercolor", None, False)

    def test_photo_reference_changes_latent_and_style(self):
        workflow = server.comfy_workflow("night garden", "checkpoint.safetensors", "Paper collage", "reference.jpg")
        self.assertEqual(workflow["5"]["inputs"]["latent_image"], ["4", 0])
        self.assertEqual(workflow["5"]["inputs"]["model"], ["12", 0])
        self.assertEqual(workflow["12"]["class_type"], "IPAdapterAdvanced")
        self.assertEqual(workflow["8"]["inputs"]["image"], "reference.jpg")
        self.assertIn("layered coloured paper", workflow["2"]["inputs"]["text"])
        self.assertGreaterEqual(workflow["5"]["inputs"]["denoise"], 0.85)
        self.assertIn("illustrated rather than an altered photograph", workflow["2"]["inputs"]["text"])

    def test_ten_image_styles_have_distinct_workflow_prompts(self):
        self.assertEqual(len(server.IMAGE_STYLES), 10)
        prompts = [server.comfy_workflow("garden", "checkpoint.safetensors", style)["2"]["inputs"]["text"]
                   for style in server.IMAGE_STYLES]
        self.assertEqual(len(set(prompts)), 10)
        self.assertIn("Japanese anime", prompts[list(server.IMAGE_STYLES).index("Anime")])
        self.assertNotIn("Pixar", prompts[list(server.IMAGE_STYLES).index("Pixar")])

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json")
    def test_every_duration_requests_short_continuing_pages(self, mocked, _models):
        def answer(url, payload, **kwargs):
            self.assertTrue(url.endswith("/api/v1/chat"))
            self.assertEqual(payload["reasoning"], "off")
            self.assertEqual(kwargs["timeout"], 120)
            spec = json.loads(payload["input"])
            number = spec["page"]
            if number > 1:
                self.assertIn(str(number - 1), spec["previousScene"])
            page = {"heading": f"Страница {number}",
                    "body": f"Герои проходят дорожку номер {number}.",
                    "imagePrompt": "An original illustrated garden scene"}
            return {"output": [{"type": "message", "content": json.dumps(page)}]}
        mocked.side_effect = answer
        for length, chapters in server.LENGTH_CHAPTERS.items():
            with self.subTest(length=length):
                mocked.reset_mock()
                story = server.generate_story({"language": "Russian", "length": length,
                                               "profile": {"avoidTopics": []}})
                self.assertEqual(len(story["pages"]), chapters * 3)
                self.assertEqual(mocked.call_count, chapters * 3)

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json")
    def test_native_unsupported_falls_back_to_short_compatible_pages(self, mocked, _models):
        def answer(url, payload, **kwargs):
            if url.endswith("/api/v1/chat"):
                raise server.StoryError("Provider unavailable: HTTP Error 400")
            self.assertTrue(url.endswith("/chat/completions"))
            self.assertEqual(payload["max_tokens"], 950)
            self.assertEqual(kwargs["timeout"], 120)
            spec = json.loads(payload["messages"][1]["content"])
            page = {"heading": f"Страница {spec['page']}", "body": "Тихий сад расцвёл.",
                    "imagePrompt": "Cartoon garden"}
            return {"choices": [{"message": {"content": json.dumps(page)}}]}
        mocked.side_effect = answer
        story = server.generate_story({"language": "Russian", "length": "3–5 minutes",
                                       "profile": {"avoidTopics": []}})
        self.assertEqual(len(story["pages"]), 3)
        self.assertEqual(mocked.call_count, 6)

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json", side_effect=server.ProviderTimeoutError("timed out"))
    def test_any_loaded_model_reports_short_page_timeout(self, _request, _models):
        with self.assertRaisesRegex(server.StoryError, "short page in two minutes"):
            server.generate_story({"language": "Russian", "length": "3–5 minutes",
                                   "profile": {"avoidTopics": []}})

    @patch.object(server, "models", return_value=["test-model"])
    @patch.object(server, "request_json")
    def test_incomplete_short_page_is_not_accepted(self, mocked, _models):
        mocked.return_value = {"output": [{"type": "message", "content": '{"body":"abc"}'}]}
        with self.assertRaisesRegex(server.StoryError, "incomplete page 1"):
            server.generate_story({"language": "Russian", "length": "3–5 minutes",
                                   "profile": {"avoidTopics": []}})

    @patch.object(server, "generate_story")
    def test_http_story_endpoint_returns_live_provider_result(self, generated):
        generated.return_value = server.validate_story(example_story(), [], "Russian")
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{httpd.server_port}/stories",
                data=json.dumps({"profile": {"avoidTopics": []}}).encode(),
                headers={"Content-Type": "application/json", "Origin": "http://localhost:50000"},
            )
            with urlopen(request, timeout=3) as result:
                self.assertEqual(json.load(result)["title"], "Тайна сада")
                self.assertEqual(result.headers["Access-Control-Allow-Origin"], "http://localhost:50000")
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
