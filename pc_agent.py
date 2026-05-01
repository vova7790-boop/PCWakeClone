"""
Запускается на домашнем ПК. Каждые 20 секунд отправляет UDP-пакет в локальную сеть —
бот на телефоне получает эти пакеты и знает что ПК включён.
"""
import socket
import time

BROADCAST = "192.168.0.151"
PORT = 7779
INTERVAL = 20


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            s.sendto(b"alive", (BROADCAST, PORT))
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
