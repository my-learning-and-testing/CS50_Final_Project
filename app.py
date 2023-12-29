from datetime import datetime, date, timedelta
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology, numcheck

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")

# значения по умолчанию для отображения (сортировка и масштаб)
sort = "0-9"
size = 31


# функция данных
def data(sort, size):
    goods = db.execute("SELECT id, goodsname, enddate, lastdays1, lastdays2 FROM goods WHERE users_id = ?", session["user_id"])
    for row in goods:
        row["today_d"] = (datetime.strptime(row["enddate"], "%Y-%m-%d").date() - date.today()).days
        if row["today_d"] <= 0:
            row["n"] = 0  # количество занимаемых ячеек всего
            row["x"] = 0  # количество занимаемых ячеек действ
            row["y"] = 0  # количество занимаемых ячеек ограниченно действ
            row["z"] = 0  # количество занимаемых ячеек переоформления
        else:
            o = 0
            if size == 31 or size == 92:
                o = 1  # количество дней в ячейке
            elif size == 26 or size == 52:
                o = 7  # количество дней в ячейке
            elif size == 60:
                o = 30.4375  # количество дней в ячейке
            elif size == 40:
                o = 91.3125  # количество дней в ячейке
            row["n"] = round(row["today_d"] / o)
            row["x"] = (round((row["today_d"] - row["lastdays2"]) / o) if round((row["today_d"] - row["lastdays2"]) / o) > 0 else 0)
            row["y"] = (round(row["lastdays2"] / o) if round(row["lastdays2"] / o) <= row["n"] else row["n"])
            row["z"] = round(row["lastdays1"] / o)  # перепроверить
    if sort == "9-0":
        goods = sorted(goods, key=lambda x: x["today_d"], reverse=True)
    elif sort == "a-z":
        goods = sorted(goods, key=lambda x: x["goodsname"])
    elif sort == "z-a":
        goods = sorted(goods, key=lambda x: x["goodsname"], reverse=True)
    else:
        goods = sorted(goods, key=lambda x: x["today_d"])
    return goods


# тут делаем календарик
# в зависимости от размера определяем градацию и считаем солько ячеек получилось, за счет прибавления к текущей дате
def sced(size):
    # текущая дата
    n_date = date.today()
    xx = []
    # переменная будет указывать какую градацию отображать: гггг, гг, месяц, мес,
    lit = ""
    days = 0
    if size == 31 or size == 92:
        lit = "%B"
        days = 1
    elif size == 26 or size == 52:
        lit = "%b"
        days = 7
    elif size == 60:
        lit = "%Y"
        days = 30.4375
    elif size == 40:
        lit = "%y"
        days = 91.3125
    n_date = n_date + timedelta(days=days)
    xx = [{"grad": n_date.strftime(lit), "parts": 1}]
    for _ in range(size - 1):
        n_date = n_date + timedelta(days=days)
        if xx[-1]["grad"] == n_date.strftime(lit):
            xx[-1]["parts"] += 1
        else:
            xx.append({"grad": n_date.strftime(lit), "parts": 1})
    return xx


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# тут заглавная страница
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # тут напоминаю что будем работать с глобальными переменными, значения по умолчанию в них
    global sort
    global size
    if request.method == "POST":
        if request.form.get("sort"):
            sort = request.form.get("sort")
        if request.form.get("size"):
            size = int(request.form.get("size"))
        return render_template(
            "index.html",
            title="Board",
            goods=data(sort, size),
            size=size,
            sort=sort,
            today=date.today(),
            sced=sced(size),
        )
    else:  # if request.method == "GET"
        return render_template(
            "index.html",
            title="Board",
            goods=data(sort, size),
            size=size,
            sort=sort,
            today=date.today(),
            sced=sced(size),
        )


# тут логинимся
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("UPDATE users SET lastentry = ? WHERE id = ?;", date, session["user_id"])
        return redirect("/")
    else:  # if request.method == "GET"
        return render_template("login.html", title="Log In")


# тут разлогиниваемся
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# тут регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # очищаем сессию
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # если пустое имя то ошибка
        if not username:
            return apology("must provide username", 400)
        # если имя есть в дб то ошибка
        elif (len(db.execute("SELECT username FROM users WHERE username = ?;", username)) == 1):
            return apology("name is used", 400)
        # если пустой пароль то ошибка
        elif not password:
            return apology("must provide password", 400)
        # если пустое подтверждение то ошибка
        elif not confirmation:
            return apology("must provide confirmation password", 400)
        # если пароль не совпадает с подтверждением то ошибка
        elif password != confirmation:
            return apology("password mismatch", 400)
        # если норм
        else:
            # вносим в бд логи-хешпароля
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.execute(
                "INSERT INTO users (username, hash, firstentry, lastentry) VALUES (?, ?, ?, ?);",
                username,
                generate_password_hash(password),
                date,
                date,
            )
            # вызов из бд новых данных, проверка
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?;",
                username,
            )
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("db insert eror", 403)
            # если все норм открываем сессию под пользователем
            else:
                session["user_id"] = rows[0]["id"]
            # все поделали, уходим
            return redirect("/")
    else:  # if request.method == "GET"
        # тут у нас форма
        return render_template("register.html", title="Register")


# тут редактор
@app.route("/editor", methods=["GET", "POST"])
@login_required
def editor():
    if request.method == "POST":
        cancel = request.form.get("cancel")
        delete_id = request.form.get("delete")
        edit_id = request.form.get("edit")
        edited_id = request.form.get("id")
        # если нажимаем кнопку отмена в редакторе
        if cancel:
            return redirect("/")
        # если нажимаем кнопку удалить в редакторе
        elif delete_id:
            db.execute(
                "DELETE FROM goods WHERE users_id = ? AND id = ?",
                 session["user_id"],
                 delete_id,
            )
            return redirect("/")
        # если нажимаем кнопку редактирования на главной
        elif edit_id:
            good = db.execute(
                "SELECT id, goodsname, enddate, lastdays1, lastdays2 FROM goods WHERE users_id = ? AND id = ?",
                session["user_id"],
                edit_id,
            )
            return render_template("editor.html", title="Editor", id=edit_id, good=good[0])
        # если нажимеем кнопку сохранить запись в редакторе
        else:
            # icon = request.form.get("icon")
            goodsname = request.form.get("goodsname")
            enddate = request.form.get("enddate")
            lastdays1 = request.form.get("lastdays1")
            lastdays2 = request.form.get("lastdays2")
            # if not icon: icon = 0
            # тут проверки данных в форме (добавить проверки на ластдейс больше срока)
            if not lastdays1:
                lastdays1 = 0
            elif not numcheck(lastdays1):
                return apology("must provide numeric lastdays", 400)
            if not lastdays2:
                lastdays2 = 0
            elif not numcheck(lastdays2):
                return apology("must provide numeric lastdays", 400)
            if not goodsname:
                return apology("must provide goodsname", 400)
            elif not enddate:
                return apology("must provide enddate", 400)
            else:
                # если такой записи нет то создаем
                if db.execute(
                    "SELECT * FROM goods WHERE users_id = ? AND id = ?",
                    session["user_id"],
                    edited_id,
                ):
                    db.execute(
                        "UPDATE goods SET goodsname = ?, enddate = ?, lastdays1 = ?, lastdays2 = ? WHERE users_id = ? AND id = ?",
                        goodsname,
                        enddate,
                        lastdays1,
                        lastdays2,
                        session["user_id"],
                        edited_id,
                    )
                    return redirect("/")
                # а если есть то редактируем
                else:
                    db.execute(
                        "INSERT INTO goods (users_id, goodsname, enddate, lastdays1, lastdays2) VALUES (?, ?, ?, ?, ?);",
                        session["user_id"],
                        goodsname,
                        enddate,
                        lastdays1,
                        lastdays2,
                    )
                    return redirect("/")
    # если нажимаем кнопку добавить запись на главной
    else:  # if request.method == "GET"
        return render_template("editor.html", title="Editor")


# это для отзывов
@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "POST":
        feedback = request.form.get("feedback")
        if not feedback:
            return apology("must provide text", 400)
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO feedback (users_id, text, date) VALUES (?, ?, ?);",
            session["user_id"],
            feedback,
            date,
        )
        return redirect("/")
    else:  # if request.method == "GET"
        return render_template("feedback.html", title="Feedback")
