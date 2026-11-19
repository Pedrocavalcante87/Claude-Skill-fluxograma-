"""Geradores de SVG com a geometria exata do modelo (opcional, mas recomendado).

Uso tipico (veja gerar_exemplo_reembolso.py):
    import sys; sys.path.insert(0, "<pasta scripts>")
    from svg_helpers import *

Cada funcao devolve uma string SVG. Nada aqui define cor, fonte ou traco: so as CLASSES do modelo.
Medidas: no 156x92, terminal 180x(64|76), repositorio 156x50, losango 156x110, inicio r=14.
"""
import re
from pathlib import Path

NODE_W, NODE_H, GAP = 156, 92, 70


def pagina(template_path, titulo_pagina, corpo_html):
    """Monta a pagina: CSS/head copiados do template (sem alteracoes) + corpo (que comeca em '</head><body>...')."""
    tpl = Path(template_path).read_text(encoding="utf-8")
    head = tpl.split("</head><body>")[0].replace("{{TITULO_DA_PAGINA}}", titulo_pagina)
    return head + corpo_html


def defs_marcadores(template_path):
    """Bloco <defs> com os 4 marcadores de seta, copiado do template."""
    tpl = Path(template_path).read_text(encoding="utf-8")
    return re.search(r"<defs>.*?</defs>", tpl, re.S).group(0)


def raia(cor, y, largura, rotulo, altura=168):
    """Faixa de raia. cor: regra|frota|fora. rotulo: 'NOME  ·  explicacao'. Desenhe as raias primeiro."""
    return (f'<g class="lane {cor}"><rect class="band" x="0" y="{y}" width="{largura}" height="{altura}" rx="3"/>'
            f'<text class="lt" x="18" y="{y + 22}">{rotulo}</text></g>')


def inicio(cx, cy, linha1, linha2, id_="n-start"):
    """Circulo de inicio r=14 com rotulo de duas linhas 40px e 27px acima do centro."""
    return (f'<circle id="{id_}" class="start" cx="{cx}" cy="{cy}" r="14"/>'
            f'<text class="el" x="{cx - 30}" y="{cy - 40}">{linha1}</text><text class="el" x="{cx - 30}" y="{cy - 27}">{linha2}</text>')


def no(id_, cor, x, y, tag, titulo, ident, d1, d2="", extra=""):
    """Atividade 156x92. extra: 'llm' (preenchimento tonal), 'tool' (traco grosso), 'search', 'code'."""
    d2_svg = f'<text class="d" x="12" y="81">{d2}</text>' if d2 else ""
    return (f'<g id="{id_}" class="node {cor}{" " + extra if extra else ""}" transform="translate({x},{y})">'
            f'<rect width="{NODE_W}" height="{NODE_H}" rx="3"/><text class="tag" x="12" y="19">{tag}</text>'
            f'<text class="t" x="12" y="38">{titulo}</text><text class="c" x="12" y="52">{ident}</text>'
            f'<text class="d" x="12" y="68">{d1}</text>{d2_svg}</g>')


def decisao(id_, cor, cx, cy, titulo, pergunta, etiqueta="", extra=""):
    """Losango 156x110 centrado em (cx,cy). etiqueta: texto .c acima do vertice superior
    (omita se esse vertice tiver seta). extra='llm' para decisao tomada por LLM."""
    pts = f"{cx - 78},{cy} {cx},{cy - 55} {cx + 78},{cy} {cx},{cy + 55}"
    et = f'<text class="c" x="{cx}" y="{cy - 63}" text-anchor="middle">{etiqueta}</text>' if etiqueta else ""
    return (f'<g id="{id_}" class="node {cor}{" " + extra if extra else ""} dia"><polygon points="{pts}"/>'
            f'<text class="t" x="{cx}" y="{cy - 2}" text-anchor="middle">{titulo}</text>'
            f'<text class="d" x="{cx}" y="{cy + 14}" text-anchor="middle">{pergunta}</text>{et}</g>')


def repositorio(id_, x, y, arquivo, descricao):
    """Cilindro 156x50 (documento, base de dados). Traco sempre muted."""
    return (f'<g id="{id_}" class="store" transform="translate({x},{y})"><path d="M0,8 v34 a78,8 0 0 0 156,0 v-34"/>'
            f'<ellipse cx="78" cy="8" rx="78" ry="8"/><text class="c2" x="78" y="30" text-anchor="middle">{arquivo}</text>'
            f'<text class="d" x="78" y="44" text-anchor="middle">{descricao}</text></g>')


def saida(id_, x, y, tag, l1, l2=""):
    """Terminal de 180 de largura; altura 76 com 2 linhas de texto, 64 com 1."""
    h = 76 if l2 else 64
    l2_svg = f'<text class="tt" x="12" y="54">{l2}</text>' if l2 else ""
    return (f'<g id="{id_}" class="term" transform="translate({x},{y})"><rect width="180" height="{h}" rx="3"/>'
            f'<text class="ttag" x="12" y="19">{tag}</text><text class="tt" x="12" y="38">{l1}</text>{l2_svg}</g>')


def seta(id_, cor, pontos, rotulo=None, lx=0, ly=0, ancora="middle", tracejada=False):
    """Seta ortogonal. pontos: 'x1,y1 x2,y2 ...' (comece NA borda da origem, termine 2px ANTES do destino).
    Rotulo horizontal: ancora middle, ly = y_da_linha - 10. Vertical: ancora start, lx = x_da_linha + 8."""
    dash = ' stroke-dasharray="5 4"' if tracejada else ""
    s = f'<polyline id="{id_}" class="e {cor}"{dash} points="{pontos}" marker-end="url(#m-{cor})"/>'
    if rotulo:
        s += f'<text class="el" x="{lx}" y="{ly}" text-anchor="{ancora}">{rotulo}</text>'
    return s


def barramento(id_, pontos):
    """Tronco sem ponta (cor ink) que se ramifica. Comece/termine exatamente na borda de um no."""
    return f'<polyline id="{id_}" class="e ink" points="{pontos}"/>'


def nota(x, y, largura, linhas, altura=None):
    """Retangulo tracejado com observacoes (uma string por linha)."""
    altura = altura or 16 * len(linhas) + 20
    txt = "".join(f'<text class="d" x="10" y="{22 + 16 * i}">{l}</text>' for i, l in enumerate(linhas))
    return f'<g class="note" transform="translate({x},{y})"><rect width="{largura}" height="{altura}" rx="3"/>{txt}</g>'
