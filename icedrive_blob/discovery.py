"""Servant implementations for service discovery."""

import logging

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self):
        self.authentications = set()

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.authentications.add(prx)
        logging.info("Discovery: received authentication service announcement: %s", prx)

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        logging.info("Discovery: received directory service announcement: %s", prx)

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        logging.info("Discovery: received blob service announcement: %s", prx)

    def getAtuhencticationService(self) -> IceDrive.AuthenticationPrx:
        """Return an active Authentication service"""
        return Discovery.__getActiveService(self.authentications)

    @staticmethod
    def __getActiveService(set):
        """Raises KeyError if there are no active services available."""
        seleccionado = None

        while not seleccionado:
            try:
                seleccionado = set.pop()
                seleccionado.ice_ping()
                set.add(seleccionado)
            except Ice.NoEndpointException:
                seleccionado = None
            except KeyError:
                raise IceDrive.TemporaryUnavailable()

        return seleccionado

