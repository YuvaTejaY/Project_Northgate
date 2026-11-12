from getpass import getpass

from app.database import SessionLocal
from app.models.user import UserRole
from app.services.auth_service import AuthService


def main() -> None:
    email = input("Work email: ").strip()
    full_name = input("Full name: ").strip()
    print("Available roles: " + ", ".join(role.value for role in UserRole))
    role_input = input("Role: ").strip()
    role = next((role for role in UserRole if role.value.lower() == role_input.lower()), None)
    if role is None:
        raise ValueError("Choose one of the listed roles.")

    password = getpass("Password (minimum 12 characters): ")
    if len(password) < 12:
        raise ValueError("The password must contain at least 12 characters.")
    if password != getpass("Confirm password: "):
        raise ValueError("The passwords did not match.")

    with SessionLocal() as db:
        user = AuthService.register_user(
            db,
            email=email,
            full_name=full_name,
            password=password,
            role=role.value,
        )
        print(f"Created {user.role.value} account for {user.email}.")


if __name__ == "__main__":
    main()
