# File: LinqDesktopPortal.py

import tkinter as tk
from tkinter import messagebox, filedialog
import socket
import threading
import pyautogui
from PIL import Image, ImageTk
import io
import os
import time


class LinqServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.running = False

    def start_server(self):
        """Start the server and accept a connection."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"Server started on {self.host}:{self.port}. Waiting for a client...")
            
            self.client_socket, client_address = self.server_socket.accept()
            print(f"Client connected: {client_address}")
            self.running = True
            
            # Start handling client in a new thread
            threading.Thread(target=self.handle_client, daemon=True).start()
        except Exception as e:
            print(f"Error starting server: {e}")

    def handle_client(self):
        """Handle client communication."""
        try:
            while self.running:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                # Handle different types of data
                if data.startswith(b"FILE:"):
                    self.receive_file(data[5:])
                else:
                    print("Received unknown data type.")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.close_connection()

    def receive_file(self, file_metadata):
        """Receive a file sent by the client."""
        try:
            file_name = file_metadata.decode()
            print(f"Receiving file: {file_name}")
            
            # Create a file to save the data
            with open(file_name, "wb") as f:
                while True:
                    data = self.client_socket.recv(4096)
                    if not data:
                        break
                    f.write(data)
            
            print(f"File {file_name} received successfully.")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def stream_desktop(self):
        """Continuously send desktop screenshots to the client."""
        try:
            while self.running:
                # Capture a screenshot
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="JPEG")
                image_data = buffer.getvalue()
                
                # Send the screenshot
                self.client_socket.sendall(image_data)
        except Exception as e:
            print(f"Error streaming desktop: {e}")

    def close_connection(self):
        """Close the client connection."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        print("Client disconnected.")

    def stop_server(self):
        """Stop the server."""
        self.close_connection()
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Server stopped.")


class LinqClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect_to_server(self):
        """Connect to the server."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def send_data(self, data):
        """Send data to the server."""
        if self.client_socket:
            self.client_socket.sendall(data)

    def receive_data(self):
        """Receive data from the server."""
        if self.client_socket:
            return self.client_socket.recv(4096)
        return None

    def close(self):
        """Close the client connection."""
        if self.client_socket:
            self.client_socket.close()


class LinqApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linq Desktop Portal")
        self.connection = None
        self.focal_point = tk.BooleanVar(value=True)
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        """Create the GUI widgets."""
        # Connection Frame
        conn_frame = tk.Frame(self.root)
        conn_frame.pack(pady=10)

        tk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(conn_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(conn_frame, text="Start Server", command=self.start_server).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(conn_frame, text="Connect to Server", command=self.connect_to_server).grid(row=1, column=1, padx=5, pady=5)

        # Security Feature
        self.focal_toggle = tk.Checkbutton(
            self.root, text="Enable FocalPoint", variable=self.focal_point, command=self.toggle_focal_point
        )
        self.focal_toggle.pack(pady=10)

        # Drag and Drop
        self.drag_drop_button = tk.Button(self.root, text="Send File", command=self.send_file)
        self.drag_drop_button.pack(pady=10)

        # Collaboration Window
        self.collab_frame = tk.LabelFrame(self.root, text="Live View")
        self.collab_frame.pack(pady=10)
        self.collab_view = tk.Label(self.collab_frame, width=60, height=20, bg="black")
        self.collab_view.pack()

        tk.Button(self.root, text="Exit", command=self.exit_app).pack(pady=10)

    def start_server(self):
        """Start the server."""
        self.connection = LinqServer()
        threading.Thread(target=self.connection.start_server, daemon=True).start()
        threading.Thread(target=self.connection.stream_desktop, daemon=True).start()
        messagebox.showinfo("Server", "Server started. Waiting for connection...")

    def connect_to_server(self):
        """Connect to the server."""
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showerror("Error", "Please enter the IP address.")
            return

        self.connection = LinqClient(host=ip)
        threading.Thread(target=self.connection.connect_to_server, daemon=True).start()
        threading.Thread(target=self.live_view_receive, daemon=True).start()
        messagebox.showinfo("Client", "Connected to server!")

    def send_file(self):
        """Send a file to the other party."""
        if not self.connection:
            messagebox.showerror("Error", "No connection established.")
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        try:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                data = f.read()

            self.connection.send_data(f"FILE:{file_name}".encode())
            self.connection.send_data(data)
            messagebox.showinfo("File Transfer", f"File '{file_name}' sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")

    def live_view_receive(self):
        """Receive the live view from the other party."""
        self.running = True
        while self.running:
            if not self.connection or not isinstance(self.connection, LinqClient):
                break

            try:
                data = self.connection.receive_data()
                if not data:
                    break
                image = Image.open(io.BytesIO(data))
                photo = ImageTk.PhotoImage(image)
                self.collab_view.config(image=photo)
                self.collab_view.image = photo
            except:
                break

    def toggle_focal_point(self):
        """Toggle the FocalPoint security feature."""
        if self.focal_point.get():
            print("FocalPoint enabled.")
        else:
            print("FocalPoint disabled.")

    def exit_app(self):
        """Exit the application."""
        self.running = False
        if self.connection:
            self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinqApp(root)
    root.mainloop()
