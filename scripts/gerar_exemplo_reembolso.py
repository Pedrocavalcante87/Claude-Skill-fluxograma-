#!/usr/bin/env python3
"""Reproduz assets/exemplo-reembolso.html usando svg_helpers (exemplo completo de uso dos helpers).

    python -I gerar_exemplo_reembolso.py [saida.html]

Sem argumento, escreve em assets/exemplo-reembolso.html. Depois valide:
    python -I validar_fluxograma.py assets/exemplo-reembolso.html
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from svg_helpers import *  # noqa: E402,F403

TEMPLATE = AQUI.parent / "assets" / "template-base.html"
W, H = 1650, 576

# Processo (entrada fornecida pelo usuario): ver references/exemplos.md, exemplo 1.
svg = [
    raia("fora", 16, W, "COLABORADOR  ·  solicita e complementa"),
    raia("regra", 204, W, "FINANCEIRO  ·  confere e agenda"),
    raia("frota", 392, W, "GESTOR  ·  aprova valores fora da alçada"),
    inicio(40, 116, "Pedido de", "reembolso"),
    seta("e1", "ink", "54,116 88,116"),
    no("n-enviar", "fora", 90, 70, "ATIVIDADE", "Enviar pedido", "E1", "Envia a solicitação", "com comprovantes"),
    seta("e2", "regra", "246,116 281,116 281,304 314,304", "pedido", 289, 160, "start"),
    no("n-conferir", "regra", 316, 258, "ATIVIDADE", "Conferir pedido", "E2", "Financeiro confere a", "documentação enviada"),
    seta("e3", "regra", "472,304 540,304"),
    decisao("n-d-completa", "regra", 620, 304, "Documentação", "completa?"),
    seta("e4", "regra", "698,304 766,304", "sim", 732, 294),
    seta("e5", "fora", "620,249 620,164", "não", 628, 210, "start"),
    no("n-complementar", "fora", 542, 70, "ATIVIDADE", "Complementar", "E3", "Colaborador completa", "a documentação"),
    seta("e6", "regra", "542,116 394,116 394,256", "volta à conferência", 468, 106),
    decisao("n-d-alcada", "regra", 846, 304, "Valor dentro", "da alçada?"),
    seta("e7", "regra", "924,304 992,304", "sim", 958, 294),
    seta("e8", "frota", "846,359 846,492 992,492", "não", 854, 420, "start"),
    no("n-agendar", "regra", 994, 258, "SUBPROCESSO", "Agendar pagamento", "E4", "Financeiro agenda o", "pagamento do reembolso", extra="tool"),
    decisao("n-d-aprova", "frota", 1072, 492, "Gestor", "aprova?"),
    seta("e9", "regra", "1072,437 1072,352", "sim", 1080, 400, "start"),
    seta("e10", "frota", "1150,492 1218,492", "não", 1184, 482),
    no("n-notificar", "frota", 1220, 446, "ATIVIDADE", "Notificar recusa", "E5", "Gestor avisa o", "colaborador"),
    seta("e11", "frota", "1376,492 1444,492"),
    seta("e12", "regra", "1150,304 1444,304", "pagamento agendado", 1297, 294),
    saida("n-t1", 1446, 266, "SAÍDA · APROVADO", "Pagamento", "agendado"),
    saida("n-t2", 1446, 454, "SAÍDA · RECUSADO", "Colaborador", "notificado"),
]

LEGENDA = """<span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--surface)" stroke="var(--regra)" stroke-width="1.6"/></svg>Atividade</span>
    <span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--surface)" stroke="var(--regra)" stroke-width="2.6"/></svg>Subprocesso</span>
    <span><svg width="26" height="22" viewBox="0 0 26 22" aria-hidden="true"><polygon points="1,11 13,2 25,11 13,20" fill="var(--surface)" stroke="var(--regra)" stroke-width="1.6"/></svg>Decisão</span>
    <span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--ink)"/></svg>Saída</span>"""

CORPO = f"""</head><body><div class="wrap">
<header>
  <div>
    <p class="eyebrow">Exemplo · Skill fluxograma · processo fictício</p>
    <h1>Reembolso de despesas</h1>
  </div>
  <div>
    <p class="lede">O colaborador envia o pedido com comprovantes e o Financeiro confere a documentação. Pedidos dentro da alçada seguem direto para o agendamento do pagamento; os demais passam pelo gestor.</p>
    <ul class="facts"><li><b>3</b>raias</li><li><b>3</b>decisões</li><li><b>2</b>saídas</li></ul>
  </div>
</header>

<section aria-labelledby="fluxo">
  <h2 id="fluxo">O processo inteiro</h2>
  <p class="sub">Leia da esquerda para a direita. Cada cor é uma raia (um responsável). A borda grossa marca um subprocesso.</p>
  <div class="legend" aria-label="Legenda">
    {LEGENDA}
  </div>
  <div class="figwrap">
    <figure>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="Fluxograma do reembolso: o colaborador envia o pedido, o Financeiro confere a documentação e a alçada do valor, o gestor aprova quando necessário, e o processo termina com pagamento agendado ou colaborador notificado da recusa.">
{defs_marcadores(TEMPLATE)}
{chr(10).join(svg)}
</svg>
    </figure>
  </div>
  <figcaption>Há dois laços de decisão: documentação incompleta volta à conferência depois de o colaborador complementar; valor fora da alçada vai ao gestor, cuja aprovação leva ao agendamento e cuja recusa encerra o pedido com aviso ao colaborador.</figcaption>
</section>

</div>
</body></html>
"""

if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "assets" / "exemplo-reembolso.html"
    destino.write_text(pagina(TEMPLATE, "Reembolso de despesas", CORPO), encoding="utf-8")
    print("escrito", destino)
