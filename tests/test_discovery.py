import pytest

import Ice

import IceDrive

from icedrive_blob.discovery import Discovery


def test_announce_directory():
	Discovery().announceDirectoryServicey(None)


def test_announce_blob():
	Discovery().announceBlobService(None)


def test_announce_authentication():
	Discovery().announceAuthentication(None)


def test_get_authentication():
	discovery = Discovery()

	class MockAuthentication:
		def ice_ping(self):
			pass

	auth = MockAuthentication()

	discovery.announceAuthentication(auth)

	assert discovery.getAtuhencticationService() == auth


def test_get_authentication_auth_raises_noendpoint():
	discovery = Discovery()

	class MockAuthentication:
		def ice_ping(self):
			raise Ice.NoEndpointException()

	auth = MockAuthentication()

	discovery.announceAuthentication(auth)

	with pytest.raises(IceDrive.TemporaryUnavailable):
		discovery.getAtuhencticationService()


def test_get_authentication_no_services():
	with pytest.raises(IceDrive.TemporaryUnavailable):
		Discovery().getAtuhencticationService()

