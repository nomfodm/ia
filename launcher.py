import os.path
import subprocess
import sys
import urllib.request


def cleanUp() -> None:
    if os.path.isfile("main.py"):
        os.remove("main.py")


def main() -> None:
    print("Installing pypi dependencies...")
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "rich", "py7zr" if sys.platform.startswith("win32") else "rich"])

    print("\n\nDownloading main.py...")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nomfodm/ia/master/main.py", "main.py")

    print("\n\nStarting...\n")
    subprocess.call([sys.executable, "main.py"])

    cleanUp()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanUp()
        exit(0)
    except Exception as e:
        print("\n\nUnexpected error:", e)
        print("Report this exception to https://github.com/nomfodm/ia/issues")
        cleanUp()
        exit(0)
