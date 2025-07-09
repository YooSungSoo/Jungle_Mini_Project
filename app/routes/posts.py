from flask import Blueprint, render_template, session ,request, redirect, current_app, flash
from bson.objectid import ObjectId
from datetime import datetime


posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def home():
    db = current_app.db

    selected_category = request.args.get('category')  # 예: category=헬스

    page = int(request.args.get('page', 1))
    per_page = 6
    skip = (page - 1) * per_page

    query = {}
    if selected_category:
        query['category'] = selected_category

    total_count = db.posts.count_documents(query)
    total_pages = (total_count + per_page - 1) // per_page

    posts = list(
        db.posts.find(query)
        .sort('created_at', -1)
        .skip(skip)
        .limit(per_page)
    )

    categories = ['산책', '러닝', '헬스', '농구']

    return render_template(
        'home.html',
        posts=posts,
        user_id=session.get('user_id'),
        nickname=session.get('nickname'),
        show_navbar=True,
        current_page=page,
        total_pages=total_pages,
        categories=categories,
        selected_category=selected_category
    )




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
        flash("이미 신청한 게시물입니다")
        return redirect('/')

    application = {
        'post_id': ObjectId(post_id),
        'applicant_id': ObjectId(user_id),
        'applicant_nickname': nickname,
        'applied_at': datetime.utcnow()
    }

    db.applications.insert_one(application)
    flash("지원이 완료되었습니다.")
    return redirect('/')


