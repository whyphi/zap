import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
import pytest

from chalicelib.decorators import add_env_suffix, auth
from chalicelib.models.roles import Roles
from chalice import UnauthorizedError


def test_add_env_suffix_dev():
    def mocked_function(self, table_name: str, *args, **kwargs):
        return table_name

    # Create an instance of the decorator
    decorated_function = add_env_suffix(mocked_function)

    # Mock the 'self' argument for the instance method
    instance_mock = object()

    # Call the decorated function with 'env=False'
    result = decorated_function(instance_mock, "test-table", env=False)

    # Check if the suffix is added correctly
    assert result == "test-table-dev"


def test_add_env_suffix_prod():
    def mocked_function(self, table_name: str, *args, **kwargs):
        return table_name

    # Create an instance of the decorator
    decorated_function = add_env_suffix(mocked_function)

    # Mock the 'self' argument for the instance method
    instance_mock = object()

    # Call the decorated function with 'env=True'
    result = decorated_function(instance_mock, "test-table", env=True)

    # Check if the suffix is added correctly
    assert result == "test-table-prod"


@pytest.fixture
def mock_blueprint():
    return Mock()


@pytest.fixture
def mock_ssm(test_secret="SAMPLE_AUTH_SECRET"):
    with patch("boto3.client") as mock_boto_client:
        mock_ssm_client = Mock()
        mock_ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": test_secret}
        }
        mock_boto_client.return_value = mock_ssm_client
        yield


def generate_token(payload, secret):
    return jwt.encode(payload, secret, algorithm="HS256")


def test_auth_allows_valid_token_with_required_role(mock_blueprint, mock_ssm):
    secret = "SAMPLE_AUTH_SECRET"
    token = generate_token(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=30), "roles": ["admin"]},
        secret,
    )
    mock_blueprint.current_request.headers = {"Authorization": f"Bearer {token}"}

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "success"}

    result = protected_route(mock_blueprint)

    assert result == {"message": "success"}


def test_auth_raises_when_authorization_header_missing(mock_blueprint):
    mock_blueprint.current_request.headers = {}

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "should not reach"}

    with pytest.raises(UnauthorizedError, match="Authorization header is missing"):
        protected_route(mock_blueprint)


def test_auth_raises_when_token_is_malformed(mock_blueprint):
    mock_blueprint.current_request.headers = {"Authorization": "InvalidHeader"}

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "should not reach"}

    with pytest.raises(UnauthorizedError, match="Token is missing"):
        protected_route(mock_blueprint)


def test_auth_raises_when_token_expired(mock_blueprint, mock_ssm):
    secret = "SAMPLE_AUTH_SECRET"
    expired_token = generate_token(
        {"exp": datetime.now(timezone.utc) - timedelta(minutes=1), "roles": ["admin"]},
        secret,
    )
    mock_blueprint.current_request.headers = {
        "Authorization": f"Bearer {expired_token}"
    }

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "should not reach"}

    with pytest.raises(UnauthorizedError, match="Token has expired"):
        protected_route(mock_blueprint)


def test_auth_raises_when_token_signature_is_invalid(mock_blueprint):
    invalid_secret = "WRONG_SECRET"
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "roles": ["admin"],
    }
    token = generate_token(payload, invalid_secret)
    mock_blueprint.current_request.headers = {"Authorization": f"Bearer {token}"}

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "should not reach"}

    # Patch SSM to return correct secret (which won’t match token)
    with patch("boto3.client") as mock_boto_client:
        mock_ssm_client = Mock()
        mock_ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": "SAMPLE_AUTH_SECRET"}
        }
        mock_boto_client.return_value = mock_ssm_client

        # Act + Assert
        with pytest.raises(UnauthorizedError, match="Invalid token"):
            protected_route(mock_blueprint)


def test_auth_raises_when_role_not_authorized(mock_blueprint, mock_ssm):
    secret = "SAMPLE_AUTH_SECRET"
    token = generate_token(
        {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "roles": ["member"],
        },
        secret,
    )
    mock_blueprint.current_request.headers = {"Authorization": f"Bearer {token}"}

    @auth(mock_blueprint, roles=[Roles.ADMIN])
    def protected_route(*_):
        return {"message": "should not reach"}

    with pytest.raises(
        UnauthorizedError, match="You do not have permission to access this resource."
    ):
        protected_route(mock_blueprint)
