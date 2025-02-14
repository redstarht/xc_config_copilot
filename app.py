from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import sqlite3
import os
# 仮想環境の指定ってどうやってやる？
# 毎回選び内押してるんだけど。。。


app = Flask(__name__,static_folder="./static")

litedb = "tests/test.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sa_test.db"
app.config["SECRET_KEY"] = os.urandom(24)

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)


# db.modelは SQLAlchemyを使用するためのクラス
class user_detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(pytz.timezone("Asia/Tokyo")),
    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)


# ログインしてるかの状態を確認するセッション
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def con_db():
    return sqlite3.connect(litedb)


def save_recode_to_db(records):
    conn = con_db()
    cursor = conn.cursor()
    # 空欄データの削除
    # リスト内包表記　https://chatgpt.com/share/6790e8f6-0468-8011-9e00-be5c9a91fbb7
    # filtered_records = [record for record in records if any(field.strip() for field in record)]
    filtered_records = []
    for record in records:
        for field in record:
            if str(field).strip():
                filtered_records.append(record)
                break

    # 必要に応じて既存データを削除する
    cursor.execute("DELETE From test_tb")
    # 新しいデータを挿入
    cursor.executemany(
        "INSERT INTO test_tb (id,name,official) VALUES(?,?,?)", filtered_records
    )

    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(
            username=username,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
        )

        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ハッシュ化されたパスワードがuser変数 (user.password) に入っている
        user = User.query.filter_by(username=username).first()
        print(user.password)
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
# @login_required ➡ログインしてないとaccess出来ない制限を付けれる
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/load_db")
def load_db():
    try:
        conn = con_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * from test_tb")
        data = cursor.fetchall()
        print(data)
        return jsonify(data)

    except Exception as e:
        print(e)


@app.route("/load_user", methods=["GET", "POST"])
def load_user():
    if request.method == "GET":
        users = user_detail.query.all()
        return render_template("load_user.html", users=users)


@app.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    # idをキーに レコードを取得,インスタンス化
    user_id = user_detail.query.get(id)
    if request.method == "GET":
        return render_template("update.html", user_id=user_id)
    else:
        user_id.username = request.form.get("username")
        user_id.password = request.form.get("password")
        db.session.commit()


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        post = user_detail(username=username, password=password)

        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("create.html")


@app.route("/delete", methods=["GET"])
@login_required
def delete():
    user_id = user_detail.query.get(id)
    db.session.delete(user_id)
    db.session.commit()
    return redirect("/")


@app.route("/save_data", methods=["POST"])
def save_data():
    data = request.get_json()
    # dict型のメソッド .get 第2引数はデフォルト値,JS側で recordsプロパティにデータ格納されてる
    records = data.get("records", [])

    # application/jsonとは　：　JSONフォーマットでデータが送信される
    if not records:
        return jsonify({"status": "error", "message": "No Records provided"}), 400

    try:
        save_recode_to_db(records)
        return jsonify({"status": "success", "message": "Records saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
