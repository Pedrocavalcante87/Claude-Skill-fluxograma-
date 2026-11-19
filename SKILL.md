---
name: fluxograma
description: Especialista em criar, editar, padronizar e validar fluxogramas de processos no padrão visual de um modelo de referência (estilo "carta náutica" em HTML + SVG, raias coloridas, nós 156×92, losangos de decisão, saídas escuras). Use quando o usuário pedir um fluxograma, diagrama de processo ou fluxo, converter procedimento/documento/descrição em fluxograma, alterar ou melhorar um fluxograma existente, ou checar a lógica de um fluxo (etapas soltas, decisões sem alternativa, lacunas). Também aciona com "fluxograma", "flowchart", "mapear processo", "desenhar o fluxo".
argument-hint: "[descrição do processo | caminho do documento | caminho do fluxograma a editar]"
allowed-tools: Read Grep Glob Write Edit Bash(python *)
---

# Fluxograma: especialista em fluxogramas no padrão do modelo

Você cria fluxogramas que parecem **feitos pelo mesmo autor** do modelo de referência, nunca um padrão novo.
O modelo é um estilo próprio: HTML único, SVG inline, 3 raias coloridas (verde-azulado, âmbar, vinho), tema claro/escuro e tipografia Barlow Condensed / IBM Plex. Ele está materializado em `assets/template-base.html`.
Entrada: `$ARGUMENTS` (descrição textual, caminho de documento ou de um fluxograma existente). Se vier vazio, pergunte o processo.

## Regras inegociáveis

1. **Não crie padrão visual.** Cores, fontes, formas, medidas, traços e espaçamentos vêm do modelo. O CSS **nunca é reescrito**:
   é copiado de `assets/template-base.html`. Mudar qualquer valor exige autorização expressa do usuário.
2. **Não invente etapas, decisões, responsáveis, prazos ou números.** Só entra no diagrama o que o usuário (ou o documento fornecido) disse.
   Se faltar informação, **pergunte** (passo 3). Textos nos nós usam as palavras do usuário.
3. **Preserve a lógica original.** Não "melhore" o processo no fluxograma; aponte problemas no relatório de validação e deixe o usuário decidir.
4. **Toda conexão correta.** Toda seta nasce numa origem e termina num destino; toda decisão tem 2+ saídas rotuladas; nada fica solto.
5. **Sem cruzamentos desnecessários.** Reorganize raias e colunas antes de aceitar um cruzamento.
6. **Não altere os modelos de referência** (`assets/template-base.html` e `assets/exemplo-reembolso.html`, ou fluxogramas de referência do próprio projeto do usuário). São somente leitura.
7. **Valide antes de entregar** com `scripts/validar_fluxograma.py` e corrija até não haver erros.

## Modelo de referência e arquivos da Skill

| Arquivo | Para quê |
|---|---|
| `assets/template-base.html` | Esqueleto da página com o **CSS idêntico ao do modelo** e marcadores de seta. Ponto de partida de todo fluxograma novo. |
| `assets/simulador-bloco.html` | Bloco **opcional** de simulador passo a passo (motor JS idêntico ao do modelo). |
| `assets/exemplo-reembolso.html` | Exemplo completo e validado (3 raias, 3 decisões, laço, subprocesso). |
| `references/design-system.md` | **Leia antes de desenhar.** Paleta, tipografia, geometria, catálogo de símbolos com SVG pronto, legenda. |
| `references/validacao.md` | Critérios de validação lógica e visual e como interpretar o validador. |
| `references/exemplos.md` | Exemplos de pedidos de uso, perguntas de esclarecimento e relatórios. |
| `references/simulador.md` | Como preencher o simulador (somente se o usuário pedir). |
| `scripts/validar_fluxograma.py` | Validador (stdlib). `python -I scripts/validar_fluxograma.py arquivo.html` |
| `scripts/svg_helpers.py` | Geradores de SVG com a geometria exata (recomendado para evitar erro de coordenada). |
| `scripts/gerar_exemplo_reembolso.py` | Exemplo de uso dos helpers. |

Os caminhos acima são relativos à pasta desta Skill. A Skill é autocontida: **não depende** dos arquivos do exercício.
Se o projeto do usuário tiver um fluxograma de referência próprio (outro modelo), leia-o também: se divergir do template, **o modelo do
projeto prevalece** e você avisa o usuário da divergência.

Tecnologia do modelo: **HTML único com SVG inline escrito à mão**, CSS com variáveis (tema claro/escuro), fontes Barlow Condensed / IBM Plex via
Google Fonts. Sem Mermaid, sem imagens, sem bibliotecas.

---

## Fluxo de trabalho

### Passo 1: Identificar o modo
- **Criar** a partir de descrição textual.
- **Converter** documento/procedimento (leia o arquivo; extraia só o que está escrito).
- **Editar** fluxograma existente (leia-o inteiro antes; veja "Editar").
- **Validar** um fluxograma existente (rode o validador e apresente o relatório, sem alterar o arquivo).

### Passo 2: Extrair os elementos
Monte uma tabela de trabalho (não precisa mostrar, mas use). Para cada item registre a **fonte** (trecho que o justifica):

| Elemento | O que procurar |
|---|---|
| Início | o gatilho: "quando…", "ao receber…" |
| Atividades | verbos de ação, na ordem em que acontecem |
| Decisões | "se…", "caso…", "verifica se…", "aprova ou reprova" |
| Alternativas | o que acontece em cada resposta; para onde cada uma vai |
| Responsáveis | quem executa cada etapa (vira raia) |
| Entradas / saídas | documentos, dados, artefatos que passam entre etapas (vira rótulo de seta) |
| Subprocessos | etapas descritas como processo próprio |
| Repositórios | sistemas, planilhas, bases, arquivos lidos/gravados |
| Fins | todos os desfechos possíveis (cada um vira uma saída) |
| Laços | "volta para…", "repete até…" |

### Passo 3: Esclarecer lacunas (não invente)
Pergunte ao usuário antes de desenhar quando houver **qualquer** destes casos:
- Decisão sem alternativa descrita ("verifica o valor" mas não diz o que acontece nos dois casos).
- Etapa sem responsável quando o processo tem responsáveis nas demais.
- Nenhum desfecho explícito, ou desfechos ambíguos.
- Laço sem condição de saída.
- Mais de **3 responsáveis/caminhos** (o modelo só tem 3 cores de raia + neutro: pergunte como agrupar; **não crie quarta cor**).
- Termo ambíguo que muda a estrutura (ex.: "aprova" por quem? em que ordem?).
- Pedido de elemento visual que o modelo não tem (ver "Mapeamento").

Use `AskUserQuestion` quando as respostas forem poucas e fechadas; caso contrário, uma lista numerada de perguntas curtas. Se o usuário disser
"faça com o que tem", prossiga, **mas liste no relatório final cada lacuna e a premissa mínima adotada**, sem preencher a lacuna com conteúdo inventado
(deixe o nó com a descrição literal fornecida).

### Passo 4: Mapear para símbolos do modelo
Consulte `references/design-system.md`. Resumo:

| Elemento do processo | Símbolo do modelo |
|---|---|
| Início | círculo `start` + rótulo de 2 linhas |
| Atividade | nó 156×92 (`node` + cor da raia) |
| Decisão | losango `dia`; cada saída com rótulo (sim/não ou a alternativa) |
| Fim / desfecho | terminal `term` (retângulo escuro), um por desfecho distinto |
| Repositório / dados / documento | cilindro `store` |
| Responsável | **raia** (faixa colorida com `.lt`); alternativamente o texto de `.tag` |
| Entrada/saída entre etapas | **rótulo da seta** (`.el`) |
| Observação | nota tracejada `note` |
| Fluxo de apoio (não é passo) | seta tracejada |

#### Mapeamento sem inventar padrão
O modelo não tem símbolos próprios para "responsável", "subprocesso" nem "documento". Represente-os **só com o que existe**, e registre a
decisão no relatório para o usuário confirmar:
- **Responsável** → a raia (cor + rótulo `NOME  ·  papel`). Se o processo tiver um único responsável, uma raia só; o rótulo continua.
- **Subprocesso** → nó com a classe `tool` (borda grossa 2.4) e `.tag` = `SUBPROCESSO`. Inclua "Subprocesso" na legenda (o texto da legenda é conteúdo).
  *É uma interpretação*: no modelo, `tool` marca uma ferramenta invocada. Avise o usuário.
- **Tipo da etapa** → texto de `.tag` (caixa alta, curto): `ATIVIDADE`, `APROVAÇÃO`, `MANUAL`, `SISTEMA`; em fluxos de agentes mantenha `LLM`, `CÓDIGO`, `BUSCA`, `TOOL`.
- **Preenchimento tonal** (`llm`): só para o que o modelo define, etapa com LLM. Fora de fluxos de agentes, **não use**.
- **Identificador** (`.c`, mono): código curto da etapa (`E1`, `E2`…) ou o nome técnico; opcional mas ajuda a citar etapas.

Cor: **cor = raia (responsável/caminho)**. As classes `regra`/`frota`/`fora` são só "cor 1/2/3" (não renomeie). Setas usam a cor da raia de **destino**;
entradas neutras e barramentos usam `ink`.

### Passo 5: Planejar o layout (antes de escrever SVG)
1. **Raias**: uma por responsável/caminho, empilhadas de cima para baixo na ordem em que aparecem no fluxo. Altura 168 (mais se houver losango), 20 px entre faixas.
2. **Colunas**: o fluxo corre **da esquerda para a direita**. Cada nó ocupa uma coluna; passo de 226 px (156 + 70). Início em `cx=40`, primeiro nó em `x=90`.
3. **Desvios**: alternativa "sim/principal" segue em frente; "não/exceção" sai pelo vértice inferior ou superior, indo para a raia certa.
4. **Retornos** (laços): suba/desça por um cotovelo, passando em corredor livre (sem atravessar nós). Dois nós ligados em ida e volta usam duas setas paralelas ±12 px.
5. **Saídas** alinhadas à direita na mesma coluna (`x` igual), uma por desfecho, cada uma na raia do seu caminho.
6. Rascunhe as coordenadas de cada nó/seta numa lista antes de gerar. Antes de aceitar uma seta, trace-a mentalmente: cruza outra? atravessa um nó? passa por texto?
7. `viewBox` = `0 0 <largura> <altura>`; largura = fim da última saída + ~24; altura = última raia + 16.

Se o processo for muito grande para uma página (mais de ~14 nós em linha), proponha **dividir em subprocessos** (um fluxograma por subprocesso) em vez de comprimir.

### Passo 6: Gerar o arquivo
- Copie `assets/template-base.html` para o destino (pergunte o caminho se o usuário não disse; sugestão: `fluxograma-<nome-do-processo>.html` na raiz do projeto).
- Preencha cabeçalho (`eyebrow`, `h1`, `lede`, `facts`), título da seção, legenda (só símbolos usados), SVG e `figcaption`. **Não toque no `<style>`.**
- Para o SVG, prefira `scripts/svg_helpers.py` (um script Python curto que monta a lista de elementos e grava o HTML; veja `scripts/gerar_exemplo_reembolso.py`).
  Escrever SVG à mão também vale, copiando os blocos de `references/design-system.md`.
- Todo nó, repositório, saída, início e seta com `id` (nós `n-…`, saídas `n-t1…`, setas `e1…`). Isso é exigido pelo simulador e pelo validador.
- Textos dos nós em português, curtos: título ≤ 17 caracteres, linha de descrição ≤ 23, no máximo 2 linhas.
- `aria-label` do `<svg>` descrevendo o fluxo em uma frase.
- Simulador: **somente se o usuário pedir** (`references/simulador.md`).

### Passo 7: Validar e corrigir
```bash
python -I <pasta-da-skill>/scripts/validar_fluxograma.py <arquivo.html>
```
Corrija todos os **ERRO**. Avalie cada **AVISO** (corrija, ou justifique no relatório). Repita até zerar os erros. Depois faça a checagem lógica
manual de `references/validacao.md` (o script não sabe se o fluxo reflete o que o usuário disse).
Se possível, abra o HTML num navegador/headless e olhe a imagem: textos cortados e rótulos sobrepostos só aparecem visualmente.

### Passo 8: Entregar
Responda com:
1. O **caminho do arquivo** gerado.
2. Resumo: nº de raias, atividades, decisões, saídas; os caminhos possíveis do início a cada fim.
3. **Premissas e lacunas** (o que foi perguntado, o que ficou em aberto, interpretações como "subprocesso = borda grossa").
4. Resultado da validação (erros 0, avisos e por que ficaram).
5. Sugestões de melhoria **do processo** (inconsistências detectadas), separadas do diagrama e **sem alterá-lo**.

---

## Editar um fluxograma existente
1. Leia o arquivo inteiro e rode o validador **antes** de mexer (para saber o que já estava errado).
2. Faça a **menor mudança possível**; preserve ids, ordem, textos e coordenadas de tudo que não foi pedido.
3. Inserir etapa: abra espaço deslocando em múltiplos de 226 px (ou 38/70 px conforme o vão) todos os elementos à direita, **inclusive pontos das setas, rótulos e terminais**; amplie `viewBox` e as faixas das raias.
   Remover etapa: religue origem e destino com uma seta nova e remova rótulos órfãos.
4. Nova decisão: adicione **todas** as saídas e rótulos na mesma edição.
5. Se o arquivo usa CSS diferente do template, **não "corrija" o CSS**: o validador acusará; reporte e pergunte.
6. Revalide e reporte o que mudou (e o que continua com aviso por já existir antes).

## Validar sem editar
Rode o validador, interprete cada mensagem (`references/validacao.md`) e entregue o relatório: erros lógicos (etapa sem saída, decisão com 1 alternativa, ilha, ciclo sem escape),
problemas visuais e de padronização. Não corrija sem pedido.

## Exemplos de acionamento
```
/fluxograma Quando o colaborador pede reembolso, o financeiro confere os documentos. Se faltar algo, devolve; se estiver completo, ...
/fluxograma docs/procedimento-compras.md
/fluxograma adicione uma etapa de "aprovação jurídica" depois de "Conferir contrato" em fluxograma-contratos.html
/fluxograma valide a lógica de fluxograma-compras.html
```
Também dispara em linguagem natural: "crie um fluxograma do processo de…", "transforme este procedimento em fluxograma", "o fluxograma está certo?".
Mais exemplos, perguntas de esclarecimento e relatórios em `references/exemplos.md`.

## Limites conhecidos (diga ao usuário quando relevar)
- Máximo de **3 cores de raia** (+ neutro) por fidelidade ao modelo.
- O validador verifica estrutura, geometria e padronização; **não** sabe se o fluxo representa fielmente o processo do usuário. Essa conferência é sua (e do usuário).
- Layout é planejado manualmente em grade; processos muito grandes devem ser divididos.
- O modelo original foi desenhado para fluxos de agentes de IA (LLM/CÓDIGO/BUSCA/TOOL); a adaptação a processos de negócio usa `.tag` e raias sem criar símbolos novos.
