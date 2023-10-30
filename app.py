from flask import Flask, redirect, render_template, request, jsonify, abort, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://joonkang@localhost:5432/todoapp"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<Todo {self.id}: {self.description}>"


@app.route("/")
def index():
    return render_template("index.html", todos=Todo.query.order_by("id").all())


@app.route("/todos/create", methods=["POST"])
def create():
    error = False
    body = {}
    try:
        data = request.get_json()
        todo = Todo()
        description = data.get("description")
        todo.description = description
        todo.completed = False
        body["description"] = todo.description
        body["completed"] = todo.completed
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
def set_completed_todo(todo_id):
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
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
