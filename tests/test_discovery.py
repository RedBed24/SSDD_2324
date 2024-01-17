import pytest

import Ice

import IceDrive

from icedrive_blob.discovery import Discovery

from mocks import MockAuthentication


def test_announce_directory():
	Discovery().announceDirectoryServicey(None)


def test_announce_blob():
	Discovery().announceBlobService(None)


def test_announce_authentication():
	Discovery().announceAuthentication(None)


def test_get_authentication():
	discovery = Discovery()

	auth = MockAuthentication(None, lambda: None)

	discovery.announceAuthentication(auth)

	assert discovery.getAtuhencticationService() == auth


def test_get_authentication_auth_raises_noendpoint():
	discovery = Discovery()

	def ice_ping():
		raise Ice.NoEndpointException()
	auth = MockAuthentication(None, ice_ping)

	discovery.announceAuthentication(auth)

	with pytest.raises(IceDrive.TemporaryUnavailable):
		discovery.getAtuhencticationService()


def test_get_authentication_no_services():
	with pytest.raises(IceDrive.TemporaryUnavailable):
		Discovery().getAtuhencticationService()

