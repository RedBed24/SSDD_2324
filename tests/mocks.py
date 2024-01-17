import Ice
import IceDrive

from icedrive_blob.blob import DataTransfer
from icedrive_blob.discovery import Discovery

class MockDataTransfer(DataTransfer):
    def __init__(self, data: bytes):
        self.read = lambda size: data[:size - 1]
        self.close = lambda: None

class MockUser(IceDrive.User):
    def __init__(self, value: bool):
        self.isAlive = lambda: value

class MockAuthentication(IceDrive.Authentication):
    def __init__(self, value: bool):
        self.verifyUser = lambda user: value

class MockDiscovery(Discovery):
    def __init__(self, service: IceDrive.AuthenticationPrx):
        self.getAtuhencticationService = lambda: service
