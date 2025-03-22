
import os

BASE_DIR = os.getcwd()
generated_files = {}

def get_generated_files():
    return generated_files


def get_user_folder(username: str) -> str:
    import os
    user_folder = os.path.join("data/uploads", username)
    os.makedirs(user_folder, exist_ok=True)  # ✅ Ensure the directory exists
    return user_folder


