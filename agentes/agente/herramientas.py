"""Herramientas locales del mini framework, limitadas a una copia de BiblioUNSA."""
import ast
import difflib
import pathlib
import re
import subprocess
import sys


class Herramientas:
    def __init__(self, raiz, original=None, prueba=None):
        self.raiz = pathlib.Path(raiz).resolve()
        self.original = pathlib.Path(original).resolve() if original else None
        self.prueba = prueba

    def _ruta(self, ruta):
        p = (self.raiz / ruta).resolve()
        if p != self.raiz and self.raiz not in p.parents:
            raise PermissionError("Ruta fuera del sandbox")
        return p

    def catalogo(self):
        return {
            "mapa_repo": "mapa_repo(): mapa compacto de clases y firmas de funciones Python en src/ mediante AST, no ejecuta código",
            "anotar": "anotar(texto): añade una nota breve (máximo 1000 caracteres) a notas.md de esta copia",
            "leer_notas": "leer_notas(): recupera notas de esta ejecución",
            "listar_archivos": "listar_archivos(carpeta='.'): lista archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): texto con números de línea",
            "buscar": "buscar(patron): expresión regular en archivos Python de src/",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta las pruebas del issue seleccionado",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplazo único en un .py de src/",
            "ver_cambios": "ver_cambios(): diff de código con la base inicial",
            "ejecutar_comando": "ejecutar_comando(comando): solo 'python -m pytest -q', todas las pruebas",
        }

    def mapa_repo(self):
        lineas = []
        for p in sorted(self._ruta("src").rglob("*.py")):
            if p.is_symlink() or "antes" in p.relative_to(self.raiz).parts:
                continue
            arbol = ast.parse(p.read_text(encoding="utf-8"))
            firmas = []
            for n in arbol.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    firmas.append(f"{n.name}({ast.unparse(n.args)})")
                elif isinstance(n, ast.ClassDef):
                    firmas.append(n.name + ":")
                    firmas.extend(f"  {m.name}({ast.unparse(m.args)})" for m in n.body
                                  if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_"))
            if firmas:
                lineas.append(p.relative_to(self.raiz).as_posix() + "\n" + "\n".join(firmas))
        return "\n".join(lineas)

    def anotar(self, texto):
        if not isinstance(texto, str) or not texto.strip() or len(texto) > 1000:
            raise ValueError("Nota: texto no vacío de hasta 1000 caracteres")
        p = self._ruta("notas.md")
        with p.open("a", encoding="utf-8") as f:
            f.write("- " + texto.strip() + "\n")
        return "OK: nota guardada"

    def leer_notas(self):
        p = self._ruta("notas.md")
        return p.read_text(encoding="utf-8") if p.exists() else "(sin notas)"

    def listar_archivos(self, carpeta="."):
        return "\n".join(sorted(p.relative_to(self.raiz).as_posix() for p in self._ruta(carpeta).rglob("*") if p.suffix in (".py", ".md") and "__pycache__" not in p.parts and not p.is_symlink()))

    def leer_archivo(self, ruta):
        return "\n".join(f"{i:3d}| {l}" for i,l in enumerate(self._ruta(ruta).read_text(encoding="utf-8").splitlines(),1))

    def buscar(self, patron):
        rx = re.compile(patron)
        hallazgos = []
        for p in sorted(self._ruta("src").rglob("*.py")):
            if p.is_symlink():
                continue
            for i,l in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz).as_posix()}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def _pytest(self, prueba=None):
        args = [sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider"]
        args += [prueba] if prueba else ["tests"]
        r = subprocess.run(args, cwd=self.raiz, capture_output=True, text=True, timeout=120)
        return f"exit={r.returncode}\n" + (r.stdout+r.stderr).strip()[-3000:]

    def ejecutar_pruebas(self):
        return self._pytest(self.prueba)

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        src = self._ruta("src")
        if src not in p.parents or p.suffix != ".py":
            raise PermissionError("Edición fuera de src/")
        texto = p.read_text(encoding="utf-8")
        if not antes or texto.count(antes) != 1:
            return "ERROR: el fragmento debe aparecer exactamente una vez"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self):
        if self.original is None:
            return "ERROR: no hay base de comparación"
        salida = []
        for p in sorted(self._ruta("src").rglob("*.py")):
            rel = p.relative_to(self.raiz)
            q = self.original / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida.extend(difflib.unified_diff(a,p.read_text(encoding="utf-8").splitlines(),f"a/{rel}",f"b/{rel}",lineterm=""))
        return "\n".join(salida) or "(sin cambios)"

    def ejecutar_comando(self, comando):
        if comando != "python -m pytest -q":
            raise PermissionError("Comando no permitido")
        return self._pytest()
