import json
import os
import subprocess
import sys
import urllib.request

from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

config = {"extensions": ["ms-vscode.cpptools-extension-pack", "formulahendry.code-runner",
                         "EliverLara.andromeda"],
          "settings": {
              "linux": {
                  "code-runner.runInTerminal": True,
                  "code-runner.saveAllFilesBeforeRun": True,
                  "code-runner.saveFileBeforeRun": True,
                  "workbench.colorTheme": "Andromeda Bordered",
                  "C_Cpp.default.compilerPath": "/usr/bin/g++",
              },
              "windows": {
                  "code-runner.runInTerminal": True,
                  "code-runner.saveAllFilesBeforeRun": True,
                  "code-runner.saveFileBeforeRun": True,
                  "workbench.colorTheme": "Andromeda Bordered",
                  "code-runner.executorMap": {
                      "c": f"cd $dir && {os.path.expanduser('~')}\\mingw64\\bin\\gcc $fileName -o $fileNameWithoutExt && $dir$fileNameWithoutExt",
                      "cpp": f"cd $dir && {os.path.expanduser('~')}\\mingw64\\bin\\g++ $fileName -o $fileNameWithoutExt && $dir$fileNameWithoutExt",
                  },
                  "C_Cpp.default.compilerPath": f"{os.path.expanduser('~')}\\mingw64\\bin\\g++",
              }
          },
          "linux": [["sudo", "apt", "update"], ["sudo", "apt", "install", "gcc"]],
          "windows": {
              "mingwUrl": "https://github.com/niXman/mingw-builds-binaries/releases/download/13.2.0-rt_v11-rev1"
                          "/x86_64-13.2.0-release-win32-seh-msvcrt-rt_v11-rev1.7z"
          },
          "settingsJsonLocation": {
              "windows": "%APPDATA%\\Code\\User\\settings.json",
              "linux": "$HOME/.config/Code/User/settings.json"
          },
          "codeCommand": {
              "windows": "%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\bin\\code",
              "linux": "/usr/share/code/bin/code"
          },
          }


class Request:
    @staticmethod
    def download(url: str, filename: str) -> None:
        with Progress(
                TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
        ) as progress:
            downloading = progress.add_task("download", filename=filename)
            urllib.request.urlretrieve(url, filename,
                                       lambda block, size, total: progress.update(downloading, total=total,
                                                                                  completed=block * size))


def main():
    from rich import print

    print("\nInstalling necessary stuff...")
    if args[0] == "linux":
        for command in config[args[0]]:
            subprocess.call(command)
    elif args[0] == "windows":
        import py7zr
        Request.download(config[args[0]]["mingwUrl"], "ia\\mingw64.7z")
        print("Extracting...")
        with py7zr.SevenZipFile('ia\\mingw64.7z', mode='r') as z:
            z.extractall(os.path.expanduser("~") + "\\")
        os.remove("ia\\mingw64.7z")

    extensions = config["extensions"]
    for extension in extensions:
        subprocess.call([config["codeCommand"][args[0]], "--install-extension", extension])

    print("\nSetting settings.json...")
    if not os.path.isfile(config["settingsJsonLocation"][args[0]]):
        with open(config["settingsJsonLocation"][args[0]], "x") as file:
            file.write("{}")

    with open(config["settingsJsonLocation"][args[0]], "r") as file:
        settingsFile = json.load(file)

    for key in config["settings"][args[0]]:
        print(key, ": ", config["settings"][args[0]][key], sep="")
        settingsFile[key] = config["settings"][args[0]][key]

    with open(config["settingsJsonLocation"][args[0]], "w") as file:
        file.write(json.dumps(settingsFile))

    print("\n[green]Configuring completed.")


def checkArgs():
    if args[0] not in ["windows", "linux"]:
        print("Wrong system type specified")
        exit(0)


if __name__ == '__main__':
    if not sys.argv[1:]:
        print("This script is destined for Installation Helper")
        exit(0)

    args = sys.argv[1:]
    checkArgs()

    if args[0].startswith("windows"):
        config["settingsJsonLocation"][args[0]] = config["settingsJsonLocation"][args[0]].replace("%APPDATA%",
                                                                                                  os.getenv("APPDATA"))
        config["codeCommand"][args[0]] = config["codeCommand"][args[0]].replace("%LOCALAPPDATA%",
                                                                                os.getenv("LOCALAPPDATA"))
    elif args[0].startswith("linux"):
        config["settingsJsonLocation"][args[0]] = config["settingsJsonLocation"][args[0]].replace("$HOME",
                                                                                                  os.getenv("HOME"))

    main()
