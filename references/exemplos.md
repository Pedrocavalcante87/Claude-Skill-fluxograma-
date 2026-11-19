# Exemplos de uso

## Exemplo 1: criar a partir de descrição (processo **fictício**, usado como demonstração)

**Pedido do usuário**
```
/fluxograma O colaborador envia o pedido de reembolso com os comprovantes. O Financeiro confere a documentação.
Se estiver incompleta, o colaborador complementa e o pedido volta para a conferência. Se estiver completa, o Financeiro
verifica se o valor está dentro da alçada. Dentro da alçada, o Financeiro agenda o pagamento (que é um subprocesso próprio
do Financeiro) e o processo termina com o pagamento agendado. Fora da alçada, o gestor decide: se aprova, segue para o
agendamento do pagamento; se recusa, o gestor notifica o colaborador e o processo termina.
```

**Extração (passo 2)**
| Elemento | Resultado | Fonte |
|---|---|---|
| Início | colaborador envia o pedido | "O colaborador envia o pedido…" |
| Atividades | Enviar pedido (E1), Conferir pedido (E2), Complementar (E3), Agendar pagamento (E4), Notificar recusa (E5) | verbos do texto |
| Decisões | Documentação completa?, Valor dentro da alçada?, Gestor aprova? | "Se estiver…", "verifica se…", "decide" |
| Responsáveis | Colaborador, Financeiro, Gestor → 3 raias | sujeitos das frases |
| Subprocesso | Agendar pagamento | "(que é um subprocesso próprio…)" |
| Laço | incompleta → complementar → volta à conferência | "volta para a conferência" |
| Fins | pagamento agendado; colaborador notificado | "termina com…" |

**Esclarecimentos (passo 3):** nenhum necessário, pois todo texto já define alternativas, responsáveis e desfechos. (Veja o exemplo 2 para um caso com lacunas.)

**Mapeamento:** 3 raias → cores `fora` (Colaborador), `regra` (Financeiro), `frota` (Gestor); subprocesso → `tool` + tag `SUBPROCESSO`; decisões → losangos sem tag;
2 terminais alinhados à direita.

**Resultado:** `assets/exemplo-reembolso.html` (reproduzível por `scripts/gerar_exemplo_reembolso.py`). Validador: 0 erros, 0 avisos.

**Relatório de entrega (modelo)**
```
Fluxograma gerado: fluxograma-reembolso.html
  3 raias · 5 atividades (1 subprocesso) · 3 decisões · 2 saídas · 12 setas.
Caminhos: (1) completo + dentro da alçada → pagamento agendado; (2) incompleto → complementa → volta à conferência;
          (3) fora da alçada + aprovado → pagamento agendado; (4) fora da alçada + recusado → colaborador notificado.
Premissas/interpretações: "subprocesso" representado pela borda grossa (símbolo `tool` do modelo), por não haver símbolo próprio. Confirma?
Validação: 0 erros, 0 avisos.
Observação sobre o processo (não alterei o diagrama): o laço "incompleta → complementa" não tem limite de tentativas.
```

---

## Exemplo 2: informação insuficiente → pedir esclarecimentos

**Pedido**
```
/fluxograma O atendente recebe o chamado e verifica se é urgente. Depois encaminha para o técnico, que resolve e fecha.
```
**Lacunas detectadas**
1. A verificação de urgência tem alternativas ("é urgente" / "não é"), mas só uma consequência foi descrita ("encaminha para o técnico"). O que acontece quando **é** urgente e quando **não é**?
2. "Resolve e fecha": o técnico **sempre** resolve? Há desfecho em que o chamado não é resolvido?
3. "Fecha" é feito pelo técnico ou pelo atendente?

**Resposta correta da Skill:** perguntar (itens 1–3) **antes** de desenhar. **Resposta errada:** inventar "chamado urgente vai ao supervisor", "escalonamento" etc.
Se o usuário responder "faça com o que tem": desenhar a decisão com as duas saídas, rotular a alternativa sem descrição como no texto original (por exemplo, "não é urgente") ligando-a ao mesmo
próximo passo **somente se o usuário confirmar**; caso contrário, entregar o diagrama com a lacuna listada no relatório e sem seta inventada.

---

## Exemplo 3: editar um fluxograma existente

**Pedido:** "adicione uma etapa 'Aprovação jurídica' do Jurídico depois de 'Conferir contrato' em `fluxograma-contratos.html`."
**Procedimento**
1. Ler o arquivo; rodar o validador (baseline).
2. Perguntar se faltar: o Jurídico é raia nova (se já há 3 raias, **não** criar uma quarta cor: perguntar como agrupar) ou uma raia existente? Há alternativa de reprovação?
3. Inserir o nó na coluna seguinte a "Conferir contrato"; deslocar tudo à direita em 226 px (nós, setas, rótulos, terminais), alargar `viewBox` e faixas.
4. Religar: seta de "Conferir contrato" → novo nó → antigo destino. Remover/atualizar rótulos de seta que ficaram sem sentido.
5. Revalidar; relatar o que mudou.

---

## Exemplo 4: validar lógica sem editar

**Pedido:** "valide a lógica de `fluxograma-compras.html`."
**Saída esperada** (exemplo ilustrativo de relatório do validador):
```
Elementos: 12 atividades, 2 decisões, 3 repositórios, 4 saídas, 1 início, 22 setas, 3 raias
AVISO [layout] o barramento bus1 começa/termina DENTRO de n-classify; encoste exatamente na borda.
Resultado: 0 erro(s), 1 aviso(s).
```
Interpretação: lógica íntegra (todas as decisões têm saídas rotuladas, todo nó alcança uma saída). O aviso é cosmético: o barramento
começa 16 px dentro do nó `classify` (x=228, borda em 244). **Não corrigir sem pedido.**

---

## Exemplo 5: pedido que viola o padrão

**Pedido:** "faça o fluxograma com mais uma cor, roxo, para o departamento jurídico."
**Resposta:** informar que o modelo tem 3 cores de raia + neutro e que alterar isso muda a identidade visual; oferecer (a) agrupar o Jurídico com uma raia existente com rótulo composto
(`FINANCEIRO E JURÍDICO  ·  …`), ou (b) dividir em dois fluxogramas, ou (c) o usuário autorizar expressamente a nova cor (nesse caso, registrar no relatório que o padrão foi estendido por autorização e
**adicionar a cor às variáveis do CSS nos modos claro e escuro**, o único caso em que o CSS é tocado).

---

## Tom e formato das perguntas (modelo)
- Curtas, numeradas, uma decisão por pergunta, citando o trecho do texto que gerou a dúvida.
- Oferecer opções quando possível; usar `AskUserQuestion` para perguntas fechadas.
- Nunca perguntar o que já está no texto nem o que o padrão do modelo já define (cores, formas, tamanhos).
