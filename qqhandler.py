from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json

import os
RECEIVE_PORT = 5701

class LimitList(list):
    def append(self, __object) -> None:
        if len(self) >= 200:self.pop(0)
        return super().append(__object)

messageHis = LimitList()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args):
        return

    def do_POST(self):
        req_body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        req_json = json.loads(req_body)

        if req_json['post_type'] == 'message':
            if req_json['message_id'] in messageHis:
                return
            else:
                messageHis.append(req_json['message_id'])
        
        self.send_response(200)
        self.end_headers()

        import qqunilt
        qqunilt._handle_(req_json)

def start_handler():
    th = ThreadingHTTPServer(('localhost',RECEIVE_PORT),Handler)
    try:
        th.serve_forever()
    except KeyboardInterrupt:
        print("退出中...")
