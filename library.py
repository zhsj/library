from flask import Flask, render_template, flash, request, redirect, \
    url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json

app = Flask(__name__)
app.config.from_pyfile("library.cfg")
db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column("book_id", db.Integer, primary_key=True)
    isbn = db.Column(db.String(13))
    all = db.Column(db.Integer)
    left = db.Column(db.Integer)
    book_name = db.Column(db.String)
    book_author = db.Column(db.String)
    book_price = db.Column(db.Float)
    comment = db.Column(db.String)

    def __init__(self, isbn, all, book_name, book_author, book_price, comment):
        self.isbn = isbn
        self.all = all
        self.left = all
        self.book_name = book_name
        self.book_author = book_author
        self.book_price = book_price
        self.comment = comment

class BookHandle(object):
    def __init__(self):
        pass

    def bookinfo(self, isbn):
        douban_api = 'https://api.douban.com/v2/book/isbn/'
        r = requests.get(douban_api + str(isbn))
        if r.status_code == 404:
            raise ValueError(str(isbn) + ' not found')
        elif r.status_code != 200:
            raise Exception('Fail to get book info of ' +  str(isbn))
        info = json.loads(r.text)
        price_fix = ''.join(list((filter(lambda ch: ch in '0123456789.', info['price']))))
        author_fix = ','.join(info['author'])
        book = Book(info['isbn13'], 0, info['title'], author_fix, price_fix, '')
        return book

    def add(self, isbn):
        check = Book.query.filter_by(isbn = isbn).all()
        if not check:
            try:
                book = self.bookinfo(isbn)
            except ValueError:
                return
            db.session.add(book)
            db.session.commit()

    def update(self, id, new_dict):
        book = Book.query.filter_by(id=id).first()
        for key in new_dict:
            if hasattr(book,key):
                setattr(book,key,new_dict[key])
        db.session.commit()

    def delete(self, id):
        book = Book.query.filter_by(id=id).first()
        db.session.delete(book)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html',
        books = Book.query.all())

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['isbn']:
            flash('ISBN is required', 'error')
        book = Book(request.form['isbn'], request.form['all'], request.form['book_name'],
                     request.form['book_author'], request.form['book_price'], request.form['comment'])
        db.session.add(book)
        db.session.commit()
    return render_template('new.html')

@app.route('/import', methods=['GET', 'POST'])
def import_book():
    if request.method == 'POST':
        if not request.form['isbn']:
            flash('ISBN is required', 'error')
        book_handle = BookHandle()
        for isbn in request.form['isbn'].split():
            book_handle.add(isbn)
    return render_template('import.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        if not request.form['isbn']:
            flash('ISBN is required', 'error')
        book_handle = BookHandle()
        book_handle.update(id, request.form)
    book = Book.query.filter_by(id=id).first()
    return render_template('edit.html', book=book)

@app.route('/del/<int:id>', methods=['GET', 'POST'])
def delete(id):
    book_handle = BookHandle()
    book_handle.delete(id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
