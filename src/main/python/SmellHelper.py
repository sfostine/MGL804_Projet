import os

import pandas as pd


class SmellHelper:
    # java -jar C:\workspace\mgl804\DesigniteJava.jar -i C:\workspace\mgl804\data\repo\ant -o C:\workspace\mgl804\data\smell
    # https://lankydan.dev/running-a-java-class-as-a-subprocess
    # https://www.datasciencelearner.com/how-to-call-jar-file-using-python/

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def run_detector(self, repo_cfg: dict, commit_hash: str):
        # init param to execute .jar
        jar = os.path.abspath(self.cfg['paths']['designite_java'])
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        temp_path = os.path.abspath(self.cfg['paths']['smell_report'] + '/temp')

        # execute .jar
        os.system("java -jar " + jar + " -i " + repo_path + " -o " + temp_path)

        # format and save data
        # merge data in temp folder while adding a columns for the commit hash
        out_path = self.cfg['paths']['smell_report'] + repo_cfg['name']
        for file in os.listdir(temp_path):
            if file.endswith(".csv"):
                temp_file_path = temp_path + '/' + file
                out_file_path = out_path  + '/' +  file

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
