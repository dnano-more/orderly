#!/usr/bin/env python3
"""Orderly: turn a customer's voice note or message into a priced order.

For small shops (kirana, tiffin, tailor) whose orders arrive as Hindi, Marathi
or Hinglish voice notes. Everything runs locally:
  voice -> faster-whisper (open source) -> Gemma via Ollama -> validated order
  -> priced from the shop's own catalogue.json -> invoice + WhatsApp reply.

Run:  python orderly.py            then open http://localhost:8000
      python orderly.py --offline  rule-based parser, no model needed
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


PROMPT = """A customer sent an order message to a local grocery shop. It may be in Hindi, Marathi, English or Hinglish (Roman letters).
Translate item names to English (e.g. cheeni/sakhar -> sugar, tel/tail -> cooking oil, chawal/tandul -> rice, atta/pith -> wheat flour, doodh/dudh -> milk, anda/ande -> eggs, chai/chaha -> tea, dal/varan -> toor dal, meeth/namak -> salt).
Map number words: ek=1, do/don=2, teen=3, char=4, paanch=5, aadha=0.5, dus/daha=10.
Keep dozen as dozen (e.g. "ek dozen" -> qty: 1, unit: "dozen", do not convert to 12).
Do NOT invent extra items. Extract ONLY items explicitly in the message.
Return ONLY valid JSON matching this schema:
{{"customer": string or null,
"items": [{{"name": string, "qty": number, "unit": "kg"|"g"|"l"|"pkt"|"dozen"|"pc"|null}}],
"notes": string}}

EXAMPLES:
Order: "2 kilo sugar, 1 litre oil deliver to Mr. Patil"
JSON: {{"customer": "Mr. Patil", "items": [{{"name": "sugar", "qty": 2, "unit": "kg"}}, {{"name": "cooking oil", "qty": 1, "unit": "l"}}], "notes": ""}}

Order: "ek dozen anda aur teen packet doodh"
JSON: {{"customer": null, "items": [{{"name": "eggs", "qty": 1, "unit": "dozen"}}, {{"name": "milk", "qty": 3, "unit": "pkt"}}], "notes": ""}}

Order: "bhaiya do kilo cheeni aur adha kilo chai patti"
JSON: {{"customer": null, "items": [{{"name": "sugar", "qty": 2, "unit": "kg"}}, {{"name": "tea", "qty": 0.5, "unit": "pkt"}}], "notes": ""}}

Order: "don kilo tandul ani ek kilo varan pathva Patil kade"
JSON: {{"customer": "Patil", "items": [{{"name": "rice", "qty": 2, "unit": "kg"}}, {{"name": "toor dal", "qty": 1, "unit": "kg"}}], "notes": ""}}

MESSAGE:
{text}
"""

UNITS = {"kg": "kg", "kilo": "kg", "kilos": "kg", "kgs": "kg", "litre": "l", "liter": "l",
         "ltr": "l", "l": "l", "packet": "pkt", "packets": "pkt", "pkt": "pkt",
         "dozen": "dozen", "gm": "g", "gram": "g", "grams": "g", "g": "g",
         "pcs": "pc", "piece": "pc", "pieces": "pc"}
NUMWORDS = {"ek": 1, "one": 1, "do": 2, "don": 2, "two": 2, "teen": 3, "three": 3, "char": 4, "chaar": 4,
            "four": 4, "paanch": 5, "panch": 5, "five": 5, "aadha": 0.5, "adha": 0.5,
            "half": 0.5, "dus": 10, "daha": 10, "ten": 10}


# ---------- parsing ----------

def _num(tok: str):
    tok = tok.lower()
    if tok in NUMWORDS:
        return NUMWORDS[tok]
    try:
        return float(tok)
    except ValueError:
        return None


def parse_offline(text: str) -> dict:
    """Rule-based fallback: handles 'quantity [unit] item' lists. Rough on purpose."""
    customer, body = None, text
    m = re.search(r"(?:deliver(?:y)?\s+(?:to|at)|send\s+to)\s+(.+)$", text, re.I | re.S)
    if m:
        customer, body = m.group(1).strip(" ."), text[:m.start()]
    items = []
    for chunk in re.split(r"[,;\n]|\b(?:and|aur|ani)\b", body, flags=re.I):
        c = re.sub(r"^(?:bhaiya|bhau|kaka|dada|hello|hi|please)\s+", "", chunk.strip(" ."), flags=re.I)
        toks = c.split()
        if len(toks) < 2 or _num(toks[0]) is None:
            continue
        qty, rest, unit = _num(toks[0]), toks[1:], None
        if rest and rest[0].lower() in UNITS:
            unit = UNITS[rest.pop(0).lower()]
        if rest and rest[0].lower() == "of":
            rest.pop(0)
        if rest:
            items.append({"name": " ".join(rest).lower(), "qty": qty, "unit": unit})
    return {"customer": customer, "items": items, "notes": ""}


def parse_with_model(text: str, model: str) -> dict:
    body = json.dumps({"model": model, "prompt": PROMPT.format(text=text[:3000]),
                       "stream": False, "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(json.load(r)["response"])


def clean_order(data: dict) -> dict:
    """Never trust model output: keep valid items, report what was dropped."""
    items, rejected = [], []
    for it in data.get("items") or []:
        try:
            name = str(it.get("name") or "").strip().lower()
            qty = float(it["qty"])
            if not name or qty <= 0 or qty > 1000:
                raise ValueError
            unit = it.get("unit") if it.get("unit") in set(UNITS.values()) else None
            items.append({"name": name, "qty": qty, "unit": unit})
        except (KeyError, TypeError, ValueError, AttributeError):
            rejected.append(it)
    cust = data.get("customer")
    return {"customer": cust.strip() if isinstance(cust, str) and cust.strip() else None,
            "items": items, "rejected": rejected, "notes": str(data.get("notes") or "")[:200]}


# ---------- pricing ----------

def load_catalogue() -> dict:
    return json.loads((HERE / "catalogue.json").read_text())


def match_item(name: str, catalogue: dict):
    n = name.lower()
    for key, entry in catalogue.items():
        for a in [key] + entry.get("aliases", []):
            if a == n or a in n or (len(n) >= 3 and n in a):
                return key, entry
    return None, None


def build_invoice(order: dict, catalogue: dict) -> dict:
    lines, total, review = [], 0.0, []
    for it in order["items"]:
        key, entry = match_item(it["name"], catalogue)
        if not entry:
            lines.append({**it, "item": it["name"], "price": None, "amount": None})
            review.append(f"'{it['name']}' is not in your catalogue")
            continue
        qty = it["qty"]
        if it["unit"] == "g" and entry["unit"] == "kg":
            qty = qty / 1000
        elif it["unit"] and it["unit"] != entry["unit"]:
            review.append(f"{key}: you sell per {entry['unit']}, customer said {it['unit']}")
        amount = round(entry["price"] * qty, 2)
        total += amount
        lines.append({"item": key, "qty": it["qty"], "unit": it["unit"] or entry["unit"],
                      "price": entry["price"], "amount": amount})
    review += [f"could not read: {r}" for r in order.get("rejected", [])]
    return {"lines": lines, "total": round(total, 2), "review": review}


def whatsapp_reply(order: dict, inv: dict) -> str:
    rows = [f"- {l['item']} x {l['qty']:g} {l['unit'] or ''}: Rs {l['amount']:g}"
            for l in inv["lines"] if l["amount"] is not None]
    who = f"Hello {order['customer']}, " if order.get("customer") else "Hello, "
    return who + "your order:\n" + "\n".join(rows) + f"\nTotal: Rs {inv['total']:g}"


def handle_order(text: str, model: str, offline: bool) -> dict:
    method = "offline"
    raw = None
    if not offline:
        try:
            raw, method = parse_with_model(text, model), "model"
        except Exception:
            raw = None
    if raw is None:
        raw, method = parse_offline(text), "offline"
    order = clean_order(raw)
    inv = build_invoice(order, load_catalogue())
    return {"method": method, "order": order, "invoice": inv, "reply": whatsapp_reply(order, inv)}


# ---------- speech to text ----------

_whisper = None


def transcribe(audio: bytes, model_size: str = "tiny") -> str:
    global _whisper
    try:
        import av
        if not hasattr(av, "_patched_metadata"):
            _orig_open = av.open
            def _safe_av_open(*a, **kw):
                kw.pop("metadata_errors", None)
                return _orig_open(*a, **kw)
            av.open = _safe_av_open
            av._patched_metadata = True
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("Voice needs: pip install faster-whisper")
    if _whisper is None:
        _whisper = WhisperModel(model_size, compute_type="int8")
    import io
    segs, _ = _whisper.transcribe(io.BytesIO(audio), task="transcribe", vad_filter=True)
    return " ".join(s.text.strip() for s in segs)




# ---------- web ----------

PAGE = (HERE / "index.html").read_text() if (HERE / "index.html").exists() else "<h1>index.html missing</h1>"


def make_handler(model: str, offline: bool):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                self._send(200, (HERE / "index.html").read_text(), "text/html; charset=utf-8")
            elif self.path == "/api/catalogue":
                self._send(200, json.dumps(load_catalogue()))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n)
            try:
                if self.path == "/api/order":
                    text = json.loads(raw).get("text", "")
                    self._send(200, json.dumps(handle_order(text, model, offline)))
                elif self.path == "/api/transcribe":
                    self._send(200, json.dumps({"text": transcribe(raw)}))
                else:
                    self._send(404, "{}")
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}))

        def log_message(self, *a):
            pass
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    print(f"Orderly on http://localhost:{a.port}  (model={'none' if a.offline else a.model})")
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.model, a.offline)).serve_forever()



if __name__ == "__main__":
    main()
