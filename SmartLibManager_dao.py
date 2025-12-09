import psycopg2
from psycopg2.extras import RealDictCursor
from smartlibrary_classes import User, Member, Librarian, Book, BookClub
import datetime


class SmartLibManagerDAO:
    def __init__(self):
        # UPDATE THESE CREDENTIALS IF NEEDED
        self.db_config = {
            "dbname": "smartlibrary_db",
            "user": "postgres",
            "password": "password",  # Change to your DB password
            "host": "localhost",
            "port": "5432"
        }
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            # Added autocommit to False for transaction control
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Database connection failed: {e}")

    # --- USER CRUD ---
    def authenticate_user(self, username, password):
        query = "SELECT * FROM Users WHERE username = %s AND password_hash = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        if result:
            if result['role_id'] == 1:
                return Librarian(**result)
            return Member(**result)
        return None

    # --- BOOK CRUD ---
    def create_book(self, title, genre, year):
        query = "INSERT INTO Books (title, genre, publication_year) VALUES (%s, %s, %s) RETURNING id"
        self.cursor.execute(query, (title, genre, year))
        book_id = self.cursor.fetchone()['id']
        self.conn.commit()
        return book_id

    def get_all_books(self, search_query=""):
        if search_query:
            query = "SELECT * FROM Books WHERE title ILIKE %s ORDER BY title"
            self.cursor.execute(query, (f"%{search_query}%",))
        else:
            query = "SELECT * FROM Books ORDER BY title"
            self.cursor.execute(query)

        books = []
        for row in self.cursor.fetchall():
            books.append(Book(**row))
        return books

    # --- LOAN SYSTEM ---
    def create_loan(self, book_id, user_id):
        # The SQL Trigger handles the 'Max 3 Loans' and 'Availability' logic
        try:
            borrow_date = datetime.date.today()
            due_date = borrow_date + datetime.timedelta(days=7)

            query = """
                INSERT INTO Loans (book_id, user_id, borrow_date, due_date) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """
            self.cursor.execute(query, (book_id, user_id, borrow_date, due_date))
            loan_id = self.cursor.fetchone()['id']  # Ensure fetchone is before commit
            self.conn.commit()
            return loan_id
        except psycopg2.Error as e:
            self.conn.rollback()
            # Extract only the message part of the error for better user display
            raise ValueError(e.pgerror.split('\n')[0].replace('ERROR:', '').strip())

    def return_loan(self, loan_id):
        try:
            # The Trigger handles making the book available again
            query = "UPDATE Loans SET return_date = CURRENT_DATE WHERE id = %s RETURNING book_id"
            self.cursor.execute(query, (loan_id,))
            if self.cursor.rowcount == 0:
                raise ValueError("No active loan found for this ID.")
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    # --- CLUBS ---
    def create_book_club(self, name, description, created_by):
        query = "INSERT INTO BookClubs (name, description, created_by) VALUES (%s, %s, %s) RETURNING id"
        self.cursor.execute(query, (name, description, created_by))
        club_id = self.cursor.fetchone()['id']
        self.conn.commit()
        return club_id

    def join_club(self, club_id, user_id):
        try:
            query = "INSERT INTO ClubMemberships (club_id, user_id) VALUES (%s, %s)"
            self.cursor.execute(query, (club_id, user_id))
            self.conn.commit()
        except psycopg2.Error:
            self.conn.rollback()
            raise ValueError("Could not join club (Already a member or invalid ID).")

    def get_clubs_summary(self):
        query = """
            SELECT bc.id, bc.name, bc.description, COUNT(cm.user_id) as members
            FROM BookClubs bc
            LEFT JOIN ClubMemberships cm ON bc.id = cm.club_id
            GROUP BY bc.id, bc.name, bc.description
            ORDER BY bc.id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # --- STATS ---
    def get_count(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result['count'] if result and 'count' in result else 0

    def get_top_books(self):
        query = """
            SELECT b.title, COUNT(l.id) as count
            FROM Books b LEFT JOIN Loans l ON b.id = l.book_id
            GROUP BY b.id, b.title
            ORDER BY count DESC LIMIT 5
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()