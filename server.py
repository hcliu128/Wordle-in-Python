import socket
import threading
import random
import signal
import sys

from utils import colors

# 一些範例單字
WORDS = ["apple", "grape", "peach", "berry", "mango", "lemon"]

# 用於伺服器運行狀態的全域變數
running = True

# 處理每個客戶端的遊戲邏輯
def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    # 隨機選擇一個單字作為目標
    target_word = random.choice(WORDS)
    print(f"[GAME START] Target word for {addr} is: {target_word}")
    
    client_socket.send("[SYS] Welcome to Wordle!\nStart guessing:\n".encode())
    
    while True:
        try:
            # 接收客戶端猜測
            guess = client_socket.recv(1024).decode().strip()
            if not guess:
                break

            if len(guess) != len(target_word):
                client_socket.send(f"[SYS] Your guess must be {len(target_word)} characters long.\n".encode())
                continue

            # 比對猜測
            response = []
            for i, char in enumerate(guess):
                if char == target_word[i]:
                    response.append(f"{colors.GREEN}{char}{colors.RESET}")  # Green: 正確字母與位置
                elif char in target_word:
                    response.append(f"{colors.YELLOW}{char}{colors.RESET}")  # Yellow: 正確字母但位置錯誤
                else:
                    response.append(f"{colors.BLACK}{char}{colors.RESET}")  # Black: 錯誤字母

            client_socket.send("".join(response).encode() + b"\n")

            # 檢查是否猜對
            if guess == target_word:
                client_socket.send("[SYS] Congratulations! You guessed the word!\n".encode())
                break
        except:
            print(f"[ERROR] Connection with {addr} lost.")
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    client_socket.close()

# 信號處理函數，處理 Ctrl+C 或 SIGINT 信號
def shutdown_server(signum, frame):
    global running
    print("\n[SERVER] Shutdown signal received. Closing server...")
    running = False

def start_server():
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen()
    print("[SERVER] Server is listening on port 12345...")
    
    # 註冊信號處理
    signal.signal(signal.SIGINT, shutdown_server)

    while running:
        try:
            # 設定 timeout 避免 accept 阻塞
            server.settimeout(1)
            client_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except socket.timeout:
            continue  # 檢查是否收到關閉信號

    server.close()
    print("[SERVER] Server has been shut down.")




if __name__ == "__main__":
    print(f'{colors.GREEN}Server is starting...{colors.RESET}')
    start_server()
