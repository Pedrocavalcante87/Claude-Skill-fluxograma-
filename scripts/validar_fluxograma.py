#!/usr/bin/env python3
"""Valida um fluxograma HTML/SVG no padrao do modelo de referencia (assets/template-base.html).

Uso:
    python -I validar_fluxograma.py arquivo.html [--css-ref caminho/template-base.html] [--sem-css]

Somente biblioteca padrao. Codigo de saida: 0 = sem erros (avisos permitidos), 1 = ha erros.

O que verifica
  FIDELIDADE  CSS identico ao do modelo, sem cores/estilos inline, so classes conhecidas, marcadores de seta,
              fontes, texto que cabe nas formas.
  LOGICA      todo no tem entrada/saida coerente, setas ligam origem e destino, decisoes com 2+ saidas rotuladas,
              inicio/fim, nos desconectados, becos sem saida, ciclos sem escape.
  LAYOUT      nos sobrepostos, fora do viewBox, setas atravessando nos, setas que se cruzam, cor do no x raia.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOL = 4.0  # tolerancia (px) para "encosta na borda"
LANES = {"regra", "frota", "fora"}
KNOWN_CLASSES = {
    "lane", "band", "lt", "node", "regra", "frota", "fora", "ink", "llm", "code", "search", "tool", "dia",
    "tag", "t", "c", "c2", "d", "done", "e", "mk", "el", "start", "store", "term", "ttag", "tt", "note",
    "seen", "active", "running",
}
NODE_CLASSES = {"node", "term", "store", "start"}
MARKER_OF = {"regra": "m-regra", "frota": "m-frota", "fora": "m-fora", "ink": "m-ink"}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# ----------------------------------------------------------------------------- utilidades geometricas
def parse_points(s):
    pts = []
    for pair in re.split(r"\s+", s.strip()):
        if pair:
            x, y = pair.split(",")
            pts.append((float(x), float(y)))
    return pts


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def polyline_dist(p, pts):
    return min(seg_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


class Shape:
    """Forma de um no: retangulo, losango, cilindro (store) ou circulo (start)."""

    def __init__(self, nid, kind, classes, bbox, diamond=None, circle=None):
        self.id, self.kind, self.classes = nid, kind, classes
        self.x0, self.y0, self.x1, self.y1 = bbox
        self.diamond = diamond  # (cx, cy, hw, hh)
        self.circle = circle  # (cx, cy, r)
        self.texts = []  # (classe, x, y, texto) em coordenadas absolutas

    @property
    def lane(self):
        for c in self.classes:
            if c in LANES or c == "ink":
                return c
        return None

    def center(self):
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)

    def boundary_dist(self, p):
        """Distancia do ponto ate a borda da forma (0 = na borda)."""
        if self.diamond:
            cx, cy, hw, hh = self.diamond
            verts = [(cx - hw, cy), (cx, cy - hh), (cx + hw, cy), (cx, cy + hh)]
            return min(seg_dist(p, verts[i], verts[(i + 1) % 4]) for i in range(4))
        if self.circle:
            cx, cy, r = self.circle
            return abs(math.hypot(p[0] - cx, p[1] - cy) - r)
        x, y = p
        inside = self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1
        dx = max(self.x0 - x, 0, x - self.x1)
        dy = max(self.y0 - y, 0, y - self.y1)
        if not inside:
            return math.hypot(dx, dy)
        return min(x - self.x0, self.x1 - x, y - self.y0, self.y1 - y)

    def contains(self, p, shrink=0.0):
        x, y = p
        if self.diamond:
            cx, cy, hw, hh = self.diamond
            return abs(x - cx) / hw + abs(y - cy) / hh < 1 - shrink / 20
        if self.circle:
            cx, cy, r = self.circle
            return math.hypot(x - cx, y - cy) < r - shrink
        return self.x0 + shrink < x < self.x1 - shrink and self.y0 + shrink < y < self.y1 - shrink


def segments_cross(a, b, c, d):
    """Cruzamento proprio (interior com interior)."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0) and 0 not in (o1, o2, o3, o4):
        # ponto de interseccao
        t = o3 / (o3 - o4) if o3 != o4 else 0
        pt = (c[0] + t * (d[0] - c[0]), c[1] + t * (d[1] - c[1]))
        ends = [a, b, c, d]
        if all(math.hypot(pt[0] - e[0], pt[1] - e[1]) > 2.0 for e in ends):
            return pt
    return None


# ----------------------------------------------------------------------------- leitura do SVG
def extract_main_svg(html):
    m = re.search(r"<figure\b.*?</figure>", html, re.S)
    if not m:
        err("Nao encontrei <figure> com o SVG do fluxograma.")
        return None
    s = re.search(r"<svg\b.*?</svg>", m.group(0), re.S)
    if not s:
        err("Nao encontrei o <svg> dentro de <figure>.")
        return None
    return s.group(0)


def tr(g):
    m = re.search(r"translate\(\s*([-\d.]+)[ ,]+([-\d.]+)\s*\)", g.get("transform", ""))
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def classes_of(el):
    return (el.get("class") or "").split()


def text_of(el):
    return "".join(el.itertext()).strip()


def collect(svg_root):
    shapes, edges, lanes, labels, notes = [], [], [], [], []
    lane_texts = []

    def walk(el, ox=0.0, oy=0.0):
        for ch in el:
            tag = ch.tag.split("}")[-1]
            cl = classes_of(ch)
            if tag == "g":
                gx, gy = tr(ch)
                if "lane" in cl:
                    r = ch.find("rect")
                    t = ch.find("text")
                    if t is not None:
                        lane_texts.append((float(t.get("x", 0)), float(t.get("y", 0)), text_of(t), "lt"))
                    if r is not None:
                        lane = next((c for c in cl if c in LANES), None)
                        lanes.append((lane, float(r.get("x", 0)), float(r.get("y", 0)),
                                      float(r.get("width")), float(r.get("height"))))
                    continue
                if "note" in cl:
                    notes.append(ch)
                    continue
                if any(c in NODE_CLASSES for c in cl):
                    s = build_shape(ch, cl, ox + gx, oy + gy)
                    if s:
                        shapes.append(s)
                    continue
                walk(ch, ox + gx, oy + gy)
            elif tag == "circle" and "start" in cl:
                cx, cy, r = float(ch.get("cx")), float(ch.get("cy")), float(ch.get("r"))
                shapes.append(Shape(ch.get("id"), "start", cl, (cx - r, cy - r, cx + r, cy + r), circle=(cx, cy, r)))
            elif tag == "polyline":
                edges.append(ch)
            elif tag == "text" and "el" in cl:
                labels.append((float(ch.get("x", 0)), float(ch.get("y", 0)), text_of(ch), ch.get("text-anchor", "start")))

    walk(svg_root)
    labels_all = labels + lane_texts
    return shapes, edges, lanes, labels, notes, labels_all


def build_shape(g, cl, ox, oy):
    nid = g.get("id")
    texts = []
    for t in g.iter("text"):
        texts.append((" ".join(classes_of(t)), ox + float(t.get("x", 0)), oy + float(t.get("y", 0)), text_of(t)))
    poly = g.find("polygon")
    if poly is not None:
        pts = parse_points(poly.get("points"))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        s = Shape(nid, "decisao", cl, (min(xs), min(ys), max(xs), max(ys)),
                  diamond=(cx, cy, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2))
        s.texts = texts
        return s
    if "store" in cl:
        e = g.find("ellipse")
        rx, ry = float(e.get("rx")), float(e.get("ry"))
        path = g.find("path").get("d")
        v = re.search(r"v\s*(-?[\d.]+)", path)
        h = 2 * ry + (float(v.group(1)) if v else 34)
        s = Shape(nid, "store", cl, (ox, oy, ox + 2 * rx, oy + h))
        s.texts = texts
        return s
    r = g.find("rect")
    if r is None:
        return None
    w, h = float(r.get("width")), float(r.get("height"))
    kind = "term" if "term" in cl else "no"
    s = Shape(nid, kind, cl, (ox, oy, ox + w, oy + h))
    s.texts = texts
    return s


# ----------------------------------------------------------------------------- verificacoes
CHAR_W = {"t": 7.7, "tt": 7.4, "d": 5.7, "c": 6.0, "c2": 6.6, "tag": 6.3, "ttag": 6.3}


def check_text_fit(shapes):
    for s in shapes:
        if s.kind not in ("no", "term", "decisao", "store"):
            continue
        for cls, x, y, txt in s.texts:
            k = cls.split()[0] if cls else ""
            if k not in CHAR_W:
                continue
            w = len(txt) * CHAR_W[k]
            if s.kind == "decisao":
                if k in ("t", "d"):
                    avail = 2 * s.diamond[2] * (1 - abs(y - s.diamond[1]) / s.diamond[3]) - 8
                    if w > avail:
                        warn(f"[texto] '{txt}' pode nao caber no losango {s.id} (~{w:.0f}px > {avail:.0f}px).")
                continue
            if s.kind == "store":
                avail = (s.x1 - s.x0) - 8
            else:
                avail = (s.x1 - s.x0) - (x - s.x0) - 4
            if w > avail:
                warn(f"[texto] '{txt}' pode estourar a forma {s.id} (~{w:.0f}px > {avail:.0f}px). Encurte ou quebre em 2 linhas.")
            if s.kind == "no" and y - s.y0 > (s.y1 - s.y0) - 4:
                warn(f"[texto] '{txt}' fica abaixo da base do no {s.id}.")
    # no sem titulo
    for s in shapes:
        if s.kind in ("no", "decisao") and not any(c.split()[0] == "t" for c, *_ in s.texts if c):
            err(f"[conteudo] o no {s.id} nao tem titulo (classe .t).")


def check_css(html, css_ref_path):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    if not m:
        err("[css] bloco <style> ausente: o fluxograma precisa do CSS do modelo.")
        return
    ref_html = Path(css_ref_path).read_text(encoding="utf-8")
    r = re.search(r"<style>(.*?)</style>", ref_html, re.S)

    def norm(css):
        css = re.sub(r"min-width:\d+px", "min-width:N", css)  # unico valor que pode variar
        return [ln.strip() for ln in css.strip().splitlines() if ln.strip()]
    a, b = norm(m.group(1)), norm(r.group(1))
    if a != b:
        diff = [ln for ln in a if ln not in b][:3] + ["(ausente) " + ln for ln in b if ln not in a][:3]
        err("[css] o CSS difere do modelo (so min-width do svg pode variar). Exemplos: " + " | ".join(diff)[:400])
    if "fonts.googleapis.com/css2?family=Barlow+Condensed" not in html:
        err("[css] link das fontes do modelo (Barlow Condensed, IBM Plex) ausente.")


def check_markup(svg_text, svg_root):
    vb = svg_root.get("viewBox")
    if not vb:
        err("[svg] viewBox ausente.")
    if svg_root.get("role") != "img" or not svg_root.get("aria-label"):
        err('[acessibilidade] o <svg> precisa de role="img" e aria-label descrevendo o fluxo.')
    for lane in LANES | {"ink"}:
        pass
    ids = [e.get("id") for e in svg_root.iter() if e.get("id")]
    for i in {x for x in ids if ids.count(x) > 1}:
        err(f"[id] id duplicado: {i}")
    if re.search(r'(?:fill|stroke)="#', svg_text):
        err("[estilo] cor hexadecimal inline no SVG. Use somente as variaveis do modelo via classes.")
    if re.search(r'\sstyle="', svg_text):
        warn("[estilo] atributo style inline no SVG: prefira as classes do modelo.")
    markers = {m.get("id") for m in svg_root.iter("marker")}
    for need in MARKER_OF.values():
        if need not in markers:
            err(f"[svg] marcador de seta {need} ausente em <defs>.")
    for el in svg_root.iter():
        for c in classes_of(el):
            if c not in KNOWN_CLASSES:
                warn(f"[estilo] classe desconhecida '{c}' (nao existe no modelo).")
                break
    if re.search(r"font-(family|size)=", svg_text):
        err("[estilo] fonte definida inline. Use as classes .t .d .c .tag etc.")


def resolve_graph(shapes, edges, lanes_present):
    """Liga cada seta (com marcador) a origem e destino. Barramentos (sem marcador) propagam a origem."""
    by_id = {s.id: s for s in shapes}
    polys = []
    for e in edges:
        pts = parse_points(e.get("points", ""))
        if len(pts) < 2:
            err(f"[seta] {e.get('id')} tem menos de 2 pontos.")
            continue
        polys.append({"el": e, "id": e.get("id"), "pts": pts, "arrow": bool(e.get("marker-end")), "cl": classes_of(e)})

    def touches_node(p, tol=TOL, allow_inside=False):
        res = []
        for s in shapes:
            if s.boundary_dist(p) <= tol or (allow_inside and s.contains(p)):
                res.append(s)
        return res

    # grupos de polylines que se tocam (barramento / ramificacao)
    n = len(polys)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            a, b = polys[i], polys[j]
            for pa, pb in ((a, b), (b, a)):
                if any(polyline_dist(p, pb["pts"]) <= 1.5 for p in (pa["pts"][0], pa["pts"][-1])):
                    parent[find(i)] = find(j)
    comp = {}
    for i in range(n):
        comp.setdefault(find(i), []).append(i)

    links = []  # (src_id|None, dst_id|None, poly)
    for i, p in enumerate(polys):
        if not p["arrow"]:
            continue
        end, start = p["pts"][-1], p["pts"][0]
        dst = [s for s in touches_node(end)]
        if not dst:
            err(f"[seta] {p['id']} termina no vazio: o ponto {end} nao encosta em nenhum no (tolerancia {TOL}px).")
        dst_s = dst[0] if dst else None
        if dst_s is not None and dst_s.kind == "start":
            err(f"[logica] {p['id']} entra no inicio: o inicio nao pode ter entrada.")
        src = touches_node(start)
        if not src:
            inside = [s for s in shapes if s.contains(start, shrink=1)]
            if inside:
                warn(f"[seta] {p['id']} comeca DENTRO de {inside[0].id}; comece exatamente na borda.")
                src = inside
        srcs = list(src)
        if not srcs:
            # procura origem via barramento
            for j in comp[find(i)]:
                q = polys[j]
                if j == i or q["arrow"]:
                    continue
                for pt in (q["pts"][0], q["pts"][-1]):
                    srcs += touches_node(pt, tol=TOL, allow_inside=True)
        if not srcs:
            err(f"[seta] {p['id']} nao parte de nenhum no (origem solta em {start}).")
        cls_color = next((c for c in p["cl"] if c in MARKER_OF), None)
        mk = re.search(r"url\(#([^)]+)\)", p["el"].get("marker-end", ""))
        if cls_color and mk and mk.group(1) != MARKER_OF[cls_color]:
            err(f"[seta] {p['id']}: cor da linha ({cls_color}) difere da ponta ({mk.group(1)}).")
        if not p["id"]:
            warn("[id] seta sem id (necessario para o simulador).")
        links.append((srcs[0] if srcs else None, dst_s, p))
    return polys, links


def check_graph(shapes, links, labels):
    out_deg = {s.id: [] for s in shapes}
    in_deg = {s.id: [] for s in shapes}
    for src, dst, p in links:
        if src is not None:
            out_deg[src.id].append((dst, p))
        if dst is not None:
            in_deg[dst.id].append((src, p))
    by_id = {s.id: s for s in shapes}

    starts = [s for s in shapes if s.kind == "start"]
    terms = [s for s in shapes if s.kind == "term"]
    if len(starts) != 1:
        (err if not starts else warn)(f"[logica] esperado 1 inicio (circulo .start); encontrado {len(starts)}.")
    if not terms:
        err("[logica] nenhuma saida/fim (retangulo .term) no fluxograma.")

    for s in shapes:
        nid = s.id or "(sem id)"
        if not s.id:
            warn(f"[id] forma sem id em {s.center()}: necessario para o simulador.")
            continue
        if s.kind == "start":
            if not out_deg[s.id]:
                err(f"[logica] o inicio {nid} nao tem seta de saida.")
        elif s.kind == "term":
            if not in_deg[s.id]:
                err(f"[logica] a saida {nid} nao recebe nenhuma seta (inalcancavel).")
            if out_deg[s.id]:
                err(f"[logica] a saida {nid} nao deveria ter setas de saida.")
        elif s.kind == "store":
            if not in_deg[s.id] and not out_deg[s.id]:
                err(f"[logica] o repositorio {nid} esta desconectado.")
        else:  # no / decisao
            if not in_deg[s.id]:
                err(f"[logica] o no {nid} nao tem entrada: ninguem chega nele.")
            if not out_deg[s.id]:
                err(f"[logica] o no {nid} nao tem saida: o fluxo morre aqui (beco sem saida).")
            if s.kind == "decisao":
                outs = out_deg[s.id]
                if len(outs) < 2:
                    err(f"[logica] a decisao {nid} tem {len(outs)} saida(s); decisao exige 2 ou mais alternativas.")
                for dst, p in outs:
                    if not label_near(p["pts"], labels):
                        err(f"[logica] a saida {p['id']} da decisao {nid} nao tem rotulo (.el) da alternativa.")
                lbls = [label_near(p["pts"], labels) for _, p in outs]
                lbls = [l for l in lbls if l]
                if len(set(lbls)) < len(lbls):
                    warn(f"[logica] a decisao {nid} tem alternativas com rotulos repetidos: {lbls}.")

    # conectividade fraca e alcance de saida
    adj = {s.id: set() for s in shapes if s.id}
    radj = {s.id: set() for s in shapes if s.id}
    for src, dst, p in links:
        if src is not None and dst is not None and src.id and dst.id:
            adj[src.id].add(dst.id)
            radj[dst.id].add(src.id)
    ids = list(adj)
    if ids:
        seen, stack = set(), [ids[0]]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adj[u] | radj[u])
        for i in ids:
            if i not in seen:
                err(f"[logica] {i} esta numa parte do diagrama desconectada do resto (ilha).")
    term_ids = {t.id for t in terms if t.id}
    can_reach = set(term_ids)
    changed = True
    while changed:
        changed = False
        for u in ids:
            if u not in can_reach and adj[u] & can_reach:
                can_reach.add(u)
                changed = True
    for s in shapes:
        if s.id and s.kind in ("no", "decisao") and s.id not in can_reach and out_deg.get(s.id):
            err(f"[logica] a partir de {s.id} nao e possivel chegar a nenhuma saida (ciclo sem escape).")
    return out_deg, in_deg


def label_near(pts, labels, max_d=26):
    best, bd = None, 1e9
    for x, y, txt, anchor in labels:
        # o ponto de ancoragem do texto: para 'middle' e o centro; para 'start' e a borda esquerda (+ meia largura estimada)
        w = len(txt) * 5.4
        cx = x if anchor == "middle" else (x + w / 2 if anchor == "start" else x - w / 2)
        d = min(polyline_dist((cx, y - 4), pts), polyline_dist((x, y - 4), pts))
        if d < bd:
            best, bd = txt, d
    return best if bd <= max_d else None


def check_layout(shapes, polys, links, lanes, notes, viewbox, texts_all=()):
    vb = [float(v) for v in viewbox.replace(",", " ").split()] if viewbox else None
    real = [s for s in shapes]
    for i, a in enumerate(real):
        if vb and (a.x0 < vb[0] - 0.5 or a.y0 < vb[1] - 0.5 or a.x1 > vb[0] + vb[2] + 0.5 or a.y1 > vb[1] + vb[3] + 0.5):
            err(f"[layout] {a.id} ultrapassa o viewBox.")
        for b in real[i + 1:]:
            if a.x0 < b.x1 - 1 and b.x0 < a.x1 - 1 and a.y0 < b.y1 - 1 and b.y0 < a.y1 - 1:
                err(f"[layout] {a.id} e {b.id} se sobrepoem.")
    # cor do no x raia
    for s in shapes:
        if s.kind in ("no", "decisao") and s.lane in LANES:
            c = s.center()
            for lane, x, y, w, h in lanes:
                if x <= c[0] <= x + w and y <= c[1] <= y + h and lane and lane != s.lane:
                    warn(f"[layout] {s.id} e da cor '{s.lane}' mas esta na raia '{lane}'.")
    # seta atravessando no
    link_of = {id(p): (src, dst) for src, dst, p in links}
    for p in polys:
        src, dst = link_of.get(id(p), (None, None))
        for s in shapes:
            if s is src or s is dst:
                continue
            if not p["arrow"] and any(s.contains(e, shrink=1) for e in (p["pts"][0], p["pts"][-1])):
                warn(f"[layout] o barramento {p['id']} comeca/termina DENTRO de {s.id}; encoste exatamente na borda.")
                continue
            for k in range(len(p["pts"]) - 1):
                a, b = p["pts"][k], p["pts"][k + 1]
                length = math.hypot(b[0] - a[0], b[1] - a[1])
                steps = max(2, int(length / 2))
                for t in range(1, steps):
                    pt = (a[0] + (b[0] - a[0]) * t / steps, a[1] + (b[1] - a[1]) * t / steps)
                    if s.contains(pt, shrink=2):
                        err(f"[layout] a seta {p['id']} atravessa o no {s.id}. Reencaminhe com cotovelos.")
                        break
                else:
                    continue
                break
    # seta passando por cima de texto (rotulos .el e titulos de raia .lt)
    for x, y, txt, anchor in texts_all:
        if anchor == "lt":
            w, box = len(txt) * 7.7, None
            box = (x, y - 9, x + w, y + 3)
        else:
            w = len(txt) * 5.4
            x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
            box = (x0, y - 9, x0 + w, y + 2)
        for p in polys:
            hit = False
            for k in range(len(p["pts"]) - 1):
                a, b = p["pts"][k], p["pts"][k + 1]
                steps = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 2))
                for t in range(steps + 1):
                    pt = (a[0] + (b[0] - a[0]) * t / steps, a[1] + (b[1] - a[1]) * t / steps)
                    if box[0] + 1 < pt[0] < box[2] - 1 and box[1] + 1 < pt[1] < box[3] - 1:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                warn(f"[layout] a seta {p['id']} passa por cima do texto '{txt}'. Mova o rotulo ou encurte o texto.")
    # cruzamento entre setas
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            a, b = polys[i], polys[j]
            hit = None
            for k in range(len(a["pts"]) - 1):
                for m in range(len(b["pts"]) - 1):
                    hit = segments_cross(a["pts"][k], a["pts"][k + 1], b["pts"][m], b["pts"][m + 1])
                    if hit:
                        break
                if hit:
                    break
            if hit:
                warn(f"[layout] as setas {a['id']} e {b['id']} se cruzam perto de ({hit[0]:.0f},{hit[1]:.0f}). Reorganize para evitar cruzamento.")
    # distancia final da ponta (modelo: 2px antes da borda)
    for src, dst, p in links:
        if dst is not None:
            d = dst.boundary_dist(p["pts"][-1])
            if d > 3.5:
                warn(f"[layout] a ponta de {p['id']} termina a {d:.1f}px de {dst.id}; o modelo termina a ~2px da borda.")
    # ortogonalidade
    for p in polys:
        for k in range(len(p["pts"]) - 1):
            a, b = p["pts"][k], p["pts"][k + 1]
            if abs(a[0] - b[0]) > 0.5 and abs(a[1] - b[1]) > 0.5:
                warn(f"[layout] {p['id']} tem segmento diagonal; o modelo usa apenas segmentos horizontais e verticais.")
                break


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = Path(argv[1])
    css_ref = Path(__file__).resolve().parent.parent / "assets" / "template-base.html"
    skip_css = "--sem-css" in argv
    if "--css-ref" in argv:
        css_ref = Path(argv[argv.index("--css-ref") + 1])
    html = path.read_text(encoding="utf-8")
    if not skip_css:
        check_css(html, css_ref)
    svg_text = extract_main_svg(html)
    if svg_text is None:
        return report(path)
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        err(f"[svg] SVG mal formado (XML invalido): {e}")
        return report(path)
    check_markup(svg_text, root)
    shapes, edges, lanes, labels, notes, labels_all = collect(root)
    polys, links = resolve_graph(shapes, edges, lanes)
    check_text_fit(shapes)
    check_graph(shapes, links, labels)
    check_layout(shapes, polys, links, lanes, notes, root.get("viewBox"), labels_all)
    stats = (f"{sum(s.kind in ('no',) for s in shapes)} atividades, {sum(s.kind == 'decisao' for s in shapes)} decisoes, "
             f"{sum(s.kind == 'store' for s in shapes)} repositorios, {sum(s.kind == 'term' for s in shapes)} saidas, "
             f"{sum(s.kind == 'start' for s in shapes)} inicio, {len([p for p in polys if p['arrow']])} setas, {len(lanes)} raias")
    return report(path, stats)


def report(path, stats=None):
    print(f"Validacao de {path.name}")
    if stats:
        print("  Elementos: " + stats)
    for e in errors:
        print("  ERRO   " + e)
    for w in warnings:
        print("  AVISO  " + w)
    if not errors and not warnings:
        print("  OK     nenhum problema encontrado.")
    print(f"Resultado: {len(errors)} erro(s), {len(warnings)} aviso(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
