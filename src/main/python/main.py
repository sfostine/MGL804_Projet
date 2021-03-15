import ctypes
import json
import logging
import os
import subprocess
import sys
import threading

from src.main.python.RepoHelper import RepoHelper
from src.main.python.datacleaner.RefactoringCleaner import RefactoringCleaner
from src.main.python.datacleaner.SmellCleaner import SmellCleaner
from src.main.python.detector.Refactoring import Refactoring
from src.main.python.detector.Smell import Smell


def validate_files(cfg):
    for name, path in cfg['paths'].items():
        if not os.path.exists(path):
            if path == cfg['paths']['refactorite_java']:
                raise FileNotFoundError(f"{path}\n\t- Must run Maven life-cycle \'clean\' and \'install\' first.")
            else:
                os.mkdir(path)

def run_project():
    # LOAD CONFIG
    cfg = json.load(open('../resources/config.json', 'r'))
    validate_files(cfg)

    # INITIALIZE RepoHelper
    rh = RepoHelper(cfg)
    rh.clone_all_repo()

    # RUN REFACTORING DETECTOR
    Refactoring(cfg).run(multi_thread=False)
    # consolidate output data
    r_cleaner = RefactoringCleaner(cfg)
    r_cleaner.generate_data_table()
    r_cleaner.generate_list_commit()

    # RUN SMELL DETECTOR
    Smell(cfg).run(repo_helper=rh)
    # consolidate output data
    s_cleaner = SmellCleaner(cfg)
    s_cleaner.merge_files()
    s_cleaner.generate_pivot_table()
    s_cleaner.generate_data_table()


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
