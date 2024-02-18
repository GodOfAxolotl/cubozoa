from models import User, db

class UserDB:
    def __init__(self):
        pass

    def add_user(self, username, email, password):
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def check_password(self, username, password):
        user = self.get_user_by_username(username)
        return user and user.check_password(password)
