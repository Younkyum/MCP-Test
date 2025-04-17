import os
from flask import Flask, jsonify # 필요한 Flask 컴포넌트 임포트
from dotenv import load_dotenv #.env 파일 로드를 위함
import requests # HTTP 요청을 보내기 위함

# 환경 변수에 접근하기 전에.env 파일 로드
load_dotenv()

# Flask 애플리케이션 초기화
app = Flask(__name__)
# 서버가 실행 중인지 확인하기 위한 간단한 루트 라우트 정의
@app.route('/')
def home():
    return jsonify({"message": "주식 정보 API 서버가 실행 중입니다!"})

# --- 주식 데이터 엔드포인트는 아래에 정의될 예정 ---
@app.route('/stock/<symbol>')
def get_stock_data(symbol): # 오류 발생 시 예외 발생
        mockData = {
            "symbol": symbol,
            "price": 100.0,
            "change": 1.0,
            "percentChange": 1.0,
            "volume": 1000
        }
        return jsonify(mockData)

# 개발 서버로 앱을 실행하기 위한 표준 파이썬 구문
if __name__ == '__main__':
    # debug=True는 코드 변경 시 자동 리로드 및 상세 오류 페이지 제공
    # 프로덕션 환경에서는 debug=True를 사용하지 마십시오!
    app.run(debug=True, port=5002) # 기본 포트는 5000