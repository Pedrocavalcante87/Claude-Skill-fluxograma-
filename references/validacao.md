# Critérios de validação

Duas camadas: o **validador automático** (`scripts/validar_fluxograma.py`) e a **checagem manual** (o que só você e o usuário sabem).
Entregue o fluxograma somente com **0 erros** no validador e a checagem manual feita.

```bash
python -I scripts/validar_fluxograma.py caminho/do/fluxograma.html
# opções: --css-ref outro-modelo.html   (comparar o CSS com outro modelo)
#         --sem-css                       (pular a checagem de CSS; use só para depurar)
# saída 0 = sem erros; 1 = há erros
```
O validador lê o **primeiro `<svg>` dentro de `<figure>`**; a legenda e o simulador não entram na análise de grafo.

---

## A. Validação lógica

| Critério | Como o validador reage | Correção típica |
|---|---|---|
| Existe exatamente 1 início (`.start`) | ERRO se 0; AVISO se >1 | Um único gatilho; se há dois, pergunte |
| Existe ao menos 1 saída (`.term`) | ERRO | Todo fluxo termina em algum desfecho |
| Toda atividade/decisão tem **entrada** | ERRO "ninguém chega nele" | Ligue de onde vem, ou remova se sobrou |
| Toda atividade/decisão tem **saída** | ERRO "beco sem saída" | Ligue ao próximo passo ou a uma saída |
| Saída (`.term`) recebe seta e **não** emite | ERRO | Setas saem só de nós, nunca de terminais |
| Início tem saída e **nenhuma** entrada | ERRO | |
| Toda seta tem **origem** e **destino** em formas reais | ERRO "termina no vazio" / "não parte de nenhum nó" | Ajuste coordenadas (ponta a 2 px da borda) |
| Decisão tem **2 ou mais** saídas | ERRO | Decisão sem alternativa = informação faltando: pergunte |
| Cada saída de decisão tem **rótulo** (`.el` perto da seta) | ERRO | Rotule com a alternativa (sim/não, ou o critério) |
| Rótulos de uma decisão **não se repetem** | AVISO | Duas alternativas com o mesmo nome = ambiguidade |
| Sem **ilhas** (partes desconectadas) | ERRO | Ligue ou remova |
| De todo nó se **alcança uma saída** | ERRO "ciclo sem escape" | Todo laço precisa de condição de saída |
| Cor da linha = cor da ponta da seta | ERRO | `class="e frota"` ↔ `marker-end="url(#m-frota)"` |

### Checagem manual (obrigatória; o script não vê)
1. **Fidelidade ao texto do usuário**: percorra o texto frase a frase e marque cada uma no diagrama. Nada a mais, nada a menos.
2. **Cada caminho** do início até cada saída faz sentido lido em voz alta ("Colaborador envia → Financeiro confere → se completa → …").
3. **Cada decisão**: as alternativas cobrem todos os casos possíveis (inclusive o "senão")? Há alternativa que o usuário não descreveu? → pergunte, não invente.
4. **Responsável** de cada etapa = raia certa.
5. **Laços**: voltam ao ponto certo? Quando terminam?
6. **Termos**: os rótulos usam o vocabulário do usuário.
7. **Contagens do cabeçalho** (`ul.facts`) batem com o diagrama (raias, decisões, saídas…).

### Inconsistências do **processo** a reportar (sem alterar o diagrama)
- Etapa que ninguém executa (sem responsável) ou executada por quem não aparece no resto.
- Decisão cuja alternativa leva a lugar nenhum (descrição incompleta).
- Dois desfechos iguais descritos de formas diferentes.
- Laço potencialmente infinito (retorno sem limite de tentativas).
- Etapa mencionada no texto mas sem relação com o resto (sem entrada/saída).
- Ordem contraditória ("A depois de B" e "B depois de A").
- Entradas/saídas citadas que nenhuma etapa produz ou consome.

---

## B. Fidelidade ao modelo (padronização)

| Critério | Validador |
|---|---|
| CSS idêntico ao do modelo (exceto `min-width` do svg) | ERRO se diferir (mostra as linhas) |
| Link das fontes (Barlow Condensed, IBM Plex) presente | ERRO |
| Sem cor hexadecimal, `fill=`/`stroke=` com `#`, nem `font-*` inline no SVG | ERRO |
| Sem `style="…"` inline no SVG | AVISO |
| Só classes que existem no modelo | AVISO |
| 4 marcadores de seta em `<defs>` | ERRO |
| `<svg role="img" aria-label=…>` e `viewBox` | ERRO |
| `id`s únicos; formas e setas com `id` | ERRO (duplicado) / AVISO (sem id) |
| Texto cabe na forma (estimativa de largura) | AVISO |
| Nó cuja cor difere da cor da raia em que está | AVISO |

Também confira à mão (o script não consegue):
- Raias na ordem do fluxo; rótulo `NOME  ·  explicação` em caixa alta.
- Legenda lista **só** símbolos usados.
- `figcaption` descreve o comportamento (laços, desvios), sem inventar.
- Páginas com simulador: ids do `SIM_CONFIG` existem no SVG (ver `references/simulador.md`).

---

## C. Legibilidade e layout

| Critério | Validador |
|---|---|
| Formas **não se sobrepõem** | ERRO |
| Formas dentro do `viewBox` | ERRO |
| Seta **não atravessa** um nó que não é sua origem/destino | ERRO |
| Setas **não se cruzam** (cruzamento próprio; encontro em "T" é permitido) | AVISO |
| Seta **não passa por cima** de rótulo ou título de raia | AVISO |
| Só segmentos horizontais/verticais | AVISO |
| Ponta termina a ≤ 3.5 px da borda do destino | AVISO |
| Barramento encosta exatamente na borda | AVISO |

### Quando um AVISO pode ficar
Só com justificativa explícita no relatório. Exemplo aceitável: um cruzamento inevitável entre dois retornos em processo denso, depois de tentar
reordenar raias. **Nunca** deixe passar: ERRO, CSS divergente, cor inline, nó solto.

### Verificação visual (recomendada)
Renderize e olhe. Exemplo com Edge/Chrome headless (Windows):
```bash
msedge --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 --window-size=1700,1000 --screenshot=saida.png file:///C:/caminho/fluxo.html
```
`--virtual-time-budget` espera as fontes carregarem; sem ele as fontes podem sair trocadas na imagem (não é defeito do arquivo).
Procure: texto cortado, rótulo sobre linha, seta colada demais, raia vazia.

---

## D. Mensagens do validador (referência rápida)
`[seta]` conexão · `[logica]` grafo · `[layout]` posição/geometria · `[texto]` caber na forma · `[css]`/`[estilo]` padronização ·
`[svg]` estrutura · `[id]` identificadores · `[acessibilidade]` · `[conteudo]` nó sem título.

Limitações do validador: estima largura de texto (pode errar por ±10%); considera apenas segmentos retos; não interpreta animações do simulador;
não confere o **significado** dos rótulos. Não substitui a leitura do fluxo.
