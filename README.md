# Skill `fluxograma`

Skill do [Claude Code](https://claude.com/claude-code) que cria, edita, padroniza e valida **fluxogramas de processos** em um único arquivo HTML com SVG inline: raias coloridas, losangos de decisão, saídas escuras, tema claro/escuro.

## O que ela faz

- **Criar** um fluxograma a partir de uma descrição em texto.
- **Converter** um documento ou procedimento em fluxograma.
- **Editar** um fluxograma existente com a menor mudança possível.
- **Validar** a lógica (etapas soltas, decisões sem alternativa, ciclos sem saída) e o padrão visual, com um validador em Python.
- **Não inventa** etapas, responsáveis ou prazos: se faltar informação, ela pergunta.

## Instalação

Clone o repositório direto na pasta de skills do seu projeto (ou em `~/.claude/skills/` para usar em todos os projetos):

```bash
git clone <URL-DO-REPOSITORIO> .claude/skills/fluxograma
```

Depois reinicie a sessão do Claude Code. A skill aparece como `/fluxograma`.

## Uso

```
/fluxograma Quando o colaborador pede reembolso, o financeiro confere os documentos. Se faltar algo, devolve; se estiver completo, aprova.
/fluxograma docs/procedimento-compras.md
/fluxograma valide a lógica de fluxograma-compras.html
```

Também dispara em linguagem natural: "crie um fluxograma do processo de…".

## Conteúdo

| Pasta | Conteúdo |
|---|---|
| `SKILL.md` | Instruções da skill |
| `assets/` | Template base (CSS do padrão visual), exemplo completo e bloco opcional de simulador passo a passo |
| `references/` | Design system, critérios de validação, exemplos de uso |
| `scripts/` | Validador e geradores de SVG (somente biblioteca padrão do Python 3) |

Para ver o resultado, abra [assets/exemplo-reembolso.html](assets/exemplo-reembolso.html) no navegador. Validador isolado:

```bash
python -I scripts/validar_fluxograma.py meu-fluxograma.html
```

## Observações

- Requer Python 3 (apenas para o validador e os helpers). Sem outras dependências.
- As fontes (Barlow Condensed, IBM Plex) são carregadas do Google Fonts; sem internet o navegador usa fontes padrão.
- O padrão visual tem no máximo 3 cores de raia, por fidelidade ao modelo original.
- A skill e a documentação estão em português.

## Licença

[MIT](LICENSE): livre para usar, copiar, modificar e redistribuir, inclusive comercialmente.
