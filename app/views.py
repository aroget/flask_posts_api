import datetime

from app import app, db
from flask import jsonify, request, g
from app.utils.media import upload_media
from app.utils.auth import create_token
from sqlalchemy.exc import IntegrityError
from app.decorators import login_required
from werkzeug.exceptions import BadRequest, Forbidden
from app.models import Account, User, Post, Role, Tag, Token, Image, Privilege


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
@login_required
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

    privilege = Privilege.query.filter_by(level=1)

    admin_role = Role(name='Admin', account_id=account.id,
                      privilege_id=privilege.id)

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
    if request.method == 'PUT':
        user = User.query.get(g.user_id)

        first_name = user.first_name
        last_name = user.last_name
        avatar = user.avatar

        if 'first_name' in request.json:
            first_name = request.json['first_name']

        if 'last_name' in request.json:
            last_name = request.json['last_name']

        if 'avatar' in request.json:
            avatar = request.json['avatar']

        user.first_name = first_name
        user.last_name = last_name
        user.avatar = avatar

        db.session.commit()

        return jsonify({'response': user.serialize})

    user_id = g.user_id
    user = User.query.get(user_id)
    return jsonify(user.serialize)


@app.route('/user/<int:user_id>/posts', methods=['GET'])
@login_required
def posts_by_user(user_id):
    posts = Post.query.filter_by(author=user_id)
    return jsonify({'response': [post.serialize for post in posts]})


@app.route('/roles', methods=['GET', 'POST'])
@login_required
def roles():
    if request.method == 'POST':
        try:
            name = request.json['name']
            privilege_id = request.json['privilege_id']
        except KeyError as missing_key:
            raise BadRequest('%s is required' % missing_key)
        user = User.query.get(g.user_id)


        role = Role(name=name, privilege_id=privilege_id, account_id=user.account_id)

        db.session.add(role)
        db.session.commit()

        return jsonify({'response': role.serialize})
    user = User.query.get(g.user_id)
    roles = Role.query.filter_by(account_id=user.account_id)
    return jsonify({'response': [role.serialize for role in roles]})


@app.route('/role/<int:role_id>', methods=['GET', 'PUT'])
@login_required
def role_details(role_id):
    user = User.query.get(g.user_id)
    role = Role.query.get_or_404(role_id)

    if role.account_id is not user.account_id:
        raise Forbidden()

    if request.method == 'PUT':
        name = role.name
        privilege_id = role.privilege_id

        if 'name' in request.json:
            name = request.json['name']

        if 'privilege_id' in request.json:
            privilege_id = request.json['privilege_id']

        role.name = name
        role.privilege_id = privilege_id

        db.session.commit()

        return jsonify({'response': role.serialize})

    return jsonify({'response': role.serialize})


@app.route('/tags', methods=['GET', 'POST'])
@login_required
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
@login_required
def tag_details(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if request.method == 'PUT':
        if 'name' not in request.json:
            raise BadRequest()

        tag.name = request.json['name']

        db.session.commit()

        return jsonify({'response': tag.serialize})

    return jsonify({'response': tag.serialize})


@app.route('/tag/<int:tag_id>/posts', methods=['GET'])
@login_required
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
        post_tags = []
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
            print(request.json['tags'])
            post_tags = [Tag.query.get_or_404(tag_id) for tag_id in request.json['tags']]
            print(post_tags)

        if 'hero_image' in request.json:
            hero_image = hero_image

        if 'is_published' in request.json:
            is_published = True
            published_date = datetime.datetime.utcnow()


        post = Post(title=title, body=body)

        post.tags = post_tags
        post.author = g.user_id
        post.hero_image = hero_image
        post.is_archived = is_archived
        post.is_published = is_published
        post.published_date = published_date

        print(post.tags)

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
@login_required
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
            published_date = datetime.datetime.utcnow()

        if 'tags' in request.json:
            post.tags = tags

        if 'hero_image' in request.json:
            post.hero_image = hero_image

        if 'is_archived' in request.json:
            post.is_archived = is_archived

        if 'is_published' in request.json:
            post.is_published = is_published

        if post.is_published:
            post.published_date = datetime.datetime.utcnow()

        db.session.commit()
        return jsonify({'response': post.serialize}), 202

    return jsonify({'response': post.serialize})


@app.route('/post/<int:post_id>/delete', methods=['DELETE'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return jsonify(), 204


@app.route('/media', methods=['GET', 'POST'])
@login_required
def media():
    if request.method == 'POST':
        user_id = g.user_id
        user = User.query.get(user_id)

        response = upload_media(request.files['file'])
        image = Image(url=response, account_id=user.account_id)

        db.session.add(image)
        db.session.commit()

        return jsonify({'response': response})

    user_id = g.user_id
    user = User.query.get(user_id)

    images = Image.query.filter_by(account_id=user.account_id)

    return jsonify({'response': [image.serialize for image in images]})



