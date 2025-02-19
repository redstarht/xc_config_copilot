from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Factory(db.Model):
    __tablename__ = 'factories'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    departments = db.relationship('Department', backref='factory', lazy=True)
    # Departmentテーブルのfactory列と双方向リレーション
    # def __repr__(self):
    #     return f'<Factory id={self.id} code={self.code} name={self.name}>'

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    factory_id = db.Column(db.Integer, db.ForeignKey(
        'factories.id'), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    mgmt_code = db.Column(db.String(10))
    name = db.Column(db.String(100), nullable=False)
    sections = db.relationship('Section', backref='department', lazy=True)


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subsections = db.relationship('Subsection', backref='section', lazy=True)


class Subsection(db.Model):
    __tablename__ = 'subsections'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey(
        'sections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    factories = Factory.query.all()
    print(f'{factories.name} {factories.code}')
    factoryclass = repr(factories)
    print(factoryclass)
    # factories_json = [factory.to_dict for factory in factories]
    return render_template('index.html', factories=factories)


@app.route('/departments/<int:factory_id>')
def departments(factory_id):
    departments = Department.query.filter_by(factory_id=factory_id).all()
    return render_template('departments.html', departments=departments)


@app.route('/sections/<int:department_id>')
def sections(department_id):
    sections = Section.query.filter_by(department_id=department_id).all()
    return render_template('sections.html', sections=sections)


@app.route('/subsections/<int:section_id>')
def subsections(section_id):
    subsections = Subsection.query.filter_by(section_id=section_id).all()
    return render_template('subsections.html', subsections=subsections)


@app.route('/add_subsection/<int:section_id>', methods=['GET', 'POST'])
def add_subsection(section_id):
    if request.method == 'POST':
        name = request.form['name']
        new_subsection = Subsection(section_id=section_id, name=name)
        db.session.add(new_subsection)
        db.session.commit()
        return redirect(url_for('subsections', section_id=section_id))
    return render_template('add_subsection.html', section_id=section_id)


@app.route('/edit_subsection/<int:subsection_id>', methods=['GET', 'POST'])
def edit_subsection(subsection_id):
    subsection = Subsection.query.get_or_404(subsection_id)
    if request.method == 'POST':
        subsection.name = request.form['name']
        db.session.commit()
        return redirect(url_for('subsections', section_id=subsection.section_id))
    return render_template('edit_subsection.html', subsection=subsection)
