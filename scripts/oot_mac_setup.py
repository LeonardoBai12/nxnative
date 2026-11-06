#!/usr/bin/env python3
# The Legend of Zelda: Ocarina of Time (Switch 2, 0400486024DEC000) on the Mac, from nothing to a Mac app: Homebrew and the tools, a clone of this fork's oot-mac branch (nxnative with the open
# work on this game applied and its shader translator already rebuilt), then build_ipa_from_nsp.py --platform mac-app. Instructions: docs/oot-mac.md.
# Usage: python3 oot_mac_setup.py <game .nup> [--dir <clone folder>] [--app <output .app>] [--prepare-only]
# Runs on the system Python (3.9) with nothing installed, on its own or from a clone. Run it again after a stop: finished steps are skipped and the build reuses what it made.
# Xcode is the one thing it cannot install. Xcode 27.2 is what the project tests with; with another Metal compiler the script adds --allow-other-metal and says so.
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

REPO_URL = 'https://github.com/LeonardoBai12/nxnative.git'
BRANCH = 'oot-mac4'
STATE = Path.home() / '.config/nxnative-oot.json'   # where oot_mac_play.py finds the app
BREW_BIN = '/opt/homebrew/bin'
FORMULAE = ('xcodegen', 'zstd', 'glslang', 'python@3.13', 'dotnet')
PIP = ('lz4', 'capstone>=5,<6', 'fonttools', 'nsz', 'zbic', 'backports.zstd')
ENV = dict(os.environ, PATH=f'{BREW_BIN}:{os.environ["PATH"]}', DOTNET_ROOT='/opt/homebrew/opt/dotnet/libexec', HOMEBREW_NO_AUTO_UPDATE='1')


def say(msg): print(f'==> {msg}', flush=True)


def die(msg): sys.exit(f'[RED] {msg}')


def run(*cmd, cwd=None, check=True, quiet=False):
    """Runs cmd as arm64: a Python under Rosetta would otherwise start the universal tools as Intel code (docs/reference/packing.md)"""
    out = subprocess.PIPE if quiet else None
    r = subprocess.run(['arch', '-arm64', *map(str, cmd)], cwd=cwd, env=ENV, stdout=out, stderr=out, text=True, errors='replace')
    if check and r.returncode: die(f'{" ".join(map(str, cmd))} exit code {r.returncode}' + (f'\n{r.stderr.strip()}' if quiet else ''))
    return r


def check_mac(nup):
    if sys.platform != 'darwin': die('this needs a Mac')
    if subprocess.run(['sysctl', '-n', 'hw.optional.arm64'], capture_output=True, text=True).stdout.strip() != '1': die('this needs a Mac with Apple silicon: the game\'s own arm64 code runs natively')
    if subprocess.run(['xcodebuild', '-version'], capture_output=True).returncode: die('Xcode is not installed or not selected: install it (27.2 if you can), open it once, then run sudo xcode-select -s /Applications/Xcode.app')
    if nup.suffix.lower() != '.nup' or not nup.is_file(): die(f'not a .nup file: {nup}')
    need = nup.stat().st_size * 2 / 1e9 + 10; free = shutil.disk_usage(nup.parent).free / 1e9
    if free < need: say(f'WARNING: {free:.0f} GB free, a first build needs about {need:.0f} GB (fine if a build already ran)')
    ram = int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout) / 2**30
    if ram < 24: say(f'WARNING: {ram:.0f} GB of memory: testers on 16 GB Macs report heavy swapping and GPU out-of-memory stops at scene changes')


def install_tools():
    if not Path(BREW_BIN, 'brew').exists():
        say('installing Homebrew (it asks for your password)')
        script = subprocess.run(['curl', '-fsSL', 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh'], capture_output=True, text=True)
        if script.returncode: die('could not download the Homebrew installer')
        run('/bin/bash', '-c', script.stdout)
    say('installing the tools with Homebrew')
    run('brew', 'install', *FORMULAE)
    if run('xcrun', 'metal', '--version', check=False, quiet=True).returncode:
        say('downloading the Metal toolchain')
        run('xcodebuild', '-downloadComponent', 'MetalToolchain')


def clone(repo):
    if (repo / '.git').exists(): say(f'{repo} is there'); return
    say(f'cloning nxnative into {repo}')
    run('git', 'clone', '-q', '--depth', '1', '-b', BRANCH, REPO_URL, repo)


def make_venv(repo):
    py = repo / '.venv/bin/python'
    if not py.exists():
        say('making the Python environment')
        run(f'{BREW_BIN}/python3.13', '-m', 'venv', repo / '.venv')
        run(py, '-m', 'pip', 'install', '-q', *PIP)
    return py


def other_metal(repo):
    lock = dict(l.split('\t', 1) for l in (repo / 'dm/gfx/tools/dmsh_chain.lock').read_text().splitlines() if '\t' in l)
    now = run('xcrun', '-sdk', 'macosx', 'metal', '--version', quiet=True).stdout.splitlines()[0]
    if now == lock['metal_macosx']: return False
    say(f'WARNING: this Metal compiler ({now}) is not the tested one ({lock["metal_macosx"]}, Xcode 27.2): building with --allow-other-metal')
    return True


def main():
    ap = argparse.ArgumentParser(description='Installs everything and builds Ocarina of Time as a Mac app')
    ap.add_argument('nup', type=Path, help='the game, a .nup file made from your own copy')
    ap.add_argument('--dir', type=Path, default=Path.home() / 'nxnative-oot', help='where nxnative goes (default: ~/nxnative-oot)')
    ap.add_argument('--app', type=Path, help='the Mac app (default: Zelda OOT.app beside the .nup)')
    ap.add_argument('--prepare-only', action='store_true', help='stop before the game\'s build')
    a = ap.parse_args()
    nup = a.nup.expanduser().resolve(); repo = a.dir.expanduser().resolve()
    app = a.app.expanduser().resolve() if a.app else nup.parent / 'Zelda OOT.app'
    check_mac(nup)
    install_tools()
    clone(repo)
    py = make_venv(repo)
    if a.prepare_only: say('prepared; the game was not built'); return
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({'repo': str(repo), 'app': str(app)}))
    say('building the game: about an hour on an M1 Pro, the Mac stays awake meanwhile (keep it plugged in, lid open)')
    run('caffeinate', '-ims', py, 'scripts/build_ipa_from_nsp.py', nup, '--platform', 'mac-app', '--env-file', 'scripts/oot_mac.env', '-o', app, *(['--allow-other-metal'] if other_metal(repo) else []), cwd=repo)
    say(f'done: {app}\nPlay with: python3 {repo}/scripts/oot_mac_play.py')


if __name__ == '__main__':
    main()
