"""
build_informe.py — Construye los PDFs del proyecto (informe técnico + memoria
resumen) a partir de Markdown. Pipeline:

    pandoc --standalone --toc → HTML temporal
    wkhtmltopdf               → PDF final con tipografía editorial

Inserta los 13 hallazgos generados por 10_hallazgos.py donde aparece el
marcador {HALLAZGOS} en informe.md.
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INF = ROOT / "informe"
PROC = ROOT / "data" / "processed"


def es_int(n) -> str:
    """123456 → '123.456'"""
    return f"{int(round(float(n))):,d}".replace(",", ".")


def es_float(n, decimals: int = 1) -> str:
    """1234.56 → '1.234,6'"""
    return f"{float(n):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def es_pct(n, decimals: int = 1) -> str:
    """45.5 → '45,5%'"""
    return f"{float(n):.{decimals}f}%".replace(".", ",")


def es_pct0(n) -> str:
    return f"{int(round(float(n)))}%"


# Filtros de plantilla disponibles dentro de los marcadores {{NOMBRE|filtro}}
FILTERS = {
    "int": es_int,
    "float": lambda n: es_float(n, 1),
    "float0": lambda n: es_float(n, 0),
    "float2": lambda n: es_float(n, 2),
    "pct": es_pct,
    "pct0": es_pct0,
    "raw": lambda n: str(n),
}


PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_0-9]+)(?:\|(\w+))?\}\}")


def render_template(text: str, nums: dict) -> str:
    """Sustituye {{NOMBRE}} o {{NOMBRE|filtro}} por valor formateado."""
    missing: list[str] = []

    def replace(m: re.Match) -> str:
        key = m.group(1)
        flt = m.group(2) or "raw"
        if key not in nums:
            missing.append(key)
            return f"{{{{MISSING:{key}}}}}"
        try:
            fn = FILTERS.get(flt, FILTERS["raw"])
            return fn(nums[key])
        except Exception as e:  # pragma: no cover
            return f"{{{{ERROR:{key}|{e}}}}}"

    out = PLACEHOLDER_RE.sub(replace, text)
    if missing:
        unique = sorted(set(missing))
        raise SystemExit(
            f"\n  ✗ Placeholders sin valor en numeros.json:\n   - "
            + "\n   - ".join(unique)
            + "\n\n  Define cada uno en etl/11_numeros.py antes de compilar."
        )
    return out


def build_hallazgos_md(hallazgos: list[dict]) -> str:
    parts = []
    for h in hallazgos:
        parts.append(f"### {h['id']} · {h['titulo']}")
        parts.append("")
        parts.append(f"> **{h['cifra']}**")
        parts.append("")
        parts.append(h["texto"])
        parts.append("")
        parts.append(f"*Fuente: {h['fuente']}*")
        parts.append("")
    return "\n".join(parts)


def build_one(md_path: Path, pdf_path: Path, html_path: Path, *, css_path: Path, nums: dict) -> None:
    md = md_path.read_text(encoding="utf-8")
    if "{HALLAZGOS}" in md:
        hallazgos = json.loads((PROC / "hallazgos.json").read_text(encoding="utf-8"))
        md = md.replace("{HALLAZGOS}", build_hallazgos_md(hallazgos))
    md = render_template(md, nums)
    built_md = md_path.with_name(f"_built_{md_path.stem}.md")
    built_md.write_text(md, encoding="utf-8")
    subprocess.run(
        ["pandoc", str(built_md), "-o", str(html_path), "--toc", "--toc-depth=2",
         "--number-sections", "--standalone", "--css", str(css_path)],
        check=True,
    )
    subprocess.run(
        ["wkhtmltopdf", "--enable-local-file-access", "--encoding", "utf-8",
         "--margin-top", "22mm", "--margin-bottom", "22mm",
         "--margin-left", "20mm", "--margin-right", "20mm",
         str(html_path), str(pdf_path)],
        check=True,
    )
    print(f"  PDF: {pdf_path.name}  ({pdf_path.stat().st_size/1024:.1f} KB)")


def main() -> None:
    numeros_path = PROC / "numeros.json"
    if not numeros_path.exists():
        raise SystemExit(
            "  ✗ Falta data/processed/numeros.json — ejecuta antes etl/11_numeros.py"
        )
    nums = json.loads(numeros_path.read_text(encoding="utf-8"))
    css = INF / "informe.css"
    build_one(INF / "informe.md", INF / "informe.pdf", INF / "_informe_built.html", css_path=css, nums=nums)
    build_one(INF / "MEMORIA_RESUMEN.md", INF / "MEMORIA_RESUMEN.pdf", INF / "_memoria_built.html", css_path=css, nums=nums)

    # README: plantilla → README.md (sin PDF)
    readme_template = ROOT / "README.template.md"
    readme_out = ROOT / "README.md"
    if readme_template.exists():
        rendered = render_template(readme_template.read_text(encoding="utf-8"), nums)
        readme_out.write_text(rendered, encoding="utf-8")
        print(f"  README:  {readme_out.name}  ({readme_out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
