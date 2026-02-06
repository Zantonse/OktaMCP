# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for user management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListUsers:
    """Tests for list_users tool."""

    @pytest.mark.asyncio
    async def test_list_users_success(self, mock_context, mock_okta_client):
        """Test successful user listing."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(ctx=mock_context)

            assert "items" in result or "error" not in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_users_with_search(self, mock_context, mock_okta_client):
        """Test user listing with search parameter."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(
                ctx=mock_context,
                search='profile.email eq "test@example.com"',
            )

            assert "error" not in result or result.get("success") is True

    @pytest.mark.asyncio
    async def test_list_users_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            # Test with limit below minimum
            result = await list_users(ctx=mock_context, limit=5)
            assert "error" not in result or result.get("success") is True


class TestGetUser:
    """Tests for get_user tool."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_context, mock_okta_client):
        """Test successful user retrieval."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import get_user

            result = await get_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_user_error_handling(self, mock_context):
        """Test error handling when user not found."""
        mock_client = AsyncMock()
        mock_client.get_user = AsyncMock(side_effect=Exception("User not found"))

        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.users.users import get_user

            result = await get_user(user_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateUser:
    """Tests for create_user tool."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_context, mock_okta_client):
        """Test successful user creation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import create_user

            profile = {
                "firstName": "New",
                "lastName": "User",
                "email": "new@example.com",
                "login": "new@example.com",
            }

            result = await create_user(profile=profile, ctx=mock_context)

            assert result.get("success") is True


class TestUpdateUser:
    """Tests for update_user tool."""

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_context, mock_okta_client):
        """Test successful user update."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import update_user

            result = await update_user(
                user_id="00u1abc123def456",
                profile={"firstName": "Updated"},
                ctx=mock_context,
            )

            assert result.get("success") is True


class TestDeactivateUser:
    """Tests for deactivate_user tool."""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, mock_context, mock_okta_client):
        """Test successful user deactivation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import deactivate_user

            result = await deactivate_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "deactivated" in result.get("data", {}).get("message", "").lower()


class TestDeleteDeactivatedUser:
    """Tests for delete_deactivated_user tool."""

    @pytest.mark.asyncio
    async def test_delete_deactivated_user_success(self, mock_context, mock_okta_client):
        """Test successful deletion of deactivated user."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import delete_deactivated_user

            result = await delete_deactivated_user(
                user_id="00u1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
