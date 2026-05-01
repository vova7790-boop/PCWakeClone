"""
Запускается на домашнем ПК. Отвечает на HTTP запросы — бот использует это для проверки статуса.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 7779


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass  # отключаем вывод логов в консоль


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
