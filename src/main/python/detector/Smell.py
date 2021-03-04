import os
import shutil

from src.main.python.detector.DetectorStrategy import DetectorStrategy


# import pandas as pd


class Smell(DetectorStrategy):

    def __init__(self, cfg: dict):
        super(Smell, self).__init__(cfg)
        self.id = 0

        self.jar_path = os.path.abspath(self.cfg['paths']['designite_java'])
        self.temp_path = os.path.abspath(self.cfg['paths']['smell_report'] + '/temp')
        self.current_path = ""

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Smell Detector ***')
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        self.current_path = os.path.abspath(self.cfg['paths']['smell_report'] + repo_cfg['name'])
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])

        # execute .jar
        os.system("java -jar " + self.jar_path + " -i " + repo_path + " -o " + self.temp_path)

    def _format_data(self, repo_cfg: dict):
        print('\n\n*** Formatting Code Smell Data ***')
        print(f"Commit: {repo_cfg['commit']}")

        self.id += 1

        for file in os.listdir(self.temp_path):
            if file.endswith(".csv"):
                old_path = self.temp_path + '\\' + file
                new_path = self.current_path + f'\\{str(self.id).zfill(6)}_' + file
                if not os.path.exists(self.current_path):
                    os.mkdir(self.current_path)
                os.rename(old_path, new_path)

        #         new_file.set_index('commit_hash', inplace=True)
        #         if not os.path.exists(out_path):
        #             os.mkdir(out_path)
        #         new_file.to_csv(out_file_path, index=False)
        #
        #         if os.path.exists(out_file_path):
        #             old_file = pd.read_csv(out_file_path, header=0)
        #             old_file.set_index("commit_hash", inplace=True)
        #
        #             new_file = old_file.join(new_file,
        #                                      how='outer',
        #                                      on='commit_hash',
        #                                      rsuffix='rsfx_')
        #             # remove some columns
        #             # new_file = new_file[new_file.columns.drop(list(new_file.filter(regex='^rsfx_.*$')))]
        #
        #         elif not os.path.exists(out_path):
        #             os.mkdir(out_path)
        #         new_file.to_csv(out_file_path, index=False)
        shutil.rmtree(self.temp_path)
