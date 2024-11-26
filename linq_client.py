import socket
import logging


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
            logging.info(f"Connected to server at {self.host}:{self.port}")
            return True
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            return False
        except Exception as e:
            logging.error(f"Error connecting to server: {e}")
            return False

    def receive_data(self):
        """Receive data from the server."""
        try:
            if self.client_socket:
                return self.client_socket.recv(4096)
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
        return None

    def send_data(self, data):
        """Send data to the server."""
        try:
            if self.client_socket:
                self.client_socket.sendall(data)
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    def close(self):
        """Close the client connection."""
        if self.client_socket:
            self.client_socket.close()
