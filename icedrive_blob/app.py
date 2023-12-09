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
        path = args[2] if len(args) > 2 else os.path.join(os.path.dirname(__file__), "..", "config", "app.ini")
        config.read(path)
        logging.debug("Configuration: %s file loaded.", path)

        servant = BlobService(config["Blobs"]["blob_directory"])

        servant_proxy = adapter.addWithUUID(servant) if config["Server"]["random_proxy"] != "false" else adapter.add(servant, self.communicator().stringToIdentity("BlobService"))

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    # usage: %prog [ice_config_file] [service_config_file]
    # default ice_config_file: config/blob.config
    ice_config_file = sys.args[1] if len(sys.args) > 1 else os.path.join(os.path.dirname(__file__), "..", "config", "blob.config")
    app = BlobApp()
    return app.main(sys.argv, ice_config_file)
