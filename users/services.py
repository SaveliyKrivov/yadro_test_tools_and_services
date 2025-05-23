import requests

from .models import Profile


def fetch_users(count=1):
    """Получает данные пользователей из API randomuser.me"""
    try:
        response = requests.get(f"https://randomuser.me/api/?results={count}")
        return response.json()["results"]
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def save_users_to_db(users_data):
    """Сохраняет данные пользователей в БД"""
    saved_count = 0
    for user_data in users_data:
        try:
            user = Profile(
                gender=user_data["gender"],
                first_name=user_data["name"]["first"],
                last_name=user_data["name"]["last"],
                phone=user_data["phone"],
                email=user_data["email"],
                location=f"{user_data['location']['country']}, {user_data['location']['city']}",
                photo=user_data["picture"]["large"],
            )
            user.save()
            saved_count += 1
        except Exception as e:
            print(f"Error saving user: {e}")

    return saved_count
