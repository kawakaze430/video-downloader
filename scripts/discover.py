import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path('/workspace/video-downloader')
BASE = '7a7e2f6cd52626f26d954ba60e4d7a838d717b56'
OUT = Path('/workspace/recovery-work')


def owner(path):
    if path.startswith('sources/ab-download-manager/'):
        rest = path.split('/')[2:]
        module = '/'.join(rest[:2]) if rest[0] in {'desktop','android','shared','downloader','integration','compositeBuilds'} else rest[0]
        purposes = {'downloader/core':'transfer engine, connections, segments, job state and persistence',
                    'downloader/monitor':'observable transfer progress and speed',
                    'integration/server':'local HTTP integration endpoints and authorization',
                    'shared/app':'shared application behavior, pages, queues, settings and UI state',
                    'shared/resources':'localized application resources and icons',
                    'shared/compose-utils':'shared Compose controls and rendering helpers',
                    'shared/config':'application configuration and defaults',
                    'shared/updater':'platform update discovery and application',
                    'shared/auto-start':'platform startup registration',
                    'shared/utils':'common platform/file/network utilities',
                    'android/app':'Android entrypoints, storage, services, permissions and UI',
                    'desktop/app':'desktop entrypoints, windows, native host and packaging',
                    'desktop/app-utils':'desktop integration and platform helpers',
                    'desktop/shared':'desktop shared state and adapters',
                    'desktop/mac_utils':'macOS native integration',
                    'desktop/slf4j-impl':'desktop logging backend'}
        return 'download-manager/'+module, purposes.get(module,'Kotlin project build, release, branding or contributor support')
    if path.startswith('sources/ab-browser-integration/'):
        rest=path.split('/')[2:]
        group=rest[1] if len(rest)>1 and rest[0]=='src' else rest[0]
        purposes={'backend':'desktop connection and native/HTTP transport',
                  'interceptors':'browser download capture and handoff',
                  'media':'HLS/media link analysis and quality selection',
                  'manifest':'browser permissions and package metadata',
                  'optionsui':'browser integration settings and permissions UI',
                  'contextmenus':'user-triggered context menu handoff',
                  'contentscripts':'in-page selection and message handling',
                  'message':'cross-context message contracts',
                  'entrypoint':'browser background/popup/options entrypoints',
                  'browseractionpopup':'popup controls and job intake',
                  'configs':'persisted extension preferences'}
        return 'browser-extension/'+group,purposes.get(group,'browser companion shared UI, assets, utilities or build configuration')
    if '/reference-projects/mediagrabber/' in path:
        rest=path.split('/mediagrabber/',1)[1].split('/')
        return 'reference/mediagrabber/'+rest[0], 'alternative media discovery, manifest parsing, native RPC and FFmpeg/yt-dlp companion; not active product integration'
    if '/reference-projects/reclip/' in path:
        return 'reference/reclip', 'alternative Flask/yt-dlp web workflow, browser UI or packaging; not a production service'
    if path.startswith('sources/downloader-blueprint/'):
        if '/tools/' in path:return 'fixture/server','original synthetic HTTP/HTTPS download fixture and CLI'
        if '/tests/' in path:return 'fixture/regression','existing fixture regression suite; retained without running tests'
        return 'project/research','earlier product planning, decisions, historical research and contributor guidance'
    if '/prior-versions/' in path:return 'preservation/history','exact previous document or helper retained for provenance'
    if path.startswith('archives/'):return 'preservation/archives','original uploaded archive or archive provenance guide'
    if path.startswith('tools/'):return 'repository/tooling','repository preservation verification or development setup helper'
    if path.startswith('docs/'):return 'repository/audit','previous structure audit and preservation evidence'
    if path=='PROJECT_IDEA.txt':return 'product/vision','detailed cross-platform product vision and future roadmap'
    if path=='AGENTS.md':return 'repository/instructions','owner working agreement and direct-main delivery rules'
    if path=='README.md':return 'repository/navigation','repository overview and setup navigation'
    if path=='.gitignore':return 'repository/configuration','exclude local dependencies and generated outputs from commits'
    return 'preservation/navigation','archive/reference navigation and preservation scope'


files=[]; content_groups=defaultdict(list)
records=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT).decode().split('\0')
for record in records:
    if not record:continue
    meta,name=record.split('\t',1);mode,oid,stage=meta.split()
    path=ROOT/name;data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
    component,purpose=owner(name)
    binary=b'\0' in data or path.suffix.lower() in {'.zip','.jar','.png','.webp','.jpg','.jpeg','.bmp','.ico','.icns','.mp4'}
    deps=[];symbols=[];doc_summary='';kind='binary asset or archive' if binary else 'text/configuration'
    if not binary:
        text=data.decode('utf-8',errors='replace')
        if path.suffix in {'.kt','.kts'}:
            kind='Kotlin implementation' if path.suffix=='.kt' else 'Gradle Kotlin configuration'
            deps=re.findall(r'^import\s+([^\s;]+)',text,re.M)
            deps+=['project:'+x for x in re.findall(r'project\(["\x27]([^"\x27]+)',text)]
            symbols=re.findall(r'\b(?:class|interface|object|fun|typealias)\s+([A-Za-z_]\w*)',text)
        elif path.suffix in {'.ts','.tsx','.js','.mjs','.cjs'}:
            kind='browser/Node source or build configuration'
            deps=re.findall(r'(?:from\s*|import\s*|require\s*\()["\x27]([^"\x27]+)',text)
            symbols=re.findall(r'\b(?:class|function|interface|type|const)\s+([A-Za-z_$][\w$]*)',text)
        elif path.suffix=='.py':
            kind='Python fixture/tool/test implementation'
            try:
                tree=ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import):deps += [v.name for v in node.names]
                    elif isinstance(node,ast.ImportFrom):deps.append('.'*node.level+(node.module or ''))
                    elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):symbols.append(node.name)
            except SyntaxError:kind+=' (static parse issue; no execution)'
        elif path.name=='package.json':
            obj=json.loads(text);kind='npm package/workspace manifest'
            deps=list(obj.get('dependencies',{}))+list(obj.get('devDependencies',{}))
            symbols=list(obj.get('scripts',{}))
        elif path.name=='package-lock.json':
            obj=json.loads(text);kind='frozen npm dependency graph'
            deps=['locked packages:'+str(len(obj.get('packages',{})))]
        elif path.suffix in {'.md','.txt','.rtf'}:
            kind='documentation or historical transcript'
            headings=re.findall(r'^(?:#+\s+|\d{2}\.\s+)(.+)',text,re.M)
            doc_summary='; '.join(headings[:4])
        elif '/res/' in name or '/resources/' in name:
            kind='platform resource or packaging configuration'
            symbols=re.findall(r'<(?:string|color|style|drawable)[^>]*name=["\x27]([^"\x27]+)',text)
        elif path.suffix in {'.sh','.bat','.ps1'}:kind='platform install/update/development script; static review only'
        elif '/.github/workflows/' in name:kind='nested inactive workflow snapshot'
        if name.endswith('requirements.txt'):deps=[x.strip() for x in text.splitlines() if x.strip() and not x.startswith('#')]
    elif path.suffix in {'.zip','.jar'}:
        with zipfile.ZipFile(path) as archive:
            symbols=['archive members:'+str(len(archive.infolist()))]
            kind='original source ZIP' if path.suffix=='.zip' else 'Gradle bootstrap JAR (not executed)'
    files.append({'path':name,'component':component,'purpose':purpose,'kind':kind,
                  'dependencies':sorted(set(deps)),'symbols':symbols,'documentation_topics':doc_summary,
                  'bytes':len(data),'sha256':digest,'git_blob_oid':oid,'git_mode':mode,
                  'review':'binary bytes/header/container metadata inspected; not decoded or executed' if binary else 'entire text read; static imports/symbols/content classified; runtime not verified',
                  'binary':binary})
    content_groups[digest].append(name)
result={'baseline_commit':BASE,'files':files,'count':len(files),'text_count':sum(not f['binary'] for f in files),
        'binary_count':sum(f['binary'] for f in files),
        'duplicates':[v for v in content_groups.values() if len(v)>1],
        'component_counts':dict(sorted(Counter(f['component'] for f in files).items()))}
(OUT/'discovery.json').write_text(json.dumps(result,indent=2)+'\n')
dest=ROOT/'AnalyseFuture/repository-inventory';dest.mkdir(parents=True,exist_ok=True)
(dest/'baseline-file-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'AnalyseFuture/WORK_PROGRESS.txt').write_text(
    'STRUCTURE RECOVERY PROGRESS\nBaseline: '+BASE+'\n'
    'Completed: fetched all advertised branches/tags; clean main; remote baseline tag preserved; local Git bundle created.\n'
    'Completed: all '+str(len(files))+' tracked files read and classified by component and content; '+str(result['text_count'])+' text files, '+str(result['binary_count'])+' binaries inspected as data.\n'
    'Current: implement functional app/tool/test/document grouping and preserve every original.\n'
    'Latest owner instruction: do not run tests. No more builds, test suites, or application startup will be run.\n'
    'Pending: path mapping, reference repair, required reports, PROJECT_STRUCTURE.md, static preservation review, direct-main push.\n'
    'Limits: no account/security-log access; GitHub protection API was unavailable; server accepted backup-tag push.\n')
print('Inventoried',len(files),'files:',result['text_count'],'text,',result['binary_count'],'binary; exact duplicate groups:',len(result['duplicates']))
