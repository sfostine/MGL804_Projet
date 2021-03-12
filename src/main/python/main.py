import ctypes
import json
import logging
import os
import sys

from src.main.python.RepoHelper import RepoHelper
from src.main.python.detector.Refactoring import Refactoring
from src.main.python.detector.Smell import Smell


def run_project():
    # LOAD CONFIG
    cfg = json.load(open('../resources/config.json', 'r'))

    # VALIDATE FOLDERS AND FILES
    for name, path in cfg['paths'].items():
        if not os.path.exists(path):
            if path == cfg['paths']['refactorite_java']:
                raise FileNotFoundError(f"{path}\n\t- Must run Maven life-cycle \'clean\' and \'install\' first.")
            else:
                os.mkdir(path)

    # INITIALIZE RepoHelper
    rh = RepoHelper(cfg)
    rh.initialize()
    rh.add_detectors(Smell(cfg))
    rh.add_detectors(Refactoring(cfg))

    # RUN ALL DETECTOR ON ALL VERSION OF ALL REPOSITORIES
    for repo in cfg['repos']:
        rh.checkout_all_commit(repo)


def main():
    if is_admin():
        run_project()
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


main()
