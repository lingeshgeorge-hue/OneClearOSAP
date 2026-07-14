from app.database.database import SessionLocal
from app.models.user import User

db = SessionLocal()

role_map = {
    "admin": "Admin",
    "manager": "Manager",
    "agent": "Sales"
}

users = db.query(User).all()

for user in users:
    if user.role in role_map:
        old_role = user.role
        user.role = role_map[user.role]
        print(f"{user.email}: {old_role} -> {user.role}")

db.commit()
db.close()

print("Roles updated successfully.")