# Itens 8 a 11 — Acessibilidade (geral, alt, contraste, teclado)

**Base:** Lei 13.146/2015 (LBI) art. 63 — acessibilidade **obrigatória** em sites de empresas com
sede ou representação no Brasil e de órgãos públicos; CDC art. 6º parágrafo único; ABNT NBR
17225:2025 (baseada na WCAG 2.2, níveis A e AA); eMAG 3.1 (governo). Meta: **WCAG 2.2 nível AA**.

Riscos: ações civis públicas do Ministério Público, ações individuais por discriminação,
reclamações em Procon; nos EUA (se atende público americano) há milhares de processos/ano com
base na ADA. Overlays/widgets de acessibilidade **não** resolvem — o código precisa estar correto.

---

## Item 9 — Texto alternativo (WCAG 1.1.1)

**Regra:** toda imagem que transmite informação tem `alt` que comunica o mesmo que a imagem;
imagem decorativa tem `alt=""` (vazio, não ausente).

| Tipo de imagem | alt correto |
|----------------|------------|
| Foto de produto | Nome + característica visível relevante: "Caneca de cerâmica azul, 300 ml" |
| Logotipo no cabeçalho (link para home) | Nome da empresa: "Ateliê Exemplo — página inicial" |
| Ícone com texto ao lado | `alt=""` (o texto já diz) |
| Botão/link só com ícone | O que ele faz: "Abrir menu", "Carrinho (3 itens)" |
| Imagem com texto (banner de promoção) | O texto da imagem, inteiro |
| Gráfico/infográfico | Resumo da conclusão + dados em tabela/texto próximo |
| Foto de pessoa em depoimento | "Foto de Maria Souza" ou `alt=""` se o nome está ao lado |
| Decorativa (fundo, separador, ilustração genérica) | `alt=""` (ou CSS background) |
| SVG inline informativo | `role="img"` + `aria-label` ou `<title>` |
| SVG inline decorativo | `aria-hidden="true"` e `focusable="false"` |

Não use "imagem de", "foto de" sem necessidade, nome de arquivo, ou o mesmo alt para tudo.

**Como corrigir:** leia o contexto (texto ao redor, nome do produto, props do componente) para
escrever o alt. Em componentes (`<ProductCard image={...}>`), faça o alt vir de dados (`alt={produto.nome}`)
e torne a prop obrigatória no tipo. Para imagens vindas de CMS, garanta que o campo de alt
exista e seja usado. Se não for possível saber o que a imagem mostra (ex.: `hero.jpg` sem
contexto), **abra a imagem** com a ferramenta de leitura de arquivos para descrevê-la; se ainda
assim não der, liste no relatório.

---

## Item 10 — Contraste (WCAG 1.4.3 e 1.4.11)

- Texto normal: **≥ 4.5:1**. Texto grande (≥ 24px, ou ≥ 18.66px em negrito): **≥ 3:1**.
- Componentes e gráficos (bordas de inputs, ícones informativos, foco, estados): **≥ 3:1**.
- Placeholder também é texto (se transmite informação, 4.5:1). Texto desabilitado é exceção.
- Não transmitir informação só por cor (1.4.1): erro do formulário precisa de texto/ícone.

**Ferramenta:** `python SKILL_DIR/scripts/contraste.py "<cor texto>" "<cor fundo>"` → razão e
**sugestão da cor mais próxima no mesmo tom** que passa (use `--grande` para 3:1).

**Como auditar:** o scanner avalia pares cor/fundo em CSS, estilos inline e classes Tailwind
(paleta padrão). Ele não sabe o fundo herdado de elementos pais: revise manualmente os textos
cinza-claro (`#999`, `#aaa`, `text-gray-400`), textos sobre imagens/gradientes, botões
"fantasma", links, placeholders, rodapés escuros, badges e o banner de cookies. Verifique
também o **modo escuro**, se existir.

**Como corrigir:** altere o token/variável de design (`--color-muted`, `theme.extend.colors`) em
vez de cada ocorrência, mantendo a identidade visual (use a sugestão do script). Para texto sobre
imagem, aplique overlay escuro/claro ou sombra. Informe no relatório quais tokens mudaram.

---

## Item 11 — Navegação por teclado (WCAG 2.1.1, 2.1.2, 2.4.1, 2.4.3, 2.4.7, 2.4.11)

Tudo que funciona com mouse precisa funcionar com Tab / Shift+Tab / Enter / Espaço / Esc / setas.

Checklist e correções:
- **Elementos clicáveis não nativos** (`<div onClick>`, `<span @click>`, `<li onclick>`): troque
  por `<button type="button">` (ou `<a href>` se navega). Se não puder trocar, adicione
  `role="button"`, `tabIndex={0}` e tratador de Enter/Espaço.
- **`<a>` sem `href`** com clique → `<button>`.
- **Foco visível**: nunca `outline: none` sem substituto. Use:
  ```css
  :focus-visible { outline: 3px solid var(--cor-foco, #1d4ed8); outline-offset: 2px; }
  ```
  Tailwind: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`.
- **Link "Pular para o conteúdo"** como primeiro elemento focável:
  ```html
  <a href="#conteudo" class="pular-conteudo">Pular para o conteúdo</a> ... <main id="conteudo">
  ```
  ```css
  .pular-conteudo { position:absolute; left:-9999px; }
  .pular-conteudo:focus { left:1rem; top:1rem; z-index:1000; background:#fff; color:#000; padding:.5rem 1rem; }
  ```
- **Ordem de foco** lógica (segue a ordem visual); sem `tabindex` positivo.
- **Modais/menus**: foco vai para dentro ao abrir, fica preso no modal enquanto aberto, `Esc`
  fecha, foco volta ao botão que abriu; `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
  Prefira `<dialog>` nativo ou bibliotecas acessíveis (Radix, Headless UI, React Aria).
- **Menus suspensos/carrosséis/abas**: operáveis por teclado; `aria-expanded` nos botões de
  abrir; carrossel automático com botão de pausa.
- **Foco não escondido** atrás de cabeçalho fixo/banner de cookies (2.4.11): `scroll-padding-top`.
- **Sem armadilha de teclado** (iframes, editores, players).

---

## Item 8 — Acessibilidade geral (demais critérios essenciais)

- `<html lang="pt-BR">` (3.1.1); trechos em outro idioma com `lang` próprio.
- `<title>` único e descritivo por página (2.4.2).
- Estrutura semântica: um `<h1>`, hierarquia de títulos sem pular níveis, `<header>`, `<nav>`,
  `<main>`, `<footer>`, listas como `<ul>/<ol>` (1.3.1).
- **Formulários**: `<label for>` em todo campo (placeholder não é rótulo), campos obrigatórios
  indicados em texto, erros descritivos ligados ao campo (`aria-describedby`, `aria-invalid`),
  `autocomplete` adequado (`name`, `email`, `tel`, `postal-code`) (1.3.5, 3.3.1, 3.3.2).
- **Botões e links com nome acessível** (4.1.2, 2.4.4): texto visível ou `aria-label`; evitar
  "clique aqui"/"saiba mais" sem contexto.
- **Zoom**: não usar `maximum-scale=1` nem `user-scalable=no` (1.4.4); layout funciona a 200%
  e em 320px de largura (1.4.10).
- **Mídia**: vídeos com legenda (1.2.2) e, se informativos, transcrição; sem áudio automático
  (1.4.2); vídeos/carrosséis automáticos com pausa (2.2.2).
- **Movimento**: respeitar `prefers-reduced-motion` em animações grandes.
- **Alvos de toque** ≥ 24×24px (2.5.8).
- **CAPTCHA**: oferecer alternativa (áudio, verificação invisível) — CAPTCHA visual puro é item
  crítico na NBR 17225 (3.3.8).
- **Tempo limite** de sessão/oferta: avisar e permitir estender (2.2.1).
- `<iframe title="...">`.
- **Declaração de acessibilidade** (boa prática; `templates/declaracao-de-acessibilidade.md`):
  nível buscado, limitações conhecidas, canal para reportar barreiras. Ajuda a demonstrar boa-fé.
- **Libras**: VLibras (gratuito, do governo) ou Hand Talk podem complementar, não substituir.

## Testes recomendados
- Navegar o fluxo principal só com teclado (home → produto → formulário/checkout).
- Leitor de tela: NVDA (Windows), VoiceOver (macOS/iOS), TalkBack (Android).
- Automático (pega ~30–40% dos problemas): axe DevTools, Lighthouse, WAVE,
  `npx --yes @axe-core/cli <url>`, `npx --yes pa11y <url>`.
