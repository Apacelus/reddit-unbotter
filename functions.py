import contextlib
import subprocess
import sys
from pathlib import Path
from threading import Thread
from time import sleep
from urllib.request import urlopen, urlretrieve


#######################################################################################
#                               PATHLIB FUNCTIONS                                     #
#######################################################################################
# unlink all files in a directory and remove the directory
def rmdir(rm_dir: str, keep_dir: bool = True) -> None:
    def unlink_files(path_to_rm: Path) -> None:
        try:
            for file in path_to_rm.iterdir():
                if file.is_file():
                    file.unlink()
                else:
                    unlink_files(path_to_rm)
        except FileNotFoundError:
            print(f"Couldn't remove non existent directory: {path_to_rm}, ignoring")

    # convert string to Path object
    rm_dir_as_path = Path(rm_dir)
    try:
        unlink_files(rm_dir_as_path)
    except RecursionError:  # python doesn't work for folders with a lot of subfolders
        print(f"Failed to remove {rm_dir} with python, using bash")
        bash(f"rm -rf {rm_dir_as_path.absolute().as_posix()}/*")
    # Remove emtpy directory
    if not keep_dir:
        try:
            rm_dir_as_path.rmdir()
        except FileNotFoundError:  # Directory doesn't exist, because bash was used
            return


# remove a single file
def rmfile(file: str, force: bool = False) -> None:
    if force:  # for symbolic links
        Path(file).unlink(missing_ok=True)
    file_as_path = Path(file)
    with contextlib.suppress(FileNotFoundError):
        file_as_path.unlink()


# make directory
def mkdir(mk_dir: str, create_parents: bool = False) -> None:
    mk_dir_as_path = Path(mk_dir)
    if not mk_dir_as_path.exists():
        mk_dir_as_path.mkdir(parents=create_parents)


def path_exists(path_str: str) -> bool:
    return Path(path_str).exists() if path_str else False  # return False if path_str is None/empty


def get_full_path(path_str: str) -> str:
    return Path(path_str).absolute().as_posix()


# recursively copy files from a dir into another dir
def cpdir(src_as_str: str, dst_as_string: str) -> None:  # dst_dir must be a full path, including the new dir name
    def copy_files(src: Path, dst: Path) -> None:
        # create dst dir if it doesn't exist
        if verbose:
            print(f"Copying {src} to {dst}")
        mkdir(dst.absolute().as_posix(), create_parents=True)
        for src_file in src.iterdir():
            if src_file.is_file():
                dst_file = dst.joinpath(src_file.stem + src_file.suffix)
                dst_file.write_bytes(src_file.read_bytes())
            elif src_file.is_dir():
                if src_file.exists():
                    new_dst = dst.joinpath(src_file.stem + src_file.suffix)
                    copy_files(src_file, new_dst)
                else:
                    raise FileNotFoundError(f"No such file or directory: {src_file.absolute().as_posix()}")

    src_as_path = Path(src_as_str)
    dst_as_path = Path(dst_as_string)
    if src_as_path.exists():
        if not dst_as_path.exists():
            mkdir(dst_as_string)
        # TODO: Fix python copy dir
        '''
        try:
            copy_files(src_as_path, dst_as_path)
        except RecursionError:
            print("\033[93m" + f"Failed to copy {root_src} to {root_dst}, using bash" + "\033[0m")
            bash(f"cp -rp {src_as_path.absolute().as_posix()} {dst_as_path.absolute().as_posix()}")
        '''
        bash(f"cp -rp {src_as_path.absolute().as_posix()}/* {dst_as_path.absolute().as_posix()}")
    else:
        raise FileNotFoundError(f"No such directory: {src_as_path.absolute().as_posix()}")


def cpfile(src_as_str: str, dst_as_str: str) -> None:  # "/etc/resolv.conf", "/var/some_config/resolv.conf"
    src_as_path = Path(src_as_str)
    dst_as_path = Path(dst_as_str)
    if verbose:
        print(f"Copying {src_as_path.absolute().as_posix()} to {dst_as_path.absolute().as_posix()}")
    if src_as_path.exists():
        dst_as_path.write_bytes(src_as_path.read_bytes())
    else:
        raise FileNotFoundError(f"No such file: {src_as_path.absolute().as_posix()}")


#######################################################################################
#                               BASH FUNCTIONS                                        #
#######################################################################################

# return the output of a command
def bash(command: str) -> str:
    output = subprocess.check_output(command, shell=True, text=True).strip()
    if verbose:
        print(output, flush=True)
    return output


#######################################################################################
#                                    MISC STUFF                                       #
#######################################################################################

def set_verbose(new_state: bool) -> None:
    global verbose
    verbose = new_state


def prevent_idle() -> None:
    Thread(target=__prevent_idle, daemon=True).start()


def __prevent_idle():
    bash('systemd-inhibit /bin/bash -c "sleep 14400" --what="idle"')  # sleep indefinitely, thereby preventing idle
    print_error("Been copying for 4 HOURS?!?!? Please create an issue")


#######################################################################################
#                              FILE PROGRESS MONITOR FUNCTIONS                        #
#######################################################################################

def extract_file(file: str, dest: str) -> None:
    """
    Extract a compressed file using tar and use pv to show progress if pv is installed.

    :param file: A string representing the full path to the compressed file to be extracted.
    :param dest: A string representing the full destination directory where the extracted files will be extracted to.
    :return: None
    """
    if no_extract_progress:  # for non-interactive shells only
        if file.endswith(".gz"):
            # --warning=no-unknown-keyword is to supress a warning about unknown headers in the arch rootfs
            bash(f"tar xfpz {file} --warning=no-unknown-keyword -C {dest}")
        elif file.endswith(".xz"):
            bash(f"tar xfpJ {file} -C {dest}")
        return

    if file.endswith(".gz"):
        # --warning=no-unknown-keyword is to supress a warning about unknown headers in the arch rootfs
        bash(f"pv {file} | tar xfpz - --warning=no-unknown-keyword -C {dest}")
    elif file.endswith(".xz"):
        bash(f"pv {file} | tar xfpJ - -C {dest}")


def download_file(url: str, path: str) -> None:
    # start monitor in a separate thread
    if no_download_progress:  # for non-interactive shells only
        # start download
        urlretrieve(url=url, filename=path)
        return

    # get total file size from server
    total_file_size = int(urlopen(url).headers["Content-Length"])
    Thread(target=_print_download_progress, args=(Path(path), total_file_size,), daemon=True).start()

    # start download
    urlretrieve(url=url, filename=path)

    # stop monitor
    open(".stop_download_progress", "a").close()
    print("\n", end="")


def _print_download_progress(file_path: Path, total_size) -> None:
    while True:
        if path_exists(".stop_download_progress"):
            rmfile(".stop_download_progress")
            return
        try:
            print("\rDownloading: " + "%.0f" % int(file_path.stat().st_size / 1048576) + "mb / "
                  + "%.0f" % (total_size / 1048576) + "mb", end="", flush=True)
        except FileNotFoundError:
            sleep(0.5)  # in case download hasn't started yet


#######################################################################################
#                                    PRINT FUNCTIONS                                  #
#######################################################################################

def print_warning(message: str) -> None:
    print("\033[93m" + message + "\033[0m", flush=True)


def print_error(message: str) -> None:
    print("\033[91m" + message + "\033[0m", flush=True)


def print_status(message: str) -> None:
    print("\033[94m" + message + "\033[0m", flush=True)


def print_question(message: str) -> None:
    print("\033[92m" + message + "\033[0m", flush=True)


def print_header(message: str) -> None:
    print("\033[95m" + message + "\033[0m", flush=True)


verbose = False
# on import check if pv is installed and set global variable
try:
    bash("which pv > /dev/null 2>&1")  # suppress all output to avoid scaring the user (pv is not a hard dependency)
    no_extract_progress = False
except subprocess.CalledProcessError:
    no_extract_progress = True
no_download_progress = not sys.stdout.isatty()  # disable download progress if terminal is not interactive
