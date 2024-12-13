# due to some stupid issues with the path of tcl/tk
import os
try: 
    print(os.environ["TCL_LIBRARY"])
    
except Exception as e:
    print(f"Error: {e}, we should manually link the library")

    os.environ["TCL_LIBRARY"] = "C:/Python313/tcl/tcl8.6"
    os.environ["TK_LIBRARY"] = "C:/Python313/tcl/tk8.6"


import socket
import tkinter as tk
from tkinter import messagebox
from tkinter import font


class WordleClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Game Client")
        self.master.geometry("1200x900")

        self.server = None
        self.count = 0 # 計數

        # 使用一個 Frame 放置非網格部分
        top_frame = tk.Frame(master)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.label = tk.Label(top_frame, text="Enter your guess:")
        self.label.pack(pady=5)

        self.guess_entry = tk.Entry(top_frame, width=20)
        self.guess_entry.pack(pady=10)

        self.send_button = tk.Button(top_frame, text="Send Guess", command=self.send_guess)
        self.send_button.pack(pady=5)

        self.sys_label = tk.Label(top_frame, text="System Message:")
        self.sys_label.pack(pady=10)

        self.sys_text = tk.Text(top_frame, width=60, height=5, state=tk.DISABLED)
        self.sys_text.pack(pady=10)

        self.history_label = tk.Label(top_frame, text="History Answer:")
        self.history_label.pack(pady=10)

        # 使用另一個 Frame 放置網格部分
        grid_frame = tk.Frame(master)
        grid_frame.pack(side=tk.TOP, pady=10)

        # 創建 6x5 的網格
        self.texts = {}
        for row in range(6):  # 6 行
            for col in range(5):  # 每行 5 個
                text_widget = tk.Label(grid_frame, text=" ", width=3, height=2, bg="white", font=("Courier New", 18, font.BOLD), relief="solid")
                text_widget.grid(row=row, column=col, padx=5, pady=5)
                self.texts[f"text_{row}_{col}"] = text_widget
        
        # 連接到伺服器
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect(("127.0.0.1", 12345))  # 替換為伺服器地址和端口
            self.display_message_sys("Connected to the server.")

            # 啟動接收伺服器消息的循環
            self.master.after(100, self.receive_messages)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
            self.master.quit()

    def send_guess(self):
        guess = self.guess_entry.get().strip()
        if not guess:
            return

        try:
            self.server.send(guess.encode())
            self.guess_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send guess: {e}")
            self.master.quit()

    def receive_messages(self):
        try:
            self.server.setblocking(False)
            data = self.server.recv(1024).decode()
            if data and "[SYS]" in data:
                self.display_message_sys(data.split("[SYS] ")[1])
            if data and "[SYS]" not in data:
                self.display_message(data)
                # 如果遊戲結束，關閉連接
                if "Congratulations" in data or "disconnected" in data:
                    self.server.close()
                    return
        except:
            pass  # 沒有消息時忽略

        # 繼續檢查新消息
        self.master.after(100, self.receive_messages)


    def display_message_sys(self, message):
        self.sys_text.config(state=tk.NORMAL)
        self.sys_text.insert(tk.END, message + "\n")
        self.sys_text.see(tk.END)
        self.sys_text.config(state=tk.DISABLED)

    def display_message(self, message):
        message = message.split("<RESET>")[0:5]
        for i in range(5):
            content = message[i]
            color, char = content.split(">")
            if color == "<GREEN":
                self.texts[f"text_{self.count}_{i}"].config(text = char, bg="green")
            elif color == "<YELLOW":
                self.texts[f"text_{self.count}_{i}"].config(text = char, bg="yellow")
            elif color == "<BLACK":
                self.texts[f"text_{self.count}_{i}"].config(text = char)
        self.count += 1

        if self.count == 6: 
            self.server.send("[GameOver]".encode())
            play_again = messagebox.askyesno("Game Over", "Do you want to play again?")
            if play_again:
                self.reset_game()
            else:
                self.server.close()
                self.master.quit()

    def reset_game(self):
        self.count = 0
        for row in range(6):
            for col in range(5):
                self.texts[f"text_{row}_{col}"].config(text=" ", bg="white")
        self.sys_text.config(state=tk.NORMAL)
        self.sys_text.delete(1.0, tk.END)
        self.sys_text.config(state=tk.DISABLED)
        self.connect_to_server()

# 啟動 GUI
if __name__ == "__main__":
    root = tk.Tk()
    client_app = WordleClient(root)
    root.mainloop()
