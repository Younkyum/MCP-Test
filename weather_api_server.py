import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv() #.env 파일에서 환경 변수 로드

app = Flask(__name__)

# 실제 날씨 API 키와 엔드포인트 URL을 환경 변수에서 가져옵니다.
# 예시: OpenWeatherMap 사용 시
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/get_weather', methods=['POST'])
def get_weather():
    """
    주어진 위치의 현재 날씨 정보를 반환하는 API 엔드포인트.
    Claude의 Tool Use 기능에 의해 호출될 것을 가정합니다.
    """
    data = request.get_json()
    if not data or 'location' not in data:
        return jsonify({"error": "Location is required"}), 400
    if not WEATHER_API_KEY:
         return jsonify({"error": "Weather API key is not configured"}), 500

    location = data['location']
    params = {
        'q': location,
        'appid': WEATHER_API_KEY,
        'units': 'metric', # 섭씨 온도 사용
        'lang': 'kr'      # 한국어 설명
    }

    try:
        response = requests.get(WEATHER_API_ENDPOINT, params=params)
        response.raise_for_status() # 오류 발생 시 예외 발생
        weather_data = response.json()

        # 필요한 정보만 추출하여 반환 (예시)
        result = {
            "location": weather_data.get("name"),
            "temperature": weather_data.get("main", {}).get("temp"),
            "feels_like": weather_data.get("main", {}).get("feels_like"),
            "description": weather_data.get("weather", [{}])[0].get("description") if weather_data.get("weather") else None,
            "humidity": weather_data.get("main", {}).get("humidity"),
            "wind_speed": weather_data.get("wind", {}).get("speed")
        }
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        print(f"Error calling Weather API: {e}")
        # 실제 오류 응답 코드를 반영하는 것이 좋습니다.
        if e.response is not None:
            status_code = e.response.status_code
            if status_code == 401:
                 return jsonify({"error": "Invalid Weather API key"}), 500
            elif status_code == 404:
                 return jsonify({"error": f"Weather data not found for location: {location}"}), 404
            else:
                 return jsonify({"error": f"Weather API error: {e}"}), status_code
        else:
            return jsonify({"error": f"Failed to connect to Weather API: {e}"}), 503
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # 실제 운영 환경에서는 Gunicorn 등의 WSGI 서버 사용을 권장합니다.
    app.run(port=5001, debug=True)