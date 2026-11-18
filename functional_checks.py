from pathlib import Path
import hashlib,http.client,json,re,subprocess,sys,time,urllib.request
root=Path('/workspace/video-downloader');out=Path('/workspace/validation-work/fixture')
process=subprocess.Popen([sys.executable,'-m','tools.fixtures.http_fixture','--port','0'],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
checks=[]
try:
 first=process.stdout.readline().strip();second=process.stdout.readline().strip()
 match=re.search(r'http://127\.0\.0\.1:(\d+)/file.bin',first)
 assert match,first
 port=int(match.group(1));expected=second.split(': ',1)[1]
 def request(path,headers=None):
  connection=http.client.HTTPConnection('127.0.0.1',port,timeout=3)
  try:
   connection.request('GET',path,headers=headers or {});response=connection.getresponse()
   return response.status,dict(response.getheaders()),response.read()
  finally:connection.close()
 status,_,body=request('/health');assert (status,body)==(200,b'ok');checks.append('CLI starts on assigned loopback port; health returns200/ok')
 status,headers,full=request('/file.bin');assert status==200 and len(full)==16384 and hashlib.sha256(full).hexdigest()==expected;checks.append('full16384byte file matches advertised SHA256')
 a=request('/file.bin',{'Range':'bytes=0-8191'});b=request('/file.bin',{'Range':'bytes=8192-'})
 assert a[0]==b[0]==206 and a[2]+b[2]==full;checks.append('two live206Range responses reassemble exact original')
 with urllib.request.urlopen(f'http://127.0.0.1:{port}/redirect.bin',timeout=3) as response:
  assert response.url.endswith('/file.bin') and response.read()==full
 checks.append('relative redirect follows to exact file bytes')
 assert request('/no-range.bin',{'Range':'bytes=8192-'})[::2]==(200,full);checks.append('Range-disabled source returns200/full body')
 try:request('/drop.bin')
 except http.client.IncompleteRead as error:
  assert len(error.partial)==2048 and error.expected==14336
 else:raise AssertionError('Truncated response not detected')
 checks.append('declared full body truncated at2048bytes raises IncompleteRead')
finally:
 process.terminate()
 try:process.communicate(timeout=5)
 except subprocess.TimeoutExpired:process.kill();process.communicate(timeout=5)
for args in [['--port','65536'],['--tls-cert','/tmp/unused-fixture-cert.pem']]:
 result=subprocess.run([sys.executable,'-m','tools.fixtures.http_fixture',*args],cwd=root,text=True,capture_output=True)
 assert result.returncode==2,(args,result.returncode)
 checks.append('invalid CLI arguments rejected with exit2: '+' '.join(args))
result={'functional_checks_passed':len(checks),'failed':0,'checks':checks,'server_process_stopped':True}
(out/'functional-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
