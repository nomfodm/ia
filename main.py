import os
import shutil
import subprocess
import sys
import typing

import urllib.request
import urllib.error
import json

import urllib.request

from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, \
    TimeRemainingColumn

from rich import print
from rich.prompt import Prompt

CONFIG = {
    "version": "1.0",
    "language": "en",
    "messages": {
        "systemNotSupported": "[red]Your OS is not supported.",
        "errorReceivingLangConf": "[red]Unable to get language config from server, "
                                  "check your internet connection, shutting down.",
        "errorReceivingAppsConf": "[red]Unable to get app config from server, "
                                  "check your internet connection, shutting down.",
        "pressEnterToContinue": "Press 'enter' key to continue...",
        "keyboardInterrupt": "[green]\n\nProcess interrupted by user.",
        "exceptionCaught": "[red]\n\nException caught: [blue]%s",
        "reportItToGithubIssues": "[red]Please report it to github issues, https://github.com/nomfodm/ia/issues",

        "welcome": "[green]Welcome to Installation Assistant, [red]v%s\n[white]This program will "
                   "install any application you want from the list with chosen configuration",
        "chooseAppYouWantToInstall": "Choose app you want to install",

        "noConfigurationNeeded": "No configuration needed",
        "chooseConfigForApp": "Now, I suggest you choosing configuration you need.",

        "youChosenAConfiguration": "[green]OK, you chose [blue]%s [green]configuration.",
        "youDontNeedAConfiguration": "[green]OK, no configuration, I just will install [blue]%s [green]for you.",

        "downloadingSetupFile": "[green]\nDownloading setup file...",
        "noSetupFile": "[green]\nNo setup file needed for this application",
        "installing": "[green]\nInstalling...",
        "installedSuccessfully": "[blue]\n%s [green]installed successfully!",

        "nowIWillApplyConfiguration": "[green]\nNow, I will apply [blue]%s [green]configuration for [bold blue]%s[green].",
        "errorOccurredWhiteConfiguring": "[red]\nError occurred while configuring [blue]%s [green]configuration for [bold blue]%s[green].",
        "configuringCompleted": "[green]\nConfiguration completed.",

        "installationCompleted": "[green]\nInstallation completed.",

        "thanksForUsingIA": "[bold green]\nThanks for using Installation Assistant!"
    }
}

DEV = False


class Helper:
    @staticmethod
    def getSystemName() -> str:
        if sys.platform.startswith("win32"):
            return "windows"
        elif sys.platform.startswith("linux"):
            return "linux"

        return ""

    @staticmethod
    def cleanUp() -> None:
        shutil.rmtree("ia", ignore_errors=True)

    @staticmethod
    def clearConsole() -> None:
        subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)

    @staticmethod
    def pauseCommand() -> None:
        input(CONFIG["messages"]["pressEnterToContinue"])

    @staticmethod
    def addFolderToFilename(filename: str) -> str:
        return os.path.join("ia", filename)

    @staticmethod
    def die(message: str = "") -> None:
        print("\n")
        print(message)
        Helper.pauseCommand()
        exit(0)

    @staticmethod
    def createPrintableAppListStringAndChooseList() -> typing.Tuple[str, typing.List[str]]:
        appListString = ""
        chooseList = []
        for i, app in enumerate(CONFIG["apps"]):
            appListString += f"\t{i + 1}. {app['fullAppName']}\n"
            chooseList.append(str(i + 1))

        return appListString, chooseList

    @staticmethod
    def createPrintableConfigurationsListAndChooseList(app: typing.Dict) -> typing.Tuple[str, typing.List[str]]:
        configurationsListString = f"\t0. {CONFIG['messages']['noConfigurationNeeded']}\n"
        chooseList = ['0']
        for i, configuration in enumerate(app["configurations"]):
            configurationsListString += f"\t{i + 1}. {configuration['fullConfigName']}\n"
            chooseList.append(str(i + 1))
        return configurationsListString, chooseList

    @staticmethod
    def installApp(app: typing.Dict) -> None:
        system = Helper.getSystemName()

        setupSection = app["setup"][system]
        if setupSection["setupFilename"] != "noSetupFile":
            print(CONFIG["messages"]["downloadingSetupFile"])
            Request.download(setupSection["setupUrl"], Helper.addFolderToFilename(setupSection["setupFilename"]))
        else:
            print(CONFIG["messages"]["noSetupFile"])

        print(CONFIG["messages"]["installing"])
        if not DEV:
            subprocess.call(setupSection["setupCommand"])

        Helper.clearConsole()
        print(CONFIG["messages"]["installedSuccessfully"] % app["shortAppName"])

    @staticmethod
    def configureApp(app: typing.Dict, configuration: typing.Dict) -> None:
        print()
        print(
            CONFIG["messages"]["nowIWillApplyConfiguration"] % (configuration["shortConfigName"], app["shortAppName"]))
        scriptFilename = Helper.addFolderToFilename(configuration["configureScriptFilename"])
        Request.download(configuration["configureScriptUrl"], scriptFilename)

        status = subprocess.call([sys.executable, scriptFilename, Helper.getSystemName()])
        if status != 0:
            print(CONFIG["messages"]["errorOccurredWhiteConfiguring"])
            print(CONFIG['messages']["reportItToGithubIssues"])

            Helper.cleanUp()
            Helper.die()

        print(CONFIG["messages"]["configuringCompleted"])


class Request:
    @staticmethod
    def getAppsConfig() -> None:

        try:
            with urllib.request.urlopen("https://infinitymc.ru/ih/info.json") as req:
                CONFIG["apps"] = json.loads(req.read().decode("utf-8"))["apps"]
        except urllib.error.HTTPError:
            Helper.die(CONFIG['messages']["errorReceivingAppsConf"])
        except urllib.error.URLError:
            Helper.die(CONFIG['messages']["errorReceivingAppsConf"])

    @staticmethod
    def getLanguageConfig() -> None:
        if CONFIG["language"] == "en":
            return

        try:
            with urllib.request.urlopen(f"https://infinitymc.ru/ih/{CONFIG['language']}.json") as req:
                CONFIG["messages"] = json.loads(req.read().decode("utf-8"))
        except urllib.error.HTTPError:
            Helper.die(CONFIG['messages']["errorReceivingLangConf"])
        except urllib.error.URLError:
            Helper.die(CONFIG['messages']["errorReceivingLangConf"])

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


def main() -> None:
    os.makedirs("ia", exist_ok=True)

    system = Helper.getSystemName()
    if not system:
        Helper.die(CONFIG["messages"]["systemNotSupported"])

    if not DEV:
        language = Prompt.ask("Choose your language/Выберите язык", choices=["en", "ru"])
        CONFIG["language"] = language.lower()

    Request.getLanguageConfig()
    Request.getAppsConfig()

    Helper.clearConsole()
    print(CONFIG["messages"]["welcome"] % CONFIG["version"])

    appListString, chooseList = Helper.createPrintableAppListStringAndChooseList()
    print(appListString)
    chosenAppId = int(Prompt.ask(CONFIG["messages"]["chooseAppYouWantToInstall"], choices=chooseList))

    app = CONFIG["apps"][chosenAppId - 1]

    Helper.clearConsole()
    print(CONFIG["messages"]["chooseConfigForApp"])
    configListString, configChooseList = Helper.createPrintableConfigurationsListAndChooseList(app)
    print(configListString)
    chosenConfigId = int(Prompt.ask(choices=configChooseList))

    Helper.clearConsole()
    if not chosenConfigId:
        print(CONFIG["messages"]["youDontNeedAConfiguration"] % app["shortAppName"])
    else:
        print(CONFIG["messages"]["youChosenAConfiguration"] % app["configurations"][chosenConfigId - 1][
            "shortConfigName"])

    Helper.installApp(app)
    if chosenConfigId:
        Helper.configureApp(app, app["configurations"][chosenConfigId - 1])

    print()
    print(CONFIG["messages"]["installationCompleted"])
    print(CONFIG["messages"]["thanksForUsingIA"])

    Helper.cleanUp()
    Helper.die()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        Helper.cleanUp()
        Helper.die(CONFIG['messages']["keyboardInterrupt"])
    except Exception as e:
        print(CONFIG['messages']["exceptionCaught"] % e)
        print(CONFIG['messages']["reportItToGithubIssues"])

        Helper.cleanUp()
        Helper.die()
