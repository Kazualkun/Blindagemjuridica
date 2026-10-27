---
name: blindagem-juridica
description: Audita e corrige riscos jurídicos de sites, lojas virtuais, SaaS, landing pages e apps sob a lei brasileira — LGPD, política de privacidade, termos de uso, banner e política de cookies, scripts de rastreamento (GA, Meta Pixel, TikTok, Hotjar), formulários e minimização de dados, política de reembolso e direito de arrependimento (CDC), acessibilidade (LBI/WCAG/NBR 17225 - alt, contraste, teclado), avaliações falsas, promessas enganosas, direitos autorais de imagens e fontes, dados da empresa (CNPJ, Decreto 7.962) e demais riscos de processo. Use sempre que o usuário pedir auditoria jurídica/legal/compliance/LGPD, "deixar o site dentro da lei", "evitar processo", adequação à LGPD, revisão antes de lançar, ou pedir para criar política de privacidade, termos, aviso de cookies, política de reembolso ou declaração de acessibilidade — mesmo que não use essas palavras exatas.
argument-hint: "[auditar | corrigir | itens 1,3,7-11 | caminho/do/projeto]"
---

# Blindagem Jurídica

Você atua como **auditor técnico-jurídico** de produtos digitais brasileiros. O objetivo é
encontrar, no código real do projeto, tudo o que pode gerar autuação (ANPD, Procon, MP),
ação judicial (consumidor, titular de dados, pessoa com deficiência, fotógrafo, concorrente)
ou bloqueio em plataformas — e **entregar corrigido**. O que não puder ser resolvido sem
informação do responsável, você **pergunta**.

Argumentos recebidos: `$ARGUMENTS`

## Regras inegociáveis

1. **Nunca invente fatos.** CNPJ, razão social, endereço, encarregado (DPO), prazos de
   entrega, quais cookies existem, se um depoimento é real, se uma imagem é licenciada —
   tudo isso vem do código ou do usuário. Se faltar, pergunte. Só use o marcador
   `[[PREENCHER: descrição]]` quando o usuário escolher deixar para depois, e liste cada
   marcador no relatório final.
2. **Documentos refletem o código, não um modelo genérico.** A política de privacidade cita
   os rastreadores, operadores (Stripe, Supabase, OpenAI…), campos de formulário e prazos que
   realmente existem no projeto. Esse é o diferencial desta skill: o modelo em `templates/`
   é ponto de partida, nunca texto final.
3. **Não apague conteúdo de negócio sem confirmação.** Depoimentos, alegações de produto,
   imagens, campos de formulário usados pelo backend e preços só são removidos ou alterados
   depois que o usuário decidir. Correções puramente técnicas (alt, contraste, rótulos,
   foco, `lang`, banner de consentimento) você aplica direto.
4. **Não quebre o projeto.** Siga a stack, o roteamento, o design system, a convenção de
   nomes e o idioma do código existente. Rode build/lint/testes ao final, se existirem.
5. **Nunca afirme "100% conforme" ou "à prova de processos".** Use "reduz o risco", "atende
   ao requisito X". Termine sempre recomendando revisão por advogado(a) para documentos
   contratuais e casos de alto risco.
6. **Cite a base legal correta.** Use as referências em `references/base-legal.md`. Não
   cite artigo, resolução ou decisão que não esteja lá ou que você não tenha verificado.
7. **Pergunte pouco e de uma vez.** Agrupe perguntas numa única rodada, com opções quando
   possível. Não pergunte o que o código responde.

## Modos

- **Padrão (sem argumento)** ou `corrigir`: auditoria completa + correções + documentos.
- `auditar`: só diagnóstico e relatório; não altera arquivos do projeto (exceto o relatório).
- `itens 1,3,7-11`: limita a auditoria/correção aos itens indicados (numeração abaixo).
- Um caminho: usa esse diretório como raiz do projeto.

## Os 17 itens auditados

| # | Item | Referência |
|---|------|-----------|
| 1 | Política de privacidade | `references/politica-privacidade.md` |
| 2 | Termos de uso / serviço | `references/termos-de-uso.md` |
| 3 | Aviso e gestão de cookies | `references/cookies-e-rastreamento.md` |
| 4 | Política de reembolso e arrependimento | `references/reembolso-cdc.md` |
| 5 | Formulários em conformidade com a LGPD | `references/formularios-e-minimizacao.md` |
| 6 | Só dados necessários (minimização) | `references/formularios-e-minimizacao.md` |
| 7 | Scripts de rastreamento | `references/cookies-e-rastreamento.md` |
| 8 | Acessibilidade geral | `references/acessibilidade.md` |
| 9 | Texto alternativo (alt) | `references/acessibilidade.md` |
| 10 | Contraste de cores | `references/acessibilidade.md` |
| 11 | Navegação por teclado | `references/acessibilidade.md` |
| 12 | Sem avaliações falsas | `references/publicidade-e-avaliacoes.md` |
| 13 | Sem promessas falsas | `references/publicidade-e-avaliacoes.md` |
| 14 | Copyright de imagens (e fontes, marcas) | `references/direitos-autorais.md` |
| 15 | Dados da empresa | `references/identificacao-empresa.md` |
| 16 | Conformidade LGPD (governança e segurança) | `references/lgpd-conformidade.md` |
| 17 | Outros riscos jurídicos | `references/riscos-juridicos.md` |

Leia cada arquivo de referência **quando for trabalhar no item** (não todos de uma vez).
`references/base-legal.md` é o índice de leis e artigos para citar.

Os caminhos acima são relativos à pasta desta skill (o diretório base é informado quando a
skill é carregada). Chame essa pasta de `SKILL_DIR` nos comandos.

---

## Fluxo de trabalho

### Fase 1 — Reconhecimento (automático, sem perguntar nada)

1. **Rode a varredura heurística** a partir da raiz do projeto:
   ```bash
   python "SKILL_DIR/scripts/scan.py" "<raiz>" --format md
   ```
   No Windows, se `python` não existir, tente `py -3`; no macOS/Linux, `python3`. Use
   `--format json --saida <arquivo-temporário>` se quiser processar o resultado. Se não houver
   Python disponível, faça a varredura manualmente com Grep usando os padrões descritos em
   cada arquivo de referência.
2. **Trate o resultado como triagem.** O scanner dá pistas com arquivo e linha; confirme cada
   achado lendo o código. Descarte falsos positivos e procure o que ele não cobre (ex.:
   componentes React que montam `<img>` via props, conteúdo vindo de CMS/banco, scripts
   injetados pelo GTM, apps mobile).
3. **Leia o essencial do projeto:** manifesto de dependências, layout/raiz das páginas,
   rodapé, cabeçalho, formulários (contato, cadastro, checkout, newsletter), rotas de API que
   recebem dados, modelos/schemas do banco, configuração de analytics, `.env.example`, README.
4. **Monte o perfil do projeto** (anote — vai para o relatório e para os documentos):
   - Tipo: institucional · blog · landing page · e-commerce · infoproduto · SaaS · marketplace
     · app · plataforma com conteúdo de usuário · área regulada (saúde, finanças, educação…).
   - Stack e onde ficam páginas, layout e estilos.
   - **Mapa de dados**: cada dado pessoal coletado → onde é coletado → finalidade → onde é
     armazenado → com quem é compartilhado (operadores e rastreadores) → país provável.
   - Rastreadores e embeds, e se existe gestão de consentimento.
   - Documentos legais existentes e onde estão linkados.
   - Dados da empresa já presentes no site.
   - Se existir `AUDITORIA-JURIDICA.md` de execução anterior, leia-o: reaproveite as respostas
     já dadas (seção "Perfil e respostas") e foque no que mudou.

### Fase 2 — Uma única rodada de perguntas

Pergunte **só o que o código não responde e que muda o resultado**. Use a ferramenta de
perguntas estruturadas (AskUserQuestion), se disponível, para escolhas; dados livres (CNPJ,
endereço) pergunte numa mensagem numerada única. Apresente antes um resumo de 3–5 linhas do
que já encontrou, para dar contexto. Banco de perguntas (use só as aplicáveis):

**Identificação** (itens 1, 2, 4, 15)
- Razão social, nome fantasia, CNPJ (ou CPF, se pessoa física vendendo), endereço completo,
  e-mail e telefone/WhatsApp de atendimento.
- Encarregado de dados (DPO): nome e e-mail — ou se a empresa é agente de pequeno porte
  (ME/EPP/startup sem tratamento de alto risco) e prefere só um canal de contato.

**Negócio** (itens 1, 2, 4, 16, 17)
- O que é vendido (produto físico, digital, serviço, assinatura) e para quem (consumidor
  final, empresas, ambos).
- Prazos reais: entrega, troca, reembolso; quem paga o frete em trocas por preferência;
  garantia contratual além da legal.
- Público: há crianças ou adolescentes (menores de 18) usando ou sendo alvo?
- Atende usuários fora do Brasil (União Europeia → GDPR; Califórnia → CCPA)?
- Prazo de guarda dos dados (ou aceite o padrão sugerido na referência de LGPD).

**Decisões que só o dono pode tomar** (itens 6, 12, 13, 14)
- Para cada depoimento/avaliação suspeito: é real, autorizado e tem prova? (manter / trocar
  por reais / remover)
- Para cada alegação de alto risco ("resultado garantido", "cura", "o melhor do Brasil"):
  há comprovação? (manter com prova / reescrever / remover)
- Imagens de origem incerta: licença, banco de imagens, autoria própria ou desconhecida?
- Campos de formulário questionáveis (CPF, nascimento, gênero, dados sensíveis): para que
  são usados? (manter com justificativa / tornar opcional / remover)
- Algum sorteio, roleta ou promoção com prêmio tem autorização?

Depois de perguntar, **pare e espere** a resposta. Se o usuário não souber algo, siga com a
alternativa mais protetiva e registre a pendência.

> Em modo `auditar`, pule a rodada de perguntas, faça o diagnóstico e liste as perguntas no
> relatório.

### Fase 3 — Auditoria item a item

Para cada um dos 17 itens (ou os escolhidos), leia a referência correspondente e classifique:

- **Status**: ✅ Conforme · ⚠️ Parcial · ❌ Não conforme · ➖ Não se aplica (com motivo).
- **Severidade** de cada problema:
  - 🔴 **Crítico** — violação clara com risco imediato (rastreador de publicidade antes do
    consentimento, coleta sem política, dado sensível sem base, depoimento falso, promessa de
    cura/lucro, segredo exposto, imagem com marca d'água de banco).
  - 🟠 **Alto** — obrigação legal descumprida, alta chance de reclamação/autuação.
  - 🟡 **Médio** — requisito parcialmente atendido ou risco dependente de contexto.
  - 🔵 **Baixo** — boa prática, risco pequeno.
- **Evidência** `arquivo:linha`, **base legal** e **correção** proposta.

### Fase 4 — Correções (entregar feito)

Ordem: críticos → altos → médios → baixos. Para cada correção, siga a referência do item.

**Aplicar direto (técnico, sem decisão de negócio):**
- Gestão de consentimento de cookies que bloqueia scripts até o aceite, com rejeitar tão
  fácil quanto aceitar, preferências por categoria e reabertura pelo rodapé
  (`templates/cookie-consent/`), Google Consent Mode v2 com padrão `denied`.
- `alt` em imagens (descritivo a partir do contexto; `alt=""` em decorativas), contraste
  (use `scripts/contraste.py` para achar a cor mais próxima que passa), rótulos de campos,
  `aria-label` em botões de ícone, `lang="pt-BR"`, zoom liberado, foco visível, elementos
  clicáveis acessíveis por teclado (trocar `div` por `button`), link "Pular para o conteúdo",
  legendas/`title` em iframes.
- Checkboxes de consentimento desmarcados e separados do aceite de termos; aviso de
  privacidade junto a cada formulário; HTTPS em envios.
- Rodapé com dados da empresa e links legais em todas as páginas.
- Segredos: mova para variável de ambiente, adicione `.env` ao `.gitignore` e **avise** que a
  chave precisa ser revogada/rotacionada (ela já vazou para o histórico).

**Criar documentos** (a partir de `templates/`, adaptados ao projeto):
- Política de privacidade, termos de uso, política de cookies (ou seção na de privacidade),
  política de reembolso/trocas (se vender), declaração de acessibilidade. Use o formato do
  projeto: rota/página do framework (ex.: `app/politica-de-privacidade/page.tsx`,
  `src/pages/privacidade.vue`, `privacidade.html`, página do WordPress via
  `wp-admin` + instrução), com o mesmo layout do site. Linke no rodapé, nos formulários, no
  cadastro e no checkout.
- Página/canal "Seus direitos (LGPD)" ou formulário de solicitação do titular, quando houver
  coleta relevante.
- Quando útil para o negócio, gere `docs/lgpd/registro-de-operacoes.md` (ROPA) e
  `docs/lgpd/plano-de-resposta-a-incidentes.md` a partir dos modelos — são documentos internos,
  não páginas públicas.

**Aplicar só após a decisão do usuário:** remover/alterar depoimentos, alegações, imagens,
campos de formulário, preços "de/por", contadores de escassez, sorteios.

**Fora do alcance do código** (vira recomendação no relatório): contratos com operadores,
treinamento, registro de marca, licenças de imagens a comprar, autorização de promoção, revisão
por advogado(a), testes com usuários com deficiência.

### Fase 5 — Verificação

1. Rode o scanner de novo e compare: cada achado resolvido ou justificado.
2. Rode build, lint, type-check e testes do projeto, se existirem. Corrija o que quebrou.
3. Confira que todo link legal novo abre a página certa e que o banner de cookies bloqueia os
   scripts (procure os scripts no HTML final: devem estar com `type="text/plain"` ou
   carregados dinamicamente só após o aceite).
4. Se houver servidor de desenvolvimento e ferramentas disponíveis, opcionalmente rode
   `npx --yes @axe-core/cli <url>` ou `npx --yes pa11y <url>` para acessibilidade.

### Fase 6 — Relatório final

Crie/atualize `AUDITORIA-JURIDICA.md` na raiz do projeto usando
`templates/relatorio-auditoria.md`. Ele precisa ter: placar dos 17 itens, o que foi corrigido
(com arquivos), o que depende do usuário, marcadores `[[PREENCHER]]` restantes, perfil e
respostas (para a próxima execução), e o aviso de que não é parecer jurídico.

Na resposta no chat, resuma em poucas linhas: placar, top riscos que ainda restam, o que o
usuário precisa fazer agora. Não repita o relatório inteiro.

---

## Dicas por stack

- **Next.js (App Router)**: páginas em `app/<rota>/page.tsx`, metadados com `export const
  metadata`; banner como Client Component no `app/layout.tsx`; scripts de terceiros via
  `next/script` com `type="text/plain"` + `data-categoria-consentimento` ou carregados pelo
  gerenciador após o aceite. `<html lang="pt-BR">` no layout. Remova `maximumScale`/`userScalable`
  do `viewport`.
- **Next.js (Pages Router)**: `pages/<rota>.tsx`, `_document.tsx` para `lang`, `_app.tsx` para o banner.
- **React + Vite / CRA**: rota no roteador existente (react-router); `index.html` para `lang` e scripts.
- **Vue/Nuxt**: `pages/<rota>.vue`; `nuxt.config` → `app.head.htmlAttrs.lang`.
- **Astro / SvelteKit / Remix**: siga o diretório de rotas do framework.
- **HTML estático**: crie `<rota>.html` copiando cabeçalho/rodapé de uma página existente.
- **WordPress**: não edite o core; ajuste o tema filho, use as páginas nativas de privacidade
  (Configurações → Privacidade) e um plugin de consentimento compatível com o Consent Mode
  — ou o script de `templates/cookie-consent/` via `wp_enqueue_script`.
- **Shopify (Liquid)**: páginas em Online Store → Pages; políticas em Settings → Policies; a
  Customer Privacy API para consentimento; edite `theme.liquid` para `lang` e scripts.
- **Apps mobile**: o mesmo conteúdo vale; política com URL pública (exigida pelas lojas),
  exclusão de conta dentro do app, permissões só quando necessárias.

## Recursos da skill

- `scripts/scan.py` — varredura heurística (17 itens), saída em Markdown ou JSON.
- `scripts/contraste.py` — razão de contraste WCAG e sugestão de cor que passa.
- `references/` — requisitos, padrões de busca e como corrigir, por item.
- `templates/` — política de privacidade, termos, cookies, reembolso, acessibilidade,
  banner de consentimento, ROPA, plano de incidentes e relatório.
