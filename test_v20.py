import base64
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import wave
import server
import series_memory
import voice_worker
from narration_catalog import select

class V20Tests(unittest.TestCase):
    def tearDown(self):
        server.BOOK_CACHE.clear()

    def test_hundred_episode_recall_keeps_origin_recent_and_relevant(self):
        archive = [{'number': n, 'title': 'Moon station' if n == 42 else f'Adventure {n}',
                    'summary': 'A lasting event', 'facts': ['old friend'], 'nextThread': ''} for n in range(1, 101)]
        result = series_memory.recall({'episodes': archive, 'bible': 'Our original world'}, 'Moon station')
        numbers = [e['number'] for e in result['recalledEpisodes']]
        self.assertEqual(result['episodeNumber'], 101)
        self.assertIn(1, numbers)
        self.assertIn(100, numbers)
        self.assertIn(99, numbers)
        self.assertIn(42, numbers)
        self.assertLessEqual(len(numbers), 5)
        self.assertEqual(len(archive), 100)

    def test_voice_cannot_silently_change_language(self):
        with self.assertRaises(ValueError):
            select('uk-UA', 'kokoro-af_heart')

    def test_missing_face_adapter_does_not_fake_reference_support(self):
        with patch.object(server, 'reference_ready', return_value=False):
            with self.assertRaisesRegex(server.StoryError, 'reference adapter'):
                server.comfy_image('garden', 'model', photo=b'photo')

    def test_portrait_uses_stronger_reference_and_empty_latent(self):
        scene = server.comfy_workflow('garden', 'model', 'Pixar', 'child.jpg')
        portrait = server.comfy_workflow('garden', 'model', 'Disney', 'child.jpg', True)
        self.assertGreater(portrait['12']['inputs']['weight'], scene['12']['inputs']['weight'])
        self.assertEqual(portrait['5']['inputs']['latent_image'], ['4', 0])
        self.assertIn('waist-up portrait', portrait['2']['inputs']['text'])

    def test_complete_audio_offsets_include_inter_page_pause(self):
        sound = io.BytesIO()
        with wave.open(sound, 'wb') as output:
            output.setnchannels(1); output.setsampwidth(2); output.setframerate(100)
            output.writeframes(b'\0' * 200)
        with patch.object(voice_worker, 'synthesize', return_value=base64.b64encode(sound.getvalue()).decode()):
            result = voice_worker.synthesize_book({'locale': 'en-US', 'pages': ['one', 'two']}, Path('.'))
        self.assertEqual(result['pageOffsets'], [0.0, 1.6])
        self.assertAlmostEqual(result['durationSeconds'], 3.2)
        with wave.open(io.BytesIO(base64.b64decode(result['audioBase64']))) as audio:
            self.assertEqual(audio.getnframes(), 320)

    def test_long_page_is_narrated_in_order_without_losing_words(self):
        sound = io.BytesIO()
        with wave.open(sound, 'wb') as output:
            output.setnchannels(1); output.setsampwidth(2); output.setframerate(100)
            output.writeframes(b'\0' * 200)
        spoken = []
        def fake_synthesize(data, root):
            spoken.append(data['text'])
            return base64.b64encode(sound.getvalue()).decode()
        original = ' '.join(f'word{n}' for n in range(450))
        with patch.object(voice_worker, 'synthesize', side_effect=fake_synthesize):
            book = voice_worker.synthesize_book({'locale': 'en-US', 'pages': [original, 'ending']}, Path('.'))
        self.assertEqual(' '.join(spoken[:-1]), original)
        self.assertEqual(spoken[-1], 'ending')
        self.assertTrue(all(len(part) <= 1200 for part in spoken))
        self.assertEqual(len(book['pageOffsets']), 2)
        self.assertGreater(book['pageOffsets'][1], 1)

    def test_complete_audio_cache_and_utf8_worker(self):
        wav = base64.b64encode(b'RIFF' + b'\0' * 60).decode()
        with patch.object(server, 'installed_voice_catalog', return_value=[{'id': 'piper-uk', 'locale': 'uk-UA'}]), \
             patch.object(server.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({'audioBase64': wav, 'pageOffsets': [0], 'durationSeconds': 2})
            payload = {'locale': 'uk-UA', 'pages': ['Місяць усміхнувся.'], 'voiceId': 'piper-uk'}
            first = server.synthesize_book(payload)
            self.assertEqual(server.synthesize_book(payload), first)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
            self.assertIn('Місяць', run.call_args.kwargs['input'])

    def test_invalid_audio_releases_worker_lock(self):
        with patch.object(server, 'installed_voice_catalog', return_value=[{'id': 'kokoro-af_heart', 'locale': 'en-US'}]), \
             patch.object(server.subprocess, 'run') as run:
            run.return_value.returncode = 0; run.return_value.stdout = '{}'
            with self.assertRaises(server.StoryError):
                server.synthesize_book({'locale': 'en-US', 'pages': ['Moon.']})
            self.assertTrue(server.VOICE_LOCK.acquire(blocking=False))
            server.VOICE_LOCK.release()

if __name__ == '__main__':
    unittest.main()
