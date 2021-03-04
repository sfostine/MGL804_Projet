import os

# import shutil
# import pandas as pd

from src.main.python.detector.DetectorStrategy import DetectorStrategy


class Smell(DetectorStrategy):

    def __init__(self, cfg: dict):
        super(Smell, self).__init__(cfg)
        self.id = 0
        self.temp_path = str()

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Smell Detector ***')
        # init param to execute .jar
        jar_path = os.path.abspath(self.cfg['paths']['designite_java'])
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        self.temp_path = os.path.abspath(self.cfg['paths']['smell_report'] + '/temp')

        # execute .jar
        os.system("java -jar " + jar_path + " -i " + repo_path + " -o " + self.temp_path)

    def _format_data(self, repo_cfg: dict, commit_hash: str):
        print('\n\n*** Formatting Code Smell Data ***')
        print(f"Commit: {commit_hash}")

        self.id += 1

        for file in os.listdir(self.temp_path):
            if file.endswith(".csv"):
                os.rename(self.temp_path + '/' + file, self.temp_path + f'/{str(self.id).zfill(6)}_' + file)

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
        # shutil.rmtree(temp_path)
