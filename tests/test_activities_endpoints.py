"""
Test suite for Mergington High School Activities API.
Tests are structured using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_success(self, client):
        """Test that GET /activities returns all activities with 200 status."""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert "Chess Club" in activities_data
        activity = activities_data["Chess Club"]
        assert required_fields.issubset(activity.keys())

    def test_get_activities_contains_participants_list(self, client):
        """Test that each activity shows current participants."""
        # Arrange
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        chess_club = activities_data["Chess Club"]
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_succeeds(self, client):
        """Test that a new student can successfully sign up for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        activities_data = response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client):
        """Test that a student cannot sign up twice for the same activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_succeeds(self, client):
        """Test that an existing participant can be removed from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_remove_participant_updates_list(self, client):
        """Test that removing a participant actually removes them from the activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        
        # Assert
        activities_data = response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing a non-existent participant returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "notasignup@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found in this activity"

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_then_readd_participant(self, client):
        """Test that a removed participant can sign up again."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        response_get = client.get("/activities")
        assert email in response_get.json()[activity_name]["participants"]
