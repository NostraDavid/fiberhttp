import socket
import random
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

HOST = 'localhost'
PORT = 8080

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler('server.log'),
    logging.StreamHandler(sys.stdout)
])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

logging.info(f"Server listening on http://{HOST}:{PORT}")

def recv_send(client_socket: socket.socket) -> None:
    try:
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break

            # Return some random payload to simulate work
            data = f"random-{random.randint(0, 1000)}"
            response = "\r\n".join([
                "HTTP/1.1 200 OK",
                "Content-Type: text/html",
                f"Content-Length: {len(data)}",
                "",
                data
            ])

            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        # Closing the socket here, but ensuring no further use of the socket happens after closing.
        try:
            client_socket.close()
        except Exception as e:
            logging.error(f"Error closing socket: {e}")

with ThreadPoolExecutor(max_workers=1) as executor:
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            logging.info(f"Connection from {client_address}")
            executor.submit(recv_send, client_socket)
        except KeyboardInterrupt:
            logging.info("Shutting down server...")
            server_socket.close()
            break
        except Exception as e:
            logging.error(f"Server error: {e}")
            break
