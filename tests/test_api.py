"""HTTP client and URL validation tests."""

import unittest

from _support import prepare_imports

prepare_imports()

from custom_components.planty.api import (
    PlantyApi,
    PlantyAuthenticationError,
    PlantyInvalidResponseError,
    normalize_base_url,
)


class FakeResponse:
    """Small async response double for API tests."""

    def __init__(self, status, body):
        self.status = status
        self.body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def json(self):
        return self.body


class FakeSession:
    """Capture the request without contacting a server."""

    def __init__(self, response):
        self.response = response
        self.call = None

    def get(self, url, **kwargs):
        self.call = (url, kwargs)
        return self.response


class PlantyApiTest(unittest.IsolatedAsyncioTestCase):
    """Check auth headers, URL validation and API response handling."""

    def test_normalize_base_url(self):
        self.assertEqual(normalize_base_url(" HTTPS://Planty.Example.org/ "),
                         "https://planty.example.org")
        for invalid_url in (
            "ftp://planty.example.org", "https://planty.example.org/api",
            "https://user@planty.example.org", "https://planty.example.org?token=x",
            "https://planty.example.org/#fragment", "https://planty.example.org:bad",
        ):
            with self.subTest(url=invalid_url), self.assertRaises(ValueError):
                normalize_base_url(invalid_url)

    async def test_profile_uses_bearer_token_without_query_secret(self):
        session = FakeSession(FakeResponse(200, {"username": "garden-owner"}))
        client = PlantyApi(session, "https://planty.example.org", "planty_secret")
        self.assertEqual(await client.async_get_profile(), {"username": "garden-owner"})
        self.assertEqual(session.call[0], "https://planty.example.org/api/auth/me")
        self.assertEqual(session.call[1]["headers"]["Authorization"], "Bearer planty_secret")
        self.assertNotIn("planty_secret", session.call[0])

    async def test_rejected_token_and_malformed_snapshot_fail_cleanly(self):
        unauthorized = PlantyApi(FakeSession(FakeResponse(401, {})),
                                 "https://planty.example.org", "revoked")
        with self.assertRaises(PlantyAuthenticationError):
            await unauthorized.async_get_profile()
        malformed = PlantyApi(FakeSession(FakeResponse(200, {"gardens": []})),
                              "https://planty.example.org", "planty_secret")
        with self.assertRaises(PlantyInvalidResponseError):
            await malformed.async_get_snapshot()


if __name__ == "__main__":
    unittest.main()
