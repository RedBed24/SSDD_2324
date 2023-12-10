#!/usr/bin/env python3
import sys
from typing import List

import importlib.util
import logging
import os

import Ice

logging.basicConfig(level=logging.DEBUG)

if importlib.util.find_spec("IceDrive") is None:
    slice_path = os.path.join(os.path.dirname(__file__), "icedrive.ice")

    if not os.path.exists(slice_path):
        raise ImportError("Cannot find icedrive.ice for loading IceDrive module")

    Ice.loadSlice(slice_path)
    logging.info("IceDrive slice loaded")

import IceDrive # noqa: E402


DATA = b"I MADE IT! Yayyy :D"
READ_SIZE = 64


class MockDataTransfer(IceDrive.DataTransfer):
    def __init__(self, data: bytes):
        self.data = data

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        return self.data[:size]

    def close(self, current: Ice.Current = None) -> None:
        pass


class ClientApp(Ice.Application):
    def run(self, args: List[str]) -> int:
        if len(args) != 2:
            logging.error("Usage: %s <proxy>", args[0])
            return 1
        
        blob_proxy = IceDrive.BlobServicePrx.checkedCast(self.communicator().stringToProxy(args[1]))

        if not blob_proxy:
            logging.error("Invalid proxy")
            return 1
        
        adapter = self.communicator().createObjectAdapter("DataTransferAdapter")
        adapter.activate()

        blob_id = blob_proxy.upload(IceDrive.DataTransferPrx.uncheckedCast(adapter.addWithUUID(MockDataTransfer(DATA))))
        
        logging.info("Uploaded blob %s", blob_id)

        blob_proxy.link(blob_id)

        blob_proxy.unlink(blob_id)

        download_proxy = blob_proxy.download(blob_id)

        dowloaded_data = b""
        while partial_data := download_proxy.read(READ_SIZE):
            dowloaded_data += partial_data

        logging.info("Downloaded blob %s: %s", blob_id, dowloaded_data)


def main():
    # config located at config/data_transfer.config
    app = ClientApp()
    return app.main(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
