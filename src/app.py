"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "dev-secret-key-change-me"),
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")


class AuthRegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class AuthLoginRequest(BaseModel):
    email: str
    password: str


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


users_db: Dict[str, Dict[str, object]] = {
    "student@mergington.edu": {
        "name": "Demo Student",
        "email": "student@mergington.edu",
        "role": "student",
        "password_hash": "",
    },
    "clubadmin@mergington.edu": {
        "name": "Demo Club Admin",
        "email": "clubadmin@mergington.edu",
        "role": "club_admin",
        "password_hash": "",
    },
    "superadmin@mergington.edu": {
        "name": "Demo Super Admin",
        "email": "superadmin@mergington.edu",
        "role": "super_admin",
        "password_hash": "",
    },
}


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{derived.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or ":" not in stored_hash:
        return False

    salt_hex, digest_hex = stored_hash.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(derived.hex(), digest_hex)


for email, user in users_db.items():
    user["password_hash"] = _hash_password("student123" if email == "student@mergington.edu" else "admin123" if email == "clubadmin@mergington.edu" else "super123")


def _serialize_user(user: Dict[str, object]) -> Dict[str, object]:
    return {
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


def _get_session_user(request: Request) -> Optional[Dict[str, object]]:
    return request.session.get("user")


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/login.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/api/auth/register")
def register_user(payload: AuthRegisterRequest, request: Request):
    email = _normalize_email(payload.email)
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password is required")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if email in users_db:
        raise HTTPException(status_code=400, detail="An account with that email already exists")

    user = {
        "name": payload.name.strip(),
        "email": email,
        "role": "student",
        "password_hash": _hash_password(payload.password),
    }
    users_db[email] = user
    request.session["user"] = _serialize_user(user)

    return {"message": "Account created successfully", "user": _serialize_user(user)}


@app.post("/api/auth/login")
def login_user(payload: AuthLoginRequest, request: Request):
    email = _normalize_email(payload.email)
    user = users_db.get(email)
    if not user or not _verify_password(payload.password, str(user["password_hash"])):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    request.session["user"] = _serialize_user(user)
    return {"message": "Signed in successfully", "user": _serialize_user(user)}


@app.get("/api/auth/me")
def get_current_user(request: Request):
    user = _get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.post("/api/auth/logout")
def logout_user(request: Request):
    request.session.clear()
    return {"message": "Signed out successfully"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: Optional[str] = None, request: Request = None):
    """Sign up a student for an activity"""
    current_user = _get_session_user(request) if request is not None else None
    selected_email = email or (current_user["email"] if current_user else None)

    if not selected_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if selected_email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(selected_email)
    return {"message": f"Signed up {selected_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: Optional[str] = None, request: Request = None):
    """Unregister a student from an activity"""
    current_user = _get_session_user(request) if request is not None else None
    selected_email = email or (current_user["email"] if current_user else None)

    if not selected_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if selected_email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(selected_email)
    return {"message": f"Unregistered {selected_email} from {activity_name}"}
