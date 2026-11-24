from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import threading
import urllib.error
import urllib.request

UPSTREAM = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def start(state):
    key = os.environ["DASHSCOPE_API_KEY"]
    secret = secrets.token_urlsafe(32)
    ledger = state / "budget-ledger.jsonl"
    lock = threading.Lock()
    spent = {"smoke": 0, "formal": 0}
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            spent[record["phase"]] += record["delta"]
    limit_file = state / 'budget-limit.json'
    total_limit = json.loads(limit_file.read_text())['ledger_ceiling_nanoyuan'] if limit_file.exists() else 20_000_000_000
    stopped = False

    def record(phase, delta, **details):
        with ledger.open("a", encoding="utf-8") as out:
            out.write(json.dumps(dict(phase=phase, delta=delta, **details)) + "\n")
            out.flush()
            os.fsync(out.fileno())
        spent[phase] += delta

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, body):
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def error(self, status, message):
            self.send(status, json.dumps({"error":{"message":message}}).encode())

        def do_POST(self):
            nonlocal stopped
            if self.path != "/chat/completions" or not secrets.compare_digest(
                self.headers.get("Authorization", ""), "Bearer " + secret
            ):
                return self.error(403, "Forbidden")
            try:
                size = int(self.headers["Content-Length"])
                if not 0 < size <= 120000:
                    raise ValueError()
                body = self.rfile.read(size)
                payload = json.loads(body)
                output = int(payload["max_tokens"])
                if payload["model"] != "qwen3.5-plus" or not 0 < output <= 8192 or payload.get("stream") or payload.get("n",1)!=1:
                    raise ValueError()
                # Nanoyuan. Full uncached price; reserve an intentionally padded byte proxy.
                input_bound = size + 4096
                reserved = 800 * input_bound + 4800 * output
            except (ValueError, KeyError, TypeError):
                return self.error(400, "Request exceeds supported budget envelope")
            with lock:
                phase = "formal" if (state / "metrics-ready.json").exists() else "smoke"
                if stopped or sum(spent.values())+reserved>total_limit or (phase=="smoke" and spent[phase]+reserved>3_000_000_000):
                    return self.error(429, "Experiment budget reached or provider stopped")
                request_id = secrets.token_hex(12)
                record(phase, reserved, request_id=request_id, event="reserved")
            request = urllib.request.Request(UPSTREAM, data=body,
                headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = response.read()
                usage = json.loads(data)["usage"]
                prompt = int(usage["prompt_tokens"])
                completion = int(usage["completion_tokens"])
                actual = 800*prompt + 4800*completion
                with lock:
                    if prompt>input_bound or completion>output:
                        stopped = True
                    record(phase, actual-reserved, request_id=request_id, event="settled",
                           prompt_tokens=prompt, completion_tokens=completion)
                return self.send(200, data)
            except urllib.error.HTTPError as exc:
                if exc.code not in (500, 502, 503, 504):
                    with lock:
                        stopped = True
                return self.send(exc.code, exc.read())
            except (OSError, ValueError, KeyError, TypeError):
                return self.error(502, "Upstream usage unavailable; reservation retained")

    server = ThreadingHTTPServer(("0.0.0.0", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, secret
