from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    media = db.relationship('Image', backref='account', lazy='dynamic')
    owner = db.relationship('User', backref='account', lazy='dynamic')
    role = db.relationship('Role', backref='account', lazy='dynamic')

    def __repr__(self):
        return '<Account %r>' % self.id

    @property
    def serialize(self):
        return {
            'id': self.id
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    user_name = db.Column(db.String(200), unique=True)
    avatar = db.Column(db.String(200), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    password_hash = db.Column(db.String(128))
    token = db.relationship('Token', uselist=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    post = db.relationship('Post', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User %r>' % self.user_name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'user_name': self.user_name,
            'avatar': self.avatar,
            'account_id': self.account_id,
            'role_id': self.role_id
        }


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    is_archived = db.Column(db.Boolean)
    is_published = db.Column(db.Boolean)
    published_date = db.Column(db.DateTime, nullable=True)
    hero_image = db.Column(db.String(200), nullable=True)
    tags = db.relationship('Tag',
                           secondary='tags_posts',
                           backref=db.backref('posts', lazy='dynamic'))


    def __repr__(self):
        return '<Post %r>' % self.title

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'is_archived': self.is_archived,
            'is_published': self.is_published,
            'published_date': self.published_date,
            'body': self.body,
            'hero_image': self.hero_image,
            'tags': self.tags
        }


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)


    def __repr__(self):
        return '<Tag %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


tags_posts = db.Table('tags_posts',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'account_id': self.account_id
        }

class Privilege(db.Model):
    __tablename__= 'privileges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    level = db.Column(db.Integer)
    role = db.relationship('Role', uselist=False)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level
        }



class Role(db.Model):
    __tablename__= 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    privilege_id = db.Column(db.Integer, db.ForeignKey('privileges.id'))
    user = db.relationship('User', backref='role', lazy='dynamic')
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))


    def __repr__(self):
        return '<Role %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_id': self.account_id
        }


class Token(db.Model):
    __tablename__ = 'tokens'
    token_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(400), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))