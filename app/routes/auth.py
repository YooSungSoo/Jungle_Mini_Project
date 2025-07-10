from flask import Blueprint, render_template, request, redirect, current_app, flash, make_response, request
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import jwt
import datetime
from utils import decode_token_from_request


auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'junglegym'

def create_token(user):
    payload = {
        'user_id': str(user['_id']),
        'nickname': user['nickname'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = current_app.db
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']

        if db.users.find_one({'nickname': nickname}):
            flash("이미 존재하는 닉네임입니다.")
            return redirect('/login')

        if db.users.find_one({'email': email}):
            flash("이미 존재하는 이메일입니다.")
            return redirect('/login')

        hashed_pw = generate_password_hash(password)
        db.users.insert_one({
            'email': email,
            'nickname': nickname,
            'password': hashed_pw
        })

        flash("회원가입이 완료되었습니다.")
        return redirect('/login')  # ✅ 여기 중요!

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

        token = create_token(user)

        resp = make_response(redirect('/'))  # ✅ 여기서만 redirect
        resp.set_cookie('token', token, httponly=True, samesite='Lax')
        return resp

    return render_template('login.html', show_navbar=False)


@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('token')
    return resp
