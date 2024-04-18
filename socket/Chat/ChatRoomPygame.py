
import sys
import socket
import threading
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal, QObject

class UpdateSignal(QObject):
    signal = pyqtSignal(str)

class ChatClient(QMainWindow):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.init_ui()
        self.init_network()
        self.rude_words = self.load_rude_words('rude_words.txt')
        self.update_chat_signal = UpdateSignal()  
        self.update_chat_signal.signal.connect(self.update_chat_history)

    def init_ui(self):
        # Set up the main window
        self.setWindowTitle('Chatroom')
        self.setGeometry(100, 100, 480, 320)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        layout = QVBoxLayout(central_widget)

        # Create a text edit for displaying chat history
        self.chat_history = QTextEdit(readOnly=True)

        # Create a line edit for typing messages
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)

        # Create a send button
        send_button = QPushButton('Send', clicked=self.send_message)

        # Add widgets to the layout
        layout.addWidget(self.chat_history)
        layout.addWidget(self.message_input)
        layout.addWidget(send_button)

    def init_network(self):
        # Connect to the server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # Start the receiving thread
        self.receiving_thread = threading.Thread(target=self.receive_messages)
        self.receiving_thread.daemon = True
        self.receiving_thread.start()

    def load_rude_words(self, filepath):
        try:
            with open(filepath, 'r') as file:
                rude_words = [line.strip().lower() for line in file.readlines()]
            return rude_words
        except FileNotFoundError:
            print(f"File {filepath} not found. No rude word filtering will be applied.")
            return []

    def filter_rude_words(self, message):
        def replace(match):
            word = match.group(0)
            return '*' * len(word)

        pattern = re.compile('|'.join(re.escape(word) for word in self.rude_words), re.IGNORECASE)
        return pattern.sub(replace, message)

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                self.update_chat_signal.signal.emit(message)
            except ConnectionError:
                print("Connection lost.")
                break

    def send_message(self):
        message = self.message_input.text()
        filtered_message = self.filter_rude_words(message)
        if filtered_message:
            try:
                self.sock.send(filtered_message.encode('utf-8'))
                self.message_input.clear()
            except ConnectionError:
                print("Message failed to send.")

    def update_chat_history(self, message):
        self.chat_history.append(message)

    def closeEvent(self, event):
        self.sock.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    client = ChatClient('192.168.100.20', 5001)  # Replace with your server's IP and port
    client.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()