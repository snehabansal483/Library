
from db_config import connect_db
from datetime import datetime, timedelta

# Book Functions
def get_all_books():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, 
               CASE WHEN br.id IS NOT NULL THEN 'Borrowed' ELSE 'Available' END as status,
               m.name as borrowed_by,
               br.due_date
        FROM books b 
        LEFT JOIN borrowings br ON b.id = br.book_id AND br.returned_date IS NULL
        LEFT JOIN members m ON br.member_id = m.id
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def add_book(title, author, year, isbn, category, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (title, author, year, isbn, category, description) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, author, year, isbn, category, description))
    conn.commit()
    conn.close()

def get_book_by_id(book_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_book(book_id, title, author, year, isbn, category, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books SET title=%s, author=%s, year=%s, isbn=%s, category=%s, description=%s 
        WHERE id=%s
    """, (title, author, year, isbn, category, description, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
    conn.commit()
    conn.close()

def search_books(query):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, 
               CASE WHEN br.id IS NOT NULL THEN 'Borrowed' ELSE 'Available' END as status,
               m.name as borrowed_by
        FROM books b 
        LEFT JOIN borrowings br ON b.id = br.book_id AND br.returned_date IS NULL
        LEFT JOIN members m ON br.member_id = m.id
        WHERE b.title LIKE %s OR b.author LIKE %s OR b.category LIKE %s
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    result = cursor.fetchall()
    conn.close()
    return result

# Member Functions
def get_all_members():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, 
               COUNT(br.id) as books_borrowed
        FROM members m 
        LEFT JOIN borrowings br ON m.id = br.member_id AND br.returned_date IS NULL
        GROUP BY m.id
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def add_member(name, email, phone, address):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO members (name, email, phone, address, join_date) 
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, phone, address, datetime.now().date()))
    conn.commit()
    conn.close()

def get_member_by_id(member_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE id=%s", (member_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_member(member_id, name, email, phone, address):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE members SET name=%s, email=%s, phone=%s, address=%s 
        WHERE id=%s
    """, (name, email, phone, address, member_id))
    conn.commit()
    conn.close()

def delete_member(member_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=%s", (member_id,))
    conn.commit()
    conn.close()

def search_members(query):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM members 
        WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    result = cursor.fetchall()
    conn.close()
    return result

# Borrowing Functions
def borrow_book(book_id, member_id, days=14):
    conn = connect_db()
    cursor = conn.cursor()
    due_date = datetime.now().date() + timedelta(days=days)
    cursor.execute("""
        INSERT INTO borrowings (book_id, member_id, borrow_date, due_date) 
        VALUES (%s, %s, %s, %s)
    """, (book_id, member_id, datetime.now().date(), due_date))
    conn.commit()
    conn.close()

def return_book(book_id, member_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE borrowings SET returned_date = %s 
        WHERE book_id = %s AND member_id = %s AND returned_date IS NULL
    """, (datetime.now().date(), book_id, member_id))
    conn.commit()
    conn.close()

def get_borrowings():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, b.title, b.author, m.name as member_name,
               CASE WHEN br.returned_date IS NULL THEN 'Active' ELSE 'Returned' END as status,
               CASE WHEN br.due_date < CURDATE() AND br.returned_date IS NULL THEN 'Overdue' ELSE 'Normal' END as overdue_status
        FROM borrowings br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
        ORDER BY br.borrow_date DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_overdue_books():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.*, b.title, b.author, m.name as member_name, m.email, m.phone
        FROM borrowings br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
        WHERE br.due_date < CURDATE() AND br.returned_date IS NULL
    """)
    result = cursor.fetchall()
    conn.close()
    return result

# Dashboard Functions
def get_dashboard_stats():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # Total books
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    total_books = cursor.fetchone()['total_books']
    
    # Total members
    cursor.execute("SELECT COUNT(*) as total_members FROM members")
    total_members = cursor.fetchone()['total_members']
    
    # Books borrowed
    cursor.execute("SELECT COUNT(*) as books_borrowed FROM borrowings WHERE returned_date IS NULL")
    books_borrowed = cursor.fetchone()['books_borrowed']
    
    # Overdue books
    cursor.execute("SELECT COUNT(*) as overdue_books FROM borrowings WHERE due_date < CURDATE() AND returned_date IS NULL")
    overdue_books = cursor.fetchone()['overdue_books']
    
    conn.close()
    
    return {
        'total_books': total_books,
        'total_members': total_members,
        'books_borrowed': books_borrowed,
        'available_books': total_books - books_borrowed,
        'overdue_books': overdue_books
    }

def get_categories():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != ''")
    result = cursor.fetchall()
    conn.close()
    return [row['category'] for row in result]

def check_isbn_exists(isbn, exclude_book_id=None):
    """Check if ISBN already exists in the database"""
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    if exclude_book_id:
        cursor.execute("SELECT id FROM books WHERE isbn = %s AND id != %s", (isbn, exclude_book_id))
    else:
        cursor.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None
