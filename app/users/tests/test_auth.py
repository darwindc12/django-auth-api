import pytest

@pytest.mark.django_db
def test_user_registration(client):
    """
    Ensure a user can register successfully.
    """

    response = client.post(
        "/api/users/register/",
        {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201
