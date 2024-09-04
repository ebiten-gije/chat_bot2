import socket
import threading
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# 서버 IP와 포트 설정
HOST = '192.168.0.240'
PORT = 2222

# 환경 변수에서 Google API 키 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Google Generative AI API 설정
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# 초기 프롬프트 설정
initial_prompt = """
あなたは現役女子高生の'ミニ'という名前の少女である。元気でかわいい性格で、最もリアルな女子高生として振る舞う。
友達のように話し、その関係性に適切な口調をしてほしい。
できるだけ会話は日本語で行う。だが、もし韓国語で話かけられたら韓国語を勉強してる日本の学生のように反応してほしい。
入力されたプロンプトの言語によって返してほしい。
以上のキャラクターを演じながら自分がAIであることを連想させる表現はしてはいけない。
"""


def handle_client(client_socket):
    # 챗봇 세션 시작
    client_chat = model.start_chat(history=[{"role": "user", "parts": [{"text": initial_prompt}]}])
    while True:
        # 클라이언트로부터 메시지 수신
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        # 챗봇 API에 메시지 전달 및 응답 수신
        response = get_chatbot_response(message, client_chat)

        # 클라이언트에게 응답 전송
        client_socket.send(response.encode('utf-8'))


def get_chatbot_response(message, client_chat):
    try:
        # 챗봇에 메시지 전송 및 응답 받기
        response = client_chat.send_message(message)

        # 응답에서 텍스트 추출
        bot_response = response.text  # 또는 response.candidates[0].text
        return bot_response

    except AttributeError as e:
        # AttributeError는 응답 객체에 필요한 속성이 없을 때 발생할 수 있음
        logging.error(f'AttributeError: {e}')
        return '응답 처리 중 오류가 발생했습니다.'
    except Exception as e:
        # 그 외의 모든 예외 처리
        logging.error(f'Unexpected error: {e}')
        return '예상치 못한 오류가 발생했습니다.'


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
