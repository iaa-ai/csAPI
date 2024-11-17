# 2.2 
import pytest
from app import app, db, Book


@pytest.fixture(scope='function')
def test_client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:bakanese@localhost/books_api'
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            db.session.query(Book).delete()
            db.session.commit()
        yield testing_client
        with app.app_context():
            db.drop_all()


def create_book(test_client, title, author, year):
    return test_client.post('/api/books', json={
        'title': title,
        'author': author,
        'year': year
    })


def test_create_book(test_client):
    response = create_book(test_client, "New Book", "John Doe", 2021)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "id" in data["data"]


def test_get_book(test_client):
    create_book(test_client, "Book 1", "Author 1", 2021)
    response = test_client.get('/api/books/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["title"] == "Book 1"


def test_get_books(test_client):
    create_book(test_client, "Book 1", "Author 1", 2021)
    response = test_client.get('/api/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 1


def test_update_book(test_client):
    create_book(test_client, "Old Title", "Old Author", 2020)
    response = test_client.put('/api/books/1', json={"title": "Updated Title", "year": 2021})
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["year"] == 2021


def test_delete_book(test_client):
    create_book(test_client, "Book to Delete", "Author", 2022)
    response = test_client.delete('/api/books/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Book with id 1 has been deleted"


def test_not_found(test_client):
    response = test_client.get('/api/books/999')
    assert response.status_code == 404
