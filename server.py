import argparse
import socket
import sys
import signal
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
from random import randint
from typing import Tuple

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer, TimeStamper, KeyValueRenderer

# Default Configuration Constants
DEFAULT_HOST: str = "localhost"
DEFAULT_PORT: int = 8080
MAX_REQUEST_SIZE: int = 4096  # Maximum size of the incoming request in bytes
MAX_THREADS: int = 50  # Maximum number of worker threads


def setup_structlog() -> structlog.BoundLogger:
    """
    Sets up and returns a configured structlog logger.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,  # Filter logs by level
            structlog.stdlib.add_logger_name,  # Add logger name
            structlog.stdlib.add_log_level,  # Add log level
            TimeStamper(fmt="iso"),  # Add timestamp in ISO format
            structlog.processors.StackInfoRenderer(),  # Add stack info if available
            structlog.processors.format_exc_info,  # Format exception info
            JSONRenderer(),  # Render logs as JSON. Use KeyValueRenderer() for plain key-value
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger("SocketServer")
    return logger


logger = setup_structlog()


def handle_client(
    client_socket: socket.socket, client_address: Tuple[str, int]
) -> None:
    """
    Handles the client connection by reading the request and sending back a random number.
    """
    logger.info("connection_established", client_address=client_address)

    try:
        request = client_socket.recv(MAX_REQUEST_SIZE)
        if not request:
            logger.warning("no_data_received", client_address=client_address)
            return

        # Decode request for logging purposes, ignoring decoding errors
        try:
            request_str = request.decode("utf-8", errors="ignore")
            logger.debug(
                "request_received", client_address=client_address, request=request_str
            )
        except UnicodeDecodeError:
            logger.warning("failed_to_decode_request", client_address=client_address)

        # Generate a random number
        random_number: int = randint(1, 100_000_000_000)
        data: str = f"random={random_number}"

        # Prepare HTTP response
        response_lines = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain; charset=utf-8",
            f"Content-Length: {len(data.encode('utf-8'))}",
            "Connection: close",
            f"Date: {dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
            "Server: PythonSocketServer/1.0",
            "",
            data,
        ]
        response = "\r\n".join(response_lines)

        # Send the response
        client_socket.sendall(response.encode("utf-8"))
        logger.info(
            "response_sent", client_address=client_address, random_number=random_number
        )
    except Exception as e:
        logger.error(
            "error_handling_client",
            client_address=client_address,
            error=str(e),
            exc_info=True,
        )
    finally:
        client_socket.close()
        logger.info("connection_closed", client_address=client_address)


def start_server(host: str, port: int, max_workers: int) -> None:
    """
    Starts the socket server and listens for incoming connections.
    """
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Allow reuse of the address
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((host, port))
            server_socket.listen()
            logger.info("server_listening", host=host, port=port)

            # Use ThreadPoolExecutor to manage a pool of threads
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                while True:
                    try:
                        client_socket, client_address = server_socket.accept()
                        # Submit the client handling task to the thread pool
                        executor.submit(handle_client, client_socket, client_address)
                    except socket.error as e:
                        logger.error("socket_error", error=str(e), exc_info=True)
                    except Exception as e:
                        logger.error("unexpected_error", error=str(e), exc_info=True)
        except KeyboardInterrupt:
            logger.info("shutdown_signal_received", signal="KeyboardInterrupt")
        except Exception as e:
            logger.critical("failed_to_start_server", error=str(e), exc_info=True)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for server configuration.
    """
    parser = argparse.ArgumentParser(
        description="Simple Python Socket Server with structlog"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help=f"Hostname to listen on (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--max-threads",
        type=int,
        default=MAX_THREADS,
        help=f"Maximum number of worker threads (default: {MAX_THREADS})",
    )
    return parser.parse_args()


def main() -> None:
    """
    Entry point of the server application.
    """
    args = parse_arguments()

    # Handle graceful shutdown on signals
    def shutdown_handler(signum, frame):
        logger.info("shutdown_signal_received", signal=signum)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    start_server(args.host, args.port, args.max_threads)


if __name__ == "__main__":
    main()
