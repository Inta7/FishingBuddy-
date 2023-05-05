from Src.GUI.App import App
from pathlib import Path


def MainLoop():
    try:
        applicationDirectory = f"{str(Path.home())}/FBApp"
        Path(applicationDirectory).mkdir(parents=True, exist_ok=True)
        app = App(applicationDirectory)
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    MainLoop()
