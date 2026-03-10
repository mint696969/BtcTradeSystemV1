# path: ./tools/ai_external_stub_server.py
# desc: Operator UI の external AI endpoint をローカルで模擬する最小HTTPサーバー。

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict


HOST = "127.0.0.1"
PORT = 18080
ROUTE = "/ai/respond"


def build_answer(payload: Dict[str, Any]) -> str:

    lang = payload.get("lang", "ja")
    prompt = str(payload.get("prompt", "")).strip()
    state = payload.get("market_state", {}) or {}

    spread = float(state.get("spread", 0.0))
    imbalance = float(state.get("imbalance", 0.0))
    delta = float(state.get("delta", 0.0))
    wall_ratio = float(state.get("wall_ratio", 0.0))

    if lang == "ja":

        if imbalance < -0.2 and delta < 0 and wall_ratio < 0:
            return (
                "external stub 判断: 売り方向の整合が強いです。"
                f" 板バランス={imbalance:.3f}, 約定デルタ={delta:.3f}, 壁比率={wall_ratio:.3f}。"
                " ショート継続シナリオを優先監視します。"
            )

        if imbalance > 0.2 and delta > 0 and wall_ratio > 0:
            return (
                "external stub 判断: 買い方向の整合が強いです。"
                f" 板バランス={imbalance:.3f}, 約定デルタ={delta:.3f}, 壁比率={wall_ratio:.3f}。"
                " ロング継続シナリオを優先監視します。"
            )

        if spread > 7000:
            return (
                "external stub 判断: スプレッドが広く不安定です。"
                f" spread={spread:.1f}。"
                " 無理な追随より確認優先が妥当です。"
            )

        return (
            "external stub 判断: 明確な片寄りは限定的です。"
            f" 板バランス={imbalance:.3f}, 約定デルタ={delta:.3f}, spread={spread:.1f}。"
            f" prompt='{prompt}' を踏まえても、現時点では待機寄りです。"
        )

    if imbalance < -0.2 and delta < 0 and wall_ratio < 0:
        return (
            "external stub: bearish alignment is strong. "
            f"imbalance={imbalance:.3f}, delta={delta:.3f}, wall_ratio={wall_ratio:.3f}. "
            "Short continuation deserves priority."
        )

    if imbalance > 0.2 and delta > 0 and wall_ratio > 0:
        return (
            "external stub: bullish alignment is strong. "
            f"imbalance={imbalance:.3f}, delta={delta:.3f}, wall_ratio={wall_ratio:.3f}. "
            "Long continuation deserves priority."
        )

    if spread > 7000:
        return (
            "external stub: spread is wide and unstable. "
            f"spread={spread:.1f}. "
            "Confirmation is preferable to chasing."
        )

    return (
        "external stub: no strong directional agreement yet. "
        f"imbalance={imbalance:.3f}, delta={delta:.3f}, spread={spread:.1f}, prompt='{prompt}'."
    )


class Handler(BaseHTTPRequestHandler):

    server_version = "BTCTSExternalStub/0.1"

    def _write_json(self, status_code: int, body: Dict[str, Any]) -> None:

        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self) -> None:

        if self.path != ROUTE:
            self._write_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._write_json(400, {"error": "invalid_content_length"})
            return

        raw = self.rfile.read(content_length)

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json(400, {"error": "invalid_json"})
            return

        answer = build_answer(payload)

        self._write_json(
            200,
            {
                "answer": answer,
                "meta": {
                    "provider": "external_stub",
                    "route": ROUTE,
                },
            },
        )

    def do_GET(self) -> None:

        if self.path == "/health":
            self._write_json(200, {"ok": True, "service": "ai_external_stub"})
            return

        self._write_json(404, {"error": "not_found"})

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:

    server = HTTPServer((HOST, PORT), Handler)
    print(f"AI external stub listening on http://{HOST}:{PORT}{ROUTE}")
    print(f"Health check: http://{HOST}:{PORT}/health")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()