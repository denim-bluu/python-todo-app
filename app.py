from flask import Flask, redirect, render_template, request, jsonify, abort, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://joonkang@localhost:5432/todoapp"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey("todolist.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Todo {self.id}: {self.description}>"


class TodoList(db.Model):
    __tablename__ = "todolist"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    todos = db.relationship("Todo", backref="list", lazy=True)


@app.route("/lists/<list_id>")
def get_list_todos(list_id):
    return render_template(
        "index.html",
        lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query.filter_by(list_id=list_id).order_by("id").all(),
    )


@app.route("/lists/<list_id>", methods=["POST"])
def create_list():
    error = False
    body = {}
    try:
        data = request.get_json()
        todo_ls = TodoList()
        name = data.get("name")
        todo_ls.name = name
        body["id"] = todo_ls.id
        body["name"] = todo_ls.name
        db.session.add(todo_ls)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            abort(400)
    if not error:
        return jsonify(body)
    else:
        return jsonify({"error": "Error occurred"})


@app.route("/lists/<list_id>/set-completed", methods=["POST"])
def set_completed_list(list_id):
    try:
        todo_ls = TodoList.query.get(list_id)
        for todo in todo_ls.todos:
            todo.completed = True
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/lists/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    try:
        todo_ls = TodoList.query.get(list_id)
        for todo in todo_ls.todos:
            db.session.delete(todo)
        db.session.delete(todo_ls)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({"success": True})


@app.route("/todos/create", methods=["POST"])
def create_task():
    error = False
    body = {}
    try:
        data = request.get_json()
        todo = Todo()
        description = data.get("description")
        list_id = data.get("list_id")
        todo.description = description
        todo.completed = False
        todo.list_id = list_id
        body["id"] = todo.id
        body["completed"] = todo.completed
        body["description"] = todo.description
        body["list_id"] = todo.list_id
        db.session.add(todo)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            abort(400)
    if not error:
        return jsonify(body)
    else:
        return jsonify({"error": "Error occurred"})


@app.route("/todos/<todo_id>/set-completed", methods=["POST"])
def set_completed_task(todo_id):
    try:
        completed = request.get_json()["completed"]
        print("completed", completed)
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/todos/<todo_id>", methods=["DELETE"])
def delete_task(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({"success": True})


@app.route("/")
def index():
    return redirect(url_for("get_list_todos", list_id=1))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
