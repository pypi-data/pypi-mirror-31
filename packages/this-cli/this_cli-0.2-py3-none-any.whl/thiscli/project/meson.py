import os

from . import Project


class MesonProject(Project):
    description = 'Meson project'

    @classmethod
    def find(cls):
        return cls.find_containing('meson.build')

    def ensure_builddir(self):
        if self.exists('build/build.ninja'):
            return

        os.makedirs('build', exist_ok=True)

        self.cmd('meson setup build --prefix=$HOME/.local')

    def build(self):
        self.ensure_builddir()
        self.cmd('ninja -C build')

    def test(self):
        self.ensure_builddir()
        self.cmd('ninja -C build test')
