import socket
import logging


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
            logging.info(f"Server started on {self.host}:{self.port}. Waiting for a client...")
            
            self.client_socket, client_address = self.server_socket.accept()
            logging.info(f"Client connected: {client_address}")
            self.running = True
            return True
        except OSError as e:
            logging.error(f"Port {self.port} may already be in use: {e}")
            return False
        except Exception as e:
            logging.error(f"Error starting server: {e}")
            return False

    def receive_data(self):
        """Receive data from the client."""
        try:
            if self.client_socket:
                return self.client_socket.recv(4096)
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
        return None

    def send_data(self, data):
        """Send data to the client."""
        try:
            if self.client_socket:
                self.client_socket.sendall(data)
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    def close_connection(self):
        """Close the client connection."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        logging.info("Client disconnected.")

    def stop_server(self):
        """Stop the server."""
        self.close_connection()
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        logging.info("Server stopped.")
