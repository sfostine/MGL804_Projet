import os
import re

import numpy as np
import pandas as pd


# remove some columns
# new_file = new_file[new_file.columns.drop(list(new_file.filter(regex='^rsfx_.*$')))]
class SmellCleaner:

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def merge_files(self):
        smell_path = self.cfg['paths']['smell_report']
        for repo in self.cfg['repos']:
            repo_path = smell_path + repo['name'] + '/'
            implementation = pd.DataFrame(index=['id_data'],
                                          columns=['id_data', 'Project Name', 'Package Name', 'Type Name',
                                                   'Method Name', 'Code Smell'])
            design = pd.DataFrame(index=['id_data'],
                                  columns=['id_data', 'Project Name', 'Package Name', 'Type Name', 'Code Smell'])
            for file in os.listdir(repo_path):
                if not re.match(r'\d+\_\w+\_\w+\.csv', file):
                    break
                file_id, cs_type, commit = file.split('_')

                current_df = pd.read_csv(repo_path + file, header=0)
                current_df['commit'] = commit
                current_df['commit'] = current_df['commit'].replace(r'\.csv$', '', regex=True)

                if cs_type == 'implementationCodeSmells':
                    next_id = len(implementation.index) + 1
                    current_df['id_data'] = range(next_id, next_id + len(current_df.index))
                    current_df.set_index('id_data', inplace=True)
                    implementation = implementation.append(current_df, ignore_index=False)
                elif cs_type == 'designCodeSmells':
                    next_id = len(design.index) + 1
                    current_df['id_data'] = range(next_id, next_id + len(current_df.index))
                    current_df.set_index('id_data', inplace=True)
                    design = design.append(current_df, ignore_index=False)
                else:
                    raise NotImplemented(f"File {cs_type} is not implemented")

            implementation.rename(columns={"Type Name": "file"}, inplace=True)
            implementation = implementation[~implementation['file'].isna()]
            implementation.to_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_implementation.csv",
                                  index=False)

            design.rename(columns={"Type Name": "file"}, inplace=True)
            design = design[~design['file'].isna()]
            design.to_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_design.csv", index=False)

    def generate_pivot_table(self, with_files=True):
        for repo in self.cfg['repos']:
            # df = pd.read_csv(self.cfg['paths']['data']+f"{repo['name']}_data.csv", header=0)
            implementation = pd.read_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_implementation.csv",
                                         header=0)
            implementation['Code Smell count'] = implementation['Code Smell']

            if with_files:
                index = ["commit", "file", "Code Smell"]
            else:
                index = ["commit", "Code Smell", ]

            pivot = pd.pivot_table(implementation, index=index,
                                   # columns=["Code Smell"],
                                   values=["Code Smell count"],
                                   aggfunc=['count'],
                                   fill_value=0
                                   )
            pivot = pivot.unstack(level="Code Smell", fill_value=0)

            if (with_files):
                suffix = "_data_2pivot_smell_wf.csv"
            else:
                suffix = "_data_2pivot_smell.csv"

            pivot.to_csv(self.cfg['paths']['data'] + repo['name'] + suffix, index=True)

    def generate_data_table(self):
        for repo in self.cfg['repos']:
            # load commits to reference previous ones
            commits = pd.read_csv(self.cfg['paths']['commit_report'] + repo['name'] + "_refactored.csv", header=0)

            # load refactoring table template
            df = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_1ref.csv", header=0)
            after = df[df['results'] == 'after'].copy(True)
            before = df[df['results'] == 'before'].copy(True)

            # load code smell
            smell = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell_wf.csv", header=2)
            smell.rename(columns={'Code Smell': 'commit', 'Unnamed: 1': 'file'}, inplace=True)

            # assign after rows
            # todo only on commit if simple?
            after = after.merge(smell.copy(True), on=['commit', 'file'], how='left',
                                indicator="data_1ref <- pivot_smell")

            # assign before rows
            before = before.merge(commits, on=['commit'], how='left', indicator=False)
            before.rename(columns={'commit': 'commit_temp'}, inplace=True)
            before.rename(columns={'previous': 'commit'}, inplace=True)
            before = before.merge(smell, on=['commit', 'file'], how='left', indicator="data_1ref <- pivot_smell")
            before['commit'] = before['commit_temp']
            del before['commit_temp']

            # save snapshot to help debug
            after.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3after.csv", index=True)
            before.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3before.csv", index=True)

            delta = self.get_delta(repo, before.copy(True), after.copy(True))

            print(len(after.index))
            print(len(before.index))
            print(len(delta.index))

            before['id'] = before['id'] = list(range(0, len(before.index) * 3, 3))
            after['id'] = after['id'] = list(range(1, len(after.index) * 3, 3))
            delta['id'] = delta['id'] = list(range(2, len(delta.index) * 3, 3))

            before.set_index('id', inplace=True)
            after.set_index('id', inplace=True)
            delta.set_index('id', inplace=True)

            df = before.append([after, delta], ignore_index=False)
            df.sort_values(by='id', inplace=True)
            df.replace(np.nan, 0, inplace=True)
            df.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_9.csv", index=True)

    def get_delta(self, repo: dict, before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
        before['id'] = before['id'] = list(range(0, len(before.index) * 2, 2))
        after['id'] = after['id'] = list(range(1, len(after.index) * 2, 2))
        before.set_index('id', inplace=True)
        after.set_index('id', inplace=True)

        if len(after.index) != len(before.index):
            raise Exception("dataframe (after) and (before) should be the same length!")

        # temp dataframe for computation
        temp = before.append([after], ignore_index=False).copy(True)
        temp.sort_values(by='id', inplace=True)
        temp['group_id'] = [i - (i % 2) for i in list(range(len(temp.index)))]
        temp.replace(np.nan, 0, inplace=True)
        temp.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_4temp.csv", index=True)

        smell_cols = list(temp.columns)[4:-2]
        print(f"smell_cols: {smell_cols}")

        # compute row delta
        delta = temp[smell_cols + ['group_id']].groupby(('group_id')).diff(axis=0, periods=1)
        delta.dropna(subset=['Complex Conditional'], inplace=True)
        delta.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_5delta.csv", index=True)

        delta = delta.merge(after[['commit', 'file', 'refactoring']].copy(True),
                            on='id',
                            how='left')

        delta['results'] = 'delta'
        delta.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_6delta.csv", index=True)
        return delta
