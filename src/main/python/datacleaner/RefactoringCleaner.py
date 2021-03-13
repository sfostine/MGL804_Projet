import json
import os

import pandas as pd


# https://pythonexamples.org/pandas-dataframe-add-append-row/


class RefactoringCleaner:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def generate_list_commit(self):
        refactor_path = self.cfg['paths']['refactor_report']
        for repo in self.cfg['repos']:
            df = pd.DataFrame(columns=['commit', 'previous'])
            for file in os.listdir(refactor_path + repo['name']):
                refactor_data = json.load(open(refactor_path + repo['name'] + '/' + file, 'r'))
                commit = refactor_data['commitId']
                previous = refactor_data['prevCommitId']
                df = df.append({"commit": commit, "previous": previous}, ignore_index=True)
            df.to_csv(self.cfg['paths']['commit_report'] + repo['name'] + "_refactored.csv", index=False)

    def generate_data_table(self):
        refactor_path = self.cfg['paths']['refactor_report']
        for repo in self.cfg['repos']:
            # index will be the first three columns
            index_col = self.cfg['refactoring_columns'][:3]
            df = pd.DataFrame(index=index_col, columns=self.cfg['refactoring_columns'])

            for file in os.listdir(refactor_path + repo['name']):
                refactor_data = json.load(open(refactor_path + repo['name'] + '/' + file, 'r'))
                new_rows = self.generate_rows(refactor_data)
                df = df.append(new_rows, ignore_index=False)

            df = df[~df['commit'].isna()]
            df = df.set_index(index_col)

            df.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data.csv", index=True)

    def generate_rows(self, refactor_data) -> list:
        rows = []
        # row = {'commit':None, 'file':None, 'refactoring':None, 'results':None}

        commit = refactor_data['commitId']
        results = ['before', 'after', 'delta']

        for detail in refactor_data['refactorings']:
            r_type = detail['type']
            file = detail['leftSideLocations'][0]['filePath']
            file = file.split('/')[-1].split('.')[0]
            for result in results:
                new_row = {'commit': commit, 'file': file, 'refactoring': r_type, 'results': result}
                rows.append(new_row)
        return rows
