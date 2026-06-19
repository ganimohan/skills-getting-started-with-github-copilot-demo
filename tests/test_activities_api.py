def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert len(payload) >= 1

    first_activity = next(iter(payload.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"

    before_response = client.get("/activities")
    before_participants = before_response.json()[activity_name]["participants"]

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": new_email}
    )

    after_response = client.get("/activities")
    after_participants = after_response.json()[activity_name]["participants"]

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in after_participants
    assert len(after_participants) == len(before_participants) + 1


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_missing_activity_returns_404(client):
    # Arrange

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": existing_email}
    )

    payload = client.get("/activities").json()

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {existing_email} from {activity_name}"
    assert existing_email not in payload[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": "nobody@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
