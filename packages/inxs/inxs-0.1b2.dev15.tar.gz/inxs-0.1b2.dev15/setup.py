#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from sys import version_info

try:
    # pip < 10
    from pip import main as pip
except ImportError:
    # pip 10
    from pip._internal import main as pip


if version_info < (3, 6):
    raise RuntimeError("Requires Python 3.6 or later.")

VERSION = '0.1b2.dev15'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


class lxmlInstall():
    @staticmethod
    def check_lxml():
        try:
            from lxml import etree  # noqa: F401
        except ImportError:
            return False
        else:
            return True

    @staticmethod
    def check_smart_prefix():
        # FIXME for some reason this check doesn't work
        #       in a repl no exception is thrown either
        from lxml import etree
        evaluator = etree.XPathEvaluator(etree.Element('x'))
        try:
            evaluator('/*', smart_prefix=True)
        except TypeError as e:
            if "got an unexpected keyword argument 'smart_prefix'" in str(e):
                return False
            raise
        else:
            return True

    def ensure_lxml_with_smart_prefix(self):
        if not self.check_lxml():
            self.install_lxml()
        elif not self.check_smart_prefix():
            pip(['uninstall', '--yes', '-v', 'lxml'])
            self.install_lxml()

    def install_lxml(self):
        # FIXME use verbosity levels from the invokation of this file
        # FIXME check success of subprocesses and abort in case of failure
        try:
            import cython  # noqa: F401
        except ImportError:
            cython_was_installed = False
            pip(['install', '-v', 'cython'])
        else:
            cython_was_installed = True

        pip(['install', '-v',
             'https://github.com/funkyfuture/lxml/tarball/smart_xpath#egg=lxml'])

        if not cython_was_installed:
            pip(['uninstall', '--yes', '-v', 'cython'])


class Develop(lxmlInstall, develop):
    def run(self):
        self.ensure_lxml_with_smart_prefix()
        super().run()


class Install(lxmlInstall, install):
    def run(self):
        self.ensure_lxml_with_smart_prefix()
        self.do_egg_install()


setup(
    name='inxs',
    version=VERSION,
    description="A framework for XML transformations without boilerplate.",
    long_description=readme + '\n\n' + history,
    author="Frank Sachsenheim",
    author_email='funkyfuture@riseup.net',
    url='https://github.com/funkyfuture/inxs',
    packages=['inxs'],
    package_dir={'inxs': 'inxs'},
    include_package_data=True,
    cmdclass={'develop': Develop, 'install': Install},
    install_requires=('cssselect', 'dependency_injection'),
    license="ISC license",
    zip_safe=False,
    entry_points={'console_scripts': ['inxs = inxs.cli:main']},
    keywords='inxs xml processing transformation framework xslt not-xslt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    test_suite='tests',
    tests_require=['pytest', 'pytest-runner']  # TODO full test cmd config
)
