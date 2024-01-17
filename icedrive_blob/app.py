"""Authentication service application."""

import logging
import sys
from typing import List
import threading

import Ice
import IceStorm
import IceDrive

from .blob import BlobService
from .discovery import Discovery
from .delayed_response import BlobQuery


class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""
    @staticmethod
    def announce(shutdown: threading.Event, publisher: IceDrive.DiscoveryPrx, blob_prx: IceDrive.BlobServicePrx):
        while not shutdown.wait(5):
            publisher.announceBlobService(blob_prx)

    @staticmethod
    def getTopic(topic_name: str, topic_manager: IceStorm.TopicManagerPrx) -> IceStorm.TopicPrx:
        try:
            topic = topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name)

        return topic

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        property = self.communicator().getProperties().getProperty
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        )

        discovery_topic = BlobApp.getTopic(property("DiscoveryTopic"), topic_manager)
        blob_query_topic = BlobApp.getTopic(property("BlobQueryTopic"), topic_manager)

        discovery_servant = Discovery()
        discovery_prx = adapter.addWithUUID(discovery_servant)
        discovery_topic.subscribeAndGetPublisher({}, discovery_prx)

        servant = BlobService(
            IceDrive.BlobQueryPrx.uncheckedCast(blob_query_topic.getPublisher()),
            discovery_servant,
            property("BlobsDirectory"),
            property("LinksDirectory"),
            int(property("DataTransferSize")),
            property("PartialUploadsDirectory")
        )

        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        query_servant = BlobQuery(servant)
        query_prx = adapter.addWithUUID(query_servant)
        blob_query_topic.subscribeAndGetPublisher({}, query_prx)

        shutdown = threading.Event()
        publisher = IceDrive.DiscoveryPrx.uncheckedCast(discovery_topic.getPublisher())
        blob_prx = IceDrive.BlobServicePrx.uncheckedCast(servant_proxy)
        threading.Thread(target=BlobApp.announce, args=(shutdown, publisher, blob_prx)).start()

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        shutdown.set()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    return app.main(sys.argv)
