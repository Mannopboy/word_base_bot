import sqlite3 as sq

db = sq.connect('base5.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS user ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT , "
                "username TEXT , "
                "telegram_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS word ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "answer TEXT, "
                "text TEXT )")
    db.commit()


async def add_user(user_id, username, name):
    user = cur.execute("SELECT * FROM user WHERE telegram_id = {}".format(user_id)).fetchone()
    print(user)
    if not user:
        user = cur.execute(
            "INSERT INTO user (telegram_id, username, name) VALUES ('%s','%s','%s')" % (user_id, username, name))
        db.commit()
        return user
    else:
        return False


async def add_word(user_id, text, answer):
    # new_word = cur.execute("INSERT INTO word (user_id, text) VALUES {?,?}", (user_id, text))
    cur.execute("INSERT INTO word (user_id, text, answer) VALUES ('%s', '%s','%s')" % (user_id, text, answer))
    db.commit()

# def get_user(name):
#     conn = sqlite3.connect('base.sql')
#     cur = conn.cursor()
#     statement = f"SELECT name from users WHERE name='{name}';"
#     cur.execute(statement)
#     user = cur.fetchone()
#     cur.close()
#     conn.close()
#     return user
