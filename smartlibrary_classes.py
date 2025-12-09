import datetime

class User:
    def __init__(self, id, username, password_hash, role_id, email, full_name):
        self._id = id
        self._username = username
        self._password_hash = password_hash
        self._role_id = role_id
        self._email = email
        self._full_name = full_name

    @property
    def id(self): return self._id
    @property
    def username(self): return self._username
    @property
    def role_id(self): return self._role_id
    @property
    def full_name(self): return self._full_name
    @property
    def email(self): return self._email

class Member(User):
    def __init__(self, id, username, password_hash, role_id, email, full_name):
        super().__init__(id, username, password_hash, role_id, email, full_name)
        # Note: loan_count is calculated via SQL, not stored permanently in the object
        # to ensure data consistency with the database.

class Librarian(User):
    def __init__(self, id, username, password_hash, role_id, email, full_name):
        super().__init__(id, username, password_hash, role_id, email, full_name)

class Book:
    def __init__(self, id, title, genre, publication_year, available=True):
        self._id = id
        self._title = title
        self._genre = genre
        self._publication_year = publication_year
        self._available = available

    @property
    def id(self): return self._id
    @property
    def title(self): return self._title
    @property
    def genre(self): return self._genre
    @property
    def publication_year(self): return self._publication_year
    @property
    def available(self): return self._available

class BookClub:
    def __init__(self, id, name, description, created_by):
        self._id = id
        self._name = name
        self._description = description
        self._created_by = created_by