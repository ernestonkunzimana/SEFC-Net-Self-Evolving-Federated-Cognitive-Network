import socket
import time


def check_connection(host="8.8.8.8", port=53, timeout=3):
try:
socket.setdefaulttimeout(timeout)
socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
return True
except Exception:
return False


def simulate_network_latency(min_delay=0.1, max_delay=0.5):
import random
delay = random.uniform(min_delay, max_delay)
time.sleep(delay)
return delay


if __name__ == "__main__":
print("Network status:", check_connection())