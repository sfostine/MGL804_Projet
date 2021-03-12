import datetime
import os
import shutil

import pandas as pd
from pydriller import RepositoryMining, GitRepository

from src.main.python.detector.DetectorStrategy import DetectorStrategy


class RepoHelper:
    """https://pydriller.readthedocs.io/en/latest/

    """
    repo_exist_msg = "Repo \"{}\" already exist.\n\t- to clone remote set \"replace_existing\" = true in \"config.json\""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.detectors = list()

    def clone_all_repo(self):
        """
        Clone repository and list all commits in (resources/data/commit).
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

    def add_detectors(self, detector: DetectorStrategy):
        self.detectors.append(detector)

    def checkout_all_commit(self, repo_cfg: dict):

        gr = GitRepository(path=self.cfg['paths']['repo'] + repo_cfg['name'])

        df = pd.read_csv(self.cfg['paths']['commit_report'] + repo_cfg['commit_file'], header=0)
        df.sort_values(ascending=True, inplace=True, by=['author_date'])

        for commit in df['hash'].tolist():
            gr.checkout(commit)
            repo_cfg['commit'] = commit
            for detector in self.detectors:
                detector.run_on(repo_cfg)
