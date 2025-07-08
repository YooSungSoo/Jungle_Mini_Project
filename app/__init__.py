from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)

    # MongoDB 연결
    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = mongo_client.get_default_database()

    # 세션 키 설정
    app.secret_key = app.config['SECRET_KEY']

    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.applications import applications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(applications_bp)

    return app
