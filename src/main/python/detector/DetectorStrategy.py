from abc import ABC, abstractmethod


class DetectorStrategy(ABC):

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def run_on(self, repo_cfg: dict, commit_hash: str):
        self._execute_jar(repo_cfg)
        self._format_data(repo_cfg, commit_hash)

    @abstractmethod
    def _execute_jar(self, repo_cfg: dict):
        pass

    @abstractmethod
    def _format_data(self, repo_cfg: dict, commit_hash: str):
        pass
