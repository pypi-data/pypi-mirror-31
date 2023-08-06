import json

import responses

from hatcher.testing import unittest
from ...brood_url_handler import BroodURLHandler
from ...model_registry import ModelRegistry
from ...url_templates import URLS_V0
from ..user import User


class TestRepository(unittest.TestCase):

    def setUp(self):
        self.url_handler = BroodURLHandler.from_auth('http://brood-dev')
        self.model_registry = ModelRegistry(api_version=0)
        self.user = User('acme', 'user@acme.org', self.url_handler,
                         model_registry=self.model_registry)

    @responses.activate
    def test_delete_user(self):
        # Given
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS_V0.admin.users.metadata.format(
                    organization_name='acme',
                    email=self.user.email,
                ),
            ),
            status=201,
        )

        # When
        self.user.delete()

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_get_metadata(self):
        # Given
        expected = {
            "email": "user@acme.org",
            "organization": "enthought",
            "teams": ["read_acme_dev_repository"]
        }
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS_V0.admin.users.metadata.format(
                    organization_name='acme',
                    email=self.user.email,
                ),
            ),
            body=json.dumps(expected),
            status=200,
        )

        # When
        metadata = self.user.metadata()

        # Then
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(metadata, expected)
