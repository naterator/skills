#!/usr/bin/env python3
"""Build reference-styled Markdown, TeX, and PDF without shell interpolation."""
import argparse
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--engine", choices=["auto", "xelatex", "tectonic"], default="auto")
    parser.add_argument("--toc", action="store_true")
    parser.add_argument("--toc-depth", type=int, choices=[1, 2, 3], default=2)
    parser.add_argument("--number-sections", action="store_true")
    parser.add_argument("--bundle", help="Optional Tectonic bundle URL or local bundle path")
    parser.add_argument("--tex-only", action="store_true", help="Generate editable sources without a compiled PDF")
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        parser.error("source must be an existing Markdown (.md) file")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        parser.error("Pandoc is required; install pandoc or add it to PATH")
    engine = args.engine
    if engine == "auto":
        engine = next((name for name in ["xelatex", "tectonic"] if shutil.which(name)), None)
    if not args.tex_only and (not engine or not shutil.which(engine)):
        parser.error("Install XeLaTeX (TeX Live/MacTeX) or Tectonic; --tex-only produces sources only")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    copied = output / source.name
    if copied != source:
        shutil.copy2(source, copied)
    tex = copied.with_suffix(".tex")
    pdf = copied.with_suffix(".pdf")
    template = Path(__file__).resolve().parents[1] / "assets" / "handbook.latex"
    command = [pandoc, str(copied), "--from=markdown+smart", "--to=latex", "--standalone",
               "--template", str(template), "--syntax-highlighting=monochrome",
               "--resource-path", str(source.parent), "--output", str(tex)]
    if args.toc:
        command += ["--toc", "--toc-depth", str(args.toc_depth)]
    if args.number_sections:
        command += ["--number-sections"]
    subprocess.run(command, check=True)
    print(f"Markdown: {copied}\nTeX: {tex}", flush=True)
    if args.tex_only:
        return
    if pdf.exists():
        pdf.unlink()
    if engine == "tectonic":
        tex_command = [shutil.which(engine), "--keep-logs", "--outdir", str(output), str(tex)]
        if args.bundle:
            tex_command += ["--bundle", args.bundle]
        subprocess.run(tex_command,
                       cwd=source.parent, check=True)
    else:
        for _ in range(3):
            subprocess.run([shutil.which(engine), "-interaction=nonstopmode", "-halt-on-error",
                            "-file-line-error", "-output-directory", str(output), str(tex)],
                           cwd=source.parent, check=True)
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise RuntimeError("TeX engine returned without producing a PDF")
    log = tex.with_suffix(".log")
    if log.exists():
        relevant = [line for line in log.read_text(errors="replace").splitlines()
                    if any(item in line for item in ["Overfull", "Missing character", "undefined", "Warning:"])]
        if relevant:
            print("Review these TeX diagnostics before delivery:\n" + "\n".join(relevant), flush=True)
    print(f"PDF: {pdf}", flush=True)


if __name__ == "__main__":
    main()
