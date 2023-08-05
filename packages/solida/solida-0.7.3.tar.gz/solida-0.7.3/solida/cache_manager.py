import os

from comoda import a_logger, ensure_dir, path_is_empty
from git import Repo

from .__details__ import cache_dir
from .config_manager import ConfigurationManager
from .pipelines_manager import Pipeline


class CacheManager:
    def __init__(self, args=None):
        self.loglevel = args.loglevel
        self.logfile = args.logfile
        self.logger = a_logger(self.__class__.__name__, level=self.loglevel,
                               filename=self.logfile)
        path_from_cli = args.config_file if args.config_file else None
        cm = ConfigurationManager(args=args,
                                  path_from_cli=path_from_cli)
        self.conf = cm.get_pipelines_config
        self.cache_dir = cache_dir
        ensure_dir(self.cache_dir)

    def clone(self, label):
        pipeline = Pipeline(self.conf[label], loglevel=self.loglevel,
                            logfile=self.logfile)
        repo_dir = os.path.join(self.cache_dir, label)
        ensure_dir(repo_dir)
        if path_is_empty(repo_dir):
            print("Cloning {}".format(pipeline.url))
            Repo.clone_from(pipeline.url, repo_dir)
            repo = Repo(repo_dir)
            heads = repo.heads
            master = heads.master
            print("commit id: {}".format(master.commit))
            print("Done.")
            self.logger.info('Cloned git repo at {} into {} '
                             'directory'.format(pipeline.url, repo_dir))
        else:
            self.logger.warning("Can't clone git repo {} "
                                "into {}".format(pipeline.url,
                                                 repo_dir))

    def clones(self):
        for p in self.conf.keys():
            self.clone(p)

    def update(self, label):
        repo_dir = os.path.join(self.cache_dir, label)
        ensure_dir(repo_dir, force=True)
        self.clone(label)

    def updates(self):
        for p in self.conf.keys():
            self.update(p)
