import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
import socket
import threading

class ChatClient(QMainWindow):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)

        # GUI 설정
        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 400, 500)

        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)

        self.message_input = QLineEdit(self)
        self.message_input.returnPressed.connect(self.send_message)  # Enter 키에 send_message 연결

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_box)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 수신 스레드 시작
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_message(self):
        message = self.message_input.text()
        if message.strip():  # 빈 메시지 전송 방지
            try:
                full_message = f"You: {message}"  # 자신이 보낸 메시지 표시
                self.chat_box.append(full_message)  # 자신의 채팅창에 메시지 추가

                self.client_socket.send(message.encode('utf-8'))
                self.message_input.clear()
            except Exception as e:
                print(f"Failed to send message: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_box.append(f"ミニ: {message}")
                else:
                    # 연결이 종료된 경우
                    break
            except Exception as e:
                print(f"Failed to receive message: {e}")
                break

        self.client_socket.close()

    def closeEvent(self, event):
        self.client_socket.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient('192.168.0.240', 2222)
    client.show()
    sys.exit(app.exec_())
