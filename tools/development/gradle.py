"""Run the pinned build with workspace-owned caches and the required JDK.

No downloads or tests happen implicitly: arguments are passed to Gradle as-is.
Install the documented JDK/Android SDK prerequisites first.
"""

import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'apps/download-manager'
CACHE = Path('/workspace/.cache')


def main():
    properties = (PROJECT / 'gradle.properties').read_text()
    required = int(re.search(r'^jvm\.toolchain=(\d+)$', properties, re.M).group(1))
    candidates = []
    if os.environ.get('JAVA_HOME'):
        candidates.append(Path(os.environ['JAVA_HOME']))
    current = shutil.which('java')
    if current:
        candidates.append(Path(current).resolve().parents[1])
    candidates.extend(sorted((CACHE / 'jdks').glob(f'jdk-{required}*'), reverse=True))
    selected = None
    for candidate in candidates:
        java = candidate / 'bin/java'
        if not java.is_file() or not (candidate / 'bin/javac').is_file():
            continue
        result = subprocess.run([str(java), '-version'], capture_output=True, text=True)
        match = re.search(r'version "(\d+)', result.stdout + result.stderr)
        if result.returncode == 0 and match and int(match.group(1)) == required:
            selected = candidate
            break
    if selected is None:
        raise SystemExit(f'JDK {required} with javac is required; set JAVA_HOME to a verified installation.')

    env = os.environ.copy()
    env['JAVA_HOME'] = str(selected)
    env['PATH'] = str(selected / 'bin') + os.pathsep + env.get('PATH', '')
    env.setdefault('GRADLE_USER_HOME', str(CACHE / 'gradle'))
    env.setdefault('ANDROID_USER_HOME', str(CACHE / 'android/user'))
    env.setdefault('XDG_CONFIG_HOME', str(CACHE / 'config'))
    sdk = CACHE / 'android/sdk'
    if sdk.is_dir():
        env.setdefault('ANDROID_HOME', str(sdk))
    env.setdefault('KONAN_DATA_DIR', str(CACHE / 'konan'))
    for name in ['GRADLE_USER_HOME', 'ANDROID_USER_HOME',
                 'XDG_CONFIG_HOME', 'KONAN_DATA_DIR']:
        Path(env[name]).mkdir(parents=True, exist_ok=True)

    # Java's downloader does not automatically use the shell HTTPS proxy.
    # Do not copy credentials into Java properties or persistent config files.
    options = shlex.split(env.get('JAVA_OPTS', ''))
    proxy = urlsplit(env.get('HTTPS_PROXY') or env.get('https_proxy') or '')
    if proxy.hostname and proxy.port:
        existing = {option.split('=', 1)[0] for option in options}
        for key, value in [('https.proxyHost', proxy.hostname), ('https.proxyPort', str(proxy.port)),
                           ('http.proxyHost', proxy.hostname), ('http.proxyPort', str(proxy.port))]:
            if '-D' + key not in existing:
                options.append('-D' + key + '=' + value)
    truststore = Path('/etc/ssl/certs/java/cacerts')
    if truststore.is_file() and not any(x.startswith('-Djavax.net.ssl.trustStore=') for x in options):
        options.append('-Djavax.net.ssl.trustStore=' + str(truststore))
    env['JAVA_OPTS'] = shlex.join(options)
    args = sys.argv[1:] or ['--version']
    return subprocess.call([str(PROJECT / 'gradlew'), *args], cwd=PROJECT, env=env)


if __name__ == '__main__':
    sys.exit(main())
