from app import create_app

print("🚀 서버 실행 준비 중...")

app = create_app()

print("✅ 서버 시작!")

if __name__ == '__main__':
    app.run(debug=True)
