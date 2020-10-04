import pathlib
import subprocess
import sys
import typing
import warnings

try:
    from IPython.core import interactiveshell
    from IPython.core import magic
    IPYTHON_INSTALLED = True
except ImportError:
    IPYTHON_INSTALLED = False


THEME = 'mario'


__all__ = [
    'error',
    'info',
    'notify_exceptions',
    'play_wav',
    'success'
    'theme',
    'themes',
    'warning'
]


def run(command: str, silent: bool):

    if silent:
        subprocess.Popen(command, shell=True, stderr=subprocess.DEVNULL)

    else:

        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            warnings.warn(f'{e} stderr: {e.stderr.decode().strip()}')


def play_wav(path: pathlib.Path, silent=False):
    """Play a .wav file.

    This function is platform agnostic, meaning that it will determine what to do based on
    the `sys.platform` variable.

    Parameters:
        path: Path to a .wav file.
        silent: A warning will be issued if something goes wrong and this is `True`. No warning
            will be issued if `False`. Note that setting this to `True` means the call will block
            until the .wav file is finished, whereas using `False` will play the .wav file in a
            separate process.

    Raises:
        RuntimeError: If the platform is not supported.

    """

    if sys.platform == 'darwin':
        run(f'afplay {path}', silent)
    else:
        raise RuntimeError(f'Unsupported platform ({sys.platform})')


def themes_dir() -> pathlib.Path:
    """Return the directory where the themes are located."""
    here = pathlib.Path(__file__).parent
    return here.joinpath('themes')


def current_theme_dir() -> pathlib.Path:
    """Return the current theme's sound directory."""
    return themes_dir().joinpath(THEME)


def themes() -> typing.Set[str]:
    """Return the themes to choose from."""
    return set(theme.name for theme in themes_dir().iterdir())


def theme(name: str = None):
    """Set the current theme.

    Parameters:
        name: The current theme is returned if `None`. The change will be switched if a valid name
            is provided.

    Raises:
        ValueError: If the theme is unknown.

    """

    global THEME

    if name is None:
        return THEME

    if name not in themes():
        raise ValueError(f'Unknown theme ({name})')

    THEME = name


def notify(event: str, silent: bool):
    path = current_theme_dir().joinpath(f'{event}.wav')
    if not path.exists():
        raise ValueError(f'{path} is undefined')
    play_wav(path, silent)


def success(silent=True):
    """Make a success sound.

    Parameters:
        silent: A warning will be issued if something goes wrong and this is `True`. No warning
            will be issued if `False`. Note that setting this to `True` means the call will block
            until the .wav file is finished, whereas using `False` will play the .wav file in a
            separate process.

    """
    return notify('success', silent)


def warning(silent=True):
    """Make a warning sound.

    Parameters:
        silent: A warning will be issued if something goes wrong and this is `True`. No warning
            will be issued if `False`. Note that setting this to `True` means the call will block
            until the .wav file is finished, whereas using `False` will play the .wav file in a
            separate process.

    """
    return notify('warning', silent)


def error(silent=True):
    """Make an error sound.

    Parameters:
        silent: A warning will be issued if something goes wrong and this is `True`. No warning
            will be issued if `False`. Note that setting this to `True` means the call will block
            until the .wav file is finished, whereas using `False` will play the .wav file in a
            separate process.

    """
    return notify('error', silent)


def info(silent=True):
    """Make a generic information sound.

    Parameters:
        silent: A warning will be issued if something goes wrong and this is `True`. No warning
            will be issued if `False`. Note that setting this to `True` means the call will block
            until the .wav file is finished, whereas using `False` will play the .wav file in a
            separate process.

    """
    return notify('info', silent)


def notify_exceptions():
    """Will call error() whenever an exception occurs."""

    def except_hook(exctype, value, traceback):
        error(silent=True)
        sys.__excepthook__(exctype, value, traceback)
    sys.excepthook = except_hook

    if IPYTHON_INSTALLED:

        class Watcher:

            def __init__(self, ipython):
                self.shell = ipython

            def post_run_cell(self, result):
                print(dir(result))
                if result.error_in_exec:
                    error(silent=True)

        # If IPYTHON_INSTALLED, then IPython is imported, which means get_ipython is available
        ipython = get_ipython()
        watcher = Watcher(ipython)
        ipython.events.register('post_run_cell', watcher.post_run_cell)


if IPYTHON_INSTALLED:

    @magic.magics_class
    class HornMagics(magic.Magics):

        @magic.line_cell_magic
        def horn(self, line, cell=None):

            def run(code):
                try:
                    exec(line)
                    success()
                except Exception as e:
                    error()

            if cell is None:
                run(line)
            else:
                run(cell)

    def load_ipython_extension(ipython):
        ipython.register_magics(HornMagics)