from pathlib import Path
import hashlib,io,json,os,subprocess,tarfile,tempfile
repo=Path('/workspace/video-downloader');out=Path('/workspace/validation-work/fixture');pinned='c1c8f0f8f80f968bb4e214678e8e91bb50c35630'
results=[]
with tempfile.TemporaryDirectory(prefix='preservation-probes-',dir='/tmp') as folder:
 base=Path(folder);snapshot=base/'snapshot';snapshot.mkdir()
 archive=subprocess.check_output(['git','archive','--format=tar',pinned],cwd=repo)
 with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(snapshot,filter='data')
 manifest=snapshot/'AnalyseFuture/migration-records/preservation-manifest.json';original=manifest.read_bytes();data=json.loads(original)
 # Git archives use canonical LF blobs; preserve the declared CRLF checkout for Windows files.
 for item in data['files']:
  path=snapshot/item['preserved_path'];content=path.read_bytes()
  if hashlib.sha256(content).hexdigest()!=item['sha256']:
   candidate=content.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
   assert hashlib.sha256(candidate).hexdigest()==item['sha256'],item['preserved_path']
   path.write_bytes(candidate)
 env=os.environ.copy();env['GIT_DIR']=str(repo/'.git');env['GIT_WORK_TREE']=str(snapshot);env['GIT_INDEX_FILE']=str(base/'temporary-index')
 def reset_index():subprocess.run(['git','read-tree',pinned],cwd=snapshot,env=env,check=True)
 def run(name,should_pass):
  result=subprocess.run(['python3','tools/repository/verify_preservation.py'],cwd=snapshot,env=env,text=True,capture_output=True)
  assert (result.returncode==0)==should_pass,(name,result.returncode,result.stdout,result.stderr)
  results.append({'name':name,'expected':'pass' if should_pass else 'reject','actual_exit':result.returncode,'result':'passed','message':(result.stderr or result.stdout).strip()})
 reset_index();run('valid isolated baseline snapshot',True)
 subprocess.run(['git','update-index','--force-remove','--','tools/fixtures/http_fixture.py'],cwd=snapshot,env=env,check=True)
 run('missing tracked preservation destination',False);reset_index()
 changed=json.loads(original);changed['files'].pop();manifest.write_text(json.dumps(changed));run('omitted baseline entry',False);manifest.write_bytes(original)
 changed=json.loads(original);changed['files'][0]['git_blob_sha256']='0'*64;manifest.write_text(json.dumps(changed));run('incorrect baseline Git hash',False);manifest.write_bytes(original)
 target=snapshot/'tools/fixtures/http_fixture.py';saved=target.read_bytes();target.write_bytes(saved+b'\n# corruption probe\n');run('altered preserved source bytes',False);target.write_bytes(saved)
 target=snapshot/'archives/reclip-main.zip';saved=target.read_bytes();target.write_bytes(saved+b'corruption probe');run('altered original archive bytes',False);target.write_bytes(saved)
result={'checks_passed':len(results),'failed':0,'actual_repository_changed':False,'cases':results}
(out/'preservation-negative-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
