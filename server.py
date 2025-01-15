import socket
import threading
import random
import signal
import time

# 一些範例單字
WORDS = []

# 用於伺服器運行狀態的全域變數
running = True
clients = {}  # {client_socket: username}

# 廣播訊息給所有客戶端
def broadcast_message(message, exclude_socket=None):
    for client_socket in clients:
        if client_socket != exclude_socket:
            try:
                client_socket.send(message.encode())
            except:
                client_socket.close()
                del clients[client_socket]

# 更新並廣播在線人數
def update_online_count():
    message = f"[SYS] Online: {len(clients)}"
    broadcast_message(message)
    time.sleep(0.5)

# 處理每個客戶端的遊戲邏輯
def handle_client(client_socket, addr):
    global clients
    try:
        # 接收用戶名稱
        username = client_socket.recv(1024).decode().strip()
        clients[client_socket] = username
        print(f"[NEW CONNECTION] {username} ({addr}) connected.")
        update_online_count()
        
        # 遊戲邏輯
        target_word = random.choice(WORDS)
        print("Answer: " + target_word)
        client_socket.send("[SYS] Welcome to Wordle!\nStart guessing:\n".encode())
        while True:
            guess = client_socket.recv(1024).decode().strip()
            if not guess:
                break
            if guess == "[GameOver]":
                client_socket.send(f"[SYS] Game over! The correct word was: {target_word}\n".encode())
                break
            if len(guess) != len(target_word):
                client_socket.send(f"[SYS] Your guess must be {len(target_word)} characters long.\n".encode())
                continue
            if not guess.isalpha():
                client_socket.send("[SYS] Your guess must contain only alphabetic characters.\n".encode())
                continue
            if guess not in WORDS:
                client_socket.send("[SYS] Your guess is not a valid English word.\n".encode())
                continue
            response = []
            for i, char in enumerate(guess):
                if char == target_word[i]:
                    response.append(f"<GREEN>{char}<RESET>")  # Green: 正確字母與位置
                elif char in target_word:
                    response.append(f"<YELLOW>{char}<RESET>")  # Yellow: 正確字母但位置錯誤
                else:
                    response.append(f"<BLACK>{char}<RESET>")  # Black: 錯誤字母

            client_socket.send("".join(response).encode() + b"\n")
            time.sleep(0.5)
            if guess == target_word:
                client_socket.send("[SYS] Congratulations! You guessed the word!\n".encode())
                broadcast_message(f"[SYS] {username} guessed the answer!", exclude_socket=client_socket)
                break
    except:
        print(f"[ERROR] Connection with {addr} lost.")
    finally:
        del clients[client_socket]
        client_socket.close()
        update_online_count()
        print(f"[DISCONNECT] {addr} disconnected.")

def start_server():
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen()
    with open("./utils/dictionary.txt", "r") as f:
        global WORDS
        WORDS = f.read().splitlines()
    print("[SERVER] Server is listening on port 12345...")

    signal.signal(signal.SIGINT, shutdown_server)
    while running:
        try:
            server.settimeout(1)
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()
        except socket.timeout:
            continue
    server.close()
    print("[SERVER] Server has been shut down.")

def shutdown_server(signum, frame):
    global running
    print("\n[SERVER] Shutdown signal received. Closing server...")
    running = False

if __name__ == "__main__":
    print(f'Server is starting...')
    start_server()
