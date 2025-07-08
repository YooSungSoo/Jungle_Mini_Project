from flask import Blueprint, render_template, session, current_app, redirect
from bson.objectid import ObjectId

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/applications/sent')
def apply_sent():
    db = current_app.db
    user_id = session.get('user_id')
    if not user_id:
        return "로그인이 필요합니다.", 401

    applications = list(db.applications.find({'applicant_id': ObjectId(user_id)}))  # ✅ 수정된 코드


    post_ids = [app['post_id'] for app in applications]
    posts = db.posts.find({'_id': {'$in': post_ids}})
    post_map = {post['_id']: post for post in posts}

    enriched_apps = []
    for app in applications:
        post = post_map.get(app['post_id'])
        if post:
            enriched_apps.append({
                'post': post,
                'status': app.get('status', '대기 중'),
                'applied_at': app.get('applied_at')
            })

    return render_template('apply_sent.html', applications=enriched_apps, show_navbar=True)

@applications_bp.route('/applications/received')
def apply_received():
    db = current_app.db
    user_id = session.get('user_id')
    if not user_id:
        return "로그인이 필요합니다.", 401

    posts = list(db.posts.find({'author_id': ObjectId(user_id)}))
    post_ids = [post['_id'] for post in posts]

    applications = list(db.applications.find({'post_id': {'$in': post_ids}}))

    post_map = {post['_id']: post for post in posts}

    enriched = []
    for app in applications:
        post = post_map.get(app['post_id'])
        if post:
            enriched.append({
                'application_id': str(app['_id']),
                'post_title': post['title'],
                'applicant_nickname': app['applicant_nickname'],
                'applied_at': app.get('applied_at'),
                'status': app.get('status', '대기 중')
            })

    return render_template('apply_received.html', applications=enriched, show_navbar=True)

@applications_bp.route('/applications/<application_id>/accept', methods=['POST'])
def accept_application(application_id):
    db = current_app.db

    db.applications.update_one(
        {'_id': ObjectId(application_id)},
        {'$set': {'status': '수락됨'}}
    )

    application = db.applications.find_one({'_id': ObjectId(application_id)})
    if application:
        post_id = application['post_id']
        db.posts.update_one(
            {'_id': post_id},
            {'$inc': {'current_people': 1}}
        )

    return redirect('/applications/received')

@applications_bp.route('/applications/<application_id>/reject', methods=['POST'])
def reject_application(application_id):
    db = current_app.db
    db.applications.update_one(
        {'_id': ObjectId(application_id)},
        {'$set': {'status': '거절됨'}}
    )
    return redirect('/applications/received')
