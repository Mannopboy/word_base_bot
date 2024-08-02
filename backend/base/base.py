import sqlite3 as sq

db = sq.connect('base.db')
cur = db.cursor()


async def db_start():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
            username TEXT, 
            telegram_id INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS word (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            answer TEXT, 
            chap_id INTEGER, 
            text TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            name TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chap (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            book_id INTEGER, 
            name TEXT
        )
    """)
    db.commit()


async def add_user(user_id, username, name):
    user = cur.execute("SELECT * FROM user WHERE telegram_id = ?", (user_id,)).fetchone()
    if not user:
        cur.execute("INSERT INTO user (telegram_id, username, name) VALUES (?, ?, ?)", (user_id, username, name))
        db.commit()
        return True
    else:
        return False


async def add_word(state):
    async with state.proxy() as data:
        word = cur.execute("SELECT * FROM word WHERE chap_id = ? AND text = ?",
                           (data['chap_id'], data['name'])).fetchone()
        if not word:
            cur.execute("INSERT INTO word (chap_id, text, answer) VALUES (?, ?, ?)",
                        (data['chap_id'], data['name'], data['answer']))
            db.commit()
            return True
        else:
            return False


async def add_words(state, words):
    async with state.proxy() as data:
        chap_id = data['chap_id']
        for word in words:
            name = word['name']
            answer = word['answer']
            existing_word = cur.execute("SELECT * FROM word WHERE chap_id = ? AND text = ?", (chap_id, name)).fetchone()
            if not existing_word:
                cur.execute("INSERT INTO word (chap_id, text, answer) VALUES (?, ?, ?)", (chap_id, name, answer))
                db.commit()


async def add_book(state):
    async with state.proxy() as data:
        book = cur.execute("SELECT * FROM book WHERE user_id = ? AND name = ?",
                           (data['user_id'], data['name'])).fetchone()
        if not book:
            cur.execute("INSERT INTO book (user_id, name) VALUES (?, ?)", (data['user_id'], data['name']))
            db.commit()
            return True
        else:
            return False


async def add_chap(state):
    async with state.proxy() as data:
        chap = cur.execute("SELECT * FROM chap WHERE book_id = ? AND name = ?",
                           (data['book_id'], data['name'])).fetchone()
        if not chap:
            cur.execute("INSERT INTO chap (book_id, name) VALUES (?, ?)", (data['book_id'], data['name']))
            db.commit()
            return True
        else:
            return False


async def get_words_in_book(book_id):
    chaps = cur.execute("SELECT id FROM chap WHERE book_id = ?", (book_id,)).fetchall()
    chap_ids = [chap[0] for chap in chaps]
    words = cur.execute("SELECT text FROM word WHERE chap_id IN ({seq})".format(
        seq=','.join(['?'] * len(chap_ids))), chap_ids).fetchall()
    return [{'name': word[0]} for word in words]


async def get_words_in_chap(chap_id):
    words = cur.execute("SELECT text FROM word WHERE chap_id = ?", (chap_id,)).fetchall()
    return [{'name': word[0]} for word in words]


async def get_chaps_for_word(user_id):
    books = cur.execute("SELECT id, name FROM book WHERE user_id = ?", (user_id,)).fetchall()
    chaps = cur.execute("SELECT book_id, name FROM chap").fetchall()
    book_dict = {book[0]: book[1] for book in books}
    result = []
    for chap in chaps:
        if chap[0] in book_dict:
            result.append({'name': chap[1], 'text': f"{book_dict[chap[0]]} - {chap[1]}"})
    return result


async def get_chaps(user_id):
    books = cur.execute("SELECT id, name FROM book WHERE user_id = ?", (user_id,)).fetchall()
    chaps = cur.execute("SELECT book_id, name FROM chap").fetchall()
    book_dict = {book[0]: {'book': book[1], 'chaps': []} for book in books}
    for chap in chaps:
        if chap[0] in book_dict:
            book_dict[chap[0]]['chaps'].append({'name': chap[1]})
    return list(book_dict.values())


async def get_word(book_id, text):
    chap_ids = cur.execute("SELECT id FROM chap WHERE book_id = ?", (book_id,)).fetchall()
    chap_ids = [chap[0] for chap in chap_ids]
    word = cur.execute("SELECT answer FROM word WHERE chap_id IN ({seq}) AND text = ?".format(
        seq=','.join(['?'] * len(chap_ids))), chap_ids + [text]).fetchone()
    return word[0] if word else None


async def get_book_chaps(book_id):
    chaps = cur.execute("SELECT name FROM chap WHERE book_id = ?", (book_id,)).fetchall()
    return [{'text': chap[0]} for chap in chaps]


async def get_books(user_id):
    books = cur.execute("SELECT name FROM book WHERE user_id = ?", (user_id,)).fetchall()
    return [{'name': book[0]} for book in books]


async def get_book(user_id, name):
    book = cur.execute("SELECT id FROM book WHERE user_id = ? AND name = ?", (user_id, name)).fetchone()
    return book[0] if book else None


async def get_book_next(user_id, name):
    return await get_book(user_id, name)


async def get_chap_next(book_id, name):
    return await get_chap(book_id, name)


async def get_chap(book_id, name):
    chap = cur.execute("SELECT id FROM chap WHERE book_id = ? AND name = ?", (book_id, name)).fetchone()
    return chap[0] if chap else None


async def get_words(user_id):
    books = cur.execute("SELECT id FROM book WHERE user_id = ?", (user_id,)).fetchall()
    book_ids = [book[0] for book in books]
    chaps = cur.execute("SELECT id FROM chap WHERE book_id IN ({seq})".format(
        seq=','.join(['?'] * len(book_ids))), book_ids).fetchall()
    chap_ids = [chap[0] for chap in chaps]
    words = cur.execute("SELECT text, answer FROM word WHERE chap_id IN ({seq})".format(
        seq=','.join(['?'] * len(chap_ids))), chap_ids).fetchall()
    return [{'word': word[0], 'answer': word[1]} for word in words]
