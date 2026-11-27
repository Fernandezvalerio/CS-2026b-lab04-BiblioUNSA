"""Proxy stdio del ejemplo: reenvía bytes intactos y captura JSON-RPC real."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('servidor', type=Path)
    parser.add_argument('--traza', type=Path, default=Path(__file__).resolve().parents[1] / 'trazas/mcp_trafico.jsonl')
    args = parser.parse_args()
    args.traza.parent.mkdir(parents=True, exist_ok=True)
    t0, candado = time.perf_counter(), threading.Lock()
    # 'x' evita mezclar capturas de distintas ejecuciones.
    with args.traza.open('x', encoding='utf-8') as log:
        servidor = subprocess.Popen([sys.executable, '-u', str(args.servidor.resolve())],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        def registrar(direccion, linea):
            try:
                msg = json.loads(linea)
            except (ValueError, UnicodeError):
                return
            with candado:
                log.write(json.dumps({'t': round(time.perf_counter()-t0, 6), 'dir': direccion,
                                      'msg': msg}, ensure_ascii=False) + '\n')
                log.flush()

        def servidor_a_host():
            try:
                for linea in servidor.stdout:
                    registrar('servidor->host', linea)
                    sys.stdout.buffer.write(linea)
                    sys.stdout.buffer.flush()
            except (BrokenPipeError, OSError):
                pass

        hilo = threading.Thread(target=servidor_a_host, daemon=True)
        hilo.start()
        try:
            for linea in sys.stdin.buffer:
                registrar('host->servidor', linea)
                servidor.stdin.write(linea)
                servidor.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                servidor.stdin.close()
            except OSError:
                pass
            try:
                servidor.wait(timeout=10)
            except subprocess.TimeoutExpired:
                servidor.terminate()
                try:
                    servidor.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    servidor.kill()
                    servidor.wait()
            hilo.join()
            servidor.stdout.close()
    return servidor.returncode


if __name__ == '__main__':
    sys.exit(main())
