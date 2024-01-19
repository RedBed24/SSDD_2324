from typing import Callable

import IceDrive

from icedrive_blob.blob import DataTransfer
from icedrive_blob.discovery import Discovery

class MockDataTransfer(DataTransfer):
    def __init__(self, data: bytes):
        self.read = lambda size, current = None: data[:size - 1]
        self.close = lambda current = None: None

class MockUser(IceDrive.User):
    def __init__(self, value: bool):
        self.isAlive = lambda current = None: value

class MockAuthentication(IceDrive.Authentication):
    def __init__(self, value: bool, ice_ping: Callable[[], None] = lambda: None):
        self.verifyUser = lambda user, current = None: value
        self.ice_ping = ice_ping

class MockDiscovery(Discovery):
    def __init__(self, service: IceDrive.AuthenticationPrx):
        self.getAtuhencticationService = lambda: service
