import sqlite3 as sq

db = sq.connect('base1.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS user ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT , "
                "username TEXT , "
                "telegram_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS word ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                # "user_id INTEGER, "
                "answer TEXT, "
                "chap_id INTEGER, "
                "text TEXT )")
    cur.execute("CREATE TABLE IF NOT EXISTS book ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "name TEXT )")
    cur.execute("CREATE TABLE IF NOT EXISTS chap ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "book_id INTEGER, "
                "name TEXT )")
    db.commit()


async def add_user(user_id, username, name):
    user = cur.execute("SELECT * FROM user WHERE telegram_id = {}".format(user_id)).fetchone()
    if not user:
        user = cur.execute(
            "INSERT INTO user (telegram_id, username, name) VALUES ('%s','%s','%s')" % (user_id, username, name))
        db.commit()
        return user
    else:
        return False


async def add_word(state):
    async with state.proxy() as data:
        word = cur.execute(
            "SELECT * FROM word WHERE (chap_id, text) = ('%s', '%s')" % (data['chap_id'], data['name'])).fetchone()
        if not word:
            cur.execute("INSERT INTO word (chap_id, text, answer) VALUES ('%s', '%s', '%s')" % (
                data['chap_id'], data['name'], data['answer']))
            db.commit()
            return True
        else:
            return False


async def add_book(state):
    async with state.proxy() as data:
        book = cur.execute(
            "SELECT * FROM book WHERE (user_id, name) = ('%s', '%s')" % (data['user_id'], data['name'])).fetchone()
        if not book:
            cur.execute("INSERT INTO book (user_id, name) VALUES ('%s', '%s')" % (data['user_id'], data['name']))
            db.commit()
            return True
        else:
            return False


async def add_chap(state):
    async with state.proxy() as data:
        chap = cur.execute(
            "SELECT * FROM chap WHERE (book_id, name) = ('%s', '%s')" % (data['book_id'], data['name'])).fetchone()
        if not chap:
            cur.execute("INSERT INTO chap (book_id, name) VALUES ('%s', '%s')" % (data['book_id'], data['name']))
            db.commit()
            return True
        else:
            return False


async def get_words(user_id):
    words = cur.execute("SELECT * FROM word").fetchall()
    list = []
    for word in words:
        if word[1] == user_id:
            info = {
                'word': word[3],
                'answer': word[2]
            }
            list.append(info)
    return list


async def get_chaps_for_word(user_id):
    chaps = cur.execute("SELECT * FROM chap").fetchall()
    books = cur.execute("SELECT * FROM book").fetchall()
    list = []
    list_books = []
    for book in books:
        if book[1] == user_id:
            info = {
                'id': book[0],
            }
            list_books.append(info)
    for book in list_books:
        for chap in chaps:
            if chap[1] == book['id']:
                info_chap = {
                    'name': chap[2]
                }
                list.append(info_chap)
    return list


async def get_chaps(user_id):
    chaps = cur.execute("SELECT * FROM chap").fetchall()
    books = cur.execute("SELECT * FROM book").fetchall()
    list = []
    list_books = []
    for book in books:
        if book[1] == user_id:
            info = {
                'id': book[0],
                'name': book[2],
            }
            list_books.append(info)
    for book in list_books:
        info = {
            'book': book['name'],
            'chaps': []
        }
        for chap in chaps:
            if chap[1] == book['id']:
                info_chap = {
                    'name': chap[2]
                }
                info['chaps'].append(info_chap)
        list.append(info)
    return list


async def get_word(user_id, text):
    words = cur.execute("SELECT * FROM word").fetchall()
    answer = None
    for word in words:
        if word[1] == user_id and word[3] == text:
            answer = word[2]
    return answer


async def get_book_chaps(book_id):
    chaps = cur.execute("SELECT * FROM chap").fetchall()
    list = []
    for chap in chaps:
        if chap[1] == book_id:
            info = {
                'name': chap[2],
            }
            list.append(info)
    return list


async def get_books(user_id):
    books = cur.execute("SELECT * FROM book").fetchall()
    list = []
    for book in books:
        if book[1] == user_id:
            info = {
                'name': book[2],
            }
            list.append(info)
    return list


async def get_book(user_id, name):
    book = cur.execute(
        "SELECT * FROM book WHERE (user_id, name) = ('%s', '%s')" % (user_id, name)).fetchone()
    return book[0]


async def get_chap(book_id, name):
    chap = cur.execute(
        "SELECT * FROM chap WHERE (book_id, name) = ('%s', '%s')" % (book_id, name)).fetchone()
    return chap[0]
