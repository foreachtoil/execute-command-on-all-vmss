import argparse
import sys
import os
import subprocess
import json

def error(message: str):
    print(message, file=sys.stderr)
    sys.exit(1)

def run_cmd(cmd, to_json=False, exit_on_error=True):
    try:
        p = subprocess.check_output(cmd, shell=True)
        # https://github.com/Azure/azure-cli/issues/9903
        raw = p.decode('utf-8').replace('\x1b[0m', '')

        if to_json:
            return json.loads(raw)
        else:
            return raw

    except subprocess.CalledProcessError as e:
        if not exit_on_error:
            return None

        error(f'command [{cmd}] failed')


def raw_parser():
    class DefaultHelpParser(argparse.ArgumentParser):
        def error(self, message):
            print(f'error: {message}\n', file=sys.stderr)
            self.print_help()
            sys.exit(2)

    parser = DefaultHelpParser(
        prog=os.path.basename(sys.argv[0]),
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=128, width=128))

    parser.add_argument('--force', action='store_true', help=argparse.SUPPRESS, default=False)
    parser.add_argument('--debug', action='store_true', help='log command execution', default=False)

    return parser