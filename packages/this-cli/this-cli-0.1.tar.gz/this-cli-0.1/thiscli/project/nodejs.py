import json
import os

from . import Project
from ..env import short_env_name
from ..util import needs_update, has_command, warn, fatal


def get_npm_cmd(path):
    has_yarn = has_command('yarn')
    has_yarn_lock = os.path.exists(os.path.join(path, 'yarn.lock'))
    has_npm_lock = os.path.exists(os.path.join(path, "package-lock.json"))

    if has_yarn_lock and has_npm_lock:
        warn("Both yarn.lock and package-lock.json found. " +
             "This may result in out-of-sync dependencies.")

    if has_yarn_lock:
        if has_yarn:
            return 'yarn'
        elif has_npm_lock:
            return 'npm'
        else:
            fatal("yarn.lock found but yarn isn't installed")
    elif has_npm_lock:
        return 'npm'
    elif has_yarn:
        return 'yarn'
    return 'npm'


class NodejsProject(Project):
    def __init__(self, cwd):
        super().__init__(cwd)
        with open('package.json') as f:
            self.package = json.load(f)
        self.npm_cmd = get_npm_cmd(self.cwd)

    @classmethod
    def find(cls):
        return cls.find_containing('package.json')

    def ensure_deps(self):
        if needs_update(self.path('package.json'), self.path('node_modules')):
            self.npm('install')

    def npm(self, cmd):
        if not isinstance(cmd, list):
            cmd = [cmd]

        self.cmd([self.npm_cmd] + cmd)

    def has_script(self, script):
        return script in self.package.get('scripts', {})

    def find_script(self, scripts, env):
        if not isinstance(scripts, list):
            scripts = [scripts]

        for script in scripts:
            env_script = script + ':' + short_env_name(env or 'dev')
            if self.has_script(env_script):
                return env_script
            if self.has_script(script):
                return script
        return None

    def npm_script(self, scripts, *args, env=None):
        args = list(args)
        if args and self.npm_cmd == 'npm':
            args = ['--'] + args
        script = self.find_script(scripts, env)

        if script is None:
            fatal("NPM script not found. Looked for: " + ' '.join(scripts))
        self.ensure_deps()
        self.npm(['run', script] + args)

    def build(self):
        self.npm_script('build')

    def run(self, env):
        self.npm_script(['watch', 'start'], env=env)

    def test(self):
        self.npm_script('test')

    def lint(self, fix):
        if fix:
            self.npm_script('lint', '--fix')
        else:
            self.npm_script('lint')
