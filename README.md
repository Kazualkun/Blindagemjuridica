# ⚖️ Blindagem Jurídica — skill para Claude Code

Skill que **audita e corrige** riscos jurídicos de sites, lojas virtuais, SaaS, landing pages e
apps sob a lei brasileira. Ela lê o código do seu projeto, encontra o que pode render multa,
reclamação no Procon ou processo, **corrige o que é técnico**, **gera os documentos legais sob
medida** e **pergunta** o que só você pode responder.

> **Aviso:** a skill reduz riscos de forma técnica e automatizada, mas **não substitui um(a)
> advogado(a)**. Documentos contratuais e casos de alto risco devem passar por revisão jurídica.

---

## O que ela verifica (17 itens)

| # | Item | O que procura e corrige |
|---|------|------------------------|
| 1 | **Política de privacidade** | Existe, está linkada e **bate com o código** (rastreadores, fornecedores e campos reais) |
| 2 | **Termos de uso** | Conteúdo mínimo, aceite no cadastro, cláusulas abusivas (CDC art. 51) |
| 3 | **Aviso de cookies** | Bloqueio prévio, botão rejeitar, categorias, revogação, consentimento tácito |
| 4 | **Política de reembolso** | Arrependimento de 7 dias (CDC art. 49), vício, frete, prazos de estorno |
| 5 | **Formulários na LGPD** | Aviso no ponto de coleta, checkbox pré-marcado, consentimentos agrupados, HTTPS |
| 6 | **Só dados necessários** | CPF, nascimento, gênero, dados sensíveis sem necessidade |
| 7 | **Scripts de tracking** | GA4, GTM, Meta Pixel, TikTok, Hotjar, Clarity… sem consentimento; Consent Mode v2 |
| 8 | **Acessibilidade** | `lang`, zoom, rótulos, botões de ícone, legendas, iframes (LBI art. 63, NBR 17225) |
| 9 | **Alt nas imagens** | Imagens sem `alt` ou com `alt` genérico |
| 10 | **Contraste** | Pares cor/fundo em CSS, inline e Tailwind, com **sugestão de cor que passa** |
| 11 | **Navegação por teclado** | `div` clicável, foco removido, `tabindex` positivo, skip link |
| 12 | **Sem avaliações falsas** | Avatares gerados, `faker`, `aggregateRating` fixo, prova social sem lastro |
| 13 | **Sem promessas falsas** | "Resultado garantido", cura, lucro, escassez falsa, contador com `Math.random()` |
| 14 | **Copyright das imagens** | Bancos pagos, hotlinks, metadados EXIF, fontes comerciais, marcas de terceiros |
| 15 | **Dados da empresa** | Razão social, CNPJ (valida dígitos, inclusive o **CNPJ alfanumérico**), endereço, contato |
| 16 | **Conformidade LGPD** | Canal do titular, encarregado, exclusão de conta, hash de senha, segredos expostos, IA, menores (ECA Digital) |
| 17 | **Riscos jurídicos** | Sorteios sem autorização, apostas, dark patterns, venda casada, e-mail sem descadastro, licenças copyleft |

## Como ela trabalha

1. **Reconhecimento** — roda um scanner (Python, sem dependências) e lê o projeto: stack, mapa
   de dados pessoais, rastreadores, fornecedores, documentos existentes.
2. **Uma rodada de perguntas** — só o que o código não responde: CNPJ, encarregado, prazos de
   troca, se os depoimentos são reais, origem das imagens…
3. **Auditoria** item a item, com severidade (🔴 crítico · 🟠 alto · 🟡 médio · 🔵 baixo),
   evidência `arquivo:linha` e base legal.
4. **Correções** — aplica direto o que é técnico (alt, contraste, teclado, banner de cookies,
   formulários, rodapé) e cria os documentos **no formato da sua stack** (página Next.js, Vue,
   HTML, WordPress…). Conteúdo de negócio (depoimentos, promessas, imagens) só muda com sua
   aprovação.
5. **Verificação** — roda o scanner de novo e o build/lint/testes do projeto.
6. **Relatório** — `AUDITORIA-JURIDICA.md` com placar antes/depois, o que foi feito, o que
   depende de você e as respostas guardadas para a próxima execução.

## Instalação

### Opção 1 — como plugin (recomendado)
No Claude Code:
```
/plugin marketplace add SEU-USUARIO/blindagem-juridica
/plugin install blindagem-juridica@blindagem-juridica
```

### Opção 2 — skill pessoal (todos os seus projetos)
```bash
git clone https://github.com/SEU-USUARIO/blindagem-juridica.git
# macOS / Linux
cp -r blindagem-juridica/skills/blindagem-juridica ~/.claude/skills/
# Windows (PowerShell)
Copy-Item -Recurse blindagem-juridica\skills\blindagem-juridica $HOME\.claude\skills\
```

### Opção 3 — skill do projeto (compartilhada com o time via git)
Copie `skills/blindagem-juridica` para `.claude/skills/` na raiz do seu projeto.

**Requisito:** Python 3.9+ para o scanner (opcional — sem Python, a skill faz a varredura com
as ferramentas de busca do Claude, só que mais devagar).

## Como usar

Com o projeto aberto no Claude Code:

```
/blindagem-juridica                 # auditoria completa + correções
/blindagem-juridica auditar         # só diagnóstico e relatório, sem alterar o projeto
/blindagem-juridica itens 3,7       # só cookies e rastreamento
/blindagem-juridica itens 8-11      # só acessibilidade
```

Ou peça em linguagem natural — a skill é acionada automaticamente:

> "Meu site está dentro da LGPD?"
> "Cria a política de privacidade e o banner de cookies da loja."
> "Vou lançar a landing page amanhã, tem algo que pode dar processo?"

(Instalada como plugin, o comando fica com o prefixo do plugin:
`/blindagem-juridica:blindagem-juridica`.)

### Usar só o scanner
```bash
python skills/blindagem-juridica/scripts/scan.py caminho/do/projeto
python skills/blindagem-juridica/scripts/scan.py caminho/do/projeto --format json --saida achados.json
python skills/blindagem-juridica/scripts/contraste.py "#999" "#fff"   # 2.85:1 → sugere #767676
```

Exemplo de saída (projeto de teste em `tests/fixtures/loja-problematica`):
```
### 3. Aviso e gestão de cookies
- 🔴 cookies-sem-consentimento Rastreadores/cookies não essenciais sem gestão de consentimento:
  Google Analytics, Meta Pixel (Facebook/Instagram), Hotjar. Precisam ser bloqueados até o
  aceite (LGPD arts. 7º I e 8º; Marco Civil art. 7º IX; Guia de Cookies da ANPD)
- 🟠 consentimento-tacito Consentimento tácito ('ao continuar navegando…') não é válido - `index.html:24`

### 13. Promessas e publicidade enganosa
- 🔴 prova-social-aleatoria Contador de pessoas/estoque/vagas gerado com Math.random() -
  informação falsa ao consumidor (CDC art. 37 e 66) - `index.html:70`
```

## O que vem na skill

```
skills/blindagem-juridica/
├── SKILL.md                     # fluxo de trabalho e regras
├── scripts/
│   ├── scan.py                  # varredura heurística dos 17 itens (Markdown ou JSON)
│   └── contraste.py             # razão de contraste WCAG + sugestão de cor
├── references/                  # requisitos legais, como auditar e como corrigir, por item
│   ├── base-legal.md            # LGPD, CDC, Decreto 7.962, LBI, Marco Civil, ECA Digital…
│   └── ...
└── templates/
    ├── politica-de-privacidade.md
    ├── termos-de-uso.md
    ├── politica-de-cookies.md
    ├── politica-de-reembolso.md
    ├── declaracao-de-acessibilidade.md
    ├── registro-de-operacoes.md       # ROPA (LGPD art. 37)
    ├── plano-resposta-incidentes.md   # Res. CD/ANPD 15/2024
    ├── relatorio-auditoria.md
    └── cookie-consent/                # banner de consentimento pronto (JS puro + CSS)
```

O **banner de consentimento** (`templates/cookie-consent/`) também pode ser usado sozinho: sem
dependências, bloqueia scripts e iframes até o aceite, tem "Rejeitar" no primeiro nível,
categorias, link permanente de preferências, Google Consent Mode v2 e navegação por teclado.

## Limitações

- O scanner é **heurístico**: aponta pistas com arquivo e linha; a skill confirma lendo o código.
  Conteúdo vindo de CMS/banco, tags configuradas dentro do Google Tag Manager e imagens sem
  metadados precisam de informação sua.
- O contraste é calculado quando cor e fundo estão no mesmo seletor/elemento; fundos herdados
  são revisados manualmente pela skill.
- Foco na legislação brasileira. Se você atende a União Europeia ou os EUA, a skill sinaliza
  GDPR/CCPA/ADA, mas recomenda análise específica.
- Normas mudam. A base legal foi revisada em outubro de 2026; contribuições de atualização são
  muito bem-vindas.

## Desenvolvimento

```bash
python -m unittest discover -s tests -v
```
Os testes usam dois sites de exemplo em `tests/fixtures/`: um cheio de problemas e um correto
(que não pode gerar achados graves). Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

[MIT](LICENSE). Os modelos de documentos podem ser usados e adaptados livremente, inclusive
comercialmente — lembrando que nenhum modelo dispensa a adaptação ao seu negócio.
#   B l i n d a g e m J u r - d i c a  
 