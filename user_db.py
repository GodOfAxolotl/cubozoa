from models import User

class UserDB:
    def __init__(self):
        self.users = {}
        self.next_user_id = 1

    def add_user(self, username, email, password):
        user_id = self.next_user_id
        new_user = User(user_id, username, email, password)
        self.users[user_id] = new_user
        self.next_user_id += 1
        return new_user

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None
