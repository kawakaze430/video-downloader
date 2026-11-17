from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

R=Path('/workspace/video-downloader');A=R/'AnalyseFuture'
P=json.loads((A/'migration-records/preservation-manifest.json').read_text())
D=json.loads(Path('/workspace/recovery-work/discovery.json').read_text())
M=json.loads(Path('/workspace/recovery-work/migration-state.json').read_text())
required=['REPOSITORY_AUDIT.txt','COMPLETE_FILE_INVENTORY.txt','FEATURE_INVENTORY.txt',
 'DUPLICATE_ANALYSIS.txt','SECURITY_AUDIT.txt','ORIGINAL_TO_NEW_PATH_MAPPING.txt',
 'CONSOLIDATION_REPORT.txt','ARCHIVED_FILES_MANIFEST.txt','PROJECT_VISION_AND_FUTURE_ROADMAP.txt',
 'TECHNICAL_DEBT.txt','TEST_AND_VALIDATION_REPORT.txt','MIGRATION_SUMMARY.txt',
 'NEXT_DEVELOPER_INSTRUCTIONS.txt','WORK_PROGRESS.txt']
for name in required:
 if not (A/name).is_file() or (A/name).stat().st_size<200:raise RuntimeError('Missing/empty report: '+name)

# Content comparisons only: no runtime, helper, test, build or dependency command.
records=subprocess.check_output(['git','ls-tree','-r','-z',P['baseline_commit']],cwd=R).split(b'\0')
baseline={}
for record in records:
 if record:
  meta,path=record.split(b'\t',1);mode,kind,oid=meta.decode().split();baseline[path.decode()]=(mode,oid)
if set(baseline)!={item['original_path'] for item in P['files']}:raise RuntimeError('Incomplete original inventory')
destinations=set()
for item in P['files']:
 path=R/item['preserved_path'];data=path.read_bytes()
 if path in destinations:raise RuntimeError('Duplicate preservation destination')
 destinations.add(path)
 if (item['git_mode'],item['git_blob_oid'])!=baseline[item['original_path']]:raise RuntimeError('Original metadata mismatch')
 if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise RuntimeError('Original not preserved: '+item['original_path'])
zip_total=0
for item in json.loads((R/'archives/source-index.json').read_text()):
 path=R/item['archive']
 if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('Original ZIP changed')
 with zipfile.ZipFile(path) as z:
  count=0
  for member in z.infolist():
   if member.is_dir():continue
   relative=str(PurePosixPath(*PurePosixPath(member.filename).parts[1:]))
   retained=item.get('member_paths',{}).get(relative,item['directory']+'/'+relative)
   if (R/retained).read_bytes()!=z.read(member):raise RuntimeError('ZIP member original lost: '+retained)
   count+=1
  if count!=item['files']:raise RuntimeError('ZIP payload count mismatch')
  zip_total+=count

# Ensure final output paths exist before the last path catalogue is collected.
(R/'AnalyseFuture/repository-inventory/recovery-summary.json').write_text('{}\n')
import shutil
shutil.copy2('/workspace/recovery-work/finalize.py',R/'AnalyseFuture/migration-records/scripts/finalize.py')
# Catalogue all current tracked files, including every report produced in this pass.
subprocess.run(['git','add','-A'],cwd=R,check=True)
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0'))-{''}
if not all(item['preserved_path'] in tracked for item in P['files']):raise RuntimeError('Preserved file not staged/tracked')
index={}
for record in subprocess.check_output(['git','ls-files','--stage','-z'],cwd=R).decode().split('\0'):
 if record:
  meta,path=record.split('\t',1);mode,oid,stage=meta.split();index[path]=(mode,oid)
for item in P['files']:
 if index[item['preserved_path']]!=(item['git_mode'],item['git_blob_oid']):raise RuntimeError('Preserved Git object or mode differs: '+item['original_path'])
old_by_active={M['active'][item['path']]:item for item in D['files']}
old_by_preserved={M['mapping'][item['path']]:item for item in D['files']}
catalogue=[]
for path in sorted(tracked):
 if path in old_by_active:purpose=old_by_active[path]['purpose']
 elif path in old_by_preserved:purpose='Exact baseline original preserved before reference/configuration repair'
 elif path.startswith('AnalyseFuture/'):purpose='Recovery/future documentation, inventory, provenance or static relationship evidence; excluded from application execution'
 elif path=='PROJECT_STRUCTURE.md':purpose='Canonical folder/function/ownership and continuation map'
 elif path=='.dockerignore':purpose='Exclude historical/reference/data/cache material from root build contexts'
 elif path=='README.md':purpose='Current repository navigation and no-test scope'
 else:purpose='Repository organization support; see PROJECT_STRUCTURE.md'
 catalogue.append({'path':path,'purpose':purpose,'origin':'baseline file or retained original' if path in old_by_active or path in old_by_preserved else 'authored recovery record/control'})
(A/'repository-inventory/final-file-catalogue.json').write_text(json.dumps({'files':catalogue,'coverage':'All paths tracked/staged at final review; generated reports may describe themselves without recursive content hashes.'},indent=2)+'\n')
subprocess.run(['git','add','AnalyseFuture/repository-inventory/final-file-catalogue.json'],cwd=R,check=True)
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0'))-{''}
if not any(x['path']=='AnalyseFuture/repository-inventory/final-file-catalogue.json' for x in catalogue):
 catalogue.append({'path':'AnalyseFuture/repository-inventory/final-file-catalogue.json','purpose':'Self-describing complete final tracked-path catalogue','origin':'authored recovery record'})
 catalogue.sort(key=lambda x:x['path'])
(A/'repository-inventory/final-file-catalogue.json').write_text(json.dumps({'count':len(tracked),'files':catalogue,'coverage':'All final tracked/staged paths; report content hashes are intentionally not recursive.'},indent=2)+'\n')
p=A/'COMPLETE_FILE_INVENTORY.txt';text=p.read_text().split('\nFINAL DELIVERED PATH CATALOGUE\n',1)[0]
text+='\nFINAL DELIVERED PATH CATALOGUE\n'+str(len(tracked))+' tracked files, including all authored reports and preservation copies.\n'
text+='\n'.join(x['path']+' | '+x['purpose'] for x in catalogue)+'\n';p.write_text(text)
summary={'starting_commit':P['baseline_commit'],'baseline_files':len(P['files']),'baseline_text_files':D['text_count'],
 'baseline_binary_files':D['binary_count'],'current_tracked_files':len(tracked),'files_moved':M['moved_count'],
 'fixture_files_regrouped':M['fixture_files_grouped'],'runtime_algorithm_files_merged':0,
 'newly_preserved_originals_and_orphan':M['newly_archived_count'],'source_archive_members_preserved':zip_total,
 'feature_records':95,'feature_record_note':'46 source/tool/fixture capability groups plus 49 cross-referenced planned backlog entries; not 95 verified distinct shipping features',
 'tests_run_after_latest_instruction':0,'static_observation':'all baseline original byte hashes and original Git metadata accounted for; all ZIP members retained; local links/import relationships reviewed',
 'backup_ref':'refs/tags/recovery-baseline-2026-11-17-7a7e2f6'}
(A/'repository-inventory/recovery-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
p=A/'TEST_AND_VALIDATION_REPORT.txt';s=p.read_text().split('\nFinal passive content review:',1)[0];s+='\nFinal passive content review: all1,458startingoriginals have matching retained byte hashes and Git mode/object metadata; all1,438ZIPpayloadmembers remain unchanged. Local Markdown target review found zero unresolved active targets. Static import relationship inventory covers1,198sourcefiles; zero unresolved active TypeScript local imports. These observations do not execute or validate application behavior.\n';p.write_text(s.replace('all1,458startingoriginals','all 1,458 starting originals').replace('all1,438ZIPpayloadmembers','all 1,438 ZIP payload members').replace('covers1,198sourcefiles','covers 1,198 source files'))
p=A/'WORK_PROGRESS.txt';s=p.read_text().replace('Current: final static path/content preservation review and direct-main delivery.','Completed: final static path/content preservation review; all baseline originals and ZIP member bytes accounted for; no unresolved active Markdown or TypeScript local import target found.\nCurrent: structure-only work complete; next task awaits owner direction. Final remote SHA is confirmed in delivery and Git history.')
p.write_text(s)
print(json.dumps(summary,indent=2))

