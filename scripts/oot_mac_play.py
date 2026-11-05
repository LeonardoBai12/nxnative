#!/usr/bin/env python3
# Opens the Ocarina of Time Mac app that oot_mac_setup.py built (docs/oot-mac.md), and keeps the Mac awake while it runs.
# Usage: python3 oot_mac_play.py [<the .app>]
import json, subprocess, sys
from pathlib import Path

STATE = Path.home() / '.config/nxnative-oot.json'


def main():
    app = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(json.loads(STATE.read_text())['app']) if STATE.is_file() else None
    if app is None or not app.is_dir(): sys.exit(f'[RED] no app at {app}: run oot_mac_setup.py first, or name the .app')
    sys.exit(subprocess.run(['caffeinate', '-di', 'open', '-W', str(app)]).returncode)


if __name__ == '__main__':
    main()
