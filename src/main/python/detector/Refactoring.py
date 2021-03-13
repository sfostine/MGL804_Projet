import os
import subprocess
import threading


class Refactoring:

    def __init__(self, config: dict):
        self.cfg = config
        self.jar_path = os.path.abspath(self.cfg['paths']['refactorite_java'])
        self.current_path = ""

    def run(self, multi_thread: bool):
        threads = []
        for repo in self.cfg['repos']:
            thread = threading.Thread(target=self._execute_jar, args=(repo,), name=f"RefactorDetector_{repo['name']}")
            thread.start()
            if multi_thread:
                threads.append(thread)
            else:
                # wait right away for the thread to complete
                thread.join()

        # wait until all repos are donne
        for t in threads:
            t.join()

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Refactoring Detector ***')

        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        out_path = os.path.abspath(self.cfg['paths']['refactor_report'] + repo_cfg['name'] + '/')
        if not os.path.exists(out_path):
            os.mkdir(out_path)

        # execute .jar
        subprocess.call(['java', '-jar', self.jar_path,
                         '-i', repo_path,
                         "-o", out_path,
                         '-b', repo_cfg['branch']])
