from database.base import *
from models.user_model import User
import re

class UserNotFoundError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class InvalidPasswordError(Exception):
    pass

class UserRepository():
    def __init__(self):
        self.session = create_session()
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("неверный формат почты")
    
    def _validate_name(self, name):
        if len(name) < 3 or len(name) > 20:
            raise ValueError("имя должно быть от 3 до 20 символов")
    
    def _validate_password(self, password):
        if len(password) < 8:
            raise ValueError("пароль должен быть не менее 8 символов")
    
    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()
    
    def get_user_by_name(self, name):
        return self.session.query(User).filter(User.name == name).first()
    
    def create_user(self, name, email, password):
        self._validate_name(name)
        self._validate_email(email)
        self._validate_password(password)
        
        if self.get_user_by_email(email):
            raise UserAlreadyExistsError("почта уже занята")
        if self.get_user_by_name(name):
            raise UserAlreadyExistsError("имя уже занято")
        
        user = User(name=name, email=email, password=self._hash_password(password))
        self.session.add(user)
        self.session.commit()
        
        return user
    
    def _hash_password(self, password):
        return password
    
    def authenticate(self, email_or_name, password):
        user = self.get_user_by_email(email_or_name) or self.get_user_by_name(email_or_name)
        
        if not user:
            raise UserNotFoundError("пользователь не найден")
        
        if user.password != self._hash_password(password):
            raise InvalidPasswordError("неверный пароль")
        
        return user
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.session.delete(user)
        self.session.commit()
        return True