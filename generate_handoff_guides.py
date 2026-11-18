"""Regenerate the complete handoff file/folder guides using tracked paths and recorded ownership.

Run from any directory. This writes documentation only; it does not execute
application code, tests, dependency scripts or historical implementations.
Review role descriptions when a feature changes, not only when paths change.
"""

from collections import defaultdict
import json, os, re, subprocess
from pathlib import Path
from urllib.parse import quote

R=Path(__file__).resolve().parents[2]; OUT=R/'docs/repository';OUT.mkdir(parents=True,exist_ok=True)
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=R,text=True).split('\0'))-{''}
prospective={'PROJECT_HANDOFF.md','docs/repository/FILE_GUIDE.md','docs/repository/FOLDER_GUIDE.md','tools/repository/generate_handoff_guides.py'}
paths=sorted(tracked|prospective)
metadata=json.loads((R/'AnalyseFuture/repository-inventory/baseline-file-analysis.json').read_text())['files']
preservation=json.loads((R/'AnalyseFuture/migration-records/preservation-manifest.json').read_text())['files']
by_old={x['path']:x for x in metadata};meta={}
for entry in preservation:
 data=by_old.get(entry['original_path'])
 if data:
  meta[entry.get('active_path',entry['preserved_path'])]=data
  if entry['preserved_path']!=entry.get('active_path'):meta[entry['preserved_path']]=data
for entry in metadata:meta.setdefault(entry['path'],entry)

def plain(value):
 value=re.sub(r'([a-z0-9])([A-Z])',r'\1 \2',value)
 value=re.sub(r'[_-]+',' ',value)
 return re.sub(r'\s+',' ',value).strip()

def text(path):
 p=R/path
 if not p.exists() or p.stat().st_size>3_000_000:return ''
 b=p.read_bytes()
 if b'\0' in b:return ''
 return b.decode('utf-8',errors='replace')

def escaped(s):return s.replace('|','\\|').replace('[','\\[').replace(']','\\]').replace('`','')
def link(path,label=None):
 relative=os.path.relpath(path,'docs/repository')
 return '['+escaped(label if label is not None else Path(path).name)+']('+quote(relative,safe='/._-')+')'

root_purposes={
 'AGENTS.md':'Owner scope, preservation and contributor delivery instructions.',
 'tools/repository/generate_handoff_guides.py':'Regenerate tracked file/folder ownership guides; documentation only, with classifications requiring review.',
 'README.md':'Homepage overview, current validation entry points and navigation.',
 'PROJECT_HANDOFF.md':'Current goals, verified status, detailed tasks and external-tool PR review contract.',
 'PROJECT_STRUCTURE.md':'Functional ownership map and reasons framework files stay together.',
 '.gitignore':'Keep dependencies, caches and generated outputs out of versioned source.',
 '.dockerignore':'Exclude archives, preserved references and caches from root Docker build contexts.',
 'tools/__init__.py':'Root tools namespace used by fixture imports.',
 'tools/development/gradle.py':'Select required JDK and writable caches; forward explicit Gradle tasks.',
 'tools/development/setup.sh':'Fixture prerequisites and explicit preservation/test opt-ins.',
 'tools/repository/verify_preservation.py':'Check retained Git objects, modes, byte hashes and original ZIP members.',
 'tools/fixtures/http_fixture.py':'Synthetic loopback HTTP/HTTPS, Range, redirects and interrupted-transfer target.',
 'tools/fixtures/__init__.py':'Synthetic fixture package boundary; supports tools.fixtures imports.',
 'tools/fixtures/README.md':'Fixture endpoints, TLS trust and commands; not a downloader implementation.',
 'tests/fixtures/__init__.py':'Regression discovery package for the original fixture.',
 'tests/fixtures/test_http_fixture.py':'14 fixture regressions for ranges, integrity, truncation and verified HTTPS.',
 'tests/references/README.md':'Safe isolated-copy procedure for non-active example tests.',
 'tests/references/test_reclip.py':'19 mocked Flask/input/download regressions; no live source requests.',
 'tests/references/mediagrabber.test.cjs':'24 isolated manifest, quality and RPC regressions; no native registration.',
 'docs/repository/FILE_GUIDE.md':'Complete current path-to-responsibility catalogue, including preserved originals.',
 'docs/repository/FOLDER_GUIDE.md':'Every tracked folder and the functional responsibility it owns.',
 'archives/source-index.json':'Original ZIP hashes and exact per-member retained-original paths.',
 'archives/README.md':'Source archive provenance and safe extraction/preservation rules.',
}
report_roles={
 'README.md':'Navigation for recovery records, references and historical evidence.',
 'REPOSITORY_AUDIT.txt':'Scope/findings of the completed structural audit, with explicit evidence limits.',
 'COMPLETE_FILE_INVENTORY.txt':'Prior per-file inventory and preserved/current path catalogue.',
 'FEATURE_INVENTORY.txt':'95 source-capability/backlog records; not 95 verified product features.',
 'DUPLICATE_ANALYSIS.txt':'Exact/semantic overlaps and reasons implementations were not blindly merged.',
 'SECURITY_AUDIT.txt':'Confirmed source concerns, unresolved risks and account-review boundaries.',
 'ORIGINAL_TO_NEW_PATH_MAPPING.txt':'Starting path, active path and exact retained-original path mapping.',
 'CONSOLIDATION_REPORT.txt':'Actual functional regrouping and intentionally unmerged runtime boundaries.',
 'ARCHIVED_FILES_MANIFEST.txt':'Archived originals/reference roles, reasons and replacement ownership.',
 'PROJECT_VISION_AND_FUTURE_ROADMAP.txt':'Detailed cross-platform ambition, AI options, limits and future research horizons.',
 'TECHNICAL_DEBT.txt':'Historical prioritized debt; current handoff/validation supersedes resolved items.',
 'TEST_AND_VALIDATION_REPORT.txt':'Structure-only pass evidence; later runnable checks are in VALIDATION_REPORT.',
 'MIGRATION_SUMMARY.txt':'Recovery baseline, moves, preservation and compatibility boundaries.',
 'NEXT_DEVELOPER_INSTRUCTIONS.txt':'Recovery continuation guidance with later validation-scope update.',
 'WORK_PROGRESS.txt':'Completed recovery work and next-session continuity record.',
 'VALIDATION_REPORT.txt':'Current 81-case validation evidence, fixes and external build/UI blockers.',
}
module_purposes={
 'downloader/core':'HTTP/HLS job, transfer-part, queue, destination and persistence logic',
 'downloader/monitor':'observable transfer progress, speed and state',
 'integration/server':'local routing, job handoff, authorization and integration models',
 'android/app':'Android activities, foreground services, storage, permissions and UI',
 'desktop/app':'desktop windows, native-host/CLI entrypoints and release packaging',
 'desktop/app-utils':'desktop adapters and platform/UI helpers',
 'desktop/shared':'desktop shared integration, filesystem and power behavior',
 'desktop/mac_utils':'macOS-specific desktop integration',
 'desktop/slf4j-impl':'desktop logging adapter',
 'shared/app':'shared application controllers, settings, categories and presentation state',
 'shared/config':'shared settings schema and configuration persistence',
 'shared/resources':'shared localization and application icons',
 'shared/compose-utils':'reusable Compose rendering and interaction controls',
 'shared/utils':'platform/common utilities used by the download and application layers',
 'shared/updater':'platform update discovery, replacement and updater resources',
 'shared/auto-start':'OS-specific application startup registration',
 'buildSrc':'Gradle build conventions and shared build declarations',
 'compositeBuilds/plugins':'included Gradle plugins for versioning, installers and Android conventions',
 'compositeBuilds/shared':'included build platform/architecture abstractions',
 'gradle':'pinned wrapper and dependency/version catalogue',
 'assets':'upstream branding, application screenshots and documentation illustrations',
 'scripts':'original platform install/uninstall utilities; review before execution',
}
browser_purposes={
 'backend':'desktop native/HTTP transport and response/error contracts',
 'linkgrabber':'browser download interception, deduplication and backend handoff',
 'media':'detected HLS/media models, parsing and quality selection',
 'manifest':'browser-specific manifests, package metadata and permissions',
 'optionsui':'browser preferences and native-host/permission diagnostics UI',
 'contextmenus':'explicit context-menu intake and link handoff',
 'contentscripts':'page selection, link collection and message handling',
 'message':'typed messages and cross-context request contracts',
 'entrypoint':'background, content-script, popup and options entrypoints',
 'browseractionpopup':'browser action popup state and presentation',
 'popup':'popup interaction support',
 'configs':'persisted extension preferences and validation',
 'interfaces':'shared browser job/options/media interface definitions',
 'utils':'browser platform, validation, collection and logging helpers',
 'components':'reusable browser UI controls',
 'base':'shared controller/observable/event abstractions',
 'background':'background entry lifecycle and service providers',
 'assets':'extension styling and bundled UI assets',
}

def context(path):
 if path.startswith('apps/download-manager/'):
  sub=path[len('apps/download-manager/'):]
  for key,value in sorted(module_purposes.items(),key=lambda x:-len(x[0])):
   if sub==key or sub.startswith(key+'/'):return value
  return 'download-manager project metadata, build or contributor support'
 if path.startswith('apps/browser-extension/'):
  sub=path[len('apps/browser-extension/'):]
  if sub.startswith('src/'):
   return browser_purposes.get(sub.split('/')[1],'browser companion source/types')
  if sub.startswith('tests/'):return 'browser declaration, manifest and native-protocol regression checks'
  if sub.startswith('scripts/'):return 'strict declaration compatibility preparation for frozen browser dependencies'
  if sub.startswith('public/'):return 'extension icons and locale assets referenced by its manifests'
  return 'browser package configuration, dependencies or contributor support'
 return ''

special={
 'DownloadManager.kt':'Main transfer coordinator: boot jobs, manage lifecycle and expose controls.',
 'HttpDownloadJob.kt':'HTTP download job lifecycle, destination setup, parts and recovery decisions.',
 'HttpDownloader.kt':'HTTP job construction and adapter between credentials/items and transfer jobs.',
 'OkHttpHttpDownloaderClient.kt':'Actual OkHttp requests, range/header/proxy handling and response streams.',
 'HttpResponseInfo.kt':'Response status, length/range, resume/auth flags and filename metadata.',
 'DefaultAppSettings.kt':'Application defaults, including current API enable/auth defaults needing review.',
 'HttpClientIntegrationTest.kt':'11 real loopback HTTP-client integration tests; not full job lifecycle coverage.',
 'Backend.ts':'Select and initialize the existing native/HTTP browser-to-desktop backend.',
 'BackendProvider.ts':'Orphan imports-only backend stub; preserved outside active browser source.',
 'NativeMessagingProtocol.ts':'Validate native message envelopes, IDs, replies and error payloads.',
 'NativeMessagingTransport.ts':'Native-host request/reply transport, pending requests and connectivity.',
 'DownloadLinkInterceptor.ts':'Capture browser downloads, forward metadata and coordinate fallback behavior.',
 'Config.ts':'Validate/store extension preferences, including header-forwarding choices.',
 'Commands.ts':'Typed ProtocolMap command IDs, request payloads and reply contracts for webext-bridge.',
 'prepare-types.mjs':'Apply exact hash/version-guarded declaration fixes without altering runtime JS.',
 'declaration-compatibility.test.mjs':'Guard idempotency and rejection of altered/unreviewed declarations.',
 'manifest.test.mjs':'Manifest variant, metadata and source-asset regression checks.',
 'native-protocol.test.mjs':'Seven runtime wire-envelope, ID and typed-error regressions.',
 'messaging.test.ts':'Positive/negative compile-time command, payload and response assertions.',
 'gradle-wrapper.jar':'Official Gradle 9.8 bootstrap; supplied older bytes preserved separately.',
 'gradle-wrapper.properties':'Gradle distribution location and published SHA-256 verification pin.',
 'libs.versions.toml':'Pinned Kotlin/Compose/Android libraries and dependency coordinates.',
 'settings.gradle.kts':'Declare this Gradle build and relative module/composite-build relationships.',
 'vite.config.ts':'Vite entry/build configuration, browser target and source alias setup.',
}

def purpose(path, historical=False):
 name=Path(path).name;parts=Path(path).parts
 if path in root_purposes:return root_purposes[path]
 if path.startswith('AnalyseFuture/handoff-originals/'):
  return 'Exact navigation/instruction version before handoff update; historical provenance, not current policy.'
 if path.startswith('AnalyseFuture/validation-originals/'):
  inner='/'.join(parts[3:]);return 'Pre-validation original of '+plain(Path(inner).stem)+'; preserve bytes, not runtime.'
 if path.startswith('AnalyseFuture/historical-implementations/'):
  return 'Pre-migration original of '+plain(Path(path).stem)+'; retained for provenance, not runtime.'
 if path.startswith('AnalyseFuture/prior-versions/'):
  return 'Earlier exact '+plain(Path(path).stem)+' version; historical preservation copy.'
 if path.startswith('AnalyseFuture/incomplete-features/'):
  return 'Unreferenced imports-only browser backend stub; active Backend.ts owns dispatch.'
 if path.startswith('AnalyseFuture/validation-results/'):
  if name=='summary.json':return 'Structured observed validation results and remaining blocked/unrun scopes.'
  if 'audit-runtime' in name:return 'Observed browser production dependency-advisory audit result.'
  if name=='ui-blocker.json':return 'Administrator-policy refusal of unpacked extension loading; not a source test failure.'
  if 'checksum' in name or name.endswith('.sha256'):return 'Published toolchain artifact checksum receipt used during verification.'
  if name.endswith('.log'):return 'Recorded '+plain(Path(name).stem)+' output; preserves actual diagnostics.'
  if name.endswith('.py'):return 'Recorded '+plain(Path(name).stem)+' validation harness; explicit execution only.'
  return 'Recorded '+plain(Path(name).stem)+' command, outcome or toolchain evidence.'
 if path.startswith('AnalyseFuture/security-reports/'):
  return 'Earlier browser build/typecheck observation; not current installed-app validation.'
 if path.startswith('AnalyseFuture/migration-records/scripts/'):
  return 'One-off '+plain(Path(name).stem)+' migration provenance; do not rerun on current tree.'
 if path.startswith('AnalyseFuture/migration-records/'):
  return 'Exact original/active/retained file identities, hashes and Git object evidence.'
 if path.startswith('AnalyseFuture/repository-inventory/'):
  inventory_roles={
   'baseline-file-analysis.json':'All baseline paths with content roles, declarations, imports and hashes.',
   'dependency-relationships.json':'Static internal import/declaration relationships and their stated limitations.',
   'feature-records.json':'Machine-readable source capability and planned-product backlog records.',
   'final-file-catalogue.json':'Tracked-path catalogue captured at the completed restructuring checkpoint.',
   'recovery-summary.json':'Counts and completion scope of the structural recovery checkpoint.',
   'LOCAL_GENERATED_FILE_INVENTORY.txt':'Paths/provenance of ignored dependencies and caches; their bodies are not published.',
   'DEPENDENCY_MAP.txt':'Component responsibilities and observed import/dependency references.',
   'static-link-observations.json':'Relative documentation-target observations from the structural review.'}
  return inventory_roles.get(name,'Machine-readable recovery inventory and scope evidence.')
 if path.startswith('AnalyseFuture/recovery-notes/'):
  if name=='LATEST_SCOPE.txt':return 'Earlier structure-only user scope; later validation/handoff requests supersede it.'
  if name=='USER_RECOVERY_REQUEST.md':return 'Preserved owner master recovery request; later scope changes take precedence.'
  return 'Prior recovery audit and continuity evidence, not current setup policy.'
 if path.startswith('AnalyseFuture/') and len(parts)==2:return report_roles.get(name,'Recovery/future documentation; excluded from application runtime.')
 if '/.github/workflows/' in path:return 'Nested upstream '+plain(Path(name).stem)+' workflow template; inactive at repository root.'
 if '/.github/' in path:return 'Upstream contributor/funding/issue metadata, kept with its original component.'
 if name.upper().startswith('LICENSE') or name.upper().startswith('NOTICE'):
  return 'Component license/attribution obligations; preserve with source and distribution.'
 if name=='AGENTS.md':return 'Component contributor instructions; latest owner scope and root agreement take precedence.'
 if path.startswith('AnalyseFuture/reference-projects/mediagrabber/'):
  if name=='README.md':return 'Reference MediaGrabber overview/source-build instructions; claims need separate validation.'
  if name=='.gitignore':return 'Reference dependency/media/build-output ignore policy; scoped to this component.'
  ref={
   'downloads.ts':'Reference Node transfer worker; TLS/header/truncation risks remain unresolved.',
   'dash-parser.ts':'Reference DASH variants/duration parser; single-quoted XML regression fixed/tested.',
   'm3u8-parser.ts':'Reference HLS variant/audio/subtitle parsing; isolated parser tests exist.',
   'mse-inject.ts':'Reference main-world MediaSource hook; not enabled in active browser app.',
   'converter.ts':'Reference FFmpeg/probe RPC handlers; synthetic conversion smoke evidence exists.',
   'ytdlp.ts':'Reference yt-dlp process/format wrapper; no live platform support claim.',
   'rpc.ts':'Reference bidirectional weh#rpc dispatcher; not the active AB bridge.',
   'native-autoinstall.ts':'Reference OS native-host registration helpers; not executed in validation.',
   'installer.ts':'Reference native installation entrypoint; requires a separate safe distribution review.',
   'paths.ts':'Reference user-local installation and media-tool lookup paths.',
   'native-messaging.ts':'Reference length-prefixed native-host stream transport.',
  }
  if name in ref:return ref[name]
  if '/docs/' in path:return 'Reference '+plain(Path(name).stem)+' research, usage or release documentation.'
  if '/src/' in path:return 'Reference '+plain(Path(name).stem)+' media/companion implementation; not production.'
  if name=='package.json':return 'Reference package/workspace dependencies and explicit build/package commands.'
  if name=='package-lock.json':return 'Frozen dependency graph for isolated reference builds.'
  return 'Reference '+plain(Path(name).stem)+' asset, platform packaging or configuration.'
 if path.startswith('AnalyseFuture/reference-projects/reclip/'):
  if name=='README.md':return 'Reference ReClip overview/setup/use guidance, not production hosting approval.'
  if name in {'.gitignore','.dockerignore'}:return 'Reference Git/container context exclusions; do not infer production isolation.'
  if name=='app.py':return 'Reference Flask info/playlist/jobs/file APIs; input-shape fix tested, hosting risks remain.'
  if name=='index.html':return 'Reference browser link/format/batch UI calling the Flask APIs.'
  if name=='requirements.txt':return 'Reference Flask/yt-dlp requirements; current file is not a frozen production lock.'
  if name in {'Dockerfile','docker-compose.yml','docker-entrypoint.sh','reclip.sh'}:return 'Reference local/container launch configuration; not an active hosted deployment.'
  if '/assets/' in path:return 'Reference UI screenshot/demo media; documentation asset, not user media.'
  return 'Reference '+plain(Path(name).stem)+' documentation, static asset or packaging metadata.'
 if path.startswith('docs/project/'):
  if '/context-archive/' in path:return 'Historical '+plain(Path(name).stem)+' continuity/source snapshot; not live implementation.'
  doc_roles={
   'FEATURE_MATRIX.md':'Original product backlog/acceptance criteria; candidates are not completion evidence.',
   'DECISIONS.md':'Original architecture/owner decisions; proposed choices remain subject to approval.',
   'M0_AUDIT.md':'Dated source/build/security research; current results are in VALIDATION_REPORT.',
   'REUSE_DECISION_MATRIX.md':'Prior 17-project source/license/reuse comparison and exact historical pins.',
   'ARCHITECTURE.md':'Proposed component/job/bridge design, not verified integration.',
   'ROADMAP.md':'Original M0–M6 milestone gates; current actionable work is in PROJECT_HANDOFF.',
   'LEGAL_SECURITY.md':'Source permission, licensing, privacy and platform trust requirements.',
   'IMPLEMENTATION_CHECKLIST.md':'Original ordered engineering/governance backlog and historical check states.',
   'DEVELOPMENT_SETUP.md':'Original setup/integration guidance; paths were repaired, current results are separate.',
  }
  if name in doc_roles:return doc_roles[name]
  body=text(path);head=re.search(r'^#+\s+(.+)',body,re.M)
  return ('Project '+head.group(1).strip().replace('**','') if head else 'Original project '+plain(Path(name).stem)+' guidance')+'.'
 if name in special:return special[name]
 if name=='package.json':return 'Browser dependency declarations, strict checks, tests and scoped package commands.'
 if name=='package-lock.json':return 'Frozen browser dependency graph, including current reviewed runtime fixes.'
 if name.startswith('tsconfig'):return 'TypeScript '+plain(Path(name).stem)+' compiler scope/options; strict checks retained.'
 if name=='build.gradle.kts':return 'Gradle dependencies, tasks and conventions for '+context(path).split(',')[0]+'.'
 if '/res/' in path or '/composeResources/' in path or '/resources/' in path:
  if '/values' in path and name.endswith('.xml'):return 'Localized strings/theme values for '+plain(Path(path).parent.name)+' in its UI consumer.'
  if '/mipmap-' in path:return 'Android launcher image for '+Path(path).parent.name+'; density-specific, not removable duplication.'
  if 'icons' in parts or '/drawable' in path:return 'UI icon/vector resource for '+plain(Path(name).stem)+' in this component.'
  if 'installer' in parts:return 'Desktop installer '+plain(Path(name).stem)+' resource; keep packaging-relative location.'
  return 'Consumer-owned '+plain(Path(name).stem)+' resource for '+context(path).split(',')[0]+'.'
 if '/assets/' in path or '/public/' in path or '/icons/' in path:
  if '/_locales/' in path:return 'Extension localized messages for '+Path(path).parent.name+'.'
  return 'Consumer-owned '+plain(Path(name).stem)+' branding, screenshot, style or icon asset.'
 if path.startswith('archives/'):
  return 'Unchanged supplied '+plain(Path(name).stem)+' source archive; extraction/provenance indexed.'
 content=text(path)
 if path.endswith(('.kt','.ts','.tsx','.py','.mjs','.cjs','.js')):
  # Declarations supplement package ownership; this is static evidence, not a behavioral proof.
  found=re.findall(r'\b(?:class|interface|object|function|fun|def)\s+([A-Za-z_$][\w$]*)',content)
  found=[v for v in found if v not in {'that','for','to','from','with','or','is'}]
  label=plain(found[0] if found else Path(name).stem)
  ctx=context(path)
  if '/pages/' in path:
   page=Path(path).parts[Path(path).parts.index('pages')+1]
   return label+' for '+plain(page)+' page/controller behavior; '+('Android' if '/android/' in path else 'desktop' if '/desktop/' in path else 'shared')+' consumer.'
  return label+' — '+(ctx or 'component implementation and its declared consumers')+'.'
 if name in {'gradlew','gradlew.bat'}:return 'Platform Gradle launcher for the pinned/verified wrapper; keep project-relative path.'
 if name in {'.gitattributes','.gitignore','.npmrc'}:return 'Component Git/line-ending/package-manager policy; preserve scope and do not expose credentials.'
 if name.endswith(('.sh','.ps1','.bat')):return 'Platform '+plain(Path(name).stem)+' launcher/install/update helper; review before use.'
 if name in {'CHANGELOG.md','CONTRIBUTING.md','README.md','VALIDATION.md'}:
  return ('Current package validation commands and declaration-compatibility design.' if name=='VALIDATION.md' else context(path).split(',')[0]+' '+plain(Path(name).stem)+' guidance.')
 if name.endswith(('.md','.txt','.rtf')):
  heading=re.search(r'^#+\s+(.+)',content,re.M)
  return ('Component '+heading.group(1).replace('**','') if heading else 'Component '+plain(Path(name).stem)+' documentation')+'.'
 return plain(Path(name).stem)+' configuration/data for '+(context(path) or 'its recorded component owner')+'.'

# Directory-specific descriptions reflect source sets, consumers and feature context.
def folder_purpose(folder):
 if folder.startswith('AnalyseFuture/handoff-originals'):return 'Exact previous navigation/instructions retained before the handoff update; not current policy.'
 if folder=='.':return 'Current project navigation, owner instructions, application collections and recovery boundary.'
 if folder=='apps':return 'Primary implementation candidates; each application retains its own supported build root.'
 if folder=='apps/download-manager':return 'One Gradle multi-project containing desktop, Android, shared app and transfer engine.'
 if folder=='apps/browser-extension':return 'One npm/Vite browser companion; all manifests/assets/aliases stay relative to this package.'
 if folder=='AnalyseFuture':return 'Current recovery/future records and non-active preserved material; never a production workspace.'
 if folder.startswith('AnalyseFuture/historical-implementations'):return 'Exact pre-migration originals, grouped by checkpoint and former path; not runtime inputs.'
 if folder.startswith('AnalyseFuture/validation-originals'):return 'Exact pre-validation originals, grouped by checkpoint and former owner path.'
 if folder.startswith('AnalyseFuture/prior-versions'):return 'Earlier exact preserved revisions; use current handoff for live instructions.'
 if folder.startswith('AnalyseFuture/validation-results'):return 'Dated observed commands/results/logs; scoped evidence, not source or complete readiness.'
 if folder.startswith('AnalyseFuture/repository-inventory'):return 'Per-file/dependency/feature catalogues and explicit scope/coverage metadata.'
 if folder.startswith('AnalyseFuture/migration-records/scripts'):return 'One-off migration provenance scripts; frozen input layout, not a reusable production tool.'
 if folder.startswith('AnalyseFuture/migration-records'):return 'Original/active/retained identities, source hashes, Git objects and migration provenance.'
 if folder.startswith('AnalyseFuture/security-reports'):return 'Preserved security/build/type observations with their historical run boundaries.'
 if folder.startswith('AnalyseFuture/recovery-notes'):return 'Original requests and earlier audits; later owner directions take precedence.'
 if folder.startswith('AnalyseFuture/incomplete-features'):return 'Unreferenced/incomplete source retained with reasons; excluded from active compilation.'
 if folder=='AnalyseFuture/reference-projects':return 'Alternative implementations for selected evaluation; never recursively included in production.'
 if '/reference-projects/mediagrabber' in folder:
  if '/coapp' in folder:return 'Reference Node/native RPC, media workers and platform registration/packaging.'
  if '/extension/src/lib' in folder:return 'Reference manifest parsers, quality models and native-client utilities.'
  if '/extension' in folder:return 'Reference browser discovery/UI/assets; selected isolated checks only.'
  if '/installer' in folder:return 'Reference OS release-installation material; not executed or approved by unit checks.'
  return 'MediaGrabber reference code, research or release assets; separate protocol from AB.'
 if '/reference-projects/reclip' in folder:
  if folder.endswith('/templates'):return 'Reference HTML/JS UI templates calling the Flask routes.'
  if folder.endswith('/static'):return 'Reference web UI static assets.'
  if folder.endswith('/assets'):return 'Reference screenshots/demo media for documentation.'
  return 'Flask/yt-dlp reference UX/server; hosting/security gaps remain.'
 if folder=='docs':return 'Product/repository documentation, separated from runnable fixtures and applications.'
 if folder=='docs/repository':return 'Current complete per-file and per-folder ownership guides.'
 if folder.startswith('docs/project/docs/context-archive'):return 'Dated historical continuity and source snapshots; not a competing active application.'
 if folder.startswith('docs/project'):return 'Original product research, decisions and backlog; current status is in root handoff.'
 if folder=='archives':return 'Immutable source ZIPs and exact member-retention index; do not extract over edits.'
 if folder.startswith('tests/fixtures'):return 'Original synthetic fixture regressions; real TLS verification with temporary certificates.'
 if folder.startswith('tests/references'):return 'Isolated/mock reference regressions; no production inclusion or live source access.'
 if folder=='tests':return 'Repository-level fixture/reference checks; app-owned suites stay with their framework.'
 if folder.startswith('tools/fixtures'):return 'Original synthetic HTTP/HTTPS target imported as tools.fixtures.'
 if folder.startswith('tools/development'):return 'Explicit local setup/build entrypoints and required writable-cache selection.'
 if folder.startswith('tools/repository'):return 'Preservation verification and generated ownership documentation; not application runtime or a safety certificate.'
 if folder=='tools':return 'Repository development/preservation tools and synthetic download fixture namespace.'
 if '/.github/workflows' in folder:return 'Nested upstream workflow templates; inactive because not at repository root.'
 if '/.github' in folder:return 'Original component contributor/workflow metadata, not new root automation.'
 if 'mipmap-' in folder:return 'Android density-specific launcher resources required by that device/resource qualifier.'
 if '/values' in folder:return 'Localized or theme/value resources for '+Path(folder).name+'; keep consumer/source set.'
 if '/drawable' in folder:return 'Android drawable/vector resources owned by this app/source set.'
 if '/src/' in folder:
  for source_set in ['commonMain','androidMain','desktopMain','desktopTest','main']:
   if folder.endswith('/src/'+source_set):return source_set+' framework source set for '+context(folder)+'.'
  if folder.endswith(('/kotlin','/java')):return 'Language/package source root required by this Gradle source set, not a global file bucket.'
  if folder.endswith(('/res','/resources','/composeResources')):return 'Source-set-owned resources consumed by this platform/application module.'
  if '/pages/' in folder:
   page=folder.split('/pages/',1)[1].split('/')[0]
   return plain(page)+' feature page/UI/controller subcollection within its platform consumer.'
  for key,description in [('connection/proxy','HTTP proxy strategies/providers'),('connection/response/headers','response header/range/filename parsing'),('connection','HTTP connection/request/response interfaces'),('downloaditem/http','HTTP job/credentials/item state'),('downloaditem/hls','HLS job/manifest/segment behavior'),('downloaditem','shared job/item contracts and state'),('/db','download, queue and part persistence'),('/queue','queue lifecycle/scheduling controls'),('/part','transfer-part splitting/state/worker logic'),('/destination','output destination and writer handling'),('/storage','application settings/bookmarks/state persistence'),('/theme','shared/platform appearance and theme definitions')]:
   if key in folder:return description+'; keep framework package/source-set relationships.'
  ctx=context(folder)
  if ctx:return 'Package/subfeature for '+ctx+'.'
 ctx=context(folder)
 if ctx:return ctx[0].upper()+ctx[1:]+'.'
 return 'Functional subcollection of '+str(Path(folder).parent)+'; ownership follows the surrounding component.'

# Generate grouped file rows: the section heading supplies the complete directory.
parents=defaultdict(list)
for p in paths:parents[str(Path(p).parent)].append(p)
lines=['# Complete file guide','',
 'Catalogue generated from the Git index plus the explicitly named handoff documents/utility in this delivery. Feature evidence remains the dated validation report; a catalogue refresh does not rerun tests.',
 '',f'**Coverage:** {len(paths):,} project paths. Every current tracked path appears exactly once below. The scope excludes `.git` internals and ignored dependency/build bodies; those are recorded separately in [the local generated-file inventory](../../AnalyseFuture/repository-inventory/LOCAL_GENERATED_FILE_INVENTORY.txt).',
 '', 'This describes responsibility, not a claim that each feature runs. Read [the root handoff](../../PROJECT_HANDOFF.md), [folder guide](FOLDER_GUIDE.md), and [current validation report](../../AnalyseFuture/VALIDATION_REPORT.txt) for status and tasks. Primary app source is under `apps`; `AnalyseFuture` originals/references are excluded from production execution. Binary assets are identified by their consumer/metadata rather than asserted decoded or tested.',
 '', 'The dependency evidence is in [the static relationship map](../../AnalyseFuture/repository-inventory/dependency-relationships.json). Imported/declaration relationships do not prove runtime call behavior. Historical originals retain their former role but are not current setup instructions.','']
for parent,items in sorted(parents.items()):
 lines+=['## '+escaped(parent),'','| File | Responsibility |','| --- | --- |']
 for p in items:
  description=purpose(p)
  # Keep the complete catalogue within GitHub rendering limits without clipping identity.
  if len(description)>122:description=description[:119].rstrip(' ,;:')+'…'
  lines.append('| '+link(p)+' | '+escaped(description)+' |')
 lines.append('')
file_text='\n'.join(lines).rstrip()+'\n';(OUT/'FILE_GUIDE.md').write_text(file_text)

folders={'.'}
for p in paths:
 current=Path(p).parent
 while str(current)!='.':folders.add(str(current));current=current.parent
folder_lines=['# Complete folder guide','',
 f'**Coverage:** {len(folders):,} tracked/proposed project folders, including the repository root. A folder is included when it owns a catalogued path or is one of its ancestors. This does not flatten Java/Kotlin packages or move required framework resources.',
 '', 'Use [the root handoff](../../PROJECT_HANDOFF.md) for task order and implementation status, and [the file guide](FILE_GUIDE.md) for every individual path. Ignored package caches/generated files are local state rather than product source.',
 '', '“Primary” means the selected implementation collection, not a verified integrated release. MediaGrabber/ReClip remain non-active references. Historical source/checkpoint folders preserve exact originals, not competing implementations to build recursively.',
 '', '| Folder | Functional responsibility |','| --- | --- |']
for folder in sorted(folders):
 target='.' if folder=='.' else folder+'/'
 description=folder_purpose(folder)
 if len(description)>150:description=description[:147].rstrip(' ,;:')+'…'
 folder_lines.append('| '+link(target,folder+'/')+' | '+escaped(description)+' |')
(OUT/'FOLDER_GUIDE.md').write_text('\n'.join(folder_lines)+'\n')

print(json.dumps({'tracked_start':len(tracked),'catalogued_paths':len(paths),'folders':len(folders),'file_guide_bytes':(OUT/'FILE_GUIDE.md').stat().st_size,'folder_guide_bytes':(OUT/'FOLDER_GUIDE.md').stat().st_size,'prospective_paths':sorted(prospective)},indent=2))
assert (OUT/'FILE_GUIDE.md').stat().st_size<512*1024
assert all(p in paths for p in tracked)
# All own links target existing paths, except the handoff concurrently owned by parent.
missing=[]
for guide in [OUT/'FILE_GUIDE.md',OUT/'FOLDER_GUIDE.md']:
 from urllib.parse import unquote
 for target in re.findall(r'\]\(([^)]+)\)',guide.read_text()):
  resolved=(guide.parent/unquote(target)).resolve()
  if not resolved.exists() and resolved!=R/'PROJECT_HANDOFF.md':missing.append(str(resolved))
assert not missing,missing
