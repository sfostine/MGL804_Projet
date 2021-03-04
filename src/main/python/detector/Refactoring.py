import os
import shutil

from src.main.python.detector.DetectorStrategy import DetectorStrategy


class Refactoring(DetectorStrategy):

    def __init__(self, config: dict):
        super(Refactoring, self).__init__(config)

        self.jar_path = os.path.abspath(self.cfg['paths']['refactorite_java'])
        self.temp_path = os.path.abspath(self.cfg['paths']['refactor_report'] + '/temp')
        self.current_path = ""

        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Refactoring Detector ***')
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        os.mkdir(self.temp_path)

        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        self.current_path = os.path.abspath(self.cfg['paths']['refactor_report'] + repo_cfg['name'])

        # execute .jar
        os.system("java -jar " + self.jar_path
                  + " -i " + repo_path
                  + " -o " + self.temp_path
                  + " -c " + repo_cfg['commit'])

    def _format_data(self, repo_cfg: dict):
        print('\n\n*** Formatting Refactoring Data ***')
        # TODO: check if can transform json to csv with column commit and other stuff ...
        for file in os.listdir(self.temp_path):
            if file.endswith(".json"):
                old_path = self.temp_path + '\\' + file
                new_path = self.current_path + '\\' + file
                if not os.path.exists(self.current_path):
                    os.mkdir(self.current_path)
                os.rename(old_path, new_path)
        shutil.rmtree(self.temp_path)
