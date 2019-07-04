from flask import Flask, request, abort, json
from datetime import datetime
import sqlite3 as lite


#       Initialization app / Инициализация приложения
app = Flask(__name__)

######################################################################################################
#       Work with database SQLite3 / Работа с БД SQLite3
#       Initialization db if you need / Инициализация БД если надо
def init_db():
    db = lite.connect('data.db3')
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Article")
    db.commit()
    cursor.execute("""
    CREATE TABLE Article(
    id INTEGER PRIMARY KEY AUTOINCREMENT ,
    author TEXT ,
    created TEXT,
    updated	INTEGER,
    content TEXT)""")
    db.commit()
    cursor.execute("INSERT INTO Article(author,created,updated,content) VALUES(?,?,?,?)",
                   ("Pushkin A.S.", datetime.now(), datetime.now(), "Я помню чудное мгновенье"))
    db.commit()
    cursor.execute("INSERT INTO Article(author,created,updated,content) VALUES(?,?,?,?)",
                   ("Pushkin A.S.", datetime.now(), datetime.now(), "Я помню чудное мгновенье"))
    db.commit()
    db.close()

#       Writing article at db / Запись статьи в бд
def write_db(a, b):
    db = lite.connect('data.db3')
    cursor = db.cursor()
    cursor.execute("INSERT INTO Article(author,created,updated,content) VALUES(?,?,?,?)",
                   (a, datetime.now(), datetime.now(), b))
    db.commit()

#       Update article at db / Обновление статьи в бд
def update_db ( id, a, b):
    db = lite.connect("data.db3")
    cursor = db.cursor()
    if a !="":
        if b != "":
            cursor.execute("UPDATE Article SET author = ?, content = ?,updated = ?  WHERE id = ?",
                           (a, b, datetime.now(), id))
        else:
            cursor.execute("UPDATE Article SET author = ?,updated = ?  WHERE id = ?",
                           (a, datetime.now(), id))
    else:
        if b != "":
            cursor.execute("UPDATE Article SET content = ?,updated = ?  WHERE id = ?",
                           (b, datetime.now(), id))
        else:
            cursor.execute("UPDATE Article SET updated = ?  WHERE id = ?",
                           (datetime.now(), id))
    db.commit()
    db.close()

#       Delete article at db / Удаление статьи из бд
def del_db(id):
    db = lite.connect('data.db3')
    cursor = db.cursor()
    cursor.execute("DELETE FROM Article WHERE id = ?", id)
    db.commit()
    db.close()

#       Reading db / Чтение бд
def read_db():
    db = lite.connect('data.db3')
    cursor = db.cursor()
    dictr = dict()
    cursor.execute("SELECT * FROM Article ")
    tmp = cursor.fetchall()
    dictr.update({"objects ": tmp})
    db.close()
    return dictr

#      Finding article/ Поиск артикля
def find_id(a):
    db = lite.connect('data.db3')
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM Article")
    n = cursor.fetchone()
    n = n[0]
    a = int(a)
    if a > 0:
        if a < n or a == n:
            return True
    return False

#      Reading db by id/ Чтение бд по id
def read_db_id(n):
    db = lite.connect('data.db3')
    cursor = db.cursor()
    if n == "max":
        cursor.execute("SELECT MAX(id) FROM Article")
        n = cursor.fetchone()
        n = n[0]
    dictr = dict()
    cursor.execute("SELECT * FROM Article WHERE id = (?)",  (n,))
    tmp = cursor.fetchall()
    dictr.update({"author": tmp[0][1]})
    dictr.update({"content": tmp[0][4]})
    dictr.update({"created": tmp[0][2]})
    dictr.update({"id": tmp[0][0]})
    dictr.update({"updated": tmp[0][3]})
    db.close()
    return dictr

##################################################################################################
#      main page / основная страница
##################################################################################################
@app.route('/api/articles', methods=["GET"])
def main():
    response = app.response_class(
        response=json.dumps(read_db()),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/api/articles', methods=["POST"])
def main_back():
    if request.is_json:
        f = request.get_json()
        if f["author"] !="":
            if f["content"] !="":
                write_db(f["author"], f["content"])
                response = app.response_class(
                    response=json.dumps(read_db_id("max")),
                    status=200,
                    mimetype='application/json'
                )
                return response
            else:
                abort(400)
        else:
            abort(400)
    else:
        abort(400)

##################################################################################################
#       articles pages / страницы статей
##################################################################################################
@app.route('/api/articles/<id>', methods=["GET"])
def get_art(id):
    if find_id(int(id)) == True:
        response = app.response_class(
            response=json.dumps(read_db_id(id)),
            status=200,
            mimetype='application/json'
        )
    else:
        data = dict()
        word = "article " + str(id) + " not found"
        data.update({"message": word})
        response = app.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
        )
    return response

@app.route('/api/articles/<id>', methods=["PUT","PATCH"])
def upd_art(id):
    if find_id(int(id)) == True:
        if request.is_json:
            f = request.get_json()
            update_db(id, f["author"], f["content"])
            response = app.response_class(
                response=json.dumps(read_db_id(int(id))),
                status=200,
                mimetype='application/json'
            )
        else:
            abort(400)
    else:
        data = dict()
        word = "article " + str(id) + " not found"
        data.update({"message": word})
        response = app.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
        )
    return response

@app.route('/api/articles/<id>', methods=["DELETE"])
def del_art(id):
    if find_id(int(id)) == True:
        del_db(id)
        response = app.response_class(
            response=json.dumps({"message": "ok"}),
            status=200,
            mimetype='application/json'
        )
    else:
        data = dict()
        word = "article " + str(id) + " not found"
        data.update({"message": word})
        response = app.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
        )
    return response

@app.errorhandler(400)
def not_found(error):
    dictr = dict()
    dictr.update({"message": "Not correct input data"})
    response = app.response_class(
        response=json.dumps(dictr),
        status=400,
        mimetype='application/json'
    )
    return response

#       Start / Старт
if __name__ == "__main__":
    init_db()
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
