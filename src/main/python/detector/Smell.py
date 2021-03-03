import os

import pandas as pd

from src.main.python.detector.DetectorStrategy import DetectorStrategy


class Smell(DetectorStrategy):

    def __init__(self, cfg: dict):
        super(Smell, self).__init__(cfg)

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Smell Detector ***')
        # init param to execute .jar
        jar_path = os.path.abspath(self.cfg['paths']['designite_java'])
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        out_path = os.path.abspath(self.cfg['paths']['smell_report'] + '/temp')

        # execute .jar
        os.system("java -jar " + jar_path + " -i " + repo_path + " -o " + out_path)

    def _format_data(self, repo_cfg: dict, commit_hash: str):
        print('\n\n*** Formatting Code Smell Data ***')
        temp_path = os.path.abspath(self.cfg['paths']['smell_report'] + '/temp')
        out_path = self.cfg['paths']['smell_report'] + repo_cfg['name']
        for file in os.listdir(temp_path):
            if file.endswith(".csv"):
                temp_file_path = temp_path + '/' + file
                out_file_path = out_path + '/' + file

                new_file = pd.read_csv(temp_file_path, index_col=1)
                new_file['commit_hash'] = commit_hash

                if os.path.exists(out_file_path):
                    old_file = pd.read_csv(out_file_path, index_col=1)
                    old_file = old_file.append(new_file, ignore_index=True)
                    old_file.to_csv(out_file_path, index=False)
                else:
                    try:
                        os.mkdir(out_path)
                    except:
                        pass
                    new_file.to_csv(out_file_path, index=False)
