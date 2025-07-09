from flask import Blueprint, render_template, request, redirect, session, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = current_app.db
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']

        existing_nickname = db.users.find_one({'nickname': nickname})
        if existing_nickname:
            flash("이미 존재하는 닉네임입니다.")
            return redirect('/login')

        existing_user = db.users.find_one({'email': email})
        if existing_user:
            flash("이미 존재하는 이메일입니다.")
            return redirect('/login')

        hashed_pw = generate_password_hash(password) 
        db.users.insert_one({
            'email': email,
            'nickname': nickname,
            'password': hashed_pw
        })
        return redirect('/login')

    return render_template('signup.html', show_navbar=False)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = current_app.db
        email = request.form['email']
        password = request.form['password']

        user = db.users.find_one({'email': email})
        if not user:
            flash("이메일이 존재하지 않습니다.")
            return redirect('/login')

        if not check_password_hash(user['password'], password):
            flash("비밀번호가 일치하지 않습니다.")
            return redirect('/login')

        session['user_id'] = str(user['_id'])
        session['nickname'] = user['nickname']
        return redirect('/')

    return render_template('login.html', show_navbar=False)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
