from flask import Blueprint, redirect, render_template, request, url_for
from ..representations.post import CreatePostRequest
from ..representations.location import Location
from .auth import verify_auth, generate_id
from .pagination import pagination, more_pages


def construct_post_blueprint(firebase_storage, user_client, post_client):
    post_crud = Blueprint('post', __name__)

    @post_crud.route('/<id>')
    def view(id):
        # check user login
        (claims, error_message) = verify_auth(request.cookies.get('token'))
        if claims is None or error_message is not None:
            return redirect(url_for('auth.login'))
        user = user_client.get_by_email_id(claims['email'])
        post = post_client.get_by_id(id)
        if post.image_id not in ["image123", "hardcode"]:
            image_link = firebase_storage.child(post.image_id).get_url(None)
            post.image_id = image_link
        return render_template('post.html', post=post, user=user)

    @post_crud.route('/tag/<tag>')
    def view_posts(tag):
        # check user login
        (claims, error_message) = verify_auth(request.cookies.get('token'))
        if claims is None or error_message is not None:
            return redirect(url_for('auth.login'))
        user = user_client.get_by_email_id(claims['email'])
        page, offset, limit = pagination(request)
        posts = post_client.get_batch({'tag': tag}, offset, limit+1)
        more = more_pages(limit, len(posts))
        return render_template('myposts.html', posts=posts, user=user, page=page, more=more)

    @post_crud.route('/tag', methods=['POST'])
    def view_posts_with_tag():
        # check user login
        (claims, error_message) = verify_auth(request.cookies.get('token'))
        if claims is None or error_message is not None:
            return redirect(url_for('auth.login'))
        user = user_client.get_by_email_id(claims['email'])

        data = request.form.to_dict(flat=True)
        tag = data['searchtext']
        page, offset, limit = pagination(request)
        posts = post_client.get_batch({'tag': tag}, offset, limit+1)
        more = more_pages(limit, len(posts))
        return render_template('myposts.html', posts=posts, user=user, page=page, more=more)

    @post_crud.route('/create', methods=['POST'])
    def create():
        # check user login
        (claims, error_message) = verify_auth(request.cookies.get('token'))
        if claims is None or error_message is not None:
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            image = request.files['image']
            image_id = "images/{}".format(generate_id())
            firebase_storage.child(image_id).put(image)
            data = request.form.to_dict(flat=True)
            tags = [x.strip() for x in data['tags'].split(',')]
            post_request = CreatePostRequest(title=data['title'],
                                             description=data['description'],
                                             image_id=image_id,
                                             user_id=data['user_id'],
                                             park_id=data['park_id'],
                                             location=Location(lat=data['lat'], lng=data['lng']),
                                             tags=tags)
            post = post_client.create(post_request)
            return redirect(url_for('park.view_posts', id=str(post.park.id)))

    return post_crud
