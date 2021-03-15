import os
import re

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

    def generate_pivot_table(self):
        for repo in self.cfg['repos']:
            # df = pd.read_csv(self.cfg['paths']['data']+f"{repo['name']}_data.csv", header=0)
            implementation = pd.read_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_implementation.csv",
                                         header=0)
            implementation['Code Smell count'] = implementation['Code Smell']
            pivot = pd.pivot_table(implementation, index=["commit", "file", "Code Smell"],
                                   # columns=["Code Smell"],
                                   values=["Code Smell count"],
                                   aggfunc=['count'],
                                   fill_value=0
                                   )
            pivot = pivot.unstack(level="Code Smell", fill_value=0)

            pivot.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell.csv", index=True)

    def generate_data_table(self):
        for repo in self.cfg['repos']:
            # load refactoring table template
            df = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_1ref.csv", header=0)
            after = df[df['results'] == 'after'].copy(True)
            before = df[df['results'] == 'before'].copy(True)
            delta = df[df['results'] == 'delta'].copy(True)

            # load code smell
            smell = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell.csv", header=2)
            smell.rename(columns={'Code Smell': 'commit', 'Unnamed: 1': 'file'}, inplace=True)

            # assign after rows
            after = after.merge(smell, on=['commit', 'file'], how='left', indicator="_merge: data_1ref <- pivot_smell")

            # assign before rows
            commits = pd.read_csv(self.cfg['paths']['commit_report'] + repo['name'] + "_refactored.csv", header=0)
            before = before.merge(commits, on=['commit'], how='outer', indicator=False)
            del before['previous']
            before = before.merge(smell, on=['commit', 'file'], how='left',
                                  indicator="_merge: data_1ref <- pivot_smell")

            # save snapshot to help debug
            after.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3after.csv", index=True)
            before.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3before.csv", index=True)
            after.drop(columns='_merge: data_1ref <- pivot_smell', inplace=True)
            before.drop(columns='_merge: data_1ref <- pivot_smell', inplace=True)

            # prepare to merge all back (before-after-delta)
            before['id']  = before['id'] = list(range(0, len(before.index) * 3, 3))
            after['id'] = after['id'] = list(range(1, len(after.index) * 3, 3))
            delta = before.copy(True)
            delta['id']= delta['id'] = list(range(2, len(after.index) * 3, 3))
            delta['results']='delta'
            # set index
            before.set_index('id', inplace=True)
            after.set_index('id', inplace=True)
            delta.set_index('id',inplace=True)
            # merge
            df = before.append([after,delta],ignore_index=False).copy(True)

            # prepare to format row['delta']
            smell_cols = list(df.columns)[4:]
            print(f"smell_cols: {smell_cols}")

            for i in range(0,len(df.index)+1):
                if i%3==0:
                    delta[smell_cols] = after[smell_cols]-before[smell_cols]






            df.sort_values(by='id',inplace=True)
            df.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_4.csv", index=True)

    # def group_by(self):
    #     implementation = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell.csv", header=2)
#
