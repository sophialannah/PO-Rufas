"""Capture real final Streamlit screens in headless Edge, using local DevTools."""

import argparse
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

from websockets.sync.client import connect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8517")
    parser.add_argument("--output", default="evidencias/publicacao/telas")
    args = parser.parse_args()
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="po-rufas-publication-browser-"))
    edge = subprocess.Popen(
        [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-proxy-server",
            "--remote-debugging-port=0",
            "--window-size=1600,1100",
            f"--user-data-dir={profile}",
            args.url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        for _ in range(120):
            if (profile / "DevToolsActivePort").exists():
                break
            time.sleep(0.25)
        port = (profile / "DevToolsActivePort").read_text().splitlines()[0]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as response:
            pages = json.load(response)
        url = next(p["webSocketDebuggerUrl"] for p in pages if p["type"] == "page")
        with connect(url) as ws:
            request_id = 0

            def call(method, **params):
                nonlocal request_id
                request_id += 1
                ws.send(json.dumps(dict(id=request_id, method=method, params=params)))
                while True:
                    result = json.loads(ws.recv(timeout=15))
                    if result.get("id") == request_id:
                        if "error" in result:
                            raise RuntimeError(result["error"])
                        return result["result"]

            def evaluate(expression):
                return call("Runtime.evaluate", expression=expression, returnByValue=True)["result"].get("value")

            def wait(expression, timeout=120):
                end = time.monotonic() + timeout
                while time.monotonic() < end:
                    if evaluate(expression):
                        return
                    time.sleep(0.5)
                raise RuntimeError("Timed out waiting for browser: " + expression)

            def click(selector, label):
                assert evaluate(
                    f"(()=>{{const e=[...document.querySelectorAll({json.dumps(selector)})].find(e=>e.innerText.trim()==={json.dumps(label)});if(!e)return false;e.click();return true}})()"
                ), label

            def capture(name):
                time.sleep(1)
                (target / name).write_bytes(base64.b64decode(call("Page.captureScreenshot")["data"]))

            wait("document.body.innerText.includes('Animal selecionado')")
            capture("visao_geral.png")
            click("[role=tab]", "Simulação anual")
            click("label", "Simulação dinâmica integrada")
            wait("document.body.innerText.includes('Otimizador dinâmico')")
            assert evaluate(
                "(()=>{const input=document.querySelector('input[aria-label=\"Otimizador dinâmico\"]');if(!input)return false;input.focus();return true})()"
            )
            call("Input.dispatchKeyEvent", type="keyDown", key="ArrowDown", code="ArrowDown")
            call("Input.dispatchKeyEvent", type="keyUp", key="ArrowDown", code="ArrowDown")
            wait("document.querySelectorAll('[role=option]').length>0")
            click("[role=option]", "Comparação SLSQP versus HiGHS exclusivo")
            wait("document.body.innerText.includes('HiGHS exclusivo: não há fallback')")
            capture("comparacao_exclusiva.png")
            click("button", "Iniciar simulação dinâmica")
            wait("document.body.innerText.split('Simulação concluída em 365 dias.').length>=3", timeout=360)
            evaluate(
                "[...document.querySelectorAll('[data-testid=stMetric]')].at(-1)?.scrollIntoView({block:'center'})"
            )
            capture("resultado_comparacao.png")
            (target / "manifesto.json").write_text(
                json.dumps(
                    dict(
                        source="Real isolated Streamlit backend",
                        days=365,
                        selection="Comparação SLSQP versus HiGHS exclusivo",
                        files=["visao_geral.png", "comparacao_exclusiva.png", "resultado_comparacao.png"],
                    ),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            print("Captured three real screens from 365-day backend comparison")
    finally:
        edge.terminate()
        edge.wait(timeout=15)


if __name__ == "__main__":
    main()
