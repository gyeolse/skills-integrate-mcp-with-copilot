"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "teams": {}
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "teams": {}
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "teams": {}
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "teams": {}
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "teams": {}
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "teams": {}
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "teams": {}
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "teams": {}
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "teams": {}
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    for activity_name, activity in activities.items():
        activity.setdefault("teams", {})
    return activities


@app.get("/activities/{activity_name}/teams")
def get_activity_teams(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    activity.setdefault("teams", {})
    return activity["teams"]


@app.post("/activities/{activity_name}/teams")
def create_team_for_activity(activity_name: str, payload: dict):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    team_name = (payload.get("team_name") or payload.get("name") or "").strip()
    if not team_name:
        raise HTTPException(status_code=400, detail="Team name is required")

    activity = activities[activity_name]
    activity.setdefault("teams", {})

    if team_name in activity["teams"]:
        raise HTTPException(status_code=400, detail="Team already exists")

    members = payload.get("members") or []
    normalized_members = []
    seen = set()

    for email in members:
        value = str(email).strip()
        if value and value not in seen:
            normalized_members.append(value)
            seen.add(value)

    team = {"name": team_name, "members": normalized_members}
    activity["teams"][team_name] = team
    return {"message": f"Created team {team_name} for {activity_name}", "team": team}


@app.post("/activities/{activity_name}/teams/{team_name}/members")
def add_member_to_team(activity_name: str, team_name: str, email: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    activity.setdefault("teams", {})

    if team_name not in activity["teams"]:
        raise HTTPException(status_code=404, detail="Team not found")

    team = activity["teams"][team_name]
    normalized_email = email.strip()

    if not normalized_email:
        raise HTTPException(status_code=400, detail="Email is required")

    if normalized_email in team["members"]:
        raise HTTPException(status_code=400, detail="Student is already on this team")

    team["members"].append(normalized_email)
    return {"message": f"Added {normalized_email} to {team_name}", "team": team}


@app.delete("/activities/{activity_name}/teams/{team_name}/members")
def remove_member_from_team(activity_name: str, team_name: str, email: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    activity.setdefault("teams", {})

    if team_name not in activity["teams"]:
        raise HTTPException(status_code=404, detail="Team not found")

    team = activity["teams"][team_name]
    normalized_email = email.strip()

    if normalized_email not in team["members"]:
        raise HTTPException(status_code=400, detail="Student is not on this team")

    team["members"].remove(normalized_email)
    return {"message": f"Removed {normalized_email} from {team_name}", "team": team}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
