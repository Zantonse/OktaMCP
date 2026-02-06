# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for OktaAuthManager authentication flow."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestOktaAuthManagerInit:
    """Tests for OktaAuthManager initialization."""

    def test_init_with_required_env_vars(self, monkeypatch):
        """Test initialization with required environment variables."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        # Patch sys.exit to prevent test from exiting
        with patch("sys.exit"):
            manager = OktaAuthManager()

        assert manager.org_url == "https://test.okta.com"
        assert manager.client_id == "test_client_id"
        assert manager.use_browserless_auth is False

    def test_init_adds_https_prefix(self, monkeypatch):
        """Test that https:// prefix is added if missing."""
        monkeypatch.setenv("OKTA_ORG_URL", "test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"):
            manager = OktaAuthManager()

        assert manager.org_url == "https://test.okta.com"

    def test_init_with_browserless_auth(self, monkeypatch):
        """Test initialization with browserless auth configuration."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"):
            manager = OktaAuthManager()

        assert manager.use_browserless_auth is True

    def test_init_with_custom_scopes(self, monkeypatch):
        """Test initialization with custom scopes."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_SCOPES", "okta.users.read okta.groups.read")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"):
            manager = OktaAuthManager()

        assert "okta.users.read" in manager.scopes
        assert "okta.groups.read" in manager.scopes


class TestTokenValidation:
    """Tests for token validation."""

    @pytest.mark.asyncio
    async def test_is_valid_token_with_valid_token(self, monkeypatch):
        """Test is_valid_token returns True when token is valid."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.get_password", return_value="valid_token"):
            manager = OktaAuthManager()
            manager.token_timestamp = time.time()  # Recent token

            result = await manager.is_valid_token()

        assert result is True

    @pytest.mark.asyncio
    async def test_is_valid_token_with_expired_token(self, monkeypatch):
        """Test is_valid_token handles expired tokens."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with (
            patch("sys.exit"),
            patch("keyring.get_password", return_value="valid_token"),
            patch("keyring.set_password"),
        ):
            manager = OktaAuthManager()
            manager.token_timestamp = 0  # Very old token

            # Mock the authenticate method to avoid actual auth
            manager.authenticate = AsyncMock()
            manager.refresh_access_token = AsyncMock(return_value=False)

            await manager.is_valid_token()

            # Should have attempted to refresh or re-authenticate
            assert manager.refresh_access_token.called or manager.authenticate.called


class TestTokenRefresh:
    """Tests for token refresh."""

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, monkeypatch):
        """Test successful token refresh."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh_token",
        }

        with (
            patch("sys.exit"),
            patch("keyring.get_password", return_value="old_refresh_token"),
            patch("keyring.set_password"),
            patch("httpx.AsyncClient") as mock_client,
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            manager = OktaAuthManager()
            result = await manager.refresh_access_token()

        assert result is True

    @pytest.mark.asyncio
    async def test_refresh_access_token_no_refresh_token(self, monkeypatch):
        """Test token refresh fails when no refresh token available."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.get_password", return_value=None):
            manager = OktaAuthManager()
            result = await manager.refresh_access_token()

        assert result is False


class TestClearTokens:
    """Tests for clearing tokens."""

    def test_clear_tokens(self, monkeypatch):
        """Test that clear_tokens removes stored tokens."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with (
            patch("sys.exit"),
            patch("keyring.delete_password") as mock_delete,
        ):
            manager = OktaAuthManager()
            manager.token_timestamp = time.time()

            manager.clear_tokens()

        assert manager.token_timestamp == 0
        assert mock_delete.call_count >= 1
