import asyncio
import ctypes
import json
import logging
import os
import sys

from RepoHelper import RepoHelper
from SmellHelper import SmellHelper


def run_refactoring_script(cfg: dict, rh: RepoHelper):
    # TODO: Not Implemented
    raise NotImplementedError("\n\n\tDoit implementer ce truc: run_refactoring_script")


def run_smell_script(cfg: dict, rh: RepoHelper):
    print('\n\n*** Run Code Smell ***')
    sh = SmellHelper(cfg)
    for repo in cfg['repos']:
        rh.checkout_all_commit(repo, sh.run_detector)


async def main():
    if is_admin():
        cfg = json.load(open('../resources/config.json', 'r'))

        for name, path in cfg['paths'].items():
            if not os.path.exists(path):
                os.mkdir(path)

        rh = RepoHelper(cfg)
        rh.initialize()

        run_smell_script(cfg, rh)
        run_refactoring_script(cfg, rh)

    else:
        # Re-run the program with admin rights
        logging.warning(f'Watch out!\n\t* Re-ran the program with admin rights'
                        f'\n\t\t-ran: ({sys.executable})'
                        f'\n\t\t-with: ({" ".join(sys.argv)})'
                        '\n\t* Alternative is to run your IDE as an Admin'
                        '\n\t\t-how-to: https://stackoverflow.com/questions/33331155/how-to-run-python-file-with-'
                        'admin-rights-in-pycharm#:~:text=From%20Windows%20start%20menu%20right,'
                        'under%20the%20%22Compatibility%22%20tab.&text=To%20run%20something%20as%20admin,'
                        'application%2Fscrpit%20from%20elevated%20CMD.')

        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def is_admin():
    """    https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script/41930586#41930586
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.exception(e)
        return False


asyncio.run(main())
