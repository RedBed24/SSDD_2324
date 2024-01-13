"""Authentication service application."""

import logging
import sys
from typing import List

import Ice

from .blob import BlobService


class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        property = self.communicator().getProperties().getProperty

        servant = BlobService(
            property("BlobsDirectory"),
            property("LinksDirectory"),
            int(property("DataTransferSize")),
            property("PartialUploadsDirectory")
        )

        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    return app.main(sys.argv)
