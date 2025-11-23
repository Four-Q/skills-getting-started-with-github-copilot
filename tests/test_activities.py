from fastapi.testclient import TestClient
import copy

from src import app as app_module

client = TestClient(app_module.app)


def backup_activities():
    return copy.deepcopy(app_module.activities)


def restore_activities(backup):
    app_module.activities.clear()
    app_module.activities.update(backup)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    backup = backup_activities()
    try:
        activity_name = "Chess Club"
        email = "test.add.remove@mergington.edu"

        # Ensure email is not present initially
        resp = client.get("/activities")
        assert resp.status_code == 200
        assert email not in resp.json()[activity_name]["participants"]

        # Sign up
        signup_resp = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_resp.status_code == 200
        assert "Signed up" in signup_resp.json().get("message", "")

        # Confirm participant present
        resp_after = client.get("/activities")
        assert email in resp_after.json()[activity_name]["participants"]

        # Unregister
        delete_resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
        assert delete_resp.status_code == 200
        assert "Removed" in delete_resp.json().get("message", "")

        # Confirm removed
        resp_final = client.get("/activities")
        assert email not in resp_final.json()[activity_name]["participants"]
    finally:
        restore_activities(backup)
