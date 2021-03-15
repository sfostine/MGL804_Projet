import os
import shutil
import subprocess

from src.main.python import RepoHelper


class Smell:

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.id = None
        self.jar_path = os.path.abspath(self.cfg['paths']['designite_java'])
        self.out_path = ""

    def run(self, repo_helper: RepoHelper):
        for repo in self.cfg['repos']:
            self.out_path = os.path.abspath(self.cfg['paths']['smell_report'] + repo['name'] + '\\temp\\')
            if os.path.exists(self.out_path):
                shutil.rmtree(self.out_path)

            self.id = 0
            repo_helper.checkout_refactored_commit(repo_cfg=repo, call_back=self.detect_smell)
            shutil.rmtree(self.out_path)

    def detect_smell(self, repo_cfg: dict):
        self.execute_jar(repo_cfg)
        self.rename_jar_output(repo_cfg)

    def execute_jar(self, repo_cfg: dict):
        print('*** Run Code Smell Detector ***')
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        subprocess.call(['java', '-jar', self.jar_path,
                         '-i', repo_path,
                         "-o", self.out_path])

    def rename_jar_output(self, repo_cfg: dict):
        self.id += 1

        keep_file = self.cfg['keep_smell']

        for file in keep_file:
            new_out = self.out_path.replace('\\temp', '')
            new_name = f'\\{str(self.id).zfill(6)}_' + file[:-4] + "_" + repo_cfg['commit'] + '.csv'
            os.rename(self.out_path + "\\" + file, new_out + new_name)
