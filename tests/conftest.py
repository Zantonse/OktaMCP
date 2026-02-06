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
class MockTempPassword:
    """Mock temporary password response."""

    temp_password: str = "TempPass123!"


@dataclass
class MockResetToken:
    """Mock password reset token response."""

    reset_password_url: str = "https://test.okta.com/reset/token"


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


@dataclass
class MockAuthorizationServer:
    """Mock Okta authorization server object."""

    id: str = "aus1abc123"
    name: str = "Test Auth Server"
    description: str = "Test Description"
    status: str = "ACTIVE"
    audiences: list = None

    def __post_init__(self):
        if self.audiences is None:
            self.audiences = ["api://default"]


@dataclass
class MockPolicy:
    """Mock Okta policy object."""

    id: str = "00p1abc123"
    name: str = "Default Policy"
    status: str = "ACTIVE"


@dataclass
class MockScope:
    """Mock OAuth2 scope object."""

    id: str = "scp1abc123"
    name: str = "test_scope"


@dataclass
class MockClaim:
    """Mock OAuth2 claim object."""

    id: str = "clm1abc123"
    name: str = "test_claim"


@dataclass
class MockIdentityProvider:
    """Mock Okta identity provider object."""

    id: str = "0oa1abc123"
    name: str = "Test IdP"
    type: str = "SAML2"
    status: str = "ACTIVE"


@dataclass
class MockFactor:
    """Mock Okta factor object."""

    id: str = "fct1abc123"
    factor_type: str = "sms"
    provider: str = "OKTA"
    status: str = "ACTIVE"


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

    async def activate_user(self, user_id: str):
        return None, None

    async def reactivate_user(self, user_id: str):
        return None, None

    async def suspend_user(self, user_id: str):
        return None, None

    async def unsuspend_user(self, user_id: str):
        return None, None

    async def unlock_user(self, user_id: str):
        return None, None

    async def expire_password(self, user_id: str):
        return None, None

    async def expire_password_and_get_temporary_password(self, user_id: str):
        return MockTempPassword(), None, None

    async def reset_password(self, user_id: str, params: Optional[Dict] = None):
        return MockResetToken(), None, None

    async def list_user_groups(self, user_id: str, query_params: Optional[Dict] = None):
        return self.groups, MockOktaResponse(), None

    async def list_app_links(self, user_id: str):
        return [], MockOktaResponse(), None

    async def list_applications(self, query_params: Optional[Dict] = None):
        apps = [type("MockApp", (), {"id": "0oa1abc123", "name": "Test App", "label": "Test Application"})]
        return apps, MockOktaResponse(), None

    async def get_application(self, app_id: str, query_params: Optional[Dict] = None):
        app = type("MockApp", (), {"id": app_id, "name": "Test App", "label": "Test Application"})
        return app, MockOktaResponse(), None

    async def create_application(self, app_config: Dict, query_params: Optional[Dict] = None):
        app = type(
            "MockApp", (), {"id": "0oa1abc123", "name": app_config.get("name"), "label": app_config.get("label")}
        )
        return app, MockOktaResponse(), None

    async def update_application(self, app_id: str, app_config: Dict):
        app = type("MockApp", (), {"id": app_id, "name": app_config.get("name"), "label": app_config.get("label")})
        return app, MockOktaResponse(), None

    async def delete_application(self, app_id: str):
        return None, None

    async def activate_application(self, app_id: str):
        return None, None

    async def deactivate_application(self, app_id: str):
        return None, None

    async def list_application_users(self, app_id, query_params=None):
        return self.users, MockOktaResponse(), None

    async def get_application_user(self, app_id, user_id):
        return MockUser(id=user_id), MockOktaResponse(), None

    async def assign_user_to_application(self, app_id, body):
        return MockUser(id=body.get("id", "test")), MockOktaResponse(), None

    async def delete_application_user(self, app_id, user_id):
        return None, None

    async def list_application_group_assignments(self, app_id, query_params=None):
        return self.groups, MockOktaResponse(), None

    async def get_application_group_assignment(self, app_id, group_id):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def create_application_group_assignment(self, app_id, group_id, body):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def delete_application_group_assignment(self, app_id, group_id):
        return None, None

    async def list_authorization_servers(self, query_params=None):
        return [MockAuthorizationServer()], MockOktaResponse(), None

    async def get_authorization_server(self, auth_server_id):
        return MockAuthorizationServer(id=auth_server_id), MockOktaResponse(), None

    async def create_authorization_server(self, body):
        return MockAuthorizationServer(), MockOktaResponse(), None

    async def update_authorization_server(self, auth_server_id, body):
        return MockAuthorizationServer(id=auth_server_id), MockOktaResponse(), None

    async def delete_authorization_server(self, auth_server_id):
        return None, None

    async def activate_authorization_server(self, auth_server_id):
        return None, None

    async def deactivate_authorization_server(self, auth_server_id):
        return None, None

    async def list_authorization_server_policies(self, auth_server_id, query_params=None):
        return [MockPolicy()], MockOktaResponse(), None

    async def create_authorization_server_policy(self, auth_server_id, body):
        return MockPolicy(), MockOktaResponse(), None

    async def list_o_auth2_scopes(self, auth_server_id, query_params=None):
        return [MockScope()], MockOktaResponse(), None

    async def create_o_auth2_scope(self, auth_server_id, body):
        return MockScope(), MockOktaResponse(), None

    async def list_o_auth2_claims(self, auth_server_id, query_params=None):
        return [MockClaim()], MockOktaResponse(), None

    async def create_o_auth2_claim(self, auth_server_id, body):
        return MockClaim(), MockOktaResponse(), None

    async def list_identity_providers(self, query_params=None):
        return [MockIdentityProvider()], MockOktaResponse(), None

    async def get_identity_provider(self, idp_id):
        return MockIdentityProvider(id=idp_id), MockOktaResponse(), None

    async def create_identity_provider(self, body):
        return MockIdentityProvider(), MockOktaResponse(), None

    async def update_identity_provider(self, idp_id, body):
        return MockIdentityProvider(id=idp_id), MockOktaResponse(), None

    async def delete_identity_provider(self, idp_id):
        return None, None

    async def activate_identity_provider(self, idp_id):
        return None, None

    async def deactivate_identity_provider(self, idp_id):
        return None, None

    async def list_factors(self, user_id):
        return [MockFactor()], MockOktaResponse(), None

    async def get_factor(self, user_id, factor_id):
        return MockFactor(id=factor_id), MockOktaResponse(), None

    async def enroll_factor(self, user_id, body):
        return MockFactor(), MockOktaResponse(), None

    async def activate_factor(self, user_id, factor_id, body):
        return MockFactor(id=factor_id), MockOktaResponse(), None

    async def delete_factor(self, user_id, factor_id):
        return None, None

    async def verify_factor(self, user_id, factor_id, body):
        return {"factorResult": "SUCCESS"}, MockOktaResponse(), None


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
