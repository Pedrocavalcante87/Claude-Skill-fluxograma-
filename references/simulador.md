# Simulador passo a passo (opcional)

O modelo traz um **simulador**: o usuário digita/escolhe uma entrada, o fluxograma "acende" o caminho percorrido, e um painel mostra o passo atual,
o estado e o trace. **Só inclua se o usuário pedir.** O motor JS e o CSS são os do modelo e **não mudam**; muda apenas `SIM_CONFIG`.

## Como montar
1. Abra `assets/simulador-bloco.html`. Parte 1 (marcação `.sim`) vai **dentro da `<section>`, antes de `<div class="figwrap">`**.
2. Parte 2 (`<script>`) vai antes de `</body>`.
3. Preencha `window.SIM_CONFIG`:

```js
window.SIM_CONFIG = {
  fields: [['chave','rótulo exibido'], ...],          // campos do "estado" exibidos no painel
  presets: [{tag:'ROTULO', lane:'regra|frota|fora', text:'entrada de exemplo'}, ...],   // chips clicáveis (pelo menos 1)
  build: function(q){                                   // q = texto digitado; devolve a lista de passos
    var S = [];
    S.push({
      n:['n-id-do-no'],            // ids dos nós/repositórios/terminais/início a acender
      e:['e1'],                    // ids das setas a animar
      node:'nome na trace',        // texto curto na lista de trace
      t:'Título do passo',         // painel "Passo atual"
      d:'Descrição (aceita <code> e <b>)',
      llm:1,                       // opcional: conta chamada de LLM e mostra o selo LLM
      tool:1,                      // opcional: selo TOOL
      patch:{chave:'valor'},       // opcional: atualiza campos do estado
      add:['item']                 // opcional: acrescenta ao campo 'fontes' (acumulador)
    });
    return S;                      // ramificações: use if/else para devolver passos de caminhos diferentes
  }
};
```

## Regras
- **Todo id referenciado em `n` e `e` precisa existir no SVG** (o motor ignora ids inexistentes em silêncio, e o passo fica sem destaque).
- Para ramos (decisões), `build` decide o caminho a partir de `q` com regras explícitas e mostra só os nós do caminho escolhido.
- **Não invente comportamento**: os passos reproduzem o que o usuário descreveu. Valores simulados vêm dos dados que o usuário forneceu.
- Barramentos (`bus1…`) podem ser listados em `e` junto com a seta de ramo.
- Mantenha os textos fixos do bloco ("Executar", "Próximo passo", "Reiniciar", "Passo atual", "Estado do grafo", "Trace") ou adapte apenas o **conteúdo**
  (ex.: "Pergunta do operador" → "Pedido do colaborador"); nunca estilos.
- `fields` deve ter pelo menos um campo; `presets` ao menos um item (o motor lê `presets[0]`).
- Dica de verificação: abra a página, clique em cada chip e confira se o caminho acende do início ao fim sem passos "mudos".

## Estados visuais (já no CSS)
`.running` no `<svg>`; `.seen` e `.active` nos elementos. Não escreva CSS novo.
