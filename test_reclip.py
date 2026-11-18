import atexit
import importlib.util
import shutil
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'AnalyseFuture/reference-projects/reclip'
ISOLATED = tempfile.TemporaryDirectory(prefix='reclip-reference-validation-')
TEST_COPY = Path(ISOLATED.name)
shutil.copy2(SOURCE / 'app.py', TEST_COPY / 'app.py')
shutil.copytree(SOURCE / 'templates', TEST_COPY / 'templates')
spec = importlib.util.spec_from_file_location('reclip_under_validation', TEST_COPY / 'app.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
atexit.register(ISOLATED.cleanup)

class ReClipChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='reclip-case-')
        self.addCleanup(self.temp.cleanup)
        module.DOWNLOAD_DIR = self.temp.name
        module.jobs.clear()
        module.app.config['TESTING'] = False
        self.client = module.app.test_client()

    def result(self, stdout='', stderr='', code=0):
        return subprocess.CompletedProcess(['yt-dlp'], code, stdout, stderr)

    def test_index_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ReClip', response.data)

    def test_missing_urls_are_rejected(self):
        for endpoint in ['/api/info', '/api/playlist', '/api/download']:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, json={'url': ''})
                self.assertEqual(response.status_code, 400)

    def test_info_best_bitrate_per_height_and_sorting(self):
        info={'title':'Synthetic','formats':[
            {'format_id':'low720','height':720,'vcodec':'avc','tbr':200},
            {'format_id':'high720','height':720,'vcodec':'avc','tbr':900},
            {'format_id':'1080','height':1080,'vcodec':'vp9','tbr':1200},
            {'format_id':'audio','height':None,'vcodec':'none','tbr':128}]}
        with mock.patch.object(module.subprocess,'run',return_value=self.result(json.dumps(info))) as call:
            response=self.client.post('/api/info',json={'url':'https://example.invalid/owned.mp4'})
        self.assertEqual(response.status_code,200)
        self.assertEqual([f['id'] for f in response.json['formats']],['1080','high720'])
        self.assertEqual(call.call_args.kwargs['timeout'],60)
        self.assertIsInstance(call.call_args.args[0],list)

    def test_info_handles_subprocess_failure(self):
        with mock.patch.object(module.subprocess,'run',return_value=self.result(stderr='detail\nSource unavailable',code=1)):
            response=self.client.post('/api/info',json={'url':'https://example.invalid/file'})
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.json['error'],'Source unavailable')

    def test_info_handles_timeout(self):
        with mock.patch.object(module.subprocess,'run',side_effect=subprocess.TimeoutExpired('yt-dlp',60)):
            response=self.client.post('/api/info',json={'url':'https://example.invalid/file'})
        self.assertEqual(response.status_code,400)
        self.assertIn('Timed out',response.json['error'])

    def test_playlist_filters_missing_urls(self):
        data={'entries':[{'url':'https://example.invalid/one'},{'title':'No URL'},{'url':'https://example.invalid/two'}]}
        with mock.patch.object(module.subprocess,'run',return_value=self.result(json.dumps(data))):
            response=self.client.post('/api/playlist',json={'url':'https://example.invalid/list'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['urls'],['https://example.invalid/one','https://example.invalid/two'])

    def test_download_queues_daemon_thread_without_execution(self):
        with mock.patch.object(module.threading,'Thread') as thread:
            response=self.client.post('/api/download',json={'url':'https://example.invalid/file','title':'Owned fixture'})
        self.assertEqual(response.status_code,200)
        key=response.json['job_id']
        self.assertEqual(module.jobs[key]['status'],'downloading')
        self.assertTrue(thread.return_value.daemon)
        thread.return_value.start.assert_called_once()
        self.assertEqual(thread.call_args.kwargs['target'],module.run_download)

    def test_unknown_job_status_and_file(self):
        self.assertEqual(self.client.get('/api/status/missing').status_code,404)
        self.assertEqual(self.client.get('/api/file/missing').status_code,404)

    def test_pending_job_file_not_ready(self):
        module.jobs['pending']={'status':'downloading'}
        self.assertEqual(self.client.get('/api/file/pending').status_code,404)

    def test_completed_file_is_served(self):
        file=Path(self.temp.name)/'owned.mp4';file.write_bytes(b'synthetic-test-content')
        module.jobs['complete']={'status':'done','file':str(file),'filename':'owned.mp4'}
        response=self.client.get('/api/file/complete')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data,b'synthetic-test-content')
        self.assertIn('attachment',response.headers['Content-Disposition'])
        response.close()

    def test_run_audio_download_selects_mp3_and_cleans_only_job_siblings(self):
        key='audiojob'
        mp3=Path(self.temp.name)/(key+'.mp3');mp3.write_bytes(b'fake-mp3')
        webm=Path(self.temp.name)/(key+'.webm');webm.write_bytes(b'fake-webm')
        other=Path(self.temp.name)/'unrelated.mp4';other.write_bytes(b'keep')
        module.jobs[key]={'status':'downloading','title':'own:/video?'}
        with mock.patch.object(module.subprocess,'run',return_value=self.result()) as call:
            module.run_download(key,'https://example.invalid/owned','audio',None)
        self.assertEqual(module.jobs[key]['status'],'done')
        self.assertEqual(module.jobs[key]['file'],str(mp3))
        self.assertEqual(module.jobs[key]['filename'],'ownvideo.mp3')
        self.assertFalse(webm.exists());self.assertTrue(other.exists())
        self.assertIn('--audio-format',call.call_args.args[0])
        self.assertEqual(call.call_args.kwargs['timeout'],300)

    def test_run_video_selected_format(self):
        key='videojob';file=Path(self.temp.name)/(key+'.mp4');file.write_bytes(b'fake-mp4')
        module.jobs[key]={'status':'downloading','title':'Synthetic'}
        with mock.patch.object(module.subprocess,'run',return_value=self.result()) as call:
            module.run_download(key,'https://example.invalid/owned','video','137')
        self.assertEqual(module.jobs[key]['status'],'done')
        command=call.call_args.args[0]
        self.assertEqual(command[command.index('-f')+1],'137+bestaudio/best')

    def test_run_download_reports_missing_output(self):
        module.jobs['none']={'status':'downloading'}
        with mock.patch.object(module.subprocess,'run',return_value=self.result()):
            module.run_download('none','https://example.invalid/owned','video',None)
        self.assertEqual(module.jobs['none']['status'],'error')
        self.assertIn('no file',module.jobs['none']['error'])

    def test_run_download_subprocess_error_and_timeout(self):
        module.jobs['error']={'status':'downloading'}
        with mock.patch.object(module.subprocess,'run',return_value=self.result(stderr='line1\nFailed',code=1)):
            module.run_download('error','https://example.invalid/owned','video',None)
        self.assertEqual(module.jobs['error']['error'],'Failed')
        module.jobs['timeout']={'status':'downloading'}
        with mock.patch.object(module.subprocess,'run',side_effect=subprocess.TimeoutExpired('yt-dlp',300)):
            module.run_download('timeout','https://example.invalid/owned','video',None)
        self.assertIn('timed out',module.jobs['timeout']['error'])

    def test_parse_multiple_json_objects_chooses_first(self):
        self.assertEqual(module.parse_ytdlp_json('\n'+json.dumps({'id':'one'})+'\n'+json.dumps({'id':'two'})),{'id':'one'})

    def test_non_object_json_is_rejected_before_work(self):
        for payload in [[], ['url'], 42, 'url', True]:
            for endpoint in ['/api/info', '/api/playlist', '/api/download']:
                with self.subTest(payload=payload, endpoint=endpoint):
                    with mock.patch.object(module.subprocess, 'run') as process, mock.patch.object(module.threading, 'Thread') as thread:
                        response = self.client.post(endpoint, json=payload)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('object', response.json['error'])
                    process.assert_not_called()
                    thread.assert_not_called()

    def test_non_string_urls_are_rejected_before_work(self):
        for value in [None, 42, [], {}, True]:
            for endpoint in ['/api/info', '/api/playlist', '/api/download']:
                with self.subTest(url=value, endpoint=endpoint):
                    with mock.patch.object(module.subprocess, 'run') as process, mock.patch.object(module.threading, 'Thread') as thread:
                        response = self.client.post(endpoint, json={'url': value})
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('string', response.json['error'])
                    process.assert_not_called()
                    thread.assert_not_called()

    def test_malformed_json_is_rejected_before_work(self):
        for endpoint in ['/api/info', '/api/playlist', '/api/download']:
            with self.subTest(endpoint=endpoint):
                with mock.patch.object(module.subprocess, 'run') as process, mock.patch.object(module.threading, 'Thread') as thread:
                    response = self.client.post(endpoint, data='{bad json', content_type='application/json')
                self.assertEqual(response.status_code, 400)
                process.assert_not_called()
                thread.assert_not_called()

    def test_null_json_returns_client_error(self):
        for endpoint in ['/api/info','/api/playlist','/api/download']:
            with self.subTest(endpoint=endpoint):
                response=self.client.post(endpoint,data='null',content_type='application/json')
                self.assertEqual(response.status_code,400,'Malformed request should be a client error rather than an internal error')

if __name__ == '__main__':
    unittest.main()
