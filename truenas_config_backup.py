import os
import sys
import platform
from datetime import datetime, timedelta
from pathlib import Path
import tarfile

TIME_STR_FORMAT: str = "%Y%m%d%H%M%S"  # String time format
CUR_TIME: datetime = datetime.now()  # Current time in datetime object


def file_name(host_name: str, os_ver: str) -> str:
    """Format output file name

    Args:
        host_name (str): Host name of the system
        os_ver (str): Current version of TrueNAS Scale

    Returns:
        str: Formatted output file name
    """

    return f"{host_name}-TrueNAS-SCALE-{os_ver}-{CUR_TIME.strftime(TIME_STR_FORMAT)}.tar"


def backup_command(path2save: Path) -> None:
    """Parse configuration file of TrueNSA Scale and compose into tar file

    Args:
        path2save (Path): Path object that containing full path of file
        including file name
    """

    try:
        # Backup config file as tar file
        with tarfile.open(path2save, "w") as f_tar:
            source_dir: str = "/data"  # Location of the config
            for file_name in ["freenas-v1.db", "pwenc_secret"]:
                f_tar.add(f"{source_dir}/{file_name}", arcname=file_name)

        # Print message of completion
        print(
            f"Backup is completed as: {path2save.name}\nPath to file: {path2save}"
        )

    except os.error as e:
        print(f"Error creating backup: {e}")


def del_old_config(
    cur_path: Path, term: str = "days", num_term: int = 14
) -> None:
    """Parse old config backups, and delete it if it is older then set amount
    of time

    Args:
        cur_path (Path): Current working directory.
    """

    try:
        old_files_path: str = (
            ""  # List of old backup files to delete in string
        )
        for file in cur_path.iterdir():
            # Only check if file suffix is "tar"
            if file.is_file() and file.suffix == ".tar":
                # Extract time from file name
                old_time: datetime = datetime.strptime(
                    file.name.split("-")[-1].split(".")[0], TIME_STR_FORMAT
                )

                # Get time difference from current
                td_delta: timedelta = CUR_TIME - old_time
                if td_delta.days > 14:  # Get only file is older then 14 days
                    old_files_path += f" {file}"

        if old_files_path != "":
            print("\nRemoveing old backups")
            os.remove(old_files_path)  # Remove old backups

    except Exception as e:
        print(f"Error deleting old backups: {e}")


def main() -> None:
    host_name: str = platform.node()  # Getting hot name of the system

    with open("/etc/version", "r") as f:
        os_ver: str = f.readline()  # Current TrueNAS version

    # Getting full path of current python file location
    cur_path: Path = (
        Path(sys.argv[0]).parent.resolve().joinpath("config_files")
    )

    # Create folder if is not exist
    cur_path.mkdir() if not cur_path.exists() else None

    # Path to save config file
    path2save: Path = cur_path.joinpath(file_name(host_name, os_ver))

    backup_command(path2save)  # Running command for backing up config

    del_old_config(cur_path)  # Delete old config


if __name__ == "__main__":
    if os.geteuid() != 0:
        raise AssertionError("Ran with sudo")
    else:
        print("TrueNAS Scale config backup started")
        main()
