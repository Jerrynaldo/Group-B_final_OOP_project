import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QGroupBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from SmartLibManager_dao import SmartLibManagerDAO

# Styling
STYLE = """
    QMainWindow { background-color: #0d1b2a; }
    QLabel { color: #000; font-size: 14px; }
    QLineEdit, QComboBox {
        background-color: #1b263b; color: #e0e1dd; border: 2px solid #415a77;
        border-radius: 10px; padding: 10px; font-size: 14px;
    }
    QPushButton {
        background-color: #415a77; color: white; border: none; padding: 12px;
        border-radius: 10px; font-weight: bold; font-size: 14px;
    }
    QPushButton:hover { background-color: #778da9; }
    QTableWidget { background-color: #1b263b; color: #e0e1dd; gridline-color: #33415c; }
    QHeaderView::section { background-color: #415a77; color: white; padding: 12px; font-weight: bold; }
    QGroupBox { color: #778da9; border: 2px solid #415a77; border-radius: 12px; margin-top: 20px; font-weight: bold;}
"""


class SmartLibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dao = SmartLibManagerDAO()
        self.current_user = None
        self.setWindowTitle("SmartLibrary System")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet(STYLE)
        self.init_login()

        # Dashboard elements initialized here to be accessible for refresh
        self.stat_widgets = {}  # Stores the QLabel objects for the counts
        self.summary_label = QLabel()

    def init_login(self):
        # ... (Login setup code remains the same)
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(300, 100, 300, 100)
        layout.setSpacing(15)

        title = QLabel("LIBRARY SYSTEM")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username (e.g., admin_sarah, mem_john)")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("LOGIN")
        login_btn.clicked.connect(self.authenticate)

        layout.addWidget(title)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(login_btn)
        widget.setLayout(layout)

    def authenticate(self):
        u = self.username_edit.text()
        p = self.password_edit.text()
        user = self.dao.authenticate_user(u, p)

        if user:
            self.current_user = user
            QMessageBox.information(self, "Success", f"Welcome {user.full_name}!")
            self.show_main_interface()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def show_main_interface(self):
        # ... (Main interface setup code remains the same)
        self.centralWidget().deleteLater()
        layout = QVBoxLayout()

        header = QLabel(
            f"Logged in as: {self.current_user.full_name} ({'Librarian' if self.current_user.role_id == 1 else 'Member'})")
        header.setStyleSheet("font-size: 18px; color: #778da9; padding: 10px;")
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_catalog_tab(), "Catalog")
        self.tabs.addTab(self.create_loan_tab(), "Borrow/Return")
        if self.current_user.role_id == 1:
            self.tabs.addTab(self.create_admin_tab(), "Admin: Add Book")
        self.tabs.addTab(self.create_club_tab(), "Clubs")
        self.tabs.addTab(self.create_dashboard_tab(), "Dashboard")

        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_catalog_tab(self):
        # ... (Catalog tab creation code remains the same)
        widget = QWidget()
        layout = QVBoxLayout()

        # Search
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search title...")
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.load_catalog)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(btn_search)

        # Table
        self.book_table = QTableWidget(0, 5)
        self.book_table.setHorizontalHeaderLabels(["ID", "Title", "Genre", "Year", "Status"])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(search_layout)
        layout.addWidget(self.book_table)
        widget.setLayout(layout)
        self.load_catalog()
        return widget

    def load_catalog(self):
        # ... (load_catalog code remains the same)
        query = self.search_bar.text()
        books = self.dao.get_all_books(query)
        self.book_table.setRowCount(len(books))
        for i, b in enumerate(books):
            status = "Available" if b.available else "Borrowed"
            color = "#4CAF50" if b.available else "#F44336"

            self.book_table.setItem(i, 0, QTableWidgetItem(str(b.id)))
            self.book_table.setItem(i, 1, QTableWidgetItem(b.title))
            self.book_table.setItem(i, 2, QTableWidgetItem(b.genre))
            self.book_table.setItem(i, 3, QTableWidgetItem(str(b.publication_year)))

            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor(color))
            self.book_table.setItem(i, 4, status_item)

    def create_loan_tab(self):
        # ... (Loan tab creation code remains the same)
        widget = QWidget()
        layout = QVBoxLayout()

        box = QGroupBox("Action Panel")
        form = QFormLayout()

        self.loan_book_id = QLineEdit()
        self.loan_book_id.setPlaceholderText("Book ID")

        btn_borrow = QPushButton("Borrow Book")
        btn_borrow.clicked.connect(self.handle_borrow)

        btn_return = QPushButton("Return Book (By Loan ID)")
        btn_return.clicked.connect(self.handle_return)

        form.addRow("Book ID (to borrow):", self.loan_book_id)
        form.addRow(btn_borrow)
        form.addRow(QLabel(" --- OR --- "))
        form.addRow(btn_return)

        box.setLayout(form)
        layout.addWidget(box)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def handle_borrow(self):
        try:
            bid = int(self.loan_book_id.text())
            # Use current logged in user ID
            self.dao.create_loan(bid, self.current_user.id)
            QMessageBox.information(self, "Success", "Book Borrowed! Due in 7 days.")
            self.load_catalog()
            self.refresh_dashboard_data()  # 🔥 NEW: Refresh Dashboard
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_return(self):
        lid, ok = QInputDialog.getText(self, "Return", "Enter Loan ID:")
        if ok and lid:
            try:
                self.dao.return_loan(int(lid))
                QMessageBox.information(self, "Success", "Book Returned.")
                self.load_catalog()
                self.refresh_dashboard_data()  # 🔥 NEW: Refresh Dashboard
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_admin_tab(self):
        # ... (Admin tab creation code remains the same)
        widget = QWidget()
        layout = QVBoxLayout()
        box = QGroupBox("Add New Book")
        form = QFormLayout()

        self.new_title = QLineEdit()
        self.new_genre = QLineEdit()
        self.new_year = QLineEdit()

        btn = QPushButton("Add to Library")
        btn.clicked.connect(self.handle_add_book)

        form.addRow("Title:", self.new_title)
        form.addRow("Genre:", self.new_genre)
        form.addRow("Year:", self.new_year)
        form.addRow(btn)

        box.setLayout(form)
        layout.addWidget(box)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def handle_add_book(self):
        try:
            self.dao.create_book(self.new_title.text(), self.new_genre.text(), int(self.new_year.text()))
            QMessageBox.information(self, "Success", "Book Added.")
            self.load_catalog()
            self.refresh_dashboard_data()  # 🔥 NEW: Refresh Dashboard
            self.new_title.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_club_tab(self):
        # ... (Club tab creation code remains the same)
        widget = QWidget()
        layout = QVBoxLayout()

        # List Clubs
        self.club_table = QTableWidget(0, 4)
        self.club_table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Members"])
        self.club_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        btn_refresh = QPushButton("Refresh List")
        btn_refresh.clicked.connect(self.load_clubs)

        # Join
        btn_join = QPushButton("Join a Club")
        btn_join.clicked.connect(self.handle_join_club)

        layout.addWidget(self.club_table)
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_join)
        widget.setLayout(layout)
        self.load_clubs()
        return widget

    def load_clubs(self):
        # ... (load_clubs code remains the same)
        clubs = self.dao.get_clubs_summary()
        self.club_table.setRowCount(len(clubs))
        for i, c in enumerate(clubs):
            self.club_table.setItem(i, 0, QTableWidgetItem(str(c['id'])))
            self.club_table.setItem(i, 1, QTableWidgetItem(c['name']))
            self.club_table.setItem(i, 2, QTableWidgetItem(c['description']))
            self.club_table.setItem(i, 3, QTableWidgetItem(str(c['members'])))

    def handle_join_club(self):
        # ... (handle_join_club code remains the same)
        cid, ok = QInputDialog.getText(self, "Join", "Enter Club ID to join:")
        if ok and cid:
            try:
                self.dao.join_club(int(cid), self.current_user.id)
                QMessageBox.information(self, "Success", "Joined Club!")
                self.load_clubs()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_dashboard_tab(self):
        widget = QWidget()
        self.dashboard_layout = QVBoxLayout()  # Store the layout for easy refresh

        # Quick Stats
        self.stats_layout = QHBoxLayout()
        self.stat_widgets = {}  # Reset to hold the current QLabel objects

        # Initialize stat labels
        stats_data = [("Total Books", "#2196F3"), ("Members", "#9C27B0"), ("Active Loans", "#FF9800")]

        for label, color in stats_data:
            lbl = QLabel(f"{label}\n--")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                f"background: {color}; color: white; font-weight: bold; padding: 20px; border-radius: 10px; font-size: 16px;")
            self.stat_widgets[label] = lbl  # Store the label object
            self.stats_layout.addWidget(lbl)

        self.dashboard_layout.addLayout(self.stats_layout)

        # Text Summary
        self.summary_label.setStyleSheet("font-size: 14px; margin-top: 20px; color: #e0e1dd;")
        self.dashboard_layout.addWidget(self.summary_label)
        self.dashboard_layout.addStretch()

        widget.setLayout(self.dashboard_layout)
        self.refresh_dashboard_data()  # Load initial data when creating the tab
        return widget

    def refresh_dashboard_data(self):
        try:
            # Update Quick Stats
            count_books = self.dao.get_count("SELECT COUNT(*) as count FROM Books")
            count_members = self.dao.get_count("SELECT COUNT(*) as count FROM Users WHERE role_id=2")
            count_loans = self.dao.get_count("SELECT COUNT(*) as count FROM Loans WHERE return_date IS NULL")

            self.stat_widgets["Total Books"].setText(f"Total Books\n{count_books}")
            self.stat_widgets["Members"].setText(f"Members\n{count_members}")
            self.stat_widgets["Active Loans"].setText(f"Active Loans\n{count_loans}")

            # Update Top Books
            top_books_data = self.dao.get_top_books()
            txt = "<h3>Top Borrowed Books</h3>"
            if top_books_data:
                for b in top_books_data:
                    txt += f"• {b['title']} ({b['count']} times)<br>"
            else:
                txt += "<i>No loans recorded yet.</i>"

            self.summary_label.setText(txt)

        except Exception as e:
            # Handle potential connection issues when refreshing
            print(f"Error refreshing dashboard: {e}")
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SmartLibraryApp()
    window.show()
    sys.exit(app.exec_())