import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        company_name="Test Company",
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    """Create an inactive test user"""
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Inactive User",
        company_name="Inactive Company",
        role="admin",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_successful_login_with_valid_credentials(client, test_user):
    """Test successful login with valid email and password"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_failure_with_invalid_email(client, test_user):
    """Test login fails with non-existent email"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect email or password"


def test_login_failure_with_invalid_password(client, test_user):
    """Test login fails with incorrect password"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect email or password"


def test_login_blocked_for_inactive_users(client, inactive_user):
    """Test login is blocked for inactive users"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "inactive@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Inactive user"


def test_login_with_empty_credentials(client):
    """Test login fails with empty credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "",
            "password": ""
        }
    )

    assert response.status_code == 401


def test_login_without_credentials(client):
    """Test login fails when credentials are not provided"""
    response = client.post("/api/v1/auth/token")

    assert response.status_code == 422  # Unprocessable Entity
