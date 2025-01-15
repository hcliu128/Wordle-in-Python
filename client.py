import socket, time
import tkinter as tk
from tkinter import messagebox, font, simpledialog


class WordleClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Game Client")
        self.master.geometry("1000x900")
        self.master.configure(bg="#f0f0f0")  # 背景顏色

        self.server = None
        self.count = 0  # 計數

        # 字體樣式
        self.label_font = ("Courier New", 14, "bold")
        self.button_font = ("Helvetica", 12)

        # 創建頂部區域框架
        top_frame = tk.Frame(master, bg="#f0f0f0")
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # 輸入框和按鈕
        self.label = tk.Label(top_frame, text="Enter your guess:", font=self.label_font, bg="#f0f0f0")
        self.label.grid(row=0, column=0, padx=30, pady=5, sticky="w")

        self.guess_entry = tk.Entry(top_frame, width=20, font=("Courier New", 14))
        self.guess_entry.grid(row=0, column=1, padx=10, pady=5)

        self.send_button = tk.Button(top_frame, text="Send Guess", font=self.button_font, command=self.send_guess, bg="#87CEEB", fg="white") # 
        self.send_button.grid(row=0, column=2, padx=10, pady=5)

        self.help_button = tk.Button(top_frame, text="HELP", font=self.button_font, command=self.show_help, bg="#FFA07A", fg="white") # 
        self.help_button.grid(row=0, column=3, padx=10, pady=5)

        # 系統消息
        self.sys_label = tk.Label(master, text="System Message:", font=self.label_font, bg="#f0f0f0")
        self.sys_label.pack(pady=10)

        self.sys_text = tk.Text(master, width=70, height=5, state=tk.DISABLED, bg="lightgrey", font=("Courier New", 12))
        self.sys_text.pack(pady=5)

        # 歷史答案標題
        self.history_label = tk.Label(master, text="Guess History:", font=self.label_font, bg="#f0f0f0")
        self.history_label.pack(pady=10)

        # 創建網格框架
        grid_frame = tk.Frame(master, bg="#f0f0f0")
        grid_frame.pack(pady=10)

        # 6x5 的網格
        self.texts = {}
        for row in range(6):
            for col in range(5):
                text_widget = tk.Label(
                    grid_frame,
                    text=" ",
                    width=4,
                    height=2,
                    bg="white",
                    font=("Courier New", 24, font.BOLD),
                    relief="solid",
                )
                text_widget.grid(row=row, column=col, padx=5, pady=5)
                self.texts[f"text_{row}_{col}"] = text_widget

        # 連接到伺服器
        self.username = self.prompt_username()
        self.online_label = tk.Label(top_frame, text="Online: 0", font=self.label_font, bg="#f0f0f0")
        self.online_label.grid(row=0, column=4, padx=10, pady=5)
        self.connect_to_server()

    def prompt_username(self):
        username = None
        while not username:
            username = simpledialog.askstring("Username", "Enter your username:")
        return username
    
    def connect_to_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect(("127.0.0.1", 12345))
            self.server.send(self.username.encode())  # 傳送使用者名稱
            self.display_message_sys("Connected to the server.")
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
            if "Game over! The correct word was:" in data:
                self.display_message_sys(data.split("[SYS] ")[1])
                play_again = messagebox.askyesno("Game Over", "Do you want to play again?")
                if play_again:
                    self.reset_game()
                else:
                    self.server.close()
                    self.master.quit()
            if data.startswith("[SYS] Online:"):
                # 更新在線人數
                online_count = data.split(": ")[1]
                self.online_label.config(text=f"Online: {online_count}")
            elif data == "[SYS] Congratulations! You guessed the word!\n":
                play_again = messagebox.askyesno("Game Over", "Do you want to play again?")
                if play_again:
                    self.reset_game()
                else:
                    self.server.close()
                    self.master.quit()
                    
            elif data and "[SYS]" in data:
                self.display_message_sys(data.split("[SYS] ")[1])

            elif data:
                self.display_message(data)
                if "disconnected" in data:
                    self.server.close()
                    return
                    
        except:
            pass
        self.master.after(50, self.receive_messages)

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
                self.texts[f"text_{self.count}_{i}"].config(text=char, bg="green")
            elif color == "<YELLOW":
                self.texts[f"text_{self.count}_{i}"].config(text=char, bg="yellow")
            elif color == "<BLACK":
                self.texts[f"text_{self.count}_{i}"].config(text=char)
        self.count += 1
        
        if self.count == 6:
            self.server.send("[GameOver]".encode())

    def reset_game(self):
        self.count = 0
        for row in range(6):
            for col in range(5):
                self.texts[f"text_{row}_{col}"].config(text=" ", bg="white")
        self.sys_text.config(state=tk.NORMAL)
        self.sys_text.delete(1.0, tk.END)
        self.sys_text.config(state=tk.DISABLED)
        self.connect_to_server()

    def show_help(self):
        messagebox.showinfo("How to Play", "1. Enter a valid English word of the correct length.\n"
                                           "2. Press 'Send Guess' to submit your guess.\n"
                                           "3. Feedback will be provided:\n"
                                           "   - Green: Correct letter and position.\n"
                                           "   - Yellow: Correct letter but wrong position.\n"
                                           "   - Black: Incorrect letter.\n"
                                           "4. Continue guessing until you find the correct word or run out of attempts.")


if __name__ == "__main__":
    root = tk.Tk()
    client_app = WordleClient(root)
    root.mainloop()
