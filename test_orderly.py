import json
import threading
import urllib.request
from http.server import HTTPServer

import orderly as O

CAT = O.load_catalogue()


def test_offline_english():
    o = O.parse_offline("2 kilo sugar, 1 litre oil deliver to Mr. Patil")
    assert o["customer"] == "Mr. Patil"
    assert [(i["name"], i["qty"], i["unit"]) for i in o["items"]] == [
        ("sugar", 2.0, "kg"), ("oil", 1.0, "l")]


def test_offline_hinglish_numbers_and_aliases():
    o = O.parse_offline("do kilo cheeni aur adha kilo chai patti")
    inv = O.build_invoice(O.clean_order(o), CAT)
    assert [l["item"] for l in inv["lines"]] == ["sugar", "tea"]
    assert inv["lines"][0]["amount"] == 90.0          # 2 kg x 45
    assert inv["lines"][1]["amount"] == 45.0          # 0.5 x 90


def test_grams_convert_to_kg():
    o = O.clean_order({"items": [{"name": "sugar", "qty": 500, "unit": "g"}]})
    assert O.build_invoice(o, CAT)["total"] == 22.5


def test_unknown_item_flagged_not_priced():
    o = O.clean_order({"items": [{"name": "dragon fruit", "qty": 1, "unit": "kg"}]})
    inv = O.build_invoice(o, CAT)
    assert inv["total"] == 0 and inv["lines"][0]["amount"] is None
    assert any("not in your catalogue" in r for r in inv["review"])


def test_unit_mismatch_flagged():
    o = O.clean_order({"items": [{"name": "milk", "qty": 2, "unit": "l"}]})
    assert any("you sell per pkt" in r for r in O.build_invoice(o, CAT)["review"])


def test_model_garbage_is_rejected():
    o = O.clean_order({"items": [{"name": "rice", "qty": "lots"}, {"name": "", "qty": 2},
                                 {"name": "salt", "qty": -1}, {"name": "rice", "qty": 2, "unit": "kg"}]})
    assert len(o["items"]) == 1 and len(o["rejected"]) == 3


def test_model_failure_falls_back(monkeypatch):
    monkeypatch.setattr(O, "parse_with_model", lambda *a: (_ for _ in ()).throw(ConnectionError()))
    r = O.handle_order("1 kg rice", "gemma3:4b", offline=False)
    assert r["method"] == "offline" and r["invoice"]["total"] == 60


def test_http_roundtrip():
    srv = HTTPServer(("127.0.0.1", 0), O.make_handler("x", True))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/order",
                                 json.dumps({"text": "2 kg sugar, 1 litre oil"}).encode())
    j = json.load(urllib.request.urlopen(req))
    assert j["invoice"]["total"] == 240.0 and "Total: Rs 240" in j["reply"]
    assert b"Orderly" in urllib.request.urlopen(f"http://127.0.0.1:{port}/").read()
    srv.shutdown()
