from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import os
from flask_migrate import Migrate

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Docker_debug用
print(os.path.exists(os.path.join(app.instance_path, 'database.db')))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Accounts(db.Model):
    __tablename__='accounts'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True,nullable=False)
    password_hash = db.Column(db.String(100),nullable=False)
    role = db.Column(db.Integer,default=1,nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone(timedelta(hours=9))))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(
            timezone(timedelta(hours=9))),
        onupdate=lambda: datetime.now(timezone(timedelta(hours=9)))
    )
    


class Factory(db.Model):
    __tablename__ = 'factories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    departments = db.relationship('Department', backref='factory', lazy=True)

    # Departmentテーブルのfactory列と双方向リレーション
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'departments': [dept.to_dict() for dept in self.departments],
            'sort_order': self.sort_order,
            'is_deleted': self.is_deleted

        }


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    factory_id = db.Column(db.Integer, db.ForeignKey(
        'factories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    sections = db.relationship('Section', backref='department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sections': [sec.to_dict() for sec in self.sections],
            'sort_order': self.sort_order,
            'is_deleted': self.is_deleted
        }


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    subsections = db.relationship('Subsection', backref='section', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subsections': [sub.to_dict() for sub in self.subsections],
            'sort_order': self.sort_order,
            'is_deleted': self.is_deleted
        }


class Subsection(db.Model):
    __tablename__ = 'subsections'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey(
        'sections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50),default='',nullable=False)
    # 順番を管理するカラム（デフォルト値なし、NULL許容）
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    # 廃盤flag （0: 現役, 1: 廃止）
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    # 作成ユーザーID（NULL許容）
    created_by = db.Column(db.Integer, nullable=True)
    # 更新ユーザーID（NULL許容）
    updated_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone(timedelta(hours=9))))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(
            timezone(timedelta(hours=9))),
        onupdate=lambda: datetime.now(timezone(timedelta(hours=9)))
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code':self.code,
            'sort_order': self.sort_order,
            'is_deleted': self.is_deleted,
            'created_by': self.created_by,
            'updated_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Production_line(db.Model):
    __tablename__='production_lines'
    id=db.Column(db.Integer, primary_key=True)
    subsection_id = db.Column(db.Integer, db.ForeignKey(
        'subsections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50),default='',nullable=False)
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone(timedelta(hours=9))))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(
            timezone(timedelta(hours=9))),
        onupdate=lambda: datetime.now(timezone(timedelta(hours=9)))
    )

class Employees(db.Model):
    __tablename__='employees'
    id=db.Column(db.Integer,primary_key=True)
    subsection_id = db.Column(db.Integer, db.ForeignKey(
        'subsections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50),default='',nullable=False)
    sort_order = db.Column(db.Integer, default=500, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone(timedelta(hours=9))))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(
            timezone(timedelta(hours=9))),
        onupdate=lambda: datetime.now(timezone(timedelta(hours=9)))
    )
    


@app.route('/api/tree', methods=['GET'])
def get_tree():
    factories = Factory.query.all()
    # 返り値テスト
    # confirm_json = []
    # for factory in factories:
    #     confirm_json.append(factory.to_dict())
    # pprint.pprint(confirm_json)

    return jsonify([factory.to_dict() for factory in factories])


@app.route('/api/subsections/<int:section_id>', methods=['GET', 'POST'])
def manage_subsection(section_id):
    if request.method == 'GET':
        print(f"section_id={section_id}")
        # 指定されたsection_idに紐づいた子係(subsections)を取得
        subsections = Subsection.query.filter_by(section_id=section_id).all()

        if not subsections:
            print("データが見つかりませんでした[]を返します")
            return jsonify([])

        response = jsonify([sub.to_dict() for sub in subsections])
        print(f"レスポンスデータ:{response.get_json}")
        return response

    # 更新・保存機能
    elif request.method == 'POST':
        data = request.json

        if not data:
            print("エラーです、リクエストデータがNone")
            return jsonify({"error": "リクエストボディが空です"}, 400)

        exsiting_subsections = Subsection.query.filter_by(
            section_id=section_id).all()

        # 既存データを更新 or 削除
        for i, sub in enumerate(exsiting_subsections):
            if i < len(data):
                # キーエラー防止
                sub.name = data[i].get('name', sub.name)
            else:
                # 余分なデータは削除
                db.session.delete(sub)

        # 新しいデータを追加
        for i in range(len(exsiting_subsections), len(data)):
            # section_id =flaskルーティング
            new_sub = Subsection(section_id=section_id, name=data[i]['name'])
            db.session.add(new_sub)

        db.session.commit()
        print(
            f"更新後のsubsections:{[sub.to_dict() for sub in Subsection.query.filter_by(section_id=section_id).all()]}")
        return jsonify({"message": "subsections updated successfully"})


@app.route('/')
def index():
    '''
    HOMEは見る専の画面
    工場➡係➡選択肢で 人員 / 異常内容 までツリービューで選択
    人員 or 異常内容を選択したら、選択した内容を画面に表示する

    '''
    # print(f'{factories.name} {factories.code}')
    # factoryclass = repr(factories)
    # print(factoryclass)
    # リスト内包表記　factories_dict = [factory.to_dict() for factory in factories]　

    factories = Factory.query.all()
    factories_dict = [factory.to_dict() for factory in factories]  # JSON変換用
    return render_template('index.html', factories=factories_dict)


@app.route('/edit_subsection')
def edit_unit():
    return render_template('edit_subsection.html')


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


if __name__ == '__main__':
    app.run(debug=True)
