"""Authentication service application."""

import configparser
import logging
import sys
import os.path
from typing import List

import Ice

from .blob import BlobService


class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        config = configparser.ConfigParser()

        # Load the configuration file, default to config/app.ini
        path = args[1] if len(args) > 1 else os.path.join(os.path.dirname(__file__), "..", "config", "app.ini")
        configs = config.read(path)

        if not len(configs):
            logging.error("Configuration: %s file not found.", path)
            return 1

        logging.debug("Configuration: %s file loaded.", path)

        servant = BlobService(config["Blobs"]["blobs_directory"], config["Blobs"]["links_directory"], int(config["Server"]["data_transfer_size"]), config["Blobs"]["partial_uploads_directory"])

        servant_proxy = adapter.addWithUUID(servant) if config["Server"]["random_proxy"] != "false" else adapter.add(servant, self.communicator().stringToIdentity("BlobService"))

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    return app.main(sys.argv)
