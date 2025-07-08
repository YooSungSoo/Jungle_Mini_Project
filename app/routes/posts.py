from flask import Blueprint, render_template, session ,request, redirect, current_app
from bson.objectid import ObjectId
from datetime import datetime


posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def home():
    db = current_app.db
    posts = list(db.posts.find())
    user_id = session.get('user_id')
    nickname = session.get('nickname')

    return render_template('home.html', posts=posts, user_id=user_id, nickname=nickname, show_navbar=True)


@posts_bp.route('/post/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        db = current_app.db
        post = {
            'author_id': ObjectId(session['user_id']),
            'author_nickname': session['nickname'],
            'title': request.form['title'],
            'content': request.form['content'],
            'category': request.form['category'],
            'date': request.form['date'],
            'time': request.form['time'],
            'max_people': int(request.form['max_people']),
            'current_people': 0,
            'created_at': datetime.utcnow()
        }
        db.posts.insert_one(post)
        return redirect('/')
    
    return render_template('post_create.html', show_navbar=True)


@posts_bp.route('/post/<post_id>/delete')
def delete_post(post_id):
    db = current_app.db
    post = db.posts.find_one({'_id': ObjectId(post_id)})

    if not post:
        return "해당 게시글이 존재하지 않습니다.", 404

    if str(post['author_id']) != session.get('user_id'):
        return "삭제 권한이 없습니다.", 403

    db.posts.delete_one({'_id': ObjectId(post_id)})
    return redirect('/')


@posts_bp.route('/post/<post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    db = current_app.db
    post = db.posts.find_one({'_id': ObjectId(post_id)})

    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    if str(post['author_id']) != session.get('user_id'):
        return "수정 권한이 없습니다.", 403

    if request.method == 'POST':
        db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': request.form['title'],
                'content': request.form['content'],
                'category': request.form['category'],
                'date': request.form['date'],
                'time': request.form['time'],
                'max_people': int(request.form['max_people']),
            }}
        )
        return redirect('/')

    return render_template('post_edit.html', post=post, show_navbar=True)


@posts_bp.route('/post/<post_id>/apply', methods=['POST'])
def apply_to_post(post_id):
    db = current_app.db
    user_id = session.get('user_id')
    nickname = session.get('nickname')

    if not user_id:
        return redirect('/login')

    existing = db.applications.find_one({
        'post_id': ObjectId(post_id),
        'applicant_id': ObjectId(user_id)
    })
    if existing:
        return "이미 신청한 게시물입니다.", 400

    application = {
        'post_id': ObjectId(post_id),
        'applicant_id': ObjectId(user_id),
        'applicant_nickname': nickname,
        'applied_at': datetime.utcnow()
    }

    db.applications.insert_one(application)
    return redirect('/')


