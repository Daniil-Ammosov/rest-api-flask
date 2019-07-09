from flask import Flask, request, abort, json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

#       Initialization app / Инициализация приложения
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db3'

db = create_engine('sqlite:///data.db3', echo=True)
Session = sessionmaker(bind=db)
Base = declarative_base()
db.execute("DROP TABLE IF EXISTS Article")

class Article(Base):
    __tablename__ = 'Article'
    id = Column(Integer, primary_key=True)
    author = Column(String(80), nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    content = Column(String(80), nullable=False)

    def __init__(self, author, created, updated, content):
        self.author = author
        self.created = created
        self.updated = updated
        self.content = content

    def __repr__(self):
        return "<Article('%s', '%s', '%s', '%s')>" % (self.author, self.created,  self.updated,  self.content)

Base.metadata.create_all(db)

######################################################################################################
#       Work with database SQLite3 / Работа с БД SQLite3
#       Initialization db if you need / Инициализация БД если надо
def init_db():
    session = Session()
    session.add_all([Article('Pushkin A.S.', datetime.now(), datetime.now(), "Я помню чудное мгновенье"),
                     Article('Pushkin A.S.', datetime.now(), datetime.now(), "Я помню чудное мгновенье")])
    session.commit()
    session.close()

#       Reading db / Чтение бд
def read_db():
    session = Session()
    session.query(Article).all()
    dictr = dict()
    dictr["objects"] = [dict({"id": id, "author": author, "created": created, "updated": updated,
                        "content": content}) for id, author, created, updated, content in session.query(Article.id,
                                                                                                        Article.author,
                                                                                                        Article.created,
                                                                                                        Article.updated,
                                                                                                        Article.content)]
    session.close()
    return dictr

#      Reading db by id/ Чтение бд по id
def read_db_id(n):
    session = Session()
    if n == "max":
        n = session.query(func.max(Article.id)).one()
        n = n[0]
    dictr = dict()
    dictr.update({"author": session.query(Article.author).filter_by(id=n).one()[0]})
    dictr.update({"content": session.query(Article.content).filter_by(id=n).one()[0]})
    dictr.update({"created": session.query(Article.created).filter_by(id=n).one()[0]})
    dictr.update({"id": n})
    dictr.update({"updated": session.query(Article.updated).filter_by(id=n).one()[0]})
    session.close()
    return dictr

#       Writing article at db / Запись статьи в бд
def write_db(a, b):
    session = Session()
    session.add(Article(str(a), datetime.now(), datetime.now(), str(b)))
    session.commit()
    session.close()

#       Update article at db / Обновление статьи в бд
def update_db (id, a, b):
    session = Session()
    art = session.query(Article).filter_by(id=id).first()
    if a != None:
        if b != None:
            art.author = a
            art.content = b
            art.updated = datetime.now()
        else:
            art.author = a
            art.updated = datetime.now()
    else:
        if b != None:
            art.content = b
            art.updated = datetime.now()
        else:
            art.updated = datetime.now()

    session.add(art)
    session.commit()
    session.close()

#       Delete article at db / Удаление статьи из бд
def del_db(id):
    session = Session()
    x = session.query(Article).filter_by(id=id).first()
    session.delete(x)
    session.commit()
    session.close()

#      Finding article/ Поиск артикля
def find_id(a):
    res = db.execute("SELECT MAX(id) FROM Article")
    n = res.fetchone()
    n = n[0]
    a = int(a)
    if a > 0:
        if a < n or a == n:
            return True
    return False

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
        if "author" in f:
            if "content" in f:
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
    if find_id(int(id)):
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
    if find_id(int(id)):
        if request.is_json:
            f = request.get_json()
            if "author" in f:
                if "content" in f:
                    update_db(id, f["author"], f["content"])
                else:
                    update_db(id, f["author"], None)
            else:
                if "content" in f:
                    update_db(id, None, f["content"])
                else:
                    update_db(id, None, None)
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
    if find_id(int(id)):
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
