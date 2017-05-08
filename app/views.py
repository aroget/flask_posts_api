import datetime

from app import app, db
from flask import jsonify, request, g
from app.utils.auth import create_token
from sqlalchemy.exc import IntegrityError
from app.decorators import login_required
from werkzeug.exceptions import BadRequest
from app.models import Account, User, Post, Role, Tag, Token

POST_TYPES = (
    1, 'ALL', # all posts
    2, 'PUBLISHED', # all published posts
    3, 'DRAFTS', # all drafts posts
    4, 'ARCHIVED', # all archived posts
)

@app.route('/')
@login_required
def hello_world():
    return 'Hello, World!'


@app.route('/login', methods=['POST'])
def login():
    if 'username' not in request.json or 'password' not in request.json:
        return jsonify('Both fields are required'), 400

    user_name = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(user_name=user_name).first()

    if user is None or user.check_password(password) is False:
        return jsonify('No account found with those credentials'), 400

    if user.token is not None:
        token = Token.query.filter_by(user_id=user.id).first()
        token.token = create_token(user)

        db.session.commit()

        return jsonify({'token': token.token})

    token = Token(user_id=user.id)
    token.token = create_token(user)

    db.session.add(token)
    db.session.commit()

    return jsonify({'token': token.token})


@app.route('/register', methods=['POST'])
def register():
    try:
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        email = request.json['email']
        user_name = request.json['user_name']
        password = request.json['password']
    except KeyError as missing_key:
        raise BadRequest('%s is required' % missing_key)

    user = User(first_name=first_name,
                last_name=last_name,
                email=email,
                user_name=user_name)

    account = Account()

    db.session.add(account)
    db.session.commit()

    admin_role = Role(name='Admin', account_id=account.id)

    db.session.add(admin_role)

    try:
        db.session.commit()
    except IntegrityError:
        raise BadRequest('Duplicate Entry')



    user.account_id = account.id
    user.role_id = admin_role.id
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize), 201


@app.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    user_id = g.user_id
    user = User.query.get(user_id)
    return jsonify(user.serialize)


@app.route('/user/<int:user_id>/posts', methods=['GET'])
def posts_by_user(user_id):
    posts = Post.query.filter_by(author=user_id)
    return jsonify({'response': [post.serialize for post in posts]})


@app.route('/roles', methods=['GET', 'POST'])
def roles():
    if request.method == 'POST':
        return jsonify({'POST'})

    roles = Role.query.all()
    return jsonify({'response': [role.serialize for role in roles]})


@app.route('/role/<int:role_id>', methods=['GET', 'PUT'])
def role_details(role_id):
    role = Role.query.get_or_404(role_id)

    if request.method == 'PUT':
        return jsonify({'PUT'})

    return jsonify({'response': role.serialize})


@app.route('/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'POST':
        if 'name' not in request.json:
            raise BadRequest('Name is required')

        tag = Tag(name=request.json['name'])

        db.session.add(tag)
        db.session.commit()

        return jsonify({'response': tag.serialize})

    return jsonify({'response': [tag.serialize for tag in Tag.query.all()]})


@app.route('/tag/<int:tag_id>', methods=['GET', 'PUT'])
def tag_details(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    return jsonify({'response': tag.serialize})


@app.route('/tag/<int:tag_id>/posts', methods=['GET'])
def posts_by_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    return jsonify({'response': [post.serialize for post in tag.posts]})


@app.route('/tag/<int:tag_id>/delete', methods=['DELETE'])
def tag_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return jsonify(), 204


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    if request.method == 'POST':
        tags = []
        hero_image = None
        is_archived = False
        is_published = False
        published_date = None

        try:
            title = request.json['title']
            body = request.json['body']
        except KeyError as missing_key:
            raise BadRequest('%s is required' % missing_key)


        if 'tags' in request.json:
            post_tags = [Tag.query.get_or_404(tag_id) for tag_id in request.json['tags']]

        if 'hero_image' in request.json:
            hero_image = hero_image

        if 'is_published' in request.json:
            is_published = True
            published_date = datetime.datetime.now()


        post = Post(title=title, body=body)

        post.tags = tags
        post.author = g.user_id
        post.hero_image = hero_image
        post.is_archived = is_archived
        post.is_published = is_published
        post.published_date = published_date

        db.session.add(post)
        db.session.commit()

        return jsonify({'response': post.serialize})

    is_archived = 0
    is_published = 1
    is_archived = request.args.get('is_archived')
    is_published = request.args.get('is_published')


    return jsonify({'response': [post.serialize for post in \
        Post.query.filter_by(is_published=is_published,is_archived=is_archived)]})


@app.route('/post/<int:post_id>', methods=['GET', 'PUT'])
def post_details(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'PUT':
        if 'title' not in request.json or 'body' not in request.json:
            raise BadRequest('Title and/or Body missing')

        post.title = request.json['title']
        post.body = request.json['body']

        if 'tags' in request.json:
            post_tags = [Tag.query.get_or_404(tag_id) for tag_id in request.json['tags']]

        if 'hero_image' in request.json:
            hero_image = hero_image

        if 'is_published' in request.json:
            is_published = True
            published_date = datetime.datetime.now()

        if 'tags' in request.json:
            post.tags = tags

        if 'hero_image' in request.json:
            post.hero_image = hero_image

        if 'is_archived' in request.json:
            post.is_archived = is_archived

        if 'is_published' in request.json:
            post.is_published = is_published

        if post.is_published:
            post.published_date = datetime.datetime.now()

        db.session.commit()
        return jsonify({'response': post.serialize}), 202

    return jsonify({'response': post.serialize})


@app.route('/post/<int:post_id>/delete', methods=['DELETE'])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return jsonify(), 204
