import socket
import re

PORT = 1075
LINE_VALIDATOR = re.compile(r"(0|1)(0|1)(0|1)(0|1)(0|1)")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", PORT))

    while True:
        data, addr = s.recvfrom(1024)
        print("Received data from %s:%s" % addr)

        lines = data.rstrip().decode("ascii").split("\n")

        assert len(lines) == 8, "Expected there to be 8 lines separated by linefeeds (0x0a)"
        assert lines[0] == "0", "Expected version number to be 0"
        assert lines[1] == "5", "Expected width to be 5"
        assert lines[2] == "5", "Expected height to be 5"
        
        for i, line in enumerate(lines[3:8]):
            assert LINE_VALIDATOR.match(line), "Line %s: Invalid pattern, must be 5 characters of '1' or '0'" % (i + 4)

        print("Message is valid: %s" % data)

if __name__ == "__main__":
    main()