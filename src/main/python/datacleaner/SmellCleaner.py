import os

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
                if file == 'temp':
                    break
                file_id, cs_type, commit = file.split('_')

                current_df = pd.read_csv(repo_path + file, header=0)
                current_df['commit'] = commit

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
            design = implementation[~design['file'].isna()]
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
