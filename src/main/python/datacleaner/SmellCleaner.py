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
            implementation = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell.csv", header=2)
            implementation.rename(columns={'Code Smell': 'commit', 'Unnamed: 1': 'file'}, inplace=True)

            df = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_1ref.csv", header=0)
            after = df[df['results'] == 'after'].copy(True)
            before = df[df['results'] == 'before'].copy(True)

            after = after.merge(implementation, on=['commit', 'file'], how='left', indicator=True)
            # print(list(after.columns)[4:-1])
            # after[4:-1] = after[4:-1].applymap(lambda x: int(x) * -1)

            commits = pd.read_csv(self.cfg['paths']['commit_report'] + repo['name'] + "_refactored.csv", header=0)
            before = before.merge(commits, on=['commit'], how='outer', indicator=False)
            before['commit'] = before['previous']
            del before['previous']
            before = before.merge(implementation, on=['commit', 'file'], how='left', indicator=True)

            after.drop(columns='_merge', inplace=True)
            before.drop(columns='_merge',inplace=True)

            c = after.append(before, ignore_index=True, )
            c = c.fillna(0)
            for col in list(c.columns)[4:]:
                c.loc[c['results']=='before',col]=c[col]*-1
            c.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_4.csv", index=True)

            pivot = c.groupby(["commit", "file","refactoring", 'results']).sum()


            # pivot = pd.pivot_table(c, index=["commit", "file","refactoring"],
            #                        values= list(c.columns)[4:],
            #                        aggfunc=['sum'],
            #                        fill_value=0                                   )
            # pivot=pivot.unstack(list(c.columns)[4:])
            print(len(pivot.index))
            pivot.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_5.csv", index=True)
            delta = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_5.csv", header=1)
            delta.rename(columns={'Unnamed: 0': 'commit', 'Unnamed: 1': 'file', 'Unnamed: 2':'refactoring'}, inplace=True)
            delta['results']='delta'

            c = c.append(delta, ignore_index=True)
            c.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_6.csv", index=True)
            return

            # after[4:-1] = after[4:-1].loc[].applymap(lambda x: int(x) * -1)

            # commit	file	refactoring	results
            # g = c.groupby(['commit','file','refactoring','results']).sum('results')
            g = c.groupby(['commit','file','refactoring','results'])['results'].cumsum()
            g.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_5.csv", index=True)

            after.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3after.csv", index=True)
            before.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data_3before.csv", index=True)

    # def group_by(self):
    #     implementation = pd.read_csv(self.cfg['paths']['data'] + repo['name'] + "_data_2pivot_smell.csv", header=2)
#
