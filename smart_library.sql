CREATE DATABASE smart_library;

CREATE TABLE Roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Users
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, 
    role_id INT NOT NULL,
    email VARCHAR(100) UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES Roles(id) ON DELETE RESTRICT
);

-- Authors
CREATE TABLE Authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    bio TEXT
);

-- Books
CREATE TABLE Books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    genre VARCHAR(50),
    publication_year INT,
    available BOOLEAN DEFAULT TRUE NOT NULL 
);

-- BookAuthors (Many-to-Many)
CREATE TABLE BookAuthors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Authors(id) ON DELETE CASCADE
);

-- Loans 
CREATE TABLE Loans (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    borrow_date DATE DEFAULT CURRENT_DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE, -- NULL means currently borrowed
    CONSTRAINT fk_book FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE RESTRICT,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE RESTRICT
);

-- BookClubs
CREATE TABLE BookClubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_by INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES Users(id) ON DELETE RESTRICT
);

-- ClubMemberships
CREATE TABLE ClubMemberships (
    id SERIAL PRIMARY KEY,
    club_id INT NOT NULL,
    user_id INT NOT NULL,
    join_date DATE DEFAULT CURRENT_DATE,
    UNIQUE (club_id, user_id),
    FOREIGN KEY (club_id) REFERENCES BookClubs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 3. TRIGGERS & FUNCTIONS

-- Trigger: Update book availability to FALSE on borrow
CREATE OR REPLACE FUNCTION update_book_on_borrow() RETURNS TRIGGER AS $$
BEGIN
    UPDATE Books SET available = FALSE WHERE id = NEW.book_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_book_borrow AFTER INSERT ON Loans
FOR EACH ROW EXECUTE FUNCTION update_book_on_borrow();

-- Trigger: Update book availability to TRUE on return
CREATE OR REPLACE FUNCTION update_book_on_return() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        UPDATE Books SET available = TRUE WHERE id = NEW.book_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_book_return AFTER UPDATE OF return_date ON Loans
FOR EACH ROW EXECUTE FUNCTION update_book_on_return();

-- Trigger: Max 3 loans
CREATE OR REPLACE FUNCTION prevent_excess_loans() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM Loans WHERE user_id = NEW.user_id AND return_date IS NULL) >= 3 THEN
        RAISE EXCEPTION 'User has reached the maximum limit of 3 active loans.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_loan_limit BEFORE INSERT ON Loans
FOR EACH ROW EXECUTE FUNCTION prevent_excess_loans();

-- 4. INSERT DATA

-- Roles
INSERT INTO Roles (name) VALUES ('Librarian'), ('Member');

-- Authors
INSERT INTO Authors (name, bio) VALUES
('Robert C. Martin', 'Uncle Bob, software engineer.'),
('Frank Herbert', 'Sci-Fi legend.'),
('J.R.R. Tolkien', 'Creator of Middle-earth.'),
('Isaac Asimov', 'Professor of biochemistry and writer.'),
('Agatha Christie', 'Queen of Crime.'),
('Walter Isaacson', ' biographer.'),
('George R.R. Martin', 'Game of Thrones creator.'),
('Brene Brown', 'Researcher on vulnerability.');

-- Users (Librarians and Members)
-- Passwords are plain text for this academic example. In production, hash them!
INSERT INTO Users (username, password_hash, full_name, email, role_id) VALUES
('admin_sarah', 'admin123', 'Sarah Connor', 'sarah@library.com', 1), -- Librarian
('lib_thomas', 'admin123', 'Thomas Anderson', 'neo@library.com', 1),   -- Librarian
('mem_john', 'pass123', 'John Wick', 'john@gmail.com', 2),             -- Member
('mem_jane', 'pass123', 'Jane Doe', 'jane@gmail.com', 2),              -- Member
('mem_peter', 'pass123', 'Peter Parker', 'peter@dailybugle.com', 2),   -- Member
('mem_tony', 'pass123', 'Tony Stark', 'tony@stark.com', 2);            -- Member

-- Books
INSERT INTO Books (title, genre, publication_year, available) VALUES
('Clean Code', 'Technology', 2008, TRUE),
('The Pragmatic Programmer', 'Technology', 1999, TRUE),
('Dune', 'Sci-Fi', 1965, TRUE),
('The Hobbit', 'Fantasy', 1937, TRUE),
('Foundation', 'Sci-Fi', 1951, TRUE),
('Murder on the Orient Express', 'Mystery', 1934, TRUE),
('Steve Jobs', 'Biography', 2011, TRUE),
('A Game of Thrones', 'Fantasy', 1996, TRUE),
('Dare to Lead', 'Self-Help', 2018, TRUE),
('Design Patterns', 'Technology', 1994, TRUE);

-- Link Books to Authors
INSERT INTO BookAuthors (book_id, author_id) VALUES
(1, 1), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 1);

-- Book Clubs
INSERT INTO BookClubs (name, description, created_by) VALUES
('Code Warriors', 'For those learning Python and SQL', 1),
('Sci-Fi Explorers', 'Discussing the future and space', 2),
('Mystery Solvers', 'Who dunnit discussions', 1);

-- Memberships
INSERT INTO ClubMemberships (club_id, user_id) VALUES
(1, 3), (1, 6), -- John and Tony in Code Warriors
(2, 5),         -- Peter in Sci-Fi
(3, 4);         -- Jane in Mystery

-- Initial Loans
-- John borrows Clean Code (Overdue simulation)
INSERT INTO Loans (book_id, user_id, borrow_date, due_date, return_date) VALUES
(1, 3, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '3 days', NULL);

-- Jane borrows Dune (Active)
INSERT INTO Loans (book_id, user_id, borrow_date, due_date, return_date) VALUES
(3, 4, CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days', NULL);