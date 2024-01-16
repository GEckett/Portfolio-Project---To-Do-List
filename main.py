from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, URL
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy()
db.init_app(app)


#To Do List TABLE Configuration
class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(250), unique=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'task_name': self.task_name,
            'start_date': self.start_date,
            'due_date': self.due_date,
            'notes': self.notes,
            'completed': self.completed,
        }


class TaskForm(FlaskForm):
    task_name = StringField('Task Header', validators=[DataRequired()])
    start_date = DateField('Start',)
    due_date = DateField('Due Date')
    notes = TextAreaField('Notes on Task')
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def home():
    all_tasks = ToDoList.query.all()
    list_of_tasks = [task.to_dict() for task in all_tasks]
    form = TaskForm()
    if form.validate_on_submit():
        try:
            new_task = ToDoList(
                task_name=form.task_name.data,
                start_date=form.start_date.data,
                due_date=form.due_date.data,
                notes=form.notes.data,
                completed=False,
            )
            db.session.add(new_task)
            db.session.commit()

            flash('Task added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Exception during form processing: {e}")
            flash('An error occurred while processing the form. Please try again.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in field "{getattr(form, field).label.text}": {error}', 'error')

    return render_template("index.html", tasks=list_of_tasks, form=form)

@app.route('/delete/<int:cafe_id>', methods=['POST'])
def delete_task(id):
    if request.method == 'POST':
        try:
            task_to_delete = ToDoList.query.get(id)
            if task_to_delete:
                db.session.delete(task_to_delete)
                db.session.commit()
                flash('Cafe deleted successfully!', 'success')
            else:
                flash('Cafe not found.', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"Exception during cafe deletion: {e}")
            flash('An error occurred while deleting the cafe. Please try again.', 'error')

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
