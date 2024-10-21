import logging
import socket
import sys
from random import randint
from threading import Thread
from typing import Tuple

# Configuration Constants
HOST: str = "localhost"
PORT: int = 8080

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def handle_client(
    client_socket: socket.socket,
    client_address: Tuple[str, int],
) -> None:
    try:
        request: bytes = client_socket.recv(1024)
        if not request:
            logging.warning(f"No data received from {client_address}.")
            return

        # Generate a random number
        random_number: int = randint(1, 100000000000)
        data: str = f"random={random_number}"

        # Prepare HTTP response
        response: str = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(data.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{data}"
        )

        # Send the response
        client_socket.sendall(response.encode("utf-8"))
    except Exception as e:
        logging.error(f"Error handling client {client_address}: {e}", exc_info=True)
    finally:
        client_socket.close()


def start_server() -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            logging.info(f"Server listening on http://{HOST}:{PORT}")

            while True:
                try:
                    client_socket: socket.socket
                    client_address: Tuple[str, int]
                    client_socket, client_address = server_socket.accept()
                    client_thread: Thread = Thread(
                        target=handle_client, args=(client_socket, client_address)
                    )
                    client_thread.daemon = (
                        True  # Allows program to exit even if threads are running
                    )
                    client_thread.start()
                except KeyboardInterrupt:
                    logging.info("Server shutting down gracefully.")
                    break
                except Exception as e:
                    logging.error(f"Error accepting connections: {e}", exc_info=True)
    except Exception as e:
        logging.critical(f"Failed to start server: {e}", exc_info=True)


if __name__ == "__main__":
    start_server()
