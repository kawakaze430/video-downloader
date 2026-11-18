from collections import Counter,defaultdict
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

R=Path('/workspace/video-downloader');W=Path('/workspace/recovery-work');A=R/'AnalyseFuture'
D=json.loads((W/'discovery.json').read_text());M=json.loads((W/'migration-state.json').read_text())
P=json.loads((A/'migration-records/preservation-manifest.json').read_text())
files=D['files'];active=M['active'];mapping=M['mapping'];base=D['baseline_commit']

def write(name,text):
 p=A/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n')

def mapped(path):return active.get(path,path)

features=[]
def feature(key,name,needles,dependency,gap,reference=False):
 evidence=[mapped(f['path']) for f in files if any(n.lower() in f['path'].lower() for n in needles)]
 features.append({'id':key,'name':name,'status':'reference implementation; not active product' if reference else 'source implementation present; runtime unverified in this pass',
 'files':sorted(set(evidence)),'dependencies':dependency,'missing':gap,
 'tests':'fixture regression source exists; not run in this pass' if key in {'C35','C36','C37'} else 'no feature-specific execution evidence collected in this no-test pass',
 'location':evidence[0] if evidence else 'see complete per-file inventory'})

specs=[
('C01','HTTP transfer lifecycle',['HttpDownloadJob.kt','HttpDownloader.kt','HttpDownloadItem.kt'],'OkHttp, Okio, Kotlin coroutines','No post-move runtime or output-integrity result.'),
('C02','Range parts and segmentation',['RangedPart.kt','HttpPartDownloader.kt','SplitToRange.kt'],'downloader/core connection and part layers','Server behavior and restart/resume need later validation.'),
('C03','Queues and schedule state',['/queue/'],'download manager, coroutines, queue persistence','Do not claim scheduling correctness without later execution.'),
('C04','Download/part persistence',['/downloader/core/','TransactionalFileSaver'],'Kotlin serialization, file storage','Runtime restart recovery not exercised.'),
('C05','Bandwidth throttling',['speedlimiter','SpeedLimiter'],'Okio throttler','No throughput benchmark or guaranteed speedup.'),
('C06','Proxy selection',['/connection/proxy/','/utils/proxy/'],'platform proxy provider, HTTP client','Credentials/configuration and platform behavior require review.'),
('C07','HLS jobs and segments',['/downloaditem/hls/','MediaSegment.kt'],'manifest parsing, downloader parts','Non-DRM fixture and track handling not exercised.'),
('C08','Progress observation',['/downloader/monitor/'],'core job state and flow observers','Accuracy/ETA not measured.'),
('C09','Checksum inspection UI',['/pages/checksum/'],'platform/shared application and hashing utilities','End-to-end expected-hash gating not established.'),
('C10','Categories and file organization',['/pages/category/','/category/'],'shared application and platform UI','No runtime persistence/usability result.'),
('C11','Per-host settings',['perhostsettings'],'shared configuration and platform pages','Policy/precedence behavior not executed.'),
('C12','Application settings UI',['/pages/settings/'],'Compose and shared settings','Platform-specific settings not exercised.'),
('C13','Batch link intake',['batchdownload'],'shared application and platform pages','No live source permission or deduplication guarantee.'),
('C14','Android in-app browser',['android/app/','/pages/browser/'],'Android WebView/activity and app services','Source declarations do not establish Android release readiness.'),
('C15','Android background download integration',['DownloadService','AndroidManifest.xml'],'Android service, storage and notification APIs','Broad permissions and background/storage rules require review.'),
('C16','Android QR intake',['/pages/qrcode/'],'Android camera/scanner','Device and permission behavior not executed.'),
('C17','Desktop native bridge and integration',['NativeHost','NativeMessaging','IntegrationUtil.kt'],'platform host and integration server','No paired browser-to-desktop demonstration.'),
('C18','Local HTTP integration',['/integration/server/'],'Ktor auth/routing, shared callbacks','Review default optional authentication and job-creating endpoints.'),
('C19','Updater and update UI',['/shared/updater/','/pages/updater/'],'platform installer/updater and release metadata','Do not run original installers; trust/provenance/signing unresolved.'),
('C20','Start with OS',['/shared/auto-start/'],'platform startup registration','No install/uninstall or OS policy tests.'),
('C21','Localized resources',['/shared/resources/','public/_locales/'],'generated resource access and UI consumers','Translations/assets preserved; accessibility not verified.'),
('C22','Platform UI and shared controls',['/shared/compose-utils/','/desktop/mac_utils/'],'Compose and platform-specific adapters','No device/window rendering result.'),
('C23','Browser native transport',['/backend/nativemessaging/','NativeMessagingApi.ts'],'browser nativeMessaging, zod, bridge schema','Pairing, typecheck and negative-origin validation remain.'),
('C24','Browser HTTP fallback',['/backend/HttpApi.ts','/backend/Backend.ts'],'browser config, local HTTP server','Fallback availability and credentials not executed.'),
('C25','Browser download interception',['/linkgrabber/'],'webRequest/downloads APIs, backend','Header/cookie forwarding and fallback cancellation need review.'),
('C26','Browser context menu and selection',['/contextmenus/','/contentscripts/'],'browser messaging and backend','Explicit user intent/host permission behavior untested.'),
('C27','Browser media/quality parsing',['/ab-browser-integration/src/media/'],'HLS parser and React views','No generalized site or DRM support implied.'),
('C28','Browser popup and preferences',['/optionsui/','/browseractionpopup/','/popup/'],'React, MobX, browser storage','Existing type errors and permission concerns remain.'),
('C29','Reference DASH/HLS parsers',['mediagrabber/extension/src/lib/dash','mediagrabber/extension/src/lib/m3u8'],'TypeScript manifest parsers','Review algorithms before selective adaptation; not compatible by filename alone.'),
('C30','Reference MSE capture hook',['mediagrabber/extension/src/mse','mediagrabber/extension/src/content'],'browser main/isolated world messaging','Broad host access and segment lifetime; no production inclusion.'),
('C31','Reference media conversion RPC',['mediagrabber/coapp/src/converter','mediagrabber/coapp/src/rpc','mediagrabber/coapp/src/downloads'],'Node, FFmpeg/ffprobe, length-prefixed weh#rpc','Protocol differs from AB; TLS bypass/truncation handling requires remediation.'),
('C32','Reference source connector wrapper',['mediagrabber/coapp/src/ytdlp'],'yt-dlp binary and Node child process','No permission/site support guarantee; binary/licensing review needed.'),
('C33','Reference web jobs and download API',['reclip/app.py'],'Flask, yt-dlp, FFmpeg, in-memory dictionary/threads','Unauthenticated/unbounded service and SSRF/argument-validation concerns.'),
('C34','Reference simple web intake UI',['reclip/templates/index.html'],'HTML/JS fetch calls to Flask','Do not connect to a public hosted service without a new security design.'),
('C35','Synthetic HTTP Range/redirect/drop fixture',['tools/fixtures/http_fixture.py'],'Python standard library','Not a downloader; client integration still absent.'),
('C36','Fixture verified-TLS support',['tools/fixtures/http_fixture.py','tests/test_http_fixture.py'],'Python ssl and caller-supplied certificate; OpenSSL for regression source','No tests run after move.'),
('C37','Fixture regression source',['tests/test_http_fixture.py'],'Python unittest and OpenSSL','14 test methods preserved; not executed in current scope.'),
('C38','Preservation and repository setup tooling',['tools/verify_repository.py','tools/onboarding/setup.sh'],'Python/Git/OpenSSL, baseline object history','Helpers repaired statically; no helper or test-suite execution in this pass.'),
]
for key,name,needles,deps,gap in specs:feature(key,name,needles,deps,gap,key in {'C29','C30','C31','C32','C33','C34'})
matrix=(R/'docs/project/docs/FEATURE_MATRIX.md').read_text()
for line in matrix.splitlines():
 match=re.match(r'\|\s*((?:D|B|M|W|P)\d{2})\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|',line)
 if match:
  key,name,priority,candidate,acceptance=map(str.strip,match.groups())
  features.append({'id':key,'name':name,'status':'product backlog; not an integrated implementation claim',
   'files':['docs/project/docs/FEATURE_MATRIX.md'],'dependencies':candidate,
   'tests':'proposed acceptance only: '+acceptance,'missing':'Must link source evidence and authorized runtime results before promotion to working product.',
   'location':'existing feature owner documented in PROJECT_STRUCTURE.md','priority':priority})
(A/'repository-inventory/feature-records.json').write_text(json.dumps(features,indent=2)+'\n')

overview=f'''COMPLETE REPOSITORY AUDIT — STRUCTURE-ONLY PASS
Repository: https://github.com/kawakaze430/video-downloader
Starting commit: {base}
Default/delivery branch: main
Remote backup tag: recovery-baseline-2026-11-17-7a7e2f6

SCOPE AND COVERAGE
All {D['count']} starting tracked paths were inventoried; {D['text_count']} text files
were read in full by static content/import/symbol analysis. {D['binary_count']} binary
files were read as bytes; archives/member metadata and relevant headers were
classified. Images/video were not decoded and the Gradle JAR was not executed.
Complete semantic runtime correctness cannot be inferred from this inspection.
No paths were skipped. Files containing repeated historical source/document
archives are identified as historical text, not counted as new live services.

The prior account-compromise report remains unconfirmed in the accessible tree.
Advertised origin heads/tags and accessible history were fetched; main matched
the known starting checkpoint. Existing local work ref was preserved. No refs
were deleted, no published commits rewritten, and no force-push was used.
GitHub REST/protection inspection was unavailable; a server-accepted ordinary
main push and backup-tag push demonstrate only those specific permissions.

ARCHITECTURE DECISION
Keep the Kotlin Gradle multi-project together under apps/download-manager and
the matching npm/Vite extension together under apps/browser-extension. Their
internal source/resource/module conventions carry actual dependency meaning.
Collect the original fixture under root tools/fixtures and tests/fixtures.
Move its project research to docs/project. Keep original ZIPs in archives.
Retain MediaGrabber/ReClip as non-active reference implementations and preserve
the orphan imports-only browser backend stub, originals and reports under
AnalyseFuture. The canonical future vision is a detailed plain-text file there.

IMPLEMENTED CHANGES
{M['moved_count']} baseline files moved to a different functional location.
{M['fixture_files_grouped']} fixture/package/test/document files regrouped as one fixture responsibility.
{M['newly_archived_count']} files newly retained as pre-edit originals or the orphan backend stub.
No source transfer algorithm was rewritten, no external bridge protocols were
merged, no runtime API/database schema was changed, and no new AI feature was
invented. Compatible organization and references were consolidated; incompatible
implementations were retained with reasons rather than forced together.

Reference repairs include Markdown identity-based links, fixture discovery
instructions, helper repository roots, preservation/index paths and per-member
source archive overrides. The browser source-pack command now scopes Git archive
to its own app tree, so source packages do not include AnalyseFuture or ZIPs.

VALIDATION BOUNDARY
The latest owner request explicitly says do not run tests. No test suites,
builds, typecheck commands, dependency installs, app startup or CI activation
were performed after that instruction. Static path/import/content preservation
review is part of organizing files, not evidence of runtime behavior.
See TEST_AND_VALIDATION_REPORT.txt for earlier available observations and gaps.
'''
write('REPOSITORY_AUDIT.txt',overview)

lines=['COMPLETE STARTING FILE INVENTORY','Baseline: '+base,
 'Each entry identifies actual component responsibility, symbols, dependencies, active location and exact retained original.',
 'Runtime status for source: unexecuted in this structure-only pass. Binary interpretation is limited to bytes/header/container inspection.','']
for f in files:
 lines += [f['path'], '  Active location: '+active[f['path']], '  Exact original: '+mapping[f['path']],
  '  Owner: '+f['component']+' | '+f['purpose'],
  '  Content: '+f['kind']+f" | {f['bytes']} bytes | mode {f['git_mode']} | SHA256 {f['sha256']}",
  '  Symbols: '+(', '.join(f['symbols']) or '(no code declarations; asset/config/doc ownership above)'),
  '  Dependencies: '+(', '.join(f['dependencies']) or '(no explicit imports/package dependencies; consumer/module ownership above)'),
  '  Review: '+f['review'],'']
write('COMPLETE_FILE_INVENTORY.txt','\n'.join(lines))

lines=[f'FEATURE INVENTORY — {len(features)} DISCOVERY RECORDS',
 '38 code/tool/fixture capability groups plus 49 earlier product backlog entries.',
 'These are cross-referenced records, not 87 verified or distinct shipping product features.',
 'Existing source is not proof of working integration. No tests were run in the structure-only pass.','']
for f in features:
 lines += [f["id"]+' — '+f['name'],'  Status: '+f['status'],'  Purpose/location: '+f['location'],
  '  Dependencies: '+f['dependencies'],'  Existing checks: '+f['tests'],
  '  Missing/decision: '+f['missing'],'  Related files ('+str(len(f['files']))+'):']
 lines += ['    '+p for p in f['files']]
 lines += ['']
write('FEATURE_INVENTORY.txt','\n'.join(lines))

lines=['DUPLICATE AND OVERLAP ANALYSIS','Exact byte duplicate groups in baseline: '+str(len(D['duplicates'])),
 'Hashes identify bytes, not interchangeable responsibilities. No identical file was deleted.','']
for i,group in enumerate(D['duplicates'],1):
 lines+=['Group '+str(i)]+['  '+mapped(p) for p in group]
 lines+=['  Decision: preserve each consumer/package location. Licenses, framework resources and repeated documentation have distinct ownership.','']
lines += ['SEMANTIC OVERLAPS',
 'Transfer engines: AB uses Kotlin jobs/queues/part persistence; MediaGrabber uses Node RPC/download workers; ReClip delegates to yt-dlp with in-memory jobs. Keep AB as the primary evaluation collection; do not merge worker code based on names.',
 'Browser bridges: AB native/HTTP dispatch and MediaGrabber weh#rpc have different envelope/state/host assumptions. No compatible shared runtime implementation was demonstrated; retain the latter as reference.',
 'Manifest parsing: AB HLS and MediaGrabber HLS/DASH overlap but have different models/callers. Preserve both and record comparative work, not an untested replacement.',
 'UI: Android/desktop pages share controllers where the Gradle project already does so; platform activities/windows/resources remain separate consumers.',
 'Fixture: code, tests and README moved together into an obvious root tool/test collection while retaining tools.fixtures imports.',
 'Orphan BackendProvider.ts: four imports, no declarations/exports or consumers; one import points to a nonexistent module. Archived intact; existing Backend.ts owns dispatch.',
 'Vision: move the existing detailed idea to one required canonical future-vision path. Earlier originals remain preservation records, not competing current specs.']
write('DUPLICATE_ANALYSIS.txt','\n'.join(lines))

write('SECURITY_AUDIT.txt','''SECURITY AUDIT — STATIC FINDINGS, NOT A MALWARE CERTIFICATE

Confirmed structural facts:
- No root workflow existed; five workflow snapshots were nested. No root CI/deployment was activated.
- No tracked symlinks, gitlinks/submodules or LFS pointers found in the reviewed baseline.
- 40 binaries are expected archives, branding/media assets and one Gradle wrapper JAR; they were not executed/decoded.
- Bounded private-key/GitHub PAT/AWS/Slack-token filename/content scans reported no matches. This does not guarantee absence of credentials.
- All supplied ZIP payloads had safe relative paths in earlier preservation review; archive bytes are retained.

Confirmed source concerns (review code before any deployment):
1. AB local integration permits optional authentication for some endpoints. Inspect apps/download-manager/integration/server/src/main/kotlin/com/abdownloadmanager/integration/Endpoints.kt and IntegrationConfig.kt. A loopback interface is not authorization.
2. Browser all-site/cookies permissions and sendHeaders default require minimization. Inspect apps/browser-extension/src/configs/Config.ts, manifest definitions and linkgrabber/DownloadLinkInterceptor.ts. Automatic capture can forward headers; source policy/consent and fallback behavior need a separate code task.
3. MediaGrabber reference coapp/src/downloads.ts permits rejectUnauthorized=false, accepts destination/header choices, forwards request headers across redirects and treats ECONNRESET after partial bytes as completion. These are adoption blockers; no TLS verification bypass was used in this task.
4. ReClip reference app.py exposes URL-to-yt-dlp subprocess endpoints and creates daemon threads per request with process-memory jobs, no authentication, bounded global queue or adequate SSRF policy. Docker publishes the service. URL arguments also need separator/schema review. Do not deploy it publicly as-is.
5. Original AB installer/updater scripts can replace application files and obtain release artifacts. They were read only, not executed. Gradle wrapper lacks a pinned distributionSha256Sum in the supplied configuration; no wrapper bootstrap was executed here.
6. The browser's original source-pack command archived the entire repository. It now targets HEAD:apps/browser-extension to avoid unintentionally packaging archives/history.

Suspicious/unconfirmed:
No available commit or file was established as attacker-added. The reported account compromise cannot be confirmed or dismissed from source inspection. No account sessions, security log, collaborator or secret settings were accessible through this task.

Exclusion controls:
No root npm workspace, wildcard app importer, Gradle settings or deployment context includes AnalyseFuture. A root .dockerignore excludes AnalyseFuture, archives, Git and generated dependencies. Reference scripts and nested Dockerfiles remain manually executable if deliberately invoked: preservation is not sandboxing. Do not call them from production configuration. No malicious sample requiring a new executable quarantine was identified.

Required owner/security follow-up:
Review GitHub security activity, collaborators, connected applications, keys, active sessions and exposed secrets; revoke unknown access and rotate any exposed credentials securely. Repo restructuring does not revoke account access. No history rewrite, branch-protection bypass or force-push was used.
''')

lines=['ORIGINAL -> ACTIVE -> EXACT RETAINED ORIGINAL','Starting commit: '+base,'']
for f in files:
 p=f['path'];lines += [p+' -> '+active[p], '  Original retained at: '+mapping[p]]
write('ORIGINAL_TO_NEW_PATH_MAPPING.txt','\n'.join(lines))

write('CONSOLIDATION_REPORT.txt',f'''CONSOLIDATION REPORT

Implemented functional grouping:
- One Kotlin application root, retaining all desktop/Android/shared/download modules and framework conventions.
- One matching browser app root, retaining source aliases, UI/assets and manifest/build relationships.
- {M['fixture_files_grouped']} original fixture files collected in root tools/tests; original imports retained.
- One current future vision path, one current recovery report set, original research clearly separated from executable code.
- One incomplete imports-only browser stub removed from active src and retained intact under incomplete-features. Existing Backend.ts remains the implementation.

Reference/config repairs:
Identity-based relative Markdown links updated after moves; source-pack scope narrowed; helper roots, source index and per-member preservation mappings repaired. No runtime API or database schema changed.

Not force-merged:
AB, MediaGrabber and ReClip transfer systems have incompatible state/protocol/trust boundaries. Combining them without running validation would risk lost recovery semantics or unsafe behavior. Latest scope forbids tests and focuses on categorization. Their unique code is preserved and related capabilities are linked by feature inventory rather than falsely advertised as integrated.

Counts:
Baseline files relocated: {M['moved_count']}.
Files collected as one fixture responsibility: {M['fixture_files_grouped']}.
Runtime algorithm files textually merged: 0.
New exact pre-edit originals: {len(M['changed_originals'])}; additional orphan archived: 1.
''')

lines=['ARCHIVED/PRESERVED MATERIAL MANIFEST','No file was classified malicious merely for being unfamiliar.','']
for item in P['files']:
 p=item['original_path'];dest=item['preserved_path']
 if dest.startswith('AnalyseFuture/'):
  lines += [dest,'  Original: '+p,'  Reason: '+item['reason'],'  Replacement/current owner: '+item['active_path'],'  SHA256: '+item['sha256'],'']
lines += ['Existing reference projects remain under reference-projects: MediaGrabber71files, ReClip14files; not part of default app entrypoints.',
 'Prior version copies, source ZIPs, request text and recovery records remain recoverable through paths and Git history.',
 'Generated node_modules/dist/__pycache__ files remain ignored local outputs; no dependency cache or user media was published.']
write('ARCHIVED_FILES_MANIFEST.txt','\n'.join(lines))

write('TECHNICAL_DEBT.txt','''TECHNICAL DEBT — PRIORITIZED

P0: review actual GitHub account access separately from file organization.
P0: when the owner authorizes validation, reproduce supported toolchains and build the selected primary apps. Supplied Gradle9.8.0/JDK25 and Android SDK37 need availability/provenance checks; SKIP_ANDROID_BUILD does not disable Android project configuration.
P0: harden local job-creating API authorization and browser cookie/header forwarding. Verify paired native messaging and negative-origin behavior in a dedicated task.
P0: resolve remaining extension standalone type issues without disabling checks. Prior logs show manifest author typing and webext-bridge/type-fest issues; orphan import stub is now preserved outside src.
P1: link real download engine tests to the original HTTP/HTTPS fixture; currently only fixture code/regression source is established, not a desktop integration test.
P1: audit third-party assets, dependency notices, FFmpeg build licensing, binary provenance and distribution/trademark obligations. No original product license was selected.
P1: review package sources/security advisories and original updater trust before installers or public packaging.
P1: verify Android storage/background/notification permissions and Windows/macOS/Linux install/update flows independently.
P2: evaluate MediaGrabber unique detection/manifest logic after fixing its unsafe transfer patterns. Do not introduce a second job engine.
P2: design an authenticated/bounded hosted service only if approved; ReClip remains a UX/code reference.
P2: optional AI indexing/transcription requires measurable value, consent and resource budgets. No AI feature is implemented by this migration.
''')

write('TEST_AND_VALIDATION_REPORT.txt','''TEST AND VALIDATION REPORT

Current instruction: DO NOT RUN TESTS. This pass focuses on content analysis, collection, categorization, references and Git delivery.

Not run after the latest instruction:
- Unit/integration/security regression tests, including all14fixture tests.
- Type checks, lint/format runners, Vite/Gradle/Android builds.
- Dependency installation, startup, browser/device flows or live media downloads.
- CI/deployment or database migration checks. No new root CI/deployment was activated.
- The relocated preservation helper itself was not executed; paths/code were reviewed statically.

Structural observations, not runtime tests:
- Every starting tracked path read/classified; no skipped path.
- Exact retained bytes and baseline Git objects/modes mapped for all1458files.
- Per-member ZIP mapping updated for moved fixture source and preserved revised docs/manifests.
- Markdown targets, import roots and explicit app package boundaries reviewed.
- Diff reviewed for unintended content loss; no valuable file deleted.
- Normal Git push accepted; final HEAD compared to remote main at delivery.

Earlier evidence, not post-migration verification:
The previous completed task recorded14passing fixture tests. Before the latest no-test scope change in this task, an agent produced npm install, Chrome/Firefox bundle and standalone typecheck logs. Bundle logs contain successful build completion messages; typecheck log contains errors. No structured exit-status record was completed before the agent stopped, so these logs are retained as observations, not fresh certified checks. They are not rerun or claimed to validate moved apps. See security-reports/pre-scope-change-logs/.

The available historical type errors include manifest author shape and webext-bridge/type-fest constraints. Desktop/Android and live-source behavior remain unverified. Runtime confidence requires a separately authorized validation task.
''')

write('MIGRATION_SUMMARY.txt',f'''MIGRATION SUMMARY
Baseline: {base}
Recoverable remote tag: recovery-baseline-2026-11-17-7a7e2f6
Local additional bundle: /workspace/recovery-backups/video-downloader-7a7e2f6.bundle

Before: root idea and tooling plus three broad sources directories; runnable fixture nested inside planning tree.
After: apps own coherent framework projects; root tools/tests own fixture; docs/project owns planning/research; archives owns uploaded ZIPs; AnalyseFuture owns current recovery/vision records, references and exact prior versions.

{M['moved_count']} baseline paths relocated; {M['fixture_files_grouped']} fixture files regrouped; {M['newly_archived_count']} new history/orphan preservation copies; no runtime algorithm merge.
All {D['count']} original tracked files accounted for. Original byte hashes and normalized Git object hashes tracked separately, including Windows CRLF batch files. Imports and package internals are preserved; only path/config/doc references changed where necessary.

No tests after latest instruction, no application integration claim, no force-push, no deletion of branches/tags/history. Recovery reports and a per-file dependency/ownership catalogue allow another developer to continue without repeating discovery.
''')

write('NEXT_DEVELOPER_INSTRUCTIONS.txt','''NEXT DEVELOPER INSTRUCTIONS

1. Read AGENTS.md and PROJECT_STRUCTURE.md. The current instruction is organization only, no tests/builds/installs/startup unless a later owner request authorizes them.
2. Verify repository identity and remote main, preserve user changes and backup tag, and read WORK_PROGRESS.txt. Work directly on main; no feature branch/PR/force-push. Push completed checkpoints at least every5minutes during active changes.
3. Baseline and complete classification are in repository-inventory/baseline-file-analysis.json. Original/active/exact-retained mapping and Git/hash evidence are in migration-records/preservation-manifest.json. Preservation helpers require baseline history in the local object database.
4. Kotlin module ownership stays within apps/download-manager; do not split Android/desktop resources or common source sets by extension. Browser package stays under apps/browser-extension with ~ pointing to its src.
5. Fixture imports resolve from repository root as tools.fixtures.http_fixture. Future authorized regression command: python3 -m unittest discover -s tests/fixtures -v. This command was NOT executed after migration.
6. A future authorized structural check can run python3 tools/repository/verify_preservation.py. Default bash tools/development/setup.sh reports prerequisites only. Never run unknown archived installers or references as a shortcut.
7. No production workspace/import/deployment includes AnalyseFuture. Reference bridge/transfer code has known trust/corruption risks. Review SECURITY_AUDIT.txt before adopting code. Do not equate archive placement with sandboxing.
8. Begin future validation with toolchain/provenance and primary app builds, then fixture-to-engine integration, then paired browser flow. Keep failed/blocked/unrun checks distinct. Do not implement every platform connector or rewrite languages without evidence.
9. Public source support and optional AI are product roadmap proposals. Use PROJECT_VISION_AND_FUTURE_ROADMAP.txt; preserve prior research rather than replacing it with unsupported claims.
''')

write('WORK_PROGRESS.txt',f'''STRUCTURE-ONLY RECOVERY PROGRESS
Baseline: {base}
Completed: fetched advertised refs/history; backup tag pushed and local Git bundle retained; clean starting main.
Completed: all{D['count']}startingfiles inventoried; {D['text_count']}text and{D['binary_count']}binary entries classified.
Completed: functional app/tool/test/document collections; {M['moved_count']}path moves; exact original mapping and preservation; orphan stub archived.
Completed: imports/framework boundaries, source-package scope, Markdown/helper/index references reviewed and repaired.
Completed: PROJECT_STRUCTURE.md, all requested .txtreports, detailed future vision, dependency/duplicate/security inventories and continuation guide.
Current: final static path/content preservation review and direct-main delivery.
Pending after this pass: runtime validation only when owner authorizes tests; security hardening and product integration as listed in TECHNICAL_DEBT.txt.
Important: no tests/builds/install/startup after latest no-test instruction. Prior logs are archived and not migration pass results.
Uninspected behavior: all runtime/device/browser/live-site behavior; binary safety not certified; account security/protection API unavailable.
No skipped tracked path; generated ignored dependencies/output caches are local only.
''')

# Preserve useful earlier agent observations without making them active code.
logs=A/'security-reports/pre-scope-change-logs';logs.mkdir(parents=True,exist_ok=True)
for p in W.glob('browser-*.log'):shutil.copy2(p,logs/p.name)
(logs/'README.md').write_text('These logs were produced before the latest no-test instruction. They do not validate the moved tree; no rerun or complete structured exit-status record is claimed. Dependency caches/build outputs remain ignored local files.\n')
request=Path('/workspace/attachments/661357f9-74ec-47b8-86a6-036a7ec99262/Pasted text.txt')
if request.exists():
 target=A/'recovery-notes/USER_RECOVERY_REQUEST.md';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(request,target)
(A/'recovery-notes/LATEST_SCOPE.txt').write_text('Latest owner instruction: analyze and organize every file by actual function, preserve all work under AnalyseFuture as needed, repair references, create PROJECT_STRUCTURE.md, push direct main without PR/force-push. DO NOT RUN TESTS FOR THIS PASS. This supersedes test execution requested in the earlier uploaded master request.\n')
scripts=A/'migration-records/scripts';scripts.mkdir(parents=True,exist_ok=True)
for name in ['discover.py','restructure.py','reports.py']:shutil.copy2(W/name,scripts/name)
(scripts/'README.md').write_text('One-off audit/migration generator sources for provenance. They describe the7a7e2f6input layout and must not be rerun on the migrated tree. They are not production entrypoints.\n')

# Internal dependency ownership map from actual imported/project references.
lines=['DEPENDENCY AND OWNERSHIP MAP','No dependency install or build run after latest no-test instruction.','']
bycomponent=defaultdict(list)
for f in files:bycomponent[f['component']].append(f)
for component,group in sorted(bycomponent.items()):
 deps=sorted({dep for f in group for dep in f['dependencies']})
 lines += [component+' — '+str(len(group))+' files','  Responsibility: '+group[0]['purpose'],
           '  Explicit dependency/import references: '+(', '.join(deps) or 'No explicit code imports; see consumer ownership and manifest.'),'']
write('repository-inventory/DEPENDENCY_MAP.txt','\n'.join(lines))
print('Wrote complete reports;',len(features),'feature records;',len(D['duplicates']),'exact duplicate groups.')
