import socket

HOSTS = [
    "host.domain.com"
]

PORTS = [
    8080
]

TIMEOUT = 3  # seconds


def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True
    except Exception:
        return False


def main():
    success = 0
    failures = 0
    status = "Pass"
    failed_ports = []

    for host in HOSTS:
        for port in PORTS:
            if check_port(host, port):
                success += 1
            else:
                failures += 1
                failed_ports.append(port)
    if failures > 0:
        status = "Fail"

    print("Total|Ports|SuccessCount|FailedCount|FailedPorts|Status")
    print(f"{success + failures}|{PORTS}|{success}|{failures}|{failed_ports}|{status}")




if __name__ == "__main__":
    main()
