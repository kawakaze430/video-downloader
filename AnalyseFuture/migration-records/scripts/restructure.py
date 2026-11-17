from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

R=Path('/workspace/video-downloader')
D=json.loads(Path('/workspace/recovery-work/discovery.json').read_text())
BASE=D['baseline_commit']
H='AnalyseFuture/historical-implementations/'+BASE[:7]
mapping={}
active={}
for item in D['files']:
 p=item['path'];new=p
 if p.startswith('sources/ab-download-manager/'):new=p.replace('sources/ab-download-manager/','apps/download-manager/',1)
 elif p.startswith('sources/ab-browser-integration/'):new=p.replace('sources/ab-browser-integration/','apps/browser-extension/',1)
 elif p.startswith('sources/downloader-blueprint/tools/'):new=p.replace('sources/downloader-blueprint/','',1)
 elif p.startswith('sources/downloader-blueprint/tests/'):new=p.replace('sources/downloader-blueprint/tests/','tests/fixtures/',1)
 elif p.startswith('sources/downloader-blueprint/'):new=p.replace('sources/downloader-blueprint/','docs/project/',1)
 elif p=='sources/archives.json':new='archives/source-index.json'
 elif p=='PROJECT_IDEA.txt':new='AnalyseFuture/PROJECT_VISION_AND_FUTURE_ROADMAP.txt'
 elif p=='tools/onboarding/setup.sh':new='tools/development/setup.sh'
 elif p=='tools/verify_repository.py':new='tools/repository/verify_preservation.py'
 elif p=='docs/REPOSITORY_AUDIT.txt':new='AnalyseFuture/recovery-notes/previous-audits/REPOSITORY_AUDIT.7a7e2f6.txt'
 elif p=='docs/preservation-manifest.json':new='AnalyseFuture/migration-records/preservation-0b2a1ad.json'
 if p=='sources/ab-browser-integration/src/backend/BackendProvider.ts':
  new='AnalyseFuture/incomplete-features/browser-extension/BackendProvider.ts'
 mapping[p]=new;active[p]=new

old_contents={i['path']:(R/i['path']).read_bytes() for i in D['files']}

def gitmove(old,new):
 target=R/new
 if target.exists():raise RuntimeError('Refusing overwrite: '+new)
 target.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['git','mv',old,new],cwd=R,check=True)

# Package roots move whole, including ignored local dependencies without publishing them.
gitmove('sources/ab-download-manager','apps/download-manager')
gitmove('sources/ab-browser-integration','apps/browser-extension')
gitmove('apps/browser-extension/src/backend/BackendProvider.ts',mapping['sources/ab-browser-integration/src/backend/BackendProvider.ts'])
gitmove('sources/downloader-blueprint','docs/project')
gitmove('docs/project/tools/__init__.py','tools/__init__.py')
gitmove('docs/project/tools/fixtures','tools/fixtures')
gitmove('docs/project/tests','tests/fixtures')
for old in ['sources/archives.json','PROJECT_IDEA.txt','tools/onboarding/setup.sh','tools/verify_repository.py','docs/REPOSITORY_AUDIT.txt','docs/preservation-manifest.json']:
 gitmove(old,mapping[old])

changed_originals=set()
def preserve_before_edit(old):
 if old in changed_originals:return
 dest=R/H/old
 if dest.exists():raise RuntimeError('Preservation destination already exists: '+str(dest))
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(old_contents[old])
 dest.chmod(int(next(i['git_mode'] for i in D['files'] if i['path']==old),8)&0o777)
 mapping[old]=str(dest.relative_to(R))
 changed_originals.add(old)

def edit(old,data):
 target=R/active[old]
 if target.read_bytes()!=data:
  preserve_before_edit(old)
  target.write_bytes(data)

# Repair Markdown links according to the identity of their original target.
# Internal links within intact Gradle/npm packages naturally remain unchanged.
old_paths=set(old_contents)
for old in old_paths:
 if not old.endswith('.md') or old.startswith('AnalyseFuture/prior-versions/'):continue
 text=old_contents[old].decode('utf-8',errors='replace')
 original_dir=Path(old).parent;new_dir=Path(active[old]).parent
 def repair(m):
  label,target=m.group(1),m.group(2)
  if re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#|/)',target):return m.group(0)
  pathpart,sep,anchor=target.partition('#')
  resolved=os.path.normpath(str(original_dir/pathpart))
  if resolved in active:
   target2=os.path.relpath(active[resolved],new_dir)
   return '['+label+']('+target2+(sep+anchor if sep else '')+')'
  return m.group(0)
 revised=re.sub(r'\[([^\]]*)\]\(([^\s)]+)\)',repair,text)
 if revised!=text:edit(old,revised.encode())

# The fixture now has one root tools namespace and a dedicated regression folder.
old='sources/downloader-blueprint/tools/fixtures/README.md'
text=(R/active[old]).read_text().replace('discover -s tests -v','discover -s tests/fixtures -v')
text=text.replace('CI is defined in .github/workflows/fixture-tests.yml. It runs for relevant pull requests or on manual invocation, with no GPU or hosted downloader deployment.',
 'The original workflow is preserved under docs/project/.github/workflows/fixture-tests.yml as inactive historical material. No root CI was activated in this no-test restructuring pass.')
edit(old,text.encode())

# Source packaging must include only this package, not every archive and reference.
old='sources/ab-browser-integration/package.json'
obj=json.loads((R/active[old]).read_text())
obj['scripts']['pack:src']='git archive --format=zip HEAD:apps/browser-extension -o ./dist/src.zip'
edit(old,(json.dumps(obj,indent=2)+'\n').encode())

# Canonical future idea belongs with the requested future roadmap, not at root.
old='PROJECT_IDEA.txt'
text=(R/active[old]).read_text()
replacements={'sources/ab-download-manager/':'apps/download-manager/',
 'sources/ab-browser-integration/':'apps/browser-extension/',
 'sources/downloader-blueprint/tools/fixtures/':'tools/fixtures/',
 'sources/downloader-blueprint/tests/':'tests/fixtures/',
 'sources/downloader-blueprint/docs/':'docs/project/docs/',
 'sources/downloader-blueprint/':'docs/project/',
 'sources/archives.json':'archives/source-index.json',
 'tools/onboarding/setup.sh':'tools/development/setup.sh',
 'tools/verify_repository.py':'tools/repository/verify_preservation.py',
 'docs/REPOSITORY_AUDIT.txt':'AnalyseFuture/REPOSITORY_AUDIT.txt',
 'docs/preservation-manifest.json':'AnalyseFuture/migration-records/preservation-manifest.json',
 'PROJECT_IDEA.txt':'AnalyseFuture/PROJECT_VISION_AND_FUTURE_ROADMAP.txt'}
for a,b in replacements.items():text=text.replace(a,b)
text=text.replace('END OF PROJECT IDEA\n',
 'STRUCTURE-ONLY RECOVERY ADDENDUM\n'
 'The latest owner instruction prohibits tests in this pass. Existing test\n'
 'source and earlier results are preserved; no post-move test success is claimed.\n'
 'The runtime structure is apps/download-manager and apps/browser-extension;\n'
 'the original fixture lives in tools/fixtures with tests in tests/fixtures.\n'
 'The full organization and ownership rules are in PROJECT_STRUCTURE.md.\n'
 'The project is a multi-platform download/media project with future AI ideas,\n'
 'not a verified universal AI downloader. No new AI implementation was created.\n\n'
 'END OF PROJECT IDEA\n')
edit(old,text.encode())

# Preserve canonical files that will be rewritten by the report stage.
for old in ['README.md','AGENTS.md','tools/onboarding/setup.sh','tools/verify_repository.py','sources/archives.json']:
 preserve_before_edit(old)

# Original archive members point to their exact retained bytes, even if active docs changed.
source_index=json.loads(old_contents['sources/archives.json'])
for item in source_index:
 oldbase=item['directory']
 item['directory']={'sources/ab-download-manager':'apps/download-manager',
                    'sources/ab-browser-integration':'apps/browser-extension',
                    'sources/downloader-blueprint':'docs/project'}.get(oldbase,oldbase)
 item['member_paths']={}
 for entry in D['files']:
  old=entry['path']
  if old.startswith(oldbase+'/'):
   relative=old[len(oldbase)+1:]
   if mapping[old]!=item['directory']+'/'+relative:
    item['member_paths'][relative]=mapping[old]
(R/'archives/source-index.json').write_text(json.dumps(source_index,indent=2)+'\n')

# Baseline Git objects and on-disk/archive bytes are recorded independently.
oids=list(dict.fromkeys(i['git_blob_oid'] for i in D['files']))
data=subprocess.run(['git','cat-file','--batch'],cwd=R,input=('\n'.join(oids)+'\n').encode(),stdout=subprocess.PIPE,check=True).stdout
blobs={};offset=0
for oid in oids:
 end=data.index(b'\n',offset);header=data[offset:end].split();size=int(header[2]);start=end+1
 blob=data[start:start+size];blobs[oid]=(hashlib.sha256(blob).hexdigest(),size);offset=start+size+1
preserved=[]
for entry in D['files']:
 old=entry['path'];oid=entry['git_blob_oid'];sha,size=blobs[oid]
 dest=R/mapping[old]
 assert dest.read_bytes()==old_contents[old],old
 preserved.append({'original_path':old,'preserved_path':mapping[old],'active_path':active[old],
  'sha256':entry['sha256'],'bytes':entry['bytes'],'git_mode':entry['git_mode'],
  'git_blob_oid':oid,'git_blob_sha256':sha,'git_blob_bytes':size,
  'reason':'original retained before path/reference/configuration update' if old in changed_originals else
   'orphan imports-only browser stub; active Backend.ts owns native/HTTP dispatch' if 'BackendProvider.ts' in old else
   'functional responsibility grouping; framework-internal structure retained' if old!=active[old] else 'retained in existing functional collection'})
dest=R/'AnalyseFuture/migration-records';dest.mkdir(parents=True,exist_ok=True)
(dest/'preservation-manifest.json').write_text(json.dumps({'baseline_commit':BASE,'files':preserved,
 'notes':'All baseline files preserved. sha256/bytes refer to working-tree bytes, git_blob_* to normalized Git objects. Active docs/configs may have repaired references; original versions remain at preserved_path. No tests executed after latest no-test instruction.'},indent=2)+'\n')
state={'baseline_commit':BASE,'mapping':mapping,'active':active,'changed_originals':sorted(changed_originals),
 'moved_count':sum(k!=v for k,v in active.items()),'newly_archived_count':len(changed_originals)+1,
 'fixture_files_grouped':6}
Path('/workspace/recovery-work/migration-state.json').write_text(json.dumps(state,indent=2)+'\n')
print('Grouped',state['moved_count'],'baseline paths; preserved',len(changed_originals),'pre-edit originals and one orphan stub.')

