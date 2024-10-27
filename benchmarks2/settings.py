from dataclasses import dataclass


@dataclass
class Settings:
    host: str = "127.0.0.1"
    port: int = 8080
    num_requests: int = 100
    test_url: str = "http://127.0.0.1:8080/"
    log_file: str = "server.log"
    timeout: int = 10
    benchmark_duration = 1

settings = Settings()
