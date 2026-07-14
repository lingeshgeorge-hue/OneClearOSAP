from app.database.database import SessionLocal
from app.models.user import User
from app.auth.hashing import hash_password

db = SessionLocal()

users = [
    {
        "full_name": "System Admin",
        "email": "admin@oneclear.com",
        "password": "Admin@123",
        "role": "admin"
    },
    {
        "full_name": "Sales Manager",
        "email": "manager@oneclear.com",
        "password": "Manager@123",
        "role": "manager"
    },
    {
        "full_name": "Lead Agent",
        "email": "agent@oneclear.com",
        "password": "Agent@123",
        "role": "agent"
    }
]

for user_data in users:
    existing = db.query(User).filter(
        User.email == user_data["email"]
    ).first()

    if existing:
        print(f"User already exists: {user_data['email']}")
        continue

    user = User(
        full_name=user_data["full_name"],
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
        role=user_data["role"]
    )

    db.add(user)

db.commit()
db.close()

print("Test users created successfully.")