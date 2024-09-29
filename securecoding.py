import os
from Foundation import NSObject, NSApplication

class AppDelegate(NSObject):
    def applicationSupportsSecureRestorableState_(self, app):
        return True