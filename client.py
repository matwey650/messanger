from customtkinter import *
import socket
import threading
from PIL import Image
import base64
import io

# клас для головного викна
class MainWindow(CTk):
    def __init__ (self):
        super().__init__()
        self.geometry("550x400")
        self.title("Masenger")
        self.user_name = "Matwei"

        self.is_show_menu = False
        self.frame_menu = CTkFrame(self, width=40, fg_color= "darkgrey")
        self.frame_menu.pack_propagate(False)
        self.frame_menu.place(x=0, y=0)

        self.btn_menu = CTkButton(self, text="▶️", width=40, command= self.toggle_menu)
        self.btn_menu.place(x=0, y=0)

        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        self.meseg_entry = CTkEntry(self, height= 40, placeholder_text= "введить повидомлення...")
        self.meseg_entry.place(x=0, y=0)

        self.btn_send = CTkButton(self, width= 50, height= 40, text = ">", command=self.sendmesege)
        self.btn_send.place(x=0, y=0)
        
        self.btn_image = CTkButton(self, width= 50, height= 40, text = "📂", command= self.open_image)
        self.btn_image.place(x=0, y=0)
        self.adaptive_ui()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            threading.Thread(target= self.recv_message).start()
        except Exception as e:
            self.add_message(f"не вдалося приэднатися до сервера {e}")
        
        
    def adaptive_ui(self):
        self.frame_menu.configure(height = self.winfo_height())

        self.chat_field.configure(height = self.winfo_height()-50,
                                  width = self.winfo_width()- self.frame_menu.winfo_width()-20)
        self.chat_field.place(x = self.frame_menu.winfo_width())

        self.meseg_entry.place(x = self.frame_menu.winfo_width(), y = self.winfo_height()-40)
        self.meseg_entry.configure(width = self.winfo_width() - self.frame_menu.winfo_width() - 110)

        self.btn_send.place(x = self.winfo_width() - 50, y = self.winfo_height() - 40)
        self.btn_image.place(x = self.winfo_width() - 105, y =self.winfo_height() - 40)

        self.after(50,self.adaptive_ui)

    def toggle_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.btn_menu.configure(text = "▶️")
            self.speed_menu = -10
            self.show_menu()
        else:
            self.is_show_menu = True
            self.btn_menu.configure(text = "◀️")
            self.speed_menu = 10
            self.show_menu()

    def show_menu(self):
        self.frame_menu.configure(width = self.frame_menu.winfo_width()+ self.speed_menu)
        if self.is_show_menu:
            if self.frame_menu.winfo_width()<200:
                self.after(10,self.show_menu)
            else:
                self.label = CTkLabel(self.frame_menu, text = "Имя")
                self.label.pack(pady = 30 )
                self.entry = CTkEntry(self.frame_menu,placeholder_text= "Введить имя...")
                self.entry.pack()
                self.btn_save_name = CTkButton(self.frame_menu, text= "зберегти", command= self.save_name)
                self.btn_save_name.pack(pady = 10)
        elif not self.is_show_menu and self.frame_menu.winfo_width() > 50:
            self.after(10,self.show_menu)
            if self.label:
                self.label.destroy()
            if self.entry:
                self.entry.destroy()
            if self.btn_save_name:
                self.btn_save_name.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.user_name = new_name
            self.add_message(f"ваш новий ник {self.user_name}")

    def add_message(self, message, img = None):
        message_frame = CTkFrame(self.chat_field, fg_color= "grey")
        message_frame.pack(pady = 5, anchor = 'w')
        size = self.winfo_width() - self.frame_menu.winfo_width() - 40
        if img:
            label = CTkLabel(message_frame,text = message, wraplength= size,
                            text_color= "white", justify = "left", image= img, compound= "top")
        else:
            label = CTkLabel(message_frame,text = message, wraplength= size,
                            text_color= "white", justify = "left")
        label.pack(padx = 10, pady = 5)

    def sendmesege(self):
        message = self.meseg_entry.get()
        if message:
            self.add_message(f"Я: {message}")
            data = f"TEXT@{self.user_name}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.meseg_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chank = self.sock.recv(4096)
                if not chank:
                    break
                buffer += chank.decode(errors= "ignore")
                while "\n" in buffer:
                    line,buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self,line):
        if not line:
            return
        parts = line.split("@")
        message_type = parts[0]

        if message_type == "TEXT":
            if len(parts) >= 3:
                name =parts[1]
                message =parts[2]
                self.add_message(f"{name}: {message}")
        elif message_type == "IMAGE":
            if len(parts) >= 4:
                name =parts[1]
                file_name = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_image = CTkImage(pil_img, size = (300, 300))
                    self.add_message(f"{name} надислав зображення: {file_name}", ctk_image)
                except:
                    self.add_message(f"помилка показу картинки")
        else:
            self.add_message(line)

    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb" ) as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            image_name = os.path.basename(file_name)
            message = f"IMAGE@{self.user_name}@{image_name}@{b64_data}\n"
            self.sock.sendall(message.encode())
            self.add_message("", CTkImage(Image.open(file_name), size= (300,300)))
        except:
            self.add_message(f"помилка завантаження картинки")

window = MainWindow()
window.mainloop()