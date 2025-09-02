#!/usr/bin/env python3
"""
나라장터 입찰공고 검색 웹 애플리케이션 실행 스크립트
"""

import os
import sys
import subprocess

def check_dependencies():
    """필요한 의존성 확인"""
    try:
        import flask
        import flask_cors
        import pandas
        import openpyxl
        return True
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("\n다음 명령어로 의존성을 설치해주세요:")
        print("pip install -r requirements.txt")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 나라장터 입찰공고 검색 웹 애플리케이션")
    print("=" * 60)
    
    # 의존성 확인
    if not check_dependencies():
        return
    
    # 웹 디렉토리로 이동
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    if not os.path.exists(web_dir):
        print("❌ web 디렉토리를 찾을 수 없습니다.")
        return
    
    os.chdir(web_dir)
    
    print("\n✅ 의존성 확인 완료")
    print("🌐 웹 서버를 시작합니다...")
    print("\n접속 주소: http://localhost:5000")
    print("종료하려면 Ctrl+C를 누르세요.\n")
    
    try:
        # Flask 애플리케이션 실행
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 웹 서버가 종료되었습니다.")

if __name__ == "__main__":
    main()