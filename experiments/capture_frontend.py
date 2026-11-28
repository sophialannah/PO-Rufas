"""Capture the local Streamlit screens in Edge using its DevTools protocol."""

import base64
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

from websockets.sync.client import connect


def main():
    target = Path("evidencias/comparacao/telas")
    target.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="rufas-browser-"))
    edge = subprocess.Popen(
        [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-proxy-server",
            "--remote-debugging-port=0",
            "--window-size=1440,1050",
            f"--user-data-dir={profile}",
            "http://127.0.0.1:8501",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            port_file = profile / "DevToolsActivePort"
            if port_file.exists():
                break
            time.sleep(0.25)
        port = port_file.read_text().splitlines()[0]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as response:
            pages = json.load(response)
        url = next(page["webSocketDebuggerUrl"] for page in pages if page["type"] == "page")
        with connect(url) as ws:

            def call(method, **params):
                ws.send(json.dumps(dict(id=1, method=method, params=params)))
                while True:
                    result = json.loads(ws.recv(timeout=10))
                    if result.get("id") == 1:
                        return result["result"]

            def evaluate(expression):
                return call("Runtime.evaluate", expression=expression, returnByValue=True)["result"].get("value")

            def wait_for(text):
                for _ in range(120):
                    body = evaluate("document.body?.innerText") or ""
                    if text in body:
                        return
                    time.sleep(0.25)
                raise RuntimeError(f"Screen did not show {text}")

            def click(selector, label):
                found = evaluate(
                    f"(()=>{{const e=Array.from(document.querySelectorAll({json.dumps(selector)}))"
                    f".find(x=>x.innerText.trim()==={json.dumps(label)});if(!e)return false;e.click();return true;}})()"
                )
                if not found:
                    raise RuntimeError(label)

            def capture(name):
                time.sleep(0.5)
                (target / name).write_bytes(base64.b64decode(call("Page.captureScreenshot")["data"]))

            wait_for("Animal selecionado")
            capture("visao_geral.png")
            click("[role=tab]", "Otimização")
            wait_for("Executar otimização")
            click("button", "Executar otimização")
            wait_for("Abra Resultados")
            click("[role=tab]", "Resultados")
            wait_for("6,68 g/dia")
            capture("resultado_referencia.png")
            click("[role=tab]", "Cenários")
            wait_for("Executar comparação dos otimizadores")
            click("button", "Executar comparação dos otimizadores")
            wait_for("Baixar comparação completa (JSON)")
            evaluate(
                "document.querySelectorAll('[data-testid=stDataFrame]')[document.querySelectorAll('[data-testid=stDataFrame]').length-1]?.scrollIntoView()"
            )
            capture("comparacao.png")
            print("Captured three real screens.")
    finally:
        edge.terminate()
        edge.wait(timeout=10)


if __name__ == "__main__":
    main()
