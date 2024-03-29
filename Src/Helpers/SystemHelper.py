import random
import psutil
import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)

class System:
    def GetRandomXYInsideBoundaries(self, xFrom, xTo, yFrom, yTo):
        return random.randint(xFrom, xTo), random.randint(yFrom, yTo)

    def IsActiveWindow(self, windowName):
        activeWindow = self.GetActiveWindow()
        print("Current active window - " + activeWindow)
        if windowName.lower() in activeWindow.lower():
            return True
        return False

    def ProcessRunning(self, processName):
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def GetActiveWindow(self):
        """
        Get the currently active window.

        Returns
        -------
        string :
            Name of the currently active window.
        """
        import sys
        active_window_name = None
        if sys.platform in ['linux', 'linux2']:
            # Alternatives: https://unix.stackexchange.com/q/38867/4784
            try:
                import wnck
            except ImportError:
                logging.info("wnck not installed")
                wnck = None
            if wnck is not None:
                screen = wnck.screen_get_default()
                screen.force_update()
                window = screen.get_active_window()
                if window is not None:
                    pid = window.get_pid()
                    with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                        active_window_name = f.read()
            else:
                try:
                    from gi.repository import Gtk, Wnck
                    gi = "Installed"
                except ImportError:
                    logging.info("gi.repository not installed")
                    gi = None
                if gi is not None:
                    Gtk.init([])  # necessary if not using a Gtk.main() loop
                    screen = Wnck.Screen.get_default()
                    screen.force_update()  # recommended per Wnck documentation
                    active_window = screen.get_active_window()
                    pid = active_window.get_pid()
                    with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                        active_window_name = f.read()
        elif sys.platform in ['Windows', 'win32', 'cygwin']:
            # https://stackoverflow.com/a/608814/562769
            import win32gui
            window = win32gui.GetForegroundWindow()
            active_window_name = win32gui.GetWindowText(window)
        elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
            # https://stackoverflow.com/a/373310/562769
            from AppKit import NSWorkspace
            active_window_name = (NSWorkspace.sharedWorkspace()
            .activeApplication()['NSApplicationName'])
        else:
            print("sys.platform={platform} is unknown. Please report."
                  .format(platform=sys.platform))
            print(sys.version)
        return active_window_name

