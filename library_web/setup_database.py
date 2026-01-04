import mysql.connector
import os
from dotenv import load_dotenv
from db_config import connect_db

# Load environment variables
load_dotenv()

def create_database_tables():
    """Create all required tables for the library management system"""
    
    # First, let's create the database if it doesn't exist
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DATABASE', 'library_db')}")
        cursor.execute(f"USE {os.getenv('MYSQL_DATABASE', 'library_db')}")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return
    
    # Now connect to the database and create tables
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Create books table with additional fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INT,
                isbn VARCHAR(20),
                category VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                join_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create borrowings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                member_id INT NOT NULL,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                returned_date DATE NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)
        
        # Check if we need to add new columns to existing books table
        cursor.execute("DESCRIBE books")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'category' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN category VARCHAR(100)")
        
        if 'description' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN description TEXT")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        
        conn.commit()
        print("✅ Database tables created/updated successfully!")
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            print("📚 Adding sample books...")
            sample_books = [
                ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "978-0-7432-7356-5", "Fiction", "A classic American novel set in the 1920s"),
                ("To Kill a Mockingbird", "Harper Lee", 1960, "978-0-06-112008-4", "Fiction", "A gripping tale of racial injustice and childhood innocence"),
                ("1984", "George Orwell", 1949, "978-0-452-28423-4", "Fiction", "A dystopian social science fiction novel"),
                ("Pride and Prejudice", "Jane Austen", 1813, "978-0-14-143951-8", "Romance", "A romantic novel of manners"),
                ("The Catcher in the Rye", "J.D. Salinger", 1951, "978-0-316-76948-0", "Fiction", "A coming-of-age story"),
                ("Python Programming", "John Smith", 2020, "978-1-234-56789-0", "Technology", "Complete guide to Python programming"),
                ("Data Science Handbook", "Jane Doe", 2019, "978-0-987-65432-1", "Technology", "Comprehensive guide to data science"),
                ("World History", "Robert Johnson", 2018, "978-1-111-22222-3", "History", "A comprehensive look at world history")
            ]
            
            for book in sample_books:
                cursor.execute("""
                    INSERT INTO books (title, author, year, isbn, category, description) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, book)
        
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            print("👥 Adding sample members...")
            sample_members = [
                ("John Doe", "john.doe@email.com", "+1-555-0123", "123 Main St, City", "2024-01-15"),
                ("Jane Smith", "jane.smith@email.com", "+1-555-0124", "456 Oak Ave, City", "2024-01-20"),
                ("Mike Johnson", "mike.johnson@email.com", "+1-555-0125", "789 Pine Rd, City", "2024-02-01"),
                ("Sarah Wilson", "sarah.wilson@email.com", "+1-555-0126", "321 Elm St, City", "2024-02-10")
            ]
            
            for member in sample_members:
                cursor.execute("""
                    INSERT INTO members (name, email, phone, address, join_date) 
                    VALUES (%s, %s, %s, %s, %s)
                """, member)
        
        conn.commit()
        conn.close()
        print("✅ Sample data added successfully!")
        print("\n🚀 Library Management System is ready!")
        print("📊 Dashboard: http://localhost:5000/")
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_database_tables()
