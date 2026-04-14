from repository.user_repositroy import UserRepository, UserNotFoundError, InvalidPasswordError, UserAlreadyExistsError

user_repo = UserRepository()

def get_user_by_id(id):
    try:
        result = user_repo.get_user_by_id(id)
        return result
    except Exception as e:
        print(f"Error getting user by id {id}: {e}")
        return None

def get_user_by_name(username):
    try:
        result = user_repo.get_user_by_name(username)
        return result
    except Exception as e:
        print(f"Error getting user by name {username}: {e}")
        return None

def register_user(name: str, email: str, password: str):
    try:
        result = user_repo.create_user(name, email, password)
        return {"success": True, "user": result, "error": None}
    except UserAlreadyExistsError as e:
        return {"success": False, "user": None, "error": str(e)}
    except ValueError as e:
        return {"success": False, "user": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "user": None, "error": f"Ошибка регистрации: {str(e)}"}

def delete_user(id):
    try:
        result = user_repo.delete_user(id)
        if result:
            return {"success": True, "error": None}
        else:
            return {"success": False, "error": "Пользователь не найден"}
    except Exception as e:
        return {"success": False, "error": f"Ошибка удаления: {str(e)}"}

def authenticate(email_or_name, password):
    try:
        result = user_repo.authenticate(email_or_name, password)
        return {"success": True, "user": result, "error": None}
    except UserNotFoundError as e:
        return {"success": False, "user": None, "error": str(e)}
    except InvalidPasswordError as e:
        return {"success": False, "user": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "user": None, "error": f"Ошибка аутентификации: {str(e)}"} 