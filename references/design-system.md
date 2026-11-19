# Design system do fluxograma (extraído do modelo)

Fonte: dois fluxogramas de referência de origem (exercícios 1 e 2 do bootcamp que originou a Skill; CSS idêntico, só muda o `min-width` do SVG).
Tudo aqui foi **medido** nesses arquivos e está materializado em `assets/template-base.html`. Nada é invenção da Skill.

**Tecnologia do modelo:** página HTML única, autocontida. Fluxograma em **SVG inline escrito à mão** (sem biblioteca,
sem Mermaid, sem imagem), estilizado por classes CSS que usam variáveis (`var(--regra)` etc.). Tema claro/escuro
automático (`prefers-color-scheme`). Fontes via Google Fonts. Simulador opcional em JS puro.

> O CSS **não é reescrito**: ele vem de `assets/template-base.html`, copiado sem alterações. As cores, fontes e
> traços abaixo estão descritos só para você saber **qual classe usar**, não para reproduzir valores.

---

## 1. Paleta (variáveis do CSS)

| Variável | Claro | Escuro | Papel |
|---|---|---|---|
| `--paper` | `#E8EEF0` | `#0A1820` | fundo da página |
| `--surface` | `#F7FAFB` | `#11262F` | fundo de nós, quadro do SVG |
| `--ink` | `#0B2230` | `#E4EEF1` | texto principal, início, saída, setas neutras |
| `--ink2` | `#2F4855` | `#B7C9D0` | texto secundário (`.d`, `.el`) |
| `--muted` | `#567080` | `#8AA3AE` | identificadores `.c`, repositórios, notas |
| `--line` | `#B4C4CB` | `#2C4754` | bordas do quadro |
| `--regra` / `--regra-t` | `#0B6B63` / `#CFE8E4` | `#5CCFC0` / `#123A3A` | **cor de caminho 1** (verde-azulado) e seu tom de preenchimento |
| `--frota` / `--frota-t` | `#8F4A00` / `#F5E1C6` | `#F0AE5A` / `#3A2A12` | **cor de caminho 2** (âmbar) |
| `--fora` / `--fora-t` | `#9C3049` / `#F3D7DD` | `#EE8DA0` / `#3D1A25` | **cor de caminho 3** (rosa-vinho) |

### Como as cores são usadas: cor = caminho/raia, não tipo de forma
No modelo, cada **raia** (faixa horizontal) tem uma cor e todos os nós dentro dela herdam essa cor. As setas
usam a cor da raia **de destino**. As setas de entrada/neutras (início → primeiro nó, barramento) usam `ink`.
O **tipo** de etapa é dado pela forma/preenchimento/etiqueta, nunca por uma cor nova.

**Os nomes das classes (`regra`, `frota`, `fora`) são nomes históricos do exercício e NÃO são renomeados.**
Para outro processo, eles são apenas "cor 1, cor 2, cor 3". Mapeie assim e escreva o rótulo da raia no texto:

| Classe CSS | Cor | Use para |
|---|---|---|
| `regra` | verde-azulado | raia/caminho 1 (primeiro responsável ou caminho principal) |
| `frota` | âmbar | raia/caminho 2 |
| `fora` | rosa-vinho | raia/caminho 3 |
| `ink` | tinta (neutra) | início, entrada neutra, barramentos, nó que não pertence a nenhuma raia |

**Limite: 3 cores de raia + neutro.** Se o processo tiver mais de 3 responsáveis/caminhos, **não invente uma quarta
cor**: agrupe responsáveis em raias, ou pergunte ao usuário (ver `SKILL.md`, passo 3).

## 2. Tipografia (classes)

| Classe | Fonte | Uso |
|---|---|---|
| `h1` | Barlow Condensed 700, `clamp(40px,6vw,72px)` | título da página |
| `h2` | Barlow Condensed 700, 30px | título de seção |
| `.eyebrow` | IBM Plex Mono 500, 12px, caixa alta, `.12em` | linha acima do h1 |
| `.lt` | IBM Plex Mono 500, 11px, `.1em` | rótulo da raia (cor da raia) |
| `.tag` | IBM Plex Mono 500, 9.5px, `.1em` | etiqueta de tipo no topo do nó (cor da raia) |
| `.t` | IBM Plex Sans 600, 13.5px | **título do nó** |
| `.c` | IBM Plex Mono 400, 10px, `--muted` | identificador técnico / código da etapa |
| `.c2` | IBM Plex Mono 500, 10.5px, `--ink` | nome do arquivo no repositório |
| `.d` | IBM Plex Sans 400, 11px, `--ink2` | descrição (máx. 2 linhas) |
| `.el` | IBM Plex Sans 500, 10.5px, `--ink2` | rótulo de seta |
| `.ttag` / `.tt` | Mono 9.5px / Sans 600 13px, cor `--paper` | etiqueta e texto da saída (sobre fundo `ink`) |

Limites de texto em um nó de 156 px: **título ≤ 17 caracteres**, **linha `.d` ≤ 23 caracteres**, **`.c` ≤ 23 caracteres**,
**no máximo 2 linhas `.d`**. Se não couber, encurte; não reduza a fonte.

---

## 3. Geometria (grade do modelo)

Tudo em coordenadas do `viewBox`. Largura padrão do viewBox: 1590–1620; altura conforme o número de raias.

| Elemento | Medida |
|---|---|
| Nó (atividade/código/busca/LLM/tool) | **156 × 92**, `rx=3` |
| Terminal (saída) | **180 × 76** (com 3 linhas de texto) ou **180 × 64** (até 2 linhas), `rx=3` |
| Repositório (cilindro) | **156 × 50** (elipse `rx=78 ry=8`, corpo `v34`) |
| Decisão (losango) | **156 × 110**: vértices `(cx-78,cy) (cx,cy-55) (cx+78,cy) (cx,cy+55)` |
| Início | círculo `r=14` |
| Raia (faixa) | `rx=3`; altura **168** (nós 92 + 54 acima + 22 abaixo) ou mais se houver losango; **20 px** entre faixas |
| Espaço horizontal entre nós | **70 px** (seta de 68, com rótulo) ou **38 px** (seta curta, sem rótulo) |
| Passo da grade | 226 px (156 + 70) |
| Seta | começa **exatamente** na borda da origem e termina **2 px antes** da borda do destino |
| Rótulo de seta horizontal | `text-anchor="middle"`, no centro do segmento, **10 px acima** da linha |
| Rótulo de seta vertical | `text-anchor="start"`, **8 px à direita** da linha |
| Rótulo da raia | `x = faixa.x + 18`, `y = faixa.y + 22` (ou 20) |
| Título da seção `.lt` | em caixa alta, separado por `  ·  `: `NOME  ·  explicação curta` |

### Posições internas de um nó (relativas ao `translate` do nó)
| Elemento | x | y |
|---|---|---|
| `.tag` (tipo) | 12 | 19 |
| `.t` (título) | 12 | 38 |
| `.c` (identificador) | 12 | 52 |
| `.d` linha 1 | 12 | 68 |
| `.d` linha 2 | 12 | 81 |
| ponto `.done` (opcional, "já implementado") | cx=143 | cy=13, r=4.5 |

### Posições internas de um losango (centro `cx, cy`)
`.t` em `(cx, cy-2)` · `.d` em `(cx, cy+14)` · ambos `text-anchor="middle"` · `.c` (etiqueta) em `(cx, cy-63)` acima do vértice
superior (**omita a etiqueta se o vértice superior tiver seta**, para não colidir).

### Posições internas de um terminal
`.ttag` em `(12,19)` · `.tt` em `(12,38)` e `(12,54)`.

### Repositório
`translate(x,y)`; texto `.c2` em `(78,30)` e `.d` em `(78,44)`, ambos `text-anchor="middle"`.

---

## 4. Catálogo de símbolos (copie estes blocos, ajustando só ids, coordenadas e texto)

### Raia
```svg
<g class="lane regra"><rect class="band" x="0" y="204" width="1620" height="168" rx="3"/><text class="lt" x="18" y="226">NOME DA RAIA  ·  explicação curta</text></g>
```
Desenhe as raias **primeiro** (ficam atrás).

### Início
```svg
<circle id="n-start" class="start" cx="40" cy="116" r="14"/><text class="el" x="10" y="76">Linha 1 do rótulo</text><text class="el" x="10" y="89">linha 2</text>
```
Rótulo de duas linhas, 40 px e 27 px acima do centro.

### Atividade / etapa comum (preenchimento `surface`)
```svg
<g id="n-ID" class="node regra code" transform="translate(268,70)"><rect width="156" height="92" rx="3"/><text class="tag" x="12" y="19">TIPO</text><text class="t" x="12" y="38">Título curto</text><text class="c" x="12" y="52">id_tecnico</text><text class="d" x="12" y="68">Primeira linha</text><text class="d" x="12" y="81">segunda linha</text></g>
```
Classes: `node` + cor da raia (`regra|frota|fora|ink`) + modificador opcional.

### Modificadores do nó
| Classe extra | Efeito no CSS | Significado no modelo |
|---|---|---|
| (nenhuma) / `code` | preenchimento `surface`, traço 1.6 | etapa de código / operação comum |
| `search` | igual ao padrão | busca / leitura de dados |
| `llm` | **preenchimento tonal** (`--lane-t`) | etapa com LLM (inteligência de linguagem) |
| `tool` | **traço grosso 2.4** | ferramenta (tool) invocada |
| `dia` | usado no losango | decisão |

### Decisão (losango)
```svg
<g id="n-d1" class="node regra dia"><polygon points="593,174 671,119 749,174 671,229"/><text class="t" x="671" y="172" text-anchor="middle">Título</text><text class="d" x="671" y="188" text-anchor="middle">pergunta?</text></g>
```
Com LLM, adicione `llm` à classe (preenchimento tonal) e a etiqueta `<text class="c" x="671" y="111" text-anchor="middle">grade · LLM</text>`.

### Repositório / documento / dados
```svg
<g id="n-s-ID" class="store" transform="translate(40,88)"><path d="M0,8 v34 a78,8 0 0 0 156,0 v-34"/><ellipse cx="78" cy="8" rx="78" ry="8"/><text class="c2" x="78" y="30" text-anchor="middle">nome_do_arquivo</text><text class="d" x="78" y="44" text-anchor="middle">descrição</text></g>
```
Traço sempre `--muted` (não leva cor de raia).

### Saída / fim
```svg
<g id="n-t1" class="term" transform="translate(1408,302)"><rect width="180" height="76" rx="3"/><text class="ttag" x="12" y="19">SAÍDA · ROTULO</text><text class="tt" x="12" y="38">Linha 1</text><text class="tt" x="12" y="54">linha 2</text></g>
```

### Seta
```svg
<polyline id="e1" class="e regra" points="196,114 266,114" marker-end="url(#m-regra)"/>
<text class="el" x="231" y="104" text-anchor="middle">rótulo</text>
```
- Classe `e` + cor (`regra|frota|fora|ink`); `marker-end` com o marcador da **mesma cor** (`m-regra`, `m-frota`, `m-fora`, `m-ink`).
- Só segmentos **horizontais e verticais**; mudanças de direção por cotovelo (`points` com vários pares).
- Ids sequenciais `e1, e2, …` (o simulador depende deles).
- **Seta tracejada** (`stroke-dasharray="5 4"`) = fluxo de apoio/proveniência (não é passo do processo).
- **Barramento** (linha sem ponta, `id="busN"`, cor `ink`): um tronco que se ramifica para várias raias. Comece e termine
  **exatamente na borda** do nó (o modelo 2 começa 16 px dentro do nó: não repita).
- **Laço de ida e volta** (ex.: análise ↔ ferramentas): duas setas paralelas, uma 12 px acima do eixo e outra 12 px abaixo, rótulos
  fora das linhas.

### Nota
```svg
<g class="note" transform="translate(952,408)"><rect width="384" height="52" rx="3"/><text class="d" x="10" y="22">Linha 1</text><text class="d" x="10" y="38">linha 2</text></g>
```
Retângulo tracejado (`--muted`) para observações. Pode ter `.c` com a palavra `EXEMPLO` na primeira linha.

### Marcadores (em `<defs>`, copiar integralmente do template)
Quatro `<marker>`: `m-regra`, `m-frota`, `m-fora`, `m-ink` (`viewBox 0 0 10 10`, `refX 9 refY 5`, 8×8, `orient auto`).

---

## 5. Legenda (opcional no modelo 1, presente no modelo 2)
`<div class="legend">` com um `<span>` + mini-SVG por símbolo **realmente usado**. Blocos prontos:

```html
<span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--regra-t)" stroke="var(--regra)" stroke-width="1.6"/></svg>Etapa com LLM</span>
<span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--surface)" stroke="var(--regra)" stroke-width="1.6"/></svg>Atividade / busca / código</span>
<span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--surface)" stroke="var(--frota)" stroke-width="2.6"/></svg>Ferramenta (tool)</span>
<span><svg width="26" height="22" viewBox="0 0 26 22" aria-hidden="true"><polygon points="1,11 13,2 25,11 13,20" fill="var(--regra-t)" stroke="var(--regra)" stroke-width="1.6"/></svg>Decisão</span>
<span><svg width="26" height="22" viewBox="0 0 26 22" aria-hidden="true"><path d="M2,6 v10 a11,4 0 0 0 22,0 v-10" fill="var(--surface)" stroke="var(--muted)" stroke-width="1.4"/><ellipse cx="13" cy="6" rx="11" ry="4" fill="var(--surface)" stroke="var(--muted)" stroke-width="1.4"/></svg>Documento indexado</span>
<span><svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><rect x="1" y="2" width="24" height="14" rx="2" fill="var(--ink)"/></svg>Saída</span>
```
Os textos da legenda são **conteúdo** e podem ser renomeados para o domínio (ex.: "Subprocesso"); a forma e o traço, não.

---

## 6. Página ao redor do SVG (estrutura fixa)
1. `<header>`: `.eyebrow` + `h1` à esquerda; `.lede` + `ul.facts` (3 números em `<b>`) à direita.
2. `<section aria-labelledby="fluxo">`: `h2`, `.sub`, `.legend` (opcional), `.sim` (opcional), `.figwrap > figure > svg`, `figcaption`.
3. Seções de apoio opcionais (já estilizadas no CSS, usar somente se o usuário pedir): colunas `.cols/.col` (`regra|frota|fora`),
   tabelas `.tbl`, `.pill`, `.two`, bloco `.status`.

## 7. Estados visuais do simulador (já no CSS; não editar)
`.running`, `.seen`, `.active` são aplicados por JS nos nós e setas. Por isso **todo nó, repositório, terminal, início e seta
precisa de `id`**. Convenção de ids: nós `n-<nome>`, repositórios `n-s-<nome>`, terminais `n-t1…`, setas `e1…`, barramentos `bus1…`.

## 8. Acessibilidade (obrigatória)
`<svg role="img" aria-label="descrição do fluxo em uma frase">`; mini-SVGs da legenda com `aria-hidden="true"`.
O CSS já respeita `prefers-reduced-motion`.

## 9. Observações sobre o próprio modelo
- O modelo 2 mostra **decisão**, **laço** e **ferramenta**; o modelo 1 mostra **duas raias** e **seta de proveniência tracejada**.
- Os modelos **não** têm símbolo próprio para "responsável", "subprocesso" nem "documento de saída". Veja `SKILL.md`
  (seção "Mapeamento sem inventar padrão") para como representar isso **usando só o que existe**.
