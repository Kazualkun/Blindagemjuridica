# Itens 3 e 7 — Aviso de cookies e scripts de rastreamento

**Base:** LGPD arts. 5º XII, 7º I, 8º, 9º, 33; Marco Civil art. 7º (VIII, IX); Guia Orientativo
de Cookies da ANPD (2022); CDC art. 6º III. Para a UE: GDPR + Diretiva ePrivacy.

## Regras que o banner precisa cumprir

1. **Nada não essencial antes do aceite.** Scripts de estatística, publicidade, gravação de
   sessão, pixels e embeds que definem cookies **não carregam** até o usuário aceitar a
   categoria. Esconder o banner não basta: o script não pode ter rodado.
2. **Rejeitar tão fácil quanto aceitar** — botões equivalentes no primeiro nível ("Aceitar
   todos" e "Rejeitar não essenciais"), mesmo destaque visual. Fechar no "X" = rejeitar.
3. **Granularidade** — categorias (necessários, estatística, marketing/publicidade,
   funcionalidades/embeds) com escolha individual. Necessários sempre ativos e explicados.
4. **Nada pré-marcado** além dos necessários.
5. **Sem consentimento tácito** — "ao continuar navegando você concorda" não vale.
6. **Informação** — link para política de cookies/privacidade com cada cookie ou fornecedor,
   finalidade e duração.
7. **Revogação a qualquer momento** — link permanente "Preferências de cookies" no rodapé que
   reabre o painel; ao revogar, parar o envio (e, quando possível, apagar cookies).
8. **Registro** — guardar escolha, data e versão (no navegador basta para o funcionamento; se o
   negócio quiser prova, registrar no servidor de forma pseudonimizada).
9. **Não bloquear o acesso** a quem rejeita (cookie wall), salvo exceções muito justificadas.
10. **Acessível** — banner navegável por teclado, com foco, contraste e `role="dialog"`.

## Classificação dos rastreadores comuns

| Ferramenta | Categoria | Precisa de consentimento? |
|-----------|-----------|---------------------------|
| Cookie de sessão/login, carrinho, CSRF, balanceador, preferência de idioma, a própria escolha de cookies | Necessário | Não (informar) |
| Google Analytics 4, Mixpanel, Amplitude, PostHog, Heap, Yandex | Estatística | Sim |
| Hotjar, Microsoft Clarity, FullStory, Smartlook, Mouseflow, Sentry Replay | Estatística (gravação de sessão) — risco alto | Sim + mascarar campos |
| Meta Pixel, TikTok Pixel, Google Ads, LinkedIn, Pinterest, X, Kwai, Taboola, Criteo | Publicidade | Sim |
| GTM | Contêiner — a categoria é a das tags que ele dispara | Configure as tags por consentimento |
| HubSpot, RD Station, ActiveCampaign (tracking) | Marketing | Sim |
| YouTube, Vimeo, Google Maps, Instagram/Facebook embeds | Funcionalidades/terceiros | Sim (ou use versão sem cookies + clique para carregar) |
| Chat (Intercom, Crisp, Tawk, Jivo) | Funcionalidade | Recomendável carregar só ao clicar no ícone, ou pedir consentimento |
| reCAPTCHA, hCaptcha, Turnstile | Segurança | Legítimo interesse; informar na política |
| Plausible, Umami, Vercel Analytics (sem cookies) | Estatística sem cookies | Em geral dispensa banner; informar na política |
| Google Fonts remoto | Não define cookie, mas envia IP ao Google | Prefira hospedar localmente |

## Como auditar

1. Procure no código (o scanner faz isso): `googletagmanager`, `gtag(`, `G-XXXX`, `GTM-`,
   `fbq(`, `fbevents.js`, `ttq.`, `analytics.tiktok`, `snap.licdn`, `hotjar`, `clarity.ms`,
   `posthog`, `mixpanel`, `amplitude`, `segment`, `youtube.com/embed`, `maps.googleapis`,
   `fonts.googleapis`, `document.cookie =`, `localStorage.setItem`.
2. Procure também em: `.env*` (IDs de pixel), configuração do framework (`next.config`,
   `nuxt.config`, `gatsby-config`, `astro.config`), plugins de WordPress/Shopify, e **tags
   dentro do GTM** (você não vê pelo código — pergunte quais tags o contêiner dispara).
3. Para cada script: carrega no `<head>` direto? É condicionado a consentimento? Envia dados
   pessoais (Pixel com `em`/`ph` — advanced matching; eventos com e-mail/CPF; gravação de
   formulários)?
4. Existe banner/CMP? Ele **bloqueia** de verdade? (Um banner que só grava "aceito" no
   localStorage sem condicionar os scripts é o erro mais comum.)
5. O Google Consent Mode v2 está com padrão `denied` antes de carregar o gtag/GTM?
6. A política lista os cookies/fornecedores?

## Como corrigir

### Opção A — gerenciador pronto da skill (sem dependências)
Use `templates/cookie-consent/` (`consentimento.js` + `consentimento.css`, instruções em
`README.md` da pasta). Ele:
- Bloqueia scripts marcados com `type="text/plain" data-categoria-consentimento="estatistica|marketing|funcionalidades"` e os ativa após o aceite.
- Bloqueia iframes com `data-src` + `data-categoria-consentimento` (YouTube, Maps) e mostra
  um aviso com botão para carregar.
- Integra o Google Consent Mode v2 (padrão `denied`, atualização ao aceitar).
- Tem "Aceitar todos", "Rejeitar não essenciais" e "Preferências", painel por categoria,
  reabertura via qualquer elemento com `data-abrir-preferencias-cookies`, foco e teclado.
- Expõe `window.blindagemConsent.tem("marketing")` e o evento `consentimento:atualizado` para
  carregar SDKs via código (ex.: `posthog.init` só quando houver consentimento).

Adapte cores/textos ao design do site (variáveis CSS no topo do arquivo) e **verifique o
contraste** dos botões.

### Opção B — CMP de mercado
Se o projeto já usa (ou o cliente prefere) Cookiebot, CookieYes, OneTrust, Usercentrics, AdOpt,
Complianz (WordPress) etc., não troque: configure corretamente (bloqueio automático/por
categoria, botão rejeitar no primeiro nível, Consent Mode v2, idioma pt-BR) e documente.

### Snippets de referência

Consent Mode v2 — **antes** de qualquer gtag/GTM:
```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', functionality_storage: 'granted', security_storage: 'granted',
    wait_for_update: 500
  });
</script>
```

Script bloqueado até o consentimento (HTML):
```html
<script type="text/plain" data-categoria-consentimento="marketing"
        data-src="https://connect.facebook.net/en_US/fbevents.js"></script>
<script type="text/plain" data-categoria-consentimento="marketing">
  fbq('init', 'PIXEL_ID'); fbq('track', 'PageView');
</script>
```

Next.js (App Router) — carregar só após consentimento:
```tsx
'use client';
import Script from 'next/script';
import { useEffect, useState } from 'react';

export function ScriptsComConsentimento() {
  const [estatistica, setEstatistica] = useState(false);
  useEffect(() => {
    const atualizar = () => setEstatistica(!!window.blindagemConsent?.tem('estatistica'));
    atualizar();
    window.addEventListener('consentimento:atualizado', atualizar);
    return () => window.removeEventListener('consentimento:atualizado', atualizar);
  }, []);
  if (!estatistica) return null;
  return <Script src="https://www.googletagmanager.com/gtag/js?id=G-XXXX" strategy="afterInteractive" />;
}
```
(Com Consent Mode v2 configurado, o gtag pode carregar antes e só coletar em modo sem cookies;
a decisão de carregar ou não antes do aceite deve ser conservadora: na dúvida, não carregue.)

### Outras correções do item 7
- **Meta Pixel com advanced matching** (`fbq('init', ID, {em: ...})`): só com consentimento de
  marketing; cite na política. Nunca envie CPF, dados de saúde ou de crianças.
- **Gravação de sessão**: ative mascaramento de todos os inputs e textos sensíveis
  (`data-hj-suppress`, `data-clarity-mask="true"`, `maskAllInputs` no PostHog/Sentry); exclua
  páginas de checkout, conta e saúde.
- **Eventos com dados pessoais** (`gtag('event', 'lead', {email})`): remova dados diretos;
  use IDs pseudonimizados.
- **YouTube**: troque `youtube.com/embed` por `youtube-nocookie.com/embed` e carregue após
  consentimento ou clique ("clique para carregar o vídeo").
- **Google Fonts**: baixe as fontes (ex.: `@fontsource/<fonte>` ou `next/font/google`, que
  hospeda localmente) e remova o link para `fonts.googleapis.com`.
- **Server-side tagging / Conversions API**: também depende do consentimento do usuário;
  verifique se o backend respeita a escolha.

## Política de cookies

Pode ser página própria (`templates/politica-de-cookies.md`) ou seção da política de
privacidade. Liste cada fornecedor/cookie detectado com finalidade, categoria, duração e
link para a política do fornecedor. Não invente cookies que não existem; se não for possível
listar nomes exatos, liste por fornecedor e oriente o usuário a completar com o scan de um
serviço de varredura (ex.: o próprio CMP) ou com o DevTools → Application → Cookies.
