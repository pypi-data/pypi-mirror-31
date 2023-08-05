import itertools
import os
import re
import shlex
import shutil
import subprocess
import sys
import types
import venv
from pathlib import Path

from .__metadata__ import package_metadata
from .cli import support
from .cli.click import api as click
from .errors import InterpreterNotFound, InvalidEnvironmentError, PathNotFoundError

__all__ = ('create', 'enter', 'remove', 'show_envs', 'show_version')


class VenvBuilder(venv.EnvBuilder):

    def create(self, env_dir, executable=None):
        """
        Create a virtual environment in a directory.

        Args:
            env_dir (str): The target directory to create an environment in.
            executable (str, optional): path to python interpreter executable [default: sys.executable]
        """
        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir=env_dir, executable=executable)
        # See issue 24875. We need system_site_packages to be False
        # until after pip is installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = False
        self.create_configuration(context)
        self.setup_python(context)
        if self.with_pip:
            self._setup_pip(context)
        if not self.upgrade:
            self.setup_scripts(context)
            self.post_setup(context)
        if true_system_site_packages:
            # We had set it to False before, now
            # restore it and rewrite the configuration
            self.system_site_packages = True
        self.create_configuration(context)

    def ensure_directories(self, env_dir, executable=None):
        """
        Create the directories for the environment.
        Returns a context object which holds paths in the environment,
        for use by subsequent logic.

        Args:
            env_dir (str): path to environment
            executable (str, optional): path to python interpreter executable [default: sys.executable]

        Returns:
            types.SimpleNamespace: context
        """

        def create_if_needed(d):
            if not os.path.exists(d):
                os.makedirs(d)
            elif os.path.islink(d) or os.path.isfile(d):
                raise ValueError('Unable to create directory %r' % d)

        executable = executable or sys.executable
        if os.path.exists(env_dir) and self.clear:
            self.clear_directory(env_dir)
        context = types.SimpleNamespace()
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt if self.prompt is not None else context.env_name
        context.prompt = '(%s) ' % prompt
        create_if_needed(env_dir)
        dirname, exename = os.path.split(os.path.abspath(executable))
        context.executable = executable
        context.python_dir = dirname
        context.python_exe = exename
        if sys.platform == 'win32':
            binname = 'Scripts'
            incpath = 'Include'
            libpath = os.path.join(env_dir, 'Lib', 'site-packages')
        else:
            binname = 'bin'
            incpath = 'include'
            libpath = os.path.join(env_dir, 'lib', exename, 'site-packages')
        context.inc_path = path = os.path.join(env_dir, incpath)
        create_if_needed(path)
        create_if_needed(libpath)
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        if (sys.maxsize > 2**32) and (os.name == 'posix') and (sys.platform != 'darwin'):
            link_path = os.path.join(env_dir, 'lib64')
            if not os.path.exists(link_path):   # Issue #21643
                os.symlink('lib', link_path)
        context.bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_name = binname
        context.env_exe = os.path.join(binpath, exename)
        create_if_needed(binpath)
        return context

    def _setup_pip(self, context):
        """Installs or upgrades pip in a virtual environment"""
        # We run ensurepip in isolated mode to avoid side effects from
        # environment vars, the current directory and anything else
        # intended for the global Python environment
        # Originally -Im, but -Esm works on both python2 and python3
        cmd = [context.env_exe, '-Esm', 'ensurepip', '--upgrade',
                                                     '--default-pip']
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)


def create(path, site_packages=None, overwrite=None, symlinks=None, upgrade=None, include_pip=None, prompt=None, python=None, verbose=None, interactive=None, dry_run=None):
    """Creates a virtual environment

    Notes: Wraps venv

    Args:
        path (str): path to virtual environment

        site_packages (bool, optional): use system packages within environment [default: False]
        overwrite (bool, optional): replace target folder [default: False]
        symlinks (bool, optional): create symbolic link to Python executable [default: True]
        upgrade (bool, optional): Upgrades existing environment with new Python executable [default: False]
        include_pip (bool, optional): Includes pip within virtualenv [default: True]
        prompt (str, optional): Modifies prompt
        python (str, optional): Version of python, python executable or path to python

        verbose (int, optional): more output [default: 0]
        interactive (bool, optional): ask before updating system [default: False]
        dry_run (bool, optional): do not update system

    Returns:
        str: path to venv
    """
    verbose = verbose or 0
    path = os.path.expanduser(path) if path.startswith('~') else os.path.abspath(path)
    name = os.path.basename(path)
    builder = _get_builder(path=path, site_packages=site_packages, overwrite=overwrite, symlinks=symlinks, upgrade=upgrade, include_pip=include_pip, prompt=prompt)
    prompt = f'Create virtual environment "{name}" under: {path}?'
    run_command = click.confirm(prompt) if interactive else True
    if run_command:
        if not dry_run:
            executable = _get_interpreter(python)
            if not executable:
                raise InterpreterNotFound(version=python)
            builder.create(env_dir=path, executable=executable)
        support.echo('Created virtual environment "' + click.style(name, fg='yellow') + " under: " + click.style(path, fg='green'), verbose=verbose)
    return path


def enter(path, command=None, verbose=None):
    """Enters a virtual environment

    Args:
        path (str): path to virtual environment
        command (tuple|list|str, optional): command to run in virtual env [default: shell]
        verbose (int, optional): Adds more information to stdout
    """
    verbose = verbose or 0
    path = os.path.expanduser(path) if path.startswith('~') else os.path.abspath(path)
    shell = os.getenv("SHELL")
    command = command or shell
    env = _update_environment(path)
    venv_name = click.style(Path(path).name, fg='green')

    # Setup the environment variables
    # TODO: Expand this with configuration code
    # Activate and run
    cmd_display = command
    if not isinstance(command, str):
        command = " ".join(command)
        cmd_display = click.style(command, fg='green')
        if Path(shell).name in ['bash', 'zsh']:
            command = f'{shell} -i -c \"{command}\"'
            cmd_display = f'{shell} -i -c \"{cmd_display}\"'
    support.echo(click.style(f'Running command in "', fg='blue') + venv_name + click.style(f'": ', fg='blue') + cmd_display, verbose=max(verbose - 1, 0))
    return_code = subprocess.call(command, shell=True, env=env, universal_newlines=True)
    rc_color = 'green' if return_code == 0 else 'red'
    rc = click.style(str(return_code), fg=rc_color)
    support.echo(click.style('Command return code: ', fg='blue') + rc, verbose=verbose)
    return return_code


def find_environment_folders(path=None):
    path = path or os.getenv('WORKON_HOME') or os.path.join(os.getenv('HOME'), '.virtualenvs')
    for root, directories, files in os.walk(path):
        found = []
        for index, name in enumerate(directories):
            directory = os.path.join(root, name)
            if not validate_environment(directory):
                continue
            yield name, directory
            found.append(name)
        # This makes the search "fast" by skipping out on folders
        #  that do not need to be searched because they have already
        #  been identified as valid environments
        directories[:] = [d for d in directories if d not in found]


def remove(path, verbose=None, interactive=None, dry_run=None, check=None):
    """Remove a virtual environment

    Args:
        path (str): path to virtual environment
        verbose (int, optional): more output [default: 0]
        interactive (bool, optional): ask before updating system [default: False]
        dry_run (bool, optional): do not update system
        check (bool, optional): Raises PathNotFoundError if True and path isn't found [default: False]

    Raises:
        PathNotFoundError:  when check is True and path is not found

    Returns:
        str: folder path removed
    """
    verbose = verbose or 0
    check = False if check is None else check
    path = os.path.expanduser(path) if path.startswith('~') else os.path.abspath(path)
    if not validate_environment(path) and check is True:
        raise InvalidEnvironmentError(path=path)
    prompt = f'Remove {path}?'
    run_command = click.confirm(prompt) == 'y' if interactive else True
    if run_command and not dry_run:
        if os.path.exists(path):
            shutil.rmtree(path)
        elif check is True:
            raise PathNotFoundError(path=path)
    support.echo(click.style('Removed: ', fg='blue') + click.style(path, fg='green'), verbose=(max(verbose - 1, 0) and path))
    return path


def show_envs(path=None):
    path = path or os.getenv('WORKON_HOME')
    for name, path in find_environment_folders(path=path):
        print(f'Found {click.style(name, fg="yellow")} under: {click.style(path, fg="yellow")}')


def show_version():
    support.echo(f"{package_metadata['name']} {package_metadata['version']}")


def validate_environment(path, check=None):
    """Validates if path is a virtual environment

    Args:
        path (str): path to virtual environment
        check (bool, optional): Raise an error if path isn't valid

    Raises:
        InvalidEnvironmentError: when environment is not valid

    Returns:
        bool: True if valid virtual environment path
    """
    path = Path(path)
    valid = None
    win32 = sys.platform == 'win32'
    # Expected structure
    structure = {
        'bin': 'Scripts' if win32 else 'bin',
        'include': 'Include' if win32 else 'include',
        'lib': os.path.join('Lib', 'site-packages') if win32 else os.path.join('lib', '*', 'site-packages'),
        }
    paths = {}
    for identifier, expected_path in structure.items():
        for p in path.glob(expected_path):
            # There should only be one path that matches the glob
            paths[identifier] = p
            break
    for identifier in structure:
        if identifier not in paths:
            valid = False
            if check:
                raise InvalidEnvironmentError(f'Could not find {structure[identifier]} under {path}.')

    if valid is not False and win32:
        # TODO: Add more validation for windows environments
        valid = valid is not False and True
    elif valid is not False:
        # check for activation scripts
        activation_scripts = list(paths['bin'].glob('activate.*'))
        valid = valid is not False and len(activation_scripts) > 0
        if check and valid is False:
            raise InvalidEnvironmentError(f'Could not find activation scripts under {path}.')

        # check for pyvenv.cfg
        pyvenv_config = paths['bin'].parent.joinpath('pyvenv.cfg')
        valid = valid is not False and pyvenv_config.exists()
        if check and valid is False:
            raise InvalidEnvironmentError(f'Could not find pyvenv.cfg under {path}.')

        # check for python binaries
        python_name = paths['lib'].parent.name
        python_ver_data = re.search('(?P<interpreter>python|pypy)\.?(?P<major>\d+)(\.?(?P<minor>\d+))', python_name)
        if python_ver_data:
            python_ver_data = python_ver_data.groupdict()
            python_executable = paths['bin'].joinpath('python')
            python_ver_executable = paths['bin'].joinpath(python_name)
            if python_executable.exists():
                valid = valid is not False and True
            if check and valid is False:
                raise InvalidEnvironmentError(f'Could not find python executable under {path}.')
            if python_ver_executable.exists():
                valid = valid is not False and True
            if check and valid is False:
                raise InvalidEnvironmentError(f'Could not find {python_name} executable under {path}.')

    return valid


# ----------------------------------------------------------------------
# Support
# ----------------------------------------------------------------------
def _get_builder(path, site_packages=None, overwrite=None, symlinks=None, upgrade=None, include_pip=None, prompt=None):
    path = os.path.expanduser(path) if path.startswith('~') else os.path.abspath(path)
    name = os.path.basename(path)
    builder = VenvBuilder(
        system_site_packages=False if site_packages is None else site_packages,
        clear=False if overwrite is None else overwrite,
        symlinks=True if symlinks is None else symlinks,
        upgrade=False if upgrade is None else upgrade,
        with_pip=True if include_pip is None else include_pip,
        prompt=f'({name})' if prompt is None else prompt,
        )
    return builder


def _get_interpreter(python=None):
    """Returns the interpreter given the string"""
    if python is None:
        return sys.executable

    # Maybe the path is already supplied
    if Path(python).exists():
        return python

    # Guess path
    paths = [os.path.join(path, '') for path in os.getenv('PATH').split(':')]
    if not python.startswith('p'):
        python = f'python{python}'
    interpreters = [python]
    interpreter_paths = list(map(''.join, itertools.chain(itertools.product(paths, interpreters))))
    for path in interpreter_paths:
        path = os.path.realpath(path)
        if os.path.exists(path):
            return path


def _update_environment(path):
    """Updates environment similar to activate from venv"""
    path = os.path.expanduser(path) if path.startswith('~') else os.path.abspath(path)
    name = os.path.basename(path)

    env = {k: v for k, v in os.environ.items()}
    env[package_metadata['name'].upper()] = name

    venv = f'{click.style("vsh", fg="magenta")} {click.style(name, fg="yellow")}'

    env['VIRTUAL_ENV'] = path
    env['PATH'] = ':'.join([os.path.join(env.get('VIRTUAL_ENV'), 'bin')] + env['PATH'].split(':'))

    shell = Path(env.get('SHELL') or '/bin/sh').name
    disable_prompt = env.get('VIRTUAL_ENV_DISABLE_PROMPT') or None
    if not disable_prompt:
        if shell in ('bash', 'sh'):
            ps1 = env.get("PS1") or click.style("\w", fg="blue") + "\$ "
            env['PS1'] = f'{venv} {ps1}'
        elif shell in ('zsh',):
            env['PROMPT'] = f'{venv} {env.get("PROMPT") or ""}'
        else:
            """TODO: Fix this for fish, csh, others, etc."""

    return env
