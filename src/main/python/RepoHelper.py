import datetime
import os
import shutil

import pandas as pd
from pydriller import RepositoryMining, GitRepository


class RepoHelper:
    """https://pydriller.readthedocs.io/en/latest/

    """
    repo_exist_msg = "Repo \"{}\" already exist.\n\t- to clone remote set \"replace_existing\" = true in \"config.json\""

    def __init__(self, cfg: dict):
        """
        According to configuration, will clone for each project its repository and output csv files listing all commits.
        :param config:
        """
        self.cfg = cfg

    def initialize(self):
        """
        Clone repository and list all commits.
        """
        repo_path = self.cfg['paths']['repo']
        since = datetime.datetime.strptime(self.cfg['filters']['since'], self.cfg['filters']['date_format'])
        # INITIALIZE ALL REPOS
        for repo in self.cfg["repos"]:
            if (not self.cfg['replace_existing_repo']) and (os.path.exists(repo_path + repo['name'])):
                print(self.repo_exist_msg.format(repo_path + repo['name']))
            else:
                if os.path.exists(repo_path + repo['name']):
                    # delete directory and contents
                    shutil.rmtree(repo_path + repo['name'])
                # creat directory
                os.makedirs(repo_path + repo['name'])

                # cloning repository from remote
                print('cloning to {}'.format(repo_path + repo['name']))
                data = pd.DataFrame(columns=self.cfg['commit_columns'])

                for commit in RepositoryMining(repo['remote_repo'],
                                               only_modifications_with_file_types=self.cfg['filters']['file_types'],
                                               only_in_branch=repo['branch'],
                                               since=since,
                                               clone_repo_to=repo_path).traverse_commits():
                    # build dictionary containing modifications
                    mdf_detail = {}
                    mdf_files = []
                    mdf_methods = []
                    for modif in commit.modifications:
                        # TODO remove print
                        if modif.filename in mdf_detail.keys():
                            print(f'filename{modif.filename} en double')
                        mdf_files.append(modif.filename)

                        mdf_detail.update({
                            modif.filename: {
                                "old_path": modif.old_path,
                                "new_path": modif.new_path,
                                "change_type": modif.change_type,
                                "cyclomatic": modif.complexity,
                                "changed_methods": []
                            }
                        })

                        for method in modif.changed_methods:
                            mdf_detail[modif.filename]['changed_methods'] += [method.name]
                            mdf_methods.append(method.name)

                    data = data.append(
                        {
                            "hash": commit.hash,
                            "author_date": commit.author_date,
                            "is_merge": commit.merge,
                            "nb_files": commit.files,
                            "files": mdf_files,
                            "methods": mdf_methods,
                            "nb_deletions": commit.deletions,
                            "nb_insertions ": commit.insertions,
                            "modifications": str(mdf_detail)
                        }, ignore_index=True
                    )
                data.to_csv(self.cfg['paths']['commit_report'] + repo['commit_file'], index=False)

    def checkout_all_commit(self, repo: dict, callback: callable):
        """
        :param repo: repo to iterate over (from config.json)
        :param callback: will be called after each checkout.
        :return:
        """

        gr = GitRepository(path=self.cfg['paths']['repo'] + repo['name'])

        commit = pd.read_csv(self.cfg['paths']['commit_report'] + repo['commit_file'], index_col=1)
        commit.sort_values(ascending=True, inplace=True, by=['author_date'])

        for c in commit['hash'].tolist():
            gr.checkout(c)
            callback(repo, c)

