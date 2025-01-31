import sqlite3

connection = sqlite3.connect('./data/book_recommendations_for_beg.db')


def init_db_books():
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            genre TEXT NOT NULL,
            name_arabic TEXT NOT NULL,
            name_russian TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    connection.commit()

def init_db_states():
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS UserStates(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cur_state INTEGER NOT NULL
        )
        """
    )
    connection.commit()


def set_user_state(user_id, state=0):
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO UserStates (user_id, cur_state)
        VALUES (?, ?)
        """,
        (user_id, state)
    )
    connection.commit()


def get_user_state(user_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT cur_state FROM UserStates WHERE user_id = ?
        """,
        (user_id,)
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def add_book(creator_id, genre, name_arabic, name_russian, description):
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO Books (creator_id, genre, name_arabic, name_russian, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (creator_id, genre, name_arabic, name_russian, description)  # Значения для вставки
    )
    connection.commit()
    return cursor.lastrowid

def get_book(book_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM Books WHERE id = ?
        """,
        (book_id,)
    )
    result = cursor.fetchone()
    if result:
        resul_dict = {
            "id": result[0],
            "creator_id": result[1],
            "genre": result[2],
            "name_arabic": result[3],
            "name_russian": result[4],
            "description": result[5]
        }
        return resul_dict
    else:
        return None


def delete_book(book_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM Books
        WHERE id = ?
        """,
        (book_id,)
    )
    connection.commit()


def get_all_books():
    cursor = connection.cursor()
    cursor.execute("SELECT id from Books ORDER by id")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        id = row[0]
        result.append(get_book(id))
    return result


def get_dict_ganres(): # возвращает словарь, ключ - жанр, значение - список [id книги, имя на арабском]
    cursor = connection.cursor()
    cursor.execute("SELECT id, genre, name_arabic from Books ORDER by id")
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        genre = row[1]
        name_arabic = row[2]
        id = row[0]
        if genre in result:
            result[genre].append([id, name_arabic])
        else:
            result[genre] = [[id, name_arabic]]
    return result

def close_connection():
    connection.close()

init_db_books()
init_db_states()