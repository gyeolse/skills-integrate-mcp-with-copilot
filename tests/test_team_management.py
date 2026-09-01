from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_create_and_list_teams_for_activity():
    activity_name = "Chess Club"

    response = client.get(f"/activities/{activity_name}/teams")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    create_response = client.post(
        f"/activities/{activity_name}/teams",
        json={"team_name": "Knight Squad", "members": ["student1@mergington.edu"]},
    )
    assert create_response.status_code == 200, create_response.text
    created_team = create_response.json()["team"]
    assert created_team["name"] == "Knight Squad"
    assert "student1@mergington.edu" in created_team["members"]

    list_response = client.get(f"/activities/{activity_name}/teams")
    assert list_response.status_code == 200
    assert "Knight Squad" in list_response.json()


def test_add_and_remove_member_from_team():
    activity_name = "Programming Class"
    team_name = "Code Crew"

    create_response = client.post(
        f"/activities/{activity_name}/teams",
        json={"team_name": team_name, "members": []},
    )
    assert create_response.status_code == 200, create_response.text

    add_response = client.post(
        f"/activities/{activity_name}/teams/{team_name}/members?email=student2@mergington.edu"
    )
    assert add_response.status_code == 200, add_response.text
    assert "student2@mergington.edu" in add_response.json()["team"]["members"]

    remove_response = client.delete(
        f"/activities/{activity_name}/teams/{team_name}/members?email=student2@mergington.edu"
    )
    assert remove_response.status_code == 200, remove_response.text
    assert "student2@mergington.edu" not in remove_response.json()["team"]["members"]
