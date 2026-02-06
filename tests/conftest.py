# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Shared pytest fixtures and mocks for Okta MCP Server tests."""

from dataclasses import dataclass
from typing import Dict, Optional
from unittest.mock import AsyncMock, patch

import pytest


@dataclass
class MockUserProfile:
    """Mock Okta user profile."""
    login: str = "test@example.com"
    email: str = "test@example.com"
    firstName: str = "Test"
    lastName: str = "User"
    displayName: str = "Test User"


@dataclass
class MockUser:
    """Mock Okta user object."""
    id: str = "00u1abc123def456"
    status: str = "ACTIVE"
    profile: MockUserProfile = None

    def __post_init__(self):
        if self.profile is None:
            self.profile = MockUserProfile()


@dataclass
class MockGroupProfile:
    """Mock Okta group profile."""
    name: str = "Test Group"
    description: str = "A test group"


@dataclass
class MockGroup:
    """Mock Okta group object."""
    id: str = "00g1abc123def456"
    profile: MockGroupProfile = None

    def __post_init__(self):
        if self.profile is None:
            self.profile = MockGroupProfile()


class MockOktaResponse:
    """Mock Okta API response object."""

    def __init__(self, has_next: bool = False, next_url: Optional[str] = None):
        self._has_next = has_next
        self._next = next_url

    def has_next(self) -> bool:
        return self._has_next

    async def next(self):
        return [], None


class MockOktaClient:
    """Mock Okta client for testing."""

    def __init__(self):
        self.users = [MockUser()]
        self.groups = [MockGroup()]

    async def list_users(self, query_params: Optional[Dict] = None):
        return self.users, MockOktaResponse(), None

    async def get_user(self, user_id: str):
        return MockUser(id=user_id)

    async def create_user(self, user_data: Dict):
        user = MockUser()
        if "profile" in user_data:
            user.profile = MockUserProfile(**user_data["profile"])
        return user, MockOktaResponse(), None

    async def update_user(self, user_id: str, user_data: Dict):
        user = MockUser(id=user_id)
        if "profile" in user_data:
            for key, value in user_data["profile"].items():
                setattr(user.profile, key, value)
        return user, MockOktaResponse(), None

    async def deactivate_user(self, user_id: str):
        return None, None

    async def deactivate_or_delete_user(self, user_id: str):
        return None, None

    async def list_groups(self, query_params: Optional[Dict] = None):
        return self.groups, MockOktaResponse(), None

    async def get_group(self, group_id: str):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def create_group(self, group_data: Dict):
        group = MockGroup()
        if "profile" in group_data:
            group.profile = MockGroupProfile(**group_data["profile"])
        return group, MockOktaResponse(), None

    async def update_group(self, group_id: str, group_data: Dict):
        group = MockGroup(id=group_id)
        if "profile" in group_data:
            for key, value in group_data["profile"].items():
                setattr(group.profile, key, value)
        return group, MockOktaResponse(), None

    async def delete_group(self, group_id: str):
        return None, None

    async def list_group_users(self, group_id: str, query_params: Optional[Dict] = None):
        return self.users, MockOktaResponse(), None

    async def list_assigned_applications_for_group(self, group_id: str):
        return [], MockOktaResponse(), None

    async def add_user_to_group(self, group_id: str, user_id: str):
        return None, None

    async def remove_user_from_group(self, group_id: str, user_id: str):
        return None, None


class MockOktaAuthManager:
    """Mock OktaAuthManager for testing."""

    def __init__(self):
        self.org_url = "https://test.okta.com"
        self.client_id = "test_client_id"
        self.token_timestamp = 0
        self.use_browserless_auth = False

    async def authenticate(self):
        pass

    async def is_valid_token(self, expiry_duration: int = 3600) -> bool:
        return True

    async def refresh_access_token(self) -> bool:
        return True

    def clear_tokens(self):
        pass


class MockLifespanContext:
    """Mock lifespan context."""

    def __init__(self):
        self.okta_auth_manager = MockOktaAuthManager()


class MockRequestContext:
    """Mock request context."""

    def __init__(self):
        self.lifespan_context = MockLifespanContext()


class MockContext:
    """Mock MCP Context."""

    def __init__(self):
        self.request_context = MockRequestContext()


@pytest.fixture
def mock_context():
    """Provide a mock MCP context."""
    return MockContext()


@pytest.fixture
def mock_okta_client():
    """Provide a mock Okta client."""
    return MockOktaClient()


@pytest.fixture
def mock_auth_manager():
    """Provide a mock auth manager."""
    return MockOktaAuthManager()


@pytest.fixture
def mock_user():
    """Provide a mock user."""
    return MockUser()


@pytest.fixture
def mock_group():
    """Provide a mock group."""
    return MockGroup()


@pytest.fixture
def env_vars(monkeypatch):
    """Set required environment variables for testing."""
    monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
    monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")


@pytest.fixture
def mock_get_okta_client(mock_okta_client):
    """Patch get_okta_client to return mock client."""
    with patch(
        "okta_mcp_server.utils.client.get_okta_client",
        new_callable=AsyncMock,
        return_value=mock_okta_client,
    ) as mock:
        yield mock
