#!/bin/env python3

import os
import sys
import venv
import argparse
import subprocess
import threading
import logging

class Installer(venv.EnvBuilder):
    """
    Create virtual environment, install packages and clone repositories
    """

    PROJECT_NAME = 'extractDataFromWeatherAPI'
    VENV_DIR_NAME = 'venv'

    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.pop('verbose', False)
        self.project_dir = None
        super().__init__(*args, **kwargs)

    def _run_script(self, args, cwd=None):
        """
        Run a script and print output

        :param args: Script arguments
        :param cwd: Execution directory
        """

        if cwd is None: cwd = self.project_dir

        runner = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

        for out in runner.stdout:
            logging.debug(out.decode('utf-8').rstrip())

        for err in runner.stderr:
            logging.debug(err.decode('utf-8').rstrip())

    def post_setup(self, context):

        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.

        :param context: The information for the virtual environment
                        creation request being processed.
        """

        
        logging.info("Upgrading package installer")
        args = [context.env_exe, '-m', 'pip', 'install', '--upgrade', 'pip']
        self._run_script(args)

        logging.info("Installing packages from requirements")
        requirements_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.PROJECT_NAME, 'requirements.txt')
        print("req:", requirements_file)
        args = [context.env_exe, '-m', 'pip', 'install', '-r', requirements_file]
        self._run_script(args)

        os.system("echo 'export PYTHONIOENCODING=utf-8:surrogateescape' >> {}/bin/activate".format(context.env_dir))
        logging.info("Activate environment with 'source {}/bin/activate'".format(context.env_dir))

    def clone_repositories(self, https=False, git_branch='master'):
        """
        Clone a repository into project directory.

        :param https: Use HTTPS instead of SSH to clone.
        :param git_branch: Branch name to be checked out
        """

        os.mkdir(self.project_dir)

        if https:
            repo_url = "https://github.com/potruamani/extractDataFromWeatherAPI.git"
        else:
            repo_url = "git@github.com:potruamani/extractDataFromWeatherAPI.git"

        clone_args = ['/usr/bin/git', 'clone','-b',git_branch,'--progress', repo_url]

        logging.info("Cloning the repository '{}'".format(repo_url))
        self._run_script(clone_args)
       
        if not os.path.isdir(os.path.join(self.project_dir,'extractDataFromWeatherAPI')):
            print("extractDataFromWeatherAPI is not cloned , use --help for more options")
            sys.exit(1)
            

    def install(self, args):
        """
        Validate install directories and create the environment
        """

        if not os.path.isdir(args.dir):
            raise ValueError("Install directory '{}' is invalid".format(args.dir))

        self.project_dir = os.path.join(args.dir, self.PROJECT_NAME)

        if os.path.isdir(self.project_dir):
            raise ValueError("Project directory '{}' already exists".format(self.project_dir))

        self.clone_repositories(args.https, args.branch)

        venv_dir = os.path.join(self.project_dir, self.VENV_DIR_NAME)

        logging.info("Creating a virtual environment '{}'".format(venv_dir))
        self.create(venv_dir)

def main():
    if sys.version_info < (3, 3):
        raise ValueError('This script is only for use with Python 3.3 or later')

    parser = argparse.ArgumentParser(description='codescore development environment installer', conflict_handler='resolve')

    parser.add_argument('--dir', help='Install directory', default=os.getcwd())
    parser.add_argument('--https', help='Use HTTPS for cloning repositories', action='store_true')
    parser.add_argument('--verbose', help='Verbose mode; show install log', action='store_true')
    parser.add_argument('--branch', help='Git branch to be used', default='master')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose  else logging.INFO,
        format='%(asctime)s %(levelname)-5s: %(message)s',
        datefmt="%H:%M:%S")

    installer = Installer(clear=True, with_pip=True, verbose=args.verbose)

    try:
        installer.install(args)
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    main()
