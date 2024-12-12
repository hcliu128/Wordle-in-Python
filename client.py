# due to some stupid issues with the path of tcl/tk
import os
os.environ["TCL_LIBRARY"] = "C:/Python313/tcl/tcl8.6"
os.environ["TK_LIBRARY"] = "C:/Python313/tcl/tk8.6"


import re
import socket
import tkinter as tk
from tkinter import messagebox

from utils import colors

class WordleClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Game Client")
        self.master.geometry("800x600")

        self.server = None

        # 建立 UI 元素
        self.label = tk.Label(master, text="Enter your guess:")
        self.label.pack(pady=10)

        self.guess_entry = tk.Entry(master, width=20)
        self.guess_entry.pack(pady=10)

        self.send_button = tk.Button(master, text="Send Guess", command=self.send_guess)
        self.send_button.pack(pady=10)

        self.label = tk.Label(master, text="System Message:")
        self.label.pack(pady=10)

        self.sys_text = tk.Text(master, width=60, height=5, state=tk.DISABLED)
        self.sys_text.pack(pady=10)

        self.label = tk.Label(master, text="History Answer:")
        self.label.pack(pady=10)

        self.output_text = tk.Text(master, width=60, height=15, state=tk.DISABLED)
        self.output_text.pack(pady=10)

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
        ansi_to_tag = {
            colors.GREEN: "green",
            colors.YELLOW: "yellow",
            colors.BLACK: "black",
        }

        # 配置樣式
        for ansi, tag in ansi_to_tag.items():
            self.output_text.tag_configure(tag, foreground=tag)

        # 解析並插入顏色文本
        self.output_text.config(state=tk.NORMAL)

        # 正則表達式匹配 ANSI 顏色碼
        ansi_pattern = re.compile(r"(\033\[[0-9;]+m)")
        parts = ansi_pattern.split(message)  # 分割文本和顏色碼

        current_tag = None
        for part in parts:
            if part in ansi_to_tag:  # 如果是 ANSI 顏色碼
                current_tag = ansi_to_tag[part]
            elif part == colors.RESET:  # 如果是重置碼
                current_tag = None
            else:  # 插入普通文本
                self.output_text.insert("end", part, current_tag)

        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

# 啟動 GUI
if __name__ == "__main__":
    root = tk.Tk()
    client_app = WordleClient(root)
    root.mainloop()
