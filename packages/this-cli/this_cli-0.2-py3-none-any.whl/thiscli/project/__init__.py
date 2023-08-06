from abc import ABC, abstractmethod
from contextlib import contextmanager
import subprocess
import os
import sys
import threading
import click

from ..util import walk_up, fail

local = threading.local()


@contextmanager
def delayed_exit():
    already_delayed = hasattr(local, 'exit_code')
    if not already_delayed:
        local.exit_code = 0
    yield
    if not already_delayed:
        if local.exit_code != 0:
            sys.exit(local.exit_code)
        delattr(local, 'exit_code')


class Project(ABC):
    def __init__(self, cwd):
        self.cwd = cwd
        self.dry_run = False

        from . import ansible
        self.can_deploy = ansible.is_present(self)

    def cmd(self, cmd, cwd=None, env=None, echo=True, shell=None):
        if isinstance(cmd, str):
            cmd = cmd.strip()
        if echo:
            echo_command(cmd, cwd, env)
        if self.dry_run:
            return

        if cwd is not None:
            cwd = self.path(cwd)
        else:
            cwd = self.cwd
        if env is not None:
            env = dict(os.environ, **env)
        if shell is None:
            shell = ' ' in cmd
        proc = subprocess.run(cmd, cwd=cwd, shell=shell, env=env)
        if proc.returncode != 0:
            if hasattr(local, 'exit_code'):
                if local.exit_code == 0:
                    local.exit_code = proc.returncode
            else:
                sys.exit(proc.returncode)

    def path(self, *path):
        return os.path.join(self.cwd, *path)

    def exists(self, *path):
        return os.path.exists(self.path(*path))

    def find_file(self, *paths):
        return next((path for path in paths if self.exists(path)), None)

    def has_action(self, action):
        if isinstance(action, str):
            action_name = action
            action = getattr(type(self), action)
        else:
            action_name = action.__name__
            action = action.__func__
        default_action = getattr(Project, action_name)

        if hasattr(self, 'can_' + action_name):
            return getattr(self, 'can_' + action_name)
        else:
            return action != default_action

    @property
    def actions(self):
        all_actions = [self.build, self.lint, self.test, self.check,
                       self.run, self.deploy]

        return [action.__name__ for action in all_actions
                if self.has_action(action)]

    def info(self):
        from . import ansible
        description = self.description
        if self.deploy.__func__ == Project.deploy and ansible.is_present(self):
            description += ' (deployed using Ansible)'
        click.secho(description, fg='blue', bold=True)
        click.echo()

        click.secho('Available commands:', fg='white', bold=True)
        for action in self.actions:
            print('  ' + action)

    @property
    @abstractmethod
    def description(self):
        pass

    def build(self):
        fail("Sorry! I don't know how to build your project")

    def test(self):
        fail("Sorry! I don't know how to test your project")

    def run(self, env):
        fail("Sorry! I don't know how to run your project")

    def deploy(self, env):
        from . import ansible

        if ansible.is_present(self):
            ansible.deploy(self, env)
        else:
            fail("Sorry! I don't know how to deploy your project")

    def lint(self, fix):
        fail("Sorry! I don't know how to lint your project")

    def check(self):
        if not (self.has_action('lint') or self.has_action('test')):
            fail("Sorry! I don't know how to check your project")

        with delayed_exit():
            if self.has_action('lint'):
                self.lint(fix=False)
            if self.has_action('test'):
                self.test()

    @property
    def can_check(self):
        return self.has_action('lint') or self.has_action('test')

    @classmethod
    @abstractmethod
    def find(cls):
        from .autotools import AutotoolsProject
        from .meson import MesonProject
        from .cmake import CMakeProject
        from .make import MakeProject
        from .nodejs import NodejsProject
        from .python import PythonProject
        from .cargo import CargoProject
        from .ansible import AnsibleProject

        project = Project.find_one_of(AutotoolsProject,
                                      MesonProject,
                                      CMakeProject,
                                      MakeProject,
                                      NodejsProject,
                                      PythonProject,
                                      CargoProject,
                                      AnsibleProject)

        if project is None:
            print("Sorry! I don't recognize your project type")
            sys.exit(1)

        return project

    @classmethod
    def find_containing(cls, *filenames):
        for root, files in walk_up(os.getcwd()):
            if any(filename in files for filename in filenames):
                return cls(root)
            if '.git' in files:
                break
        return None

    @staticmethod
    def find_one_of(*classes):
        for cls in classes:
            project = cls.find()
            if project is not None:
                return project
        return None


def format_command(cmd, cwd, env):
    if isinstance(cmd, list):
        cmd = ' '.join(maybe_quote_arg(arg) for arg in cmd)
    if env is not None:
        cmd = (' '.join(key + '=' + value for key, value in env.items()) +
               ' ' + cmd)
    if cwd is not None:
        cmd = 'cd {} && {}'.format(cwd, cmd)
    return cmd


def echo_command(cmd, cwd, env):
    click.secho('$ ' + format_command(cmd, cwd, env),
                fg='white', bold=True)


def maybe_quote_arg(arg):
    if ' ' not in arg:
        return arg
    elif '"' in arg:
        return "'" + arg + "'"
    return '"' + arg + '"'
