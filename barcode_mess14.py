import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk
import socket
import threading
import json
import time
import random


class NetworkedBarcodeChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Barcode Messenger")
        self.root.geometry("1000x800")
        self.root.configure(bg='#0f1626')

        # Networking setup
        self.socket = None
        self.connected = False
        self.is_server = False
        self.clients = []

        # Character mapping
        self.char_to_pattern = {
            'A': '|||| ||', 'B': '||| |||', 'C': '|| ||||', 'D': '|| ||| |',
            'E': '|| || ||', 'F': '| |||||', 'G': '| |||| |',
            'H': '| ||| ||', 'I': '| || |||', 'J': '| | ||||',
            'K': '|||| | |', 'L': '||| || |', 'M': '||| | ||',
            'N': '|| ||| |', 'O': '|| || ||', 'P': '|| | |||',
            'Q': '|| | || |', 'R': '| |||| |', 'S': '| ||| ||',
            'T': '| || |||', 'U': '| | ||||', 'V': '|||| | |',
            'W': '||| || |', 'X': '||| | ||', 'Y': '|| ||| |',
            'Z': '|| || ||',
            '0': '|||||| ', '1': '||||| |', '2': '|||| ||',
            '3': '|||| | ', '4': '||| || ', '5': '||| | |',
            '6': '|| ||| ', '7': '|| || |', '8': '|| | ||',
            '9': '| |||||',
            ' ': '|||| || ', '*': '||| ||| ', '-': '|| |||| ',
            '$': '|| ||| | ', '%': '|| || || ', '.': '|| | ||| ',
            '/': '| ||||| ', '+': '| |||| | '
        }
        self.pattern_to_char = {v: k for k, v in self.char_to_pattern.items()}

        # Initialize chat history
        self.chat_history = []

        # Create GUI elements
        self.setup_gui()

    def setup_gui(self):
        # Title label
        title_label = tk.Label(self.root, text="QUANTUM BARCODE MESSENGER",
                               font=("Courier", 20, "bold"),
                               bg='#0f1626', fg='#4cC2ff')
        title_label.pack(pady=10)

        # Connection status
        self.connection_label = tk.Label(self.root, text="DISCONNECTED",
                                         font=("Courier", 10),
                                         bg='#0f1626', fg='#ff4c4c')
        self.connection_label.pack(pady=5)

        # Scanner frame
        self.scanner_frame = tk.Frame(self.root, bg='#1e2c40',
                                      highlightbackground='#4cC2ff',
                                      highlightthickness=2)
        self.scanner_frame.pack(fill=tk.X, padx=20, pady=10, ipady=10)

        # Barcode display
        self.barcode_label = tk.Label(self.scanner_frame, bg='#1e2c40')
        self.barcode_label.pack(fill=tk.X, expand=True, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(self.scanner_frame, text="READY TO SCAN",
                                     font=("Courier", 10),
                                     bg='#1e2c40', fg='#7fceff')
        self.status_label.pack(pady=5)

        # Chat display
        chat_frame = tk.Frame(self.root, bg='#0f1626')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=("Courier", 11),
            bg='#1a2639', fg='#e6f5ff',
            insertbackground='#4cC2ff',
            bd=0,
            highlightbackground='#4cC2ff',
            highlightthickness=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Input frame
        self.input_frame = tk.Frame(self.root, bg='#0f1626')
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Message input
        self.message_input = tk.Entry(
            self.input_frame,
            font=("Courier", 12),
            bg='#1a2639', fg='#e6f5ff',
            insertbackground='#4cC2ff',
            relief=tk.FLAT,
            highlightbackground='#4cC2ff',
            highlightthickness=1
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.message_input.bind("<Return>", lambda event: self.send_message())

        # Buttons
        button_style = {
            "font": ("Courier", 10, "bold"),
            "bg": "#4cC2ff",
            "fg": "#0f1626",
            "activebackground": "#7fceff",
            "activeforeground": "#0f1626",
            "relief": tk.FLAT,
            "padx": 10,
            "pady": 5,
            "width": 12
        }

        # Host/Join buttons
        self.host_button = tk.Button(self.input_frame, text="HOST",
                                     command=self.start_server,
                                     **button_style)
        self.host_button.pack(side=tk.LEFT, padx=5)

        self.join_button = tk.Button(self.input_frame, text="JOIN",
                                     command=self.join_server,
                                     **button_style)
        self.join_button.pack(side=tk.LEFT, padx=5)

        # Send button
        self.send_button = tk.Button(self.input_frame, text="SEND",
                                     command=self.send_message,
                                     **button_style)
        self.send_button.pack(side=tk.LEFT, padx=5)

    def text_to_barcode(self, text):
        bar_width = 3
        space_width = 3
        bar_height = 100
        padding = 20

        total_width = padding * 2
        for char in text:
            if char in self.char_to_pattern:
                pattern = self.char_to_pattern[char]
                char_width = len(pattern) * bar_width + space_width
                total_width += char_width

        img = Image.new('RGB', (total_width, bar_height), color='#1a2639')
        draw = ImageDraw.Draw(img)

        x_pos = padding
        for char in text:
            if char in self.char_to_pattern:
                pattern = self.char_to_pattern[char]
                for bar in pattern:
                    if bar == '|':
                        draw.line([(x_pos, 10), (x_pos, bar_height - 10)],
                                  fill='#4cC2ff', width=bar_width)
                    x_pos += bar_width
                x_pos += space_width

        return img

    def start_server(self):
        try:
            port = simpledialog.askinteger("Host Server",
                                           "Enter port number (1024-65535):",
                                           minvalue=1024, maxvalue=65535)
            if not port:
                return

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', port))
            self.socket.listen(5)
            self.connected = True
            self.is_server = True

            # Update UI
            self.connection_label.config(text=f"HOSTING ON PORT {port}",
                                         fg='#4cff8d')
            self.host_button.config(state='disabled')
            self.join_button.config(state='disabled')

            # Start accepting connections
            threading.Thread(target=self.accept_connections,
                             daemon=True).start()

            messagebox.showinfo("Success", f"Server started on port {port}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not start server: {str(e)}")

    def join_server(self):
        try:
            host = simpledialog.askstring("Join Server",
                                          "Enter server IP address:")
            if not host:
                return

            port = simpledialog.askinteger("Join Server",
                                           "Enter server port:",
                                           minvalue=1024, maxvalue=65535)
            if not port:
                return

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True

            # Update UI
            self.connection_label.config(text=f"CONNECTED TO {host}:{port}",
                                         fg='#4cff8d')
            self.host_button.config(state='disabled')
            self.join_button.config(state='disabled')

            # Start receiving messages
            threading.Thread(target=self.receive_messages,
                             daemon=True).start()

            messagebox.showinfo("Success", "Connected to server!")

        except Exception as e:
            messagebox.showerror("Error", f"Could not connect: {str(e)}")

    def accept_connections(self):
        while self.connected:
            try:
                client, address = self.socket.accept()
                self.clients.append(client)
                threading.Thread(target=self.handle_client,
                                 args=(client, address),
                                 daemon=True).start()
            except:
                break

    def handle_client(self, client_socket, address):
        while self.connected:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                message = json.loads(data)
                self.display_received_message(message['text'])

                # Forward message to other clients
                for client in self.clients:
                    if client != client_socket:
                        try:
                            client.send(data.encode())
                        except:
                            self.clients.remove(client)
            except:
                break

        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break

                message = json.loads(data)
                self.display_received_message(message['text'])
            except:
                break

        self.disconnect()

    def send_message(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected")
            return

        message = self.message_input.get().upper()
        if not message:
            return

        try:
            # Create message packet
            packet = json.dumps({
                'text': message,
                'timestamp': time.time()
            })

            # Send message
            if self.is_server:
                # Broadcast to all clients
                for client in self.clients:
                    try:
                        client.send(packet.encode())
                    except:
                        self.clients.remove(client)
            else:
                # Send to server
                self.socket.send(packet.encode())

            # Update local display
            self.display_sent_message(message)

            # Clear input
            self.message_input.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    def display_sent_message(self, message):
        self.chat_history.append(("Me", message))
        barcode_img = self.text_to_barcode(message)
        self.display_barcode(barcode_img)
        self.update_chat_display()

    def display_received_message(self, message):
        self.chat_history.append(("Friend", message))
        barcode_img = self.text_to_barcode(message)
        self.display_barcode(barcode_img)
        self.update_chat_display()

    def display_barcode(self, img):
        self.pil_image = img
        photo_image = ImageTk.PhotoImage(img)
        self.barcode_label.config(image=photo_image)
        self.barcode_label.image = photo_image

    def update_chat_display(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)

        for sender, message in self.chat_history:
            if sender == "Me":
                self.chat_display.insert(tk.END, f"YOU » {message}\n", "me")
            else:
                self.chat_display.insert(tk.END, f"REMOTE » {message}\n", "friend")

        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

        self.chat_display.tag_configure("me", foreground="#4cC2ff")
        self.chat_display.tag_configure("friend", foreground="#ff9c4c")

    def disconnect(self):
        self.connected = False
        if self.socket:
            self.socket.close()
        self.socket = None
        self.clients = []

        # Update UI
        self.connection_label.config(text="DISCONNECTED", fg='#ff4c4c')
        self.host_button.config(state='normal')
        self.join_button.config(state='normal')

    def __del__(self):
        self.disconnect()


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkedBarcodeChatApp(root)
    root.mainloop()