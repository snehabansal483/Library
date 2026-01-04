from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from library_db import (
    get_all_books, add_book, get_book_by_id, update_book, delete_book, search_books,
    get_all_members, add_member, get_member_by_id, update_member, delete_member, search_members,
    borrow_book, return_book, get_borrowings, get_overdue_books,
    get_dashboard_stats, get_categories, check_isbn_exists
)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Dashboard Route
@app.route('/')
def dashboard():
    stats = get_dashboard_stats()
    recent_borrowings = get_borrowings()[:5]  # Get 5 most recent borrowings
    overdue_books = get_overdue_books()
    return render_template('dashboard.html', stats=stats, recent_borrowings=recent_borrowings, overdue_books=overdue_books)

# Book Routes
@app.route('/books')
def books():
    search_query = request.args.get('search', '')
    if search_query:
        books = search_books(search_query)
    else:
        books = get_all_books()
    return render_template('books.html', books=books, search_query=search_query)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book_route():
    if request.method == 'POST':
        # Validate ISBN is required
        isbn = request.form.get('isbn', '').strip()
        if not isbn:
            flash('ISBN is required to add a book!', 'error')
            categories = get_categories()
            return render_template('add_book.html', categories=categories)
        
        # Check if ISBN already exists
        if check_isbn_exists(isbn):
            flash(f'A book with ISBN "{isbn}" already exists in the library!', 'error')
            categories = get_categories()
            return render_template('add_book.html', categories=categories)
        
        add_book(
            request.form['title'],
            request.form['author'],
            request.form['year'],
            isbn,
            request.form['category'],
            request.form['description']
        )
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    categories = get_categories()
    return render_template('add_book.html', categories=categories)

@app.route('/books/update/<int:book_id>', methods=['GET', 'POST'])
def update_book_route(book_id):
    book = get_book_by_id(book_id)
    if request.method == 'POST':
        # Validate ISBN is required
        isbn = request.form.get('isbn', '').strip()
        if not isbn:
            flash('ISBN is required for the book!', 'error')
            categories = get_categories()
            return render_template('update_book.html', book=book, categories=categories)
        
        # Check if ISBN already exists (excluding current book)
        if check_isbn_exists(isbn, book_id):
            flash(f'A book with ISBN "{isbn}" already exists in the library!', 'error')
            categories = get_categories()
            return render_template('update_book.html', book=book, categories=categories)
        
        update_book(
            book_id,
            request.form['title'],
            request.form['author'],
            request.form['year'],
            isbn,
            request.form['category'],
            request.form['description']
        )
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    categories = get_categories()
    return render_template('update_book.html', book=book, categories=categories)

@app.route('/books/delete/<int:book_id>')
def delete_book_route(book_id):
    delete_book(book_id)
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/books/view/<int:book_id>')
def view_book(book_id):
    book = get_book_by_id(book_id)
    return render_template('view_book.html', book=book)

# Member Routes
@app.route('/members')
def members():
    search_query = request.args.get('search', '')
    if search_query:
        members = search_members(search_query)
    else:
        members = get_all_members()
    return render_template('members.html', members=members, search_query=search_query)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member_route():
    if request.method == 'POST':
        add_member(
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['address']
        )
        flash('Member added successfully!', 'success')
        return redirect(url_for('members'))
    return render_template('add_member.html')

@app.route('/members/update/<int:member_id>', methods=['GET', 'POST'])
def update_member_route(member_id):
    member = get_member_by_id(member_id)
    if request.method == 'POST':
        update_member(
            member_id,
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['address']
        )
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members'))
    return render_template('update_member.html', member=member)

@app.route('/members/delete/<int:member_id>')
def delete_member_route(member_id):
    delete_member(member_id)
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members'))

@app.route('/members/view/<int:member_id>')
def view_member(member_id):
    member = get_member_by_id(member_id)
    return render_template('view_member.html', member=member)

# Borrowing Routes
@app.route('/borrowings')
def borrowings():
    borrowings = get_borrowings()
    return render_template('borrowings.html', borrowings=borrowings)

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        days = int(request.form.get('days', 14))
        borrow_book(book_id, member_id, days)
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('borrowings'))
    
    books = [book for book in get_all_books() if book['status'] == 'Available']
    members = get_all_members()
    return render_template('borrow_book.html', books=books, members=members)

@app.route('/return/<int:book_id>/<int:member_id>')
def return_book_route(book_id, member_id):
    return_book(book_id, member_id)
    flash('Book returned successfully!', 'success')
    return redirect(url_for('borrowings'))

@app.route('/overdue')
def overdue():
    overdue_books = get_overdue_books()
    return render_template('overdue.html', overdue_books=overdue_books)

# API Routes for AJAX
@app.route('/api/books')
def api_books():
    books = get_all_books()
    return jsonify(books)

@app.route('/api/members')
def api_members():
    members = get_all_members()
    return jsonify(members)

# Legacy routes for backward compatibility
@app.route('/add', methods=['GET', 'POST'])
def add():
    return redirect(url_for('add_book_route'))

@app.route('/update/<int:book_id>', methods=['GET', 'POST'])
def update(book_id):
    return redirect(url_for('update_book_route', book_id=book_id))

@app.route('/delete/<int:book_id>')
def delete(book_id):
    return redirect(url_for('delete_book_route', book_id=book_id))

if __name__ == '__main__':
    app.run(debug=True)
