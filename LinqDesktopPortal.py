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
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            return False

    def handle_client(self):
        """Handle client communication."""
        try:
            while self.running:
                data = self.client_socket.recv(4096)
                if not data:
                    break
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.close_connection()

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
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def close(self):
        """Close the client connection."""
        if self.client_socket:
            self.client_socket.close()


class LinqApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linq Desktop Portal")
        self.connection = None
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        """Create the GUI widgets."""
        # Connection Frame
        conn_frame = tk.Frame(self.root)
        conn_frame.pack(pady=10)

        tk.Label(conn_frame, text="Enter remote IP to connect:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(conn_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(conn_frame, text="Start Server", command=self.start_server).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(conn_frame, text="Connect to Server", command=self.connect_to_server).grid(row=1, column=1, padx=5, pady=5)

        # Host IP Display
        host_ip_frame = tk.Frame(self.root)
        host_ip_frame.pack(pady=10)

        tk.Label(host_ip_frame, text="Your IP Address:").grid(row=0, column=0, padx=5, pady=5)
        self.host_ip_display = tk.Entry(host_ip_frame, state="readonly", width=20)
        self.host_ip_display.grid(row=0, column=1, padx=5, pady=5)
        self.host_ip_display.insert(0, self.get_host_ip())

        # Connection Status
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)

        tk.Label(status_frame, text="Connection Status:").grid(row=0, column=0, padx=5, pady=5)
        self.status_display = tk.Entry(status_frame, state="readonly", width=20)
        self.status_display.grid(row=0, column=1, padx=5, pady=5)
        self.update_status("Disconnected", "red")

        # Collaboration Window
        self.collab_frame = tk.LabelFrame(self.root, text="Live View")
        self.collab_frame.pack(pady=10)
        self.collab_view = tk.Label(self.collab_frame, width=60, height=20, bg="black")
        self.collab_view.pack()

        tk.Button(self.root, text="Exit", command=self.exit_app).pack(pady=10)

    def start_server(self):
        """Start the server."""
        self.connection = LinqServer()
        if self.connection.start_server():
            self.update_status("Connected", "green")
        else:
            self.update_status("Disconnected", "red")

    def connect_to_server(self):
        """Connect to the server."""
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showerror("Error", "Please enter the IP address.")
            return

        self.connection = LinqClient(host=ip)
        if self.connection.connect_to_server():
            self.update_status("Connected", "green")
        else:
            self.update_status("Disconnected", "red")

    def update_status(self, text, color):
        """Update the connection status."""
        self.status_display.config(state="normal")
        self.status_display.delete(0, tk.END)
        self.status_display.insert(0, text)
        self.status_display.config({"foreground": color})
        self.status_display.config(state="readonly")

    def get_host_ip(self):
        """Get the host's IP address."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception as e:
            print(f"Error retrieving IP: {e}")
            return "Unknown"

    def exit_app(self):
        """Exit the application."""
        if self.connection:
            self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinqApp(root)
    root.mainloop()
