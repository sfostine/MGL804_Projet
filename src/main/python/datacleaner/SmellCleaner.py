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

            print(self.cfg['paths']['data'] + repo['name'] + "_data_s.csv")
            implementation.to_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_implementation.csv",
                                  index=False)
            design.to_csv(self.cfg['paths']['smell_report'] + repo['name'] + "/_design.csv", index=False)

    # def generate_data_table(self):
    #     refactor_path = self.cfg['paths']['smell_report']
    #     for repo in self.cfg['repos']:
    #         # index will be the first three columns
    #         index_col = self.cfg['refactoring_columns'][:3]
    #         df = pd.read_csv('.csv', header=0)
    #
    #         for file in os.listdir(refactor_path + repo['name']):
    #             refactor_data = json.load(open(refactor_path + repo['name'] + '/' + file, 'r'))
    #             new_rows = self.generate_rows(refactor_data)
    #             df = df.append(new_rows, ignore_index=False)
    #
    #         df = df[~df['commit'].isna()]
    #         df = df.set_index(index_col)
    #
    #         df.to_csv(self.cfg['paths']['data'] + repo['name'] + "_data.csv", index=True)
