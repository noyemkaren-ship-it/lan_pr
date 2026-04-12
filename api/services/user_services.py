from repository.user_repositroy import UserRepository

user_repo = UserRepository()

def get_user_by_id(id):
    result = user_repo.get_user_by_id(id)
    return result

def get_user_by_name(username):
    result = user_repo.get_user_by_name(username)
    return result

def register_user(name: str, email: str, password: str):
    result = user_repo.create_user(name, email, password)
    return result

def delete_user(id):
    result = user_repo.delete_user(id)
    return result

def authenticate(email_or_name, password):
    result = user_repo.authenticate(email_or_name, password)
    return result