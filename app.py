from flask import Flask, render_template, request, redirect, url_for, jsonify
# from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/todoapp'

# db = SQLAlchemy(app, session_options={"expire_on_commit": False})
db = SQLAlchemy(app)


migrate = Migrate(app, db)
db.create_all()


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


# db.create_all()
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })



@app.route('/todos/<todo_id>/get-checked', methods=['POST'])
def check_completed(todo_id):
    try:
        checked = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = checked
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/create', methods=['POST'])
def create_todo():
    # description = request.form.get('description', '')
    # todo = Todo(description=description)
    # db.session.add(todo)
    # db.session.commit()
    # return redirect(url_for('index'))
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)



@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())
