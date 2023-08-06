"""
Part of the kecpkg-tools project.

Parts are borrowed from hatch Those parts are are released under the MIT license
"""
import fnmatch
import os
import platform
import re
import shutil
import sys
from contextlib import contextmanager

import six

from kecpkg.commands.utils import echo_failure, echo_info, echo_warning


def ensure_dir_exists(d):
    """Ensure that directory exists, otherwise make directory."""
    if not os.path.exists(d):
        os.makedirs(d)


def create_file(filepath, content=None, overwrite=True):
    """
    Create file and optionally fill it with content.

    Will overwrite file already in place if overwrite flag is set

    :param filepath: full path to a file to create
    :param content:
    :return:
    """
    ensure_dir_exists(os.path.dirname(os.path.abspath(filepath)))
    # if overwrite is set to True overwrite file, otherwise if file exist, exit.

    if not os.path.exists(filepath) or (os.path.exists(filepath) and overwrite):
        with open(filepath, 'w') as fd:
            # os.utime(filepath, times=None)
            if content:
                fd.write(content)
    else:
        echo_failure("File '{}' already exists.".format(filepath))
        sys.exit(1)


def copy_path(sourcepath, destpath):
    """
    Copy path.

    :param sourcepath: source path to copy from, if dir, copy subtree
    :param destpath: destination path to copy to
    """
    if os.path.isdir(sourcepath):
        if six.PY3:
            shutil.copytree(sourcepath, os.path.join(destpath, basepath(sourcepath)),
                            copy_function=shutil.copy)
        else:
            shutil.copytree(sourcepath, os.path.join(destpath, basepath(sourcepath)))

    else:
        shutil.copy(sourcepath, destpath)


def remove_path(path):
    """
    Remove directory structure.

    :param path: path to remove
    """
    try:
        shutil.rmtree(path)
    except (IOError, OSError):
        try:
            os.remove(path)
        except (IOError):
            pass


def basepath(path):
    """Get full basepath from path."""
    return os.path.basename(os.path.normpath(path))


def normalise_name(raw_name):
    """
    Normalise the name to be used in python package allowable names.

    conforms to PEP-423 package naming conventions

    :param raw_name: raw string
    :return: normalised string
    """
    return re.sub(r"[-_. ]+", "_", raw_name).lower()


def get_package_dir(package_name=None, fail=True):
    """
    Check and retrieve the package directory.

    :param package_name: (optional) package name
    :param fail: (optional, default=True) fail hard with exit when no package dir found
    :return: full path name to the package directory
    """
    from kecpkg.settings import SETTINGS_FILENAME

    def _inner(d):
        if os.path.exists(os.path.join(d, SETTINGS_FILENAME)):
            return d
        elif os.path.exists(os.path.join(d, 'package_info.json')):
            return d
        else:
            return None

    package_dir = _inner(os.getcwd())
    if not package_dir:
        package_dir = _inner(os.path.join(os.getcwd(), package_name))
    if not package_dir:
        package_dir = _inner(package_name)
    if not package_dir:
        echo_failure('This does not seem to be a package in path `{}` - please check that there is a '
                     '`package_info.json` or a `{}`'.format(package_dir, SETTINGS_FILENAME))
        if fail:
            sys.exit(1)
    else:
        return package_dir


def get_package_name():
    """
    Provide the name of the package (in current dir).

    :param fail: ensure that directory search does not fail in a exit.
    :return: package name or None
    """
    package_dir = get_package_dir(fail=False)
    if package_dir:
        return os.path.basename(package_dir)
    else:
        return None


def get_artifacts_on_disk(root_path, additional_exclude_paths=None, default_exclude_paths=None, verbose=False):
    """
    Retrieve all artifacts on disk.

    :param root_path: root_path to collect all artifacts from
    :param exclude_paths: (optional) directory names and filenames to exclude
    :return: dictionary with {'property_id': ['attachment_path1', ...], ...}
    """
    from kecpkg.settings import EXCLUDE_IN_BUILD
    exclude_paths = default_exclude_paths or EXCLUDE_IN_BUILD
    if verbose:
        echo_info("basic excluded paths are: `{}`".format(exclude_paths))

    # get additional exclude paths from the settings file
    if additional_exclude_paths and isinstance(additional_exclude_paths, list):
        exclude_paths.extend(additional_exclude_paths)
        if verbose:
            echo_info("additional exclude paths are: `{}`".format(additional_exclude_paths))

    if not os.path.exists(root_path):
        echo_failure("The root path: '{}' does not exist".format(root_path))
        sys.exit(1)

    # getting all attachments
    artifacts = []
    for root, dirs, filenames in os.walk(root_path, topdown=True):
        for exclude_path in exclude_paths:
            if exclude_path in dirs:
                dirs.remove(exclude_path)
                if verbose:
                    echo_warning("Ignored path `{}`".format(exclude_path))

        for filename in filenames:
            # print([(filename,ptrn,fnmatch.fnmatch(filename, ptrn)) for ptrn in exclude_paths])
            if not any([fnmatch.fnmatch(filename, ptrn) for ptrn in exclude_paths]):
                full_artifact_subpath = '{}{}{}'.format(root, os.path.sep, filename). \
                    replace('{}{}'.format(root_path, os.path.sep), '')
                artifacts.append(full_artifact_subpath)
                if verbose:
                    echo_info('Found `{}`'.format(full_artifact_subpath))
            else:
                if verbose:
                    echo_warning('Ignored `{}`'.format(filename))

    if verbose:
        echo_info('{}'.format(artifacts))
    return artifacts


def render_package_info(settings, package_dir, backup=True):
    """Render a new package_info.json based on the settings.

    :param settings: settings
    :param package_dir: directory where to put the package_info.json
    :param backup: (optional) if set to True the original package_info will be backed-up
    :return:
    """
    package_info_filename = 'package_info.json'
    package_info_path = os.path.join(package_dir, package_info_filename)
    if backup and os.path.exists(package_info_path):
        if os.path.exists("{}-dist".format(package_info_path)):
            os.remove("{}-dist".format(package_info_path))
        os.rename(package_info_path, "{}-dist".format(package_info_path))
    elif os.path.exists(package_info_path):
        os.remove(package_info_path)

    from kecpkg.files.rendering import render_to_file
    render_to_file(package_info_filename,
                   content=dict(requirements_txt='requirements.txt',
                                entrypoint_script=settings.get('entrypoint_script'),
                                entrypoint_func=settings.get('entrypoint_func')),
                   target_dir=package_dir)


# Python Operation regarding Virtual environments
# Graceously borrowed From hatch package.

__platform = platform.system()
ON_MACOS = os.name == 'mac' or __platform == 'Darwin'
ON_WINDOWS = NEED_SUBPROCESS_SHELL = os.name == 'nt' or __platform == 'Windows'
VENV_FLAGS = {
    '_HATCHING_',
    'VIRTUAL_ENV',
    'CONDA_PREFIX',
}


def venv_ignored():
    """
    Check if virtual env is to be ignored.

    Graceously borrowed From hatch package.
    """
    return os.environ.get('_IGNORE_VENV_') == '1'


def venv_active():
    """
    Check if virtual env is active.

    Graceously borrowed From hatch package.
    """
    return bool(VENV_FLAGS & set(os.environ)) and not venv_ignored()


def get_proper_python():  # no cov
    """
    Retrieve the proper python version on the platform.

    Graceously borrowed From hatch package.
    """
    if not venv_active():
        default_python = os.environ.get('_DEFAULT_PYTHON_', None)
        if default_python:
            return default_python
        elif not ON_WINDOWS:
            return 'python3'
    return 'python'


def get_proper_pip():  # no cov
    """
    Retrieve the propery pip executable on the platform.

    Graceously borrowed From hatch package.
    """
    if not venv_active():
        default_pip = os.environ.get('_DEFAULT_PIP_', None)
        if default_pip:
            return default_pip
        elif not ON_WINDOWS:
            return 'pip3'
    return 'pip'


def locate_exe_dir(d, check=True):
    """
    Locate the python or pip executables on the platform.

    Graceously borrowed From hatch package.
    """
    exe_dir = os.path.join(d, 'Scripts') if ON_WINDOWS else os.path.join(d, 'bin')
    if check and not os.path.isdir(exe_dir):
        raise OSError('Unable to locate python virtual environment executables directory.')
    return exe_dir


@contextmanager
def env_vars(evars, ignore=None):
    """
    Contextmanager to provide filtering on the environment variables already on the system.

    Graceously borrowed From hatch package.

    :param evars: new environment variables to inject or override
    :param ignore: ignored environment variables
    :return: context in which the environment variable dictionary is rewritten
    """
    ignore = ignore or {}
    ignored_evars = {}
    old_evars = {}

    for ev in evars:
        if ev in os.environ:
            old_evars[ev] = os.environ[ev]
        os.environ[ev] = evars[ev]

    for ev in ignore:
        if ev in os.environ:  # no cov
            ignored_evars[ev] = os.environ[ev]
            os.environ.pop(ev)

    try:
        yield
    finally:
        for ev in evars:
            if ev in old_evars:
                os.environ[ev] = old_evars[ev]
            else:
                os.environ.pop(ev)

        for ev in ignored_evars:
            os.environ[ev] = ignored_evars[ev]


@contextmanager
def venv(venv_path, evars=None):
    """
    Operate within the confines of a virtual environment.

    Graceously borrowed From hatch package.

    :param venv_path: virtual environment path
    :param evars: additional environment variables, which will be overwritten
    :return: context in which the virtual environment directory is set to the venv_path.
    """
    venv_exe_dir = locate_exe_dir(venv_path)

    evars = evars or {}
    evars['_HATCHING_'] = '1'
    evars['VIRTUAL_ENV'] = venv_path
    evars['PATH'] = '{}{}{}'.format(
        venv_exe_dir, os.pathsep, os.environ.get('PATH', '')
    )

    with env_vars(evars, ignore={'__PYVENV_LAUNCHER__'}):
        yield venv_exe_dir
