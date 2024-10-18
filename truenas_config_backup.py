import os
import sys
import platform
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

TIME_STR_FORMAT: str = "%Y%m%d%H%M%S" # String time format
CUR_TIME: datetime = datetime.now() # Current time in datetime object

def file_name(host_name: str, os_ver: str) -> str:
    # time: str = datetime.now().strftime(TIME_STR_FORMAT)
    return f"{host_name}-TrueNAS-SCALE-{os_ver}-{CUR_TIME.strftime(TIME_STR_FORMAT)}.tar"


def backup_command(path2save: Path) -> None:
    try:
        # Backup command
        subprocess.run(
            [
                "tar",
                "-cf",
                path2save,
                "--directory=/data",
                "freenas-v1.db",
                "pwenc_secret",
            ],
            check=True,
        )

        # Print message of completion
        tmp_path: str = str(path2save).split("/")[-1]
        print(
            f"Backup is completed as: {tmp_path}\nPath to file: {path2save}" 
        )

    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e}")


def del_old_config(cur_path: Path) -> None:
    try:
        old_files_path: str = "" # List of old backup files to delete in string
        for file in cur_path.iterdir():
            # Only check if file suffix is "tar"
            if file.is_file() and file.suffix == ".tar":
                # Extract time from file name
                old_time: datetime = datetime.strptime(
                    file.name.split("-")[-1].split(".")[0], 
                    TIME_STR_FORMAT
                )

                # Get time difference from current
                td_delta: timedelta = CUR_TIME - old_time 
                if td_delta.days > 14: # Get only file is older then 14 days
                    old_files_path += f" {file}"

        if old_files_path != "":
            print("\nRemoveing old backups")
            os.remove(old_files_path) # Remove old backups

    except Exception as e:
        print(f"Error deleting old backups: {e}")


def main() -> None:
    host_name: str = platform.node()  # Getting hot name of the system

    with open("/etc/version", "r") as f:
        os_ver: str = f.readline()  # Current TrueNAS version

    # Getting full path of current python file location
    cur_path: Path = Path(sys.argv[0]).parent.resolve()

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
