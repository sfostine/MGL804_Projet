import os

from src.main.python.detector.DetectorStrategy import DetectorStrategy


class Refactoring(DetectorStrategy):

    def __init__(self, config: dict):
        super(Refactoring, self).__init__(config)

    def _execute_jar(self, repo_cfg: dict):
        print('\n\n*** Run Code Refactoring Detector ***')
        # init param to execute .jar
        jar_path = os.path.abspath(self.cfg['paths']['refactorite_java'])
        repo_path = os.path.abspath(self.cfg['paths']['repo'] + repo_cfg['name'])
        out_path = os.path.abspath(self.cfg['paths']['refactor_report'] + '/temp')

        # execute .jar
        os.system("java -jar " + jar_path + " -i " + repo_path + " -o " + out_path)

    def _format_data(self, repo_cfg: dict, commit_hash: str):
        print('\n\n*** Formatting Refactoring Data ***')
        # todo: implement function
        print(f"Refactoring.__format_data:\tNotImplemented")
