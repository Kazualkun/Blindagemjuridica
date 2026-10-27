# Gerenciador de consentimento de cookies

`consentimento.js` + `consentimento.css` — sem dependências, ~6 KB minificado. Atende ao Guia
de Cookies da ANPD: bloqueio prévio, rejeitar tão fácil quanto aceitar, categorias, revogação,
link permanente de preferências e integração com o Google Consent Mode v2.

## 1. Instalar

Copie os dois arquivos para a pasta pública do projeto (`public/`, `static/`, `assets/`) e
carregue o script **antes** de qualquer GTM/gtag/pixel, sem `async`/`defer`:

```html
<link rel="stylesheet" href="/consentimento.css">
<script>
  window.blindagemConsentConfig = {
    versao: '1',                              // mude ao alterar fornecedores/categorias
    urlPolitica: '/politica-de-privacidade',
    // textos: { titulo: '...', descricao: '...' },   // opcional
    // categorias: [...]                              // opcional: remova as que não usa
  };
</script>
<script src="/consentimento.js"></script>
```

> Remova do `cfg.categorias` (via `blindagemConsentConfig.categorias`) as categorias que o site
> não usa — não mostre opções sem efeito.

## 2. Marcar os scripts de terceiros

Troque `type` para `text/plain` e indique a categoria (`estatistica`, `marketing` ou
`funcionalidades`). Scripts externos usam `data-src` no lugar de `src`:

```html
<!-- Google Analytics 4 -->
<script type="text/plain" data-categoria-consentimento="estatistica"
        data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX" async></script>
<script type="text/plain" data-categoria-consentimento="estatistica">
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date()); gtag('config', 'G-XXXXXXX');
</script>

<!-- Meta Pixel -->
<script type="text/plain" data-categoria-consentimento="marketing">
  !function(f,b,e,v,n,t,s){/* snippet oficial do Pixel */}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', 'PIXEL_ID'); fbq('track', 'PageView');
</script>

<!-- Hotjar / Clarity -->
<script type="text/plain" data-categoria-consentimento="estatistica">/* snippet */</script>
```

**Google Tag Manager**: o script já define o Consent Mode v2 com tudo `denied`. Você pode
carregar o GTM normalmente (sem bloquear) **desde que** cada tag dentro dele esteja configurada
com "Configurações de consentimento" exigindo `analytics_storage`/`ad_storage`. Se não tiver
certeza de como o contêiner está configurado, bloqueie o GTM inteiro com
`data-categoria-consentimento="marketing"`.

## 3. Iframes (YouTube, Maps, Vimeo)

```html
<iframe data-src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
        data-categoria-consentimento="funcionalidades"
        title="Vídeo: como usar o produto" width="560" height="315" allowfullscreen></iframe>
```
Sem consentimento, aparece um aviso acessível com o botão "Autorizar e carregar".

## 4. Link permanente no rodapé (obrigatório)

```html
<button type="button" data-abrir-preferencias-cookies>Preferências de cookies</button>
```
(Qualquer elemento com esse atributo abre o painel. Estilize como link se preferir.)

## 5. Carregar SDKs via código (React, Vue, apps SPA)

```js
// Lê o estado atual
if (window.blindagemConsent?.tem('estatistica')) iniciarAnalytics();

// Reage a mudanças (também dispara no carregamento quando já há escolha salva)
window.addEventListener('consentimento:atualizado', (e) => {
  if (e.detail.estatistica) iniciarAnalytics();
});
```
API: `tem(categoria)`, `obter()`, `definir({estatistica: true})`, `abrirPreferencias()`, `revogar()`.

### Next.js (App Router)
Copie os arquivos para `public/` e, no `app/layout.tsx`:
```tsx
import Script from 'next/script';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="stylesheet" href="/consentimento.css" />
        <Script id="consentimento-config" strategy="beforeInteractive">
          {`window.blindagemConsentConfig = { versao: '1', urlPolitica: '/politica-de-privacidade' };`}
        </Script>
        <Script src="/consentimento.js" strategy="beforeInteractive" />
      </head>
      <body>{children}</body>
    </html>
  );
}
```
Carregue GA/pixels num Client Component que escuta `consentimento:atualizado` (exemplo em
`references/cookies-e-rastreamento.md`). Se usar `@next/third-parties`, renderize o componente
`<GoogleAnalytics>` só quando `tem('estatistica')` for verdadeiro.

### Vue / Nuxt
`nuxt.config`: adicione os arquivos em `app.head.link`/`app.head.script` (o script sem
`defer`), e use um plugin client-side que escuta `consentimento:atualizado`.

### WordPress
`functions.php` do tema filho:
```php
add_action('wp_enqueue_scripts', function () {
  wp_enqueue_style('consentimento', get_stylesheet_directory_uri() . '/consentimento.css');
  wp_enqueue_script('consentimento', get_stylesheet_directory_uri() . '/consentimento.js', [], '1', false);
  wp_add_inline_script('consentimento', "window.blindagemConsentConfig={versao:'1',urlPolitica:'/politica-de-privacidade'};", 'before');
}, 1);
```
Plugins que inserem scripts de rastreamento (Site Kit, PixelYourSite) precisam respeitar o
consentimento — configure-os ou use um CMP compatível (ex.: Complianz) em vez deste script.

## 6. Verificar
1. Abra o site em aba anônima → DevTools → Network: nenhum request para Google Analytics,
   Meta, TikTok, Hotjar etc. antes de aceitar.
2. Application → Cookies: só cookies necessários.
3. Clique em "Rejeitar não essenciais" → continua sem requests.
4. Abra "Preferências de cookies" pelo rodapé, ative "Estatística" → GA carrega.
5. Desative de novo → a página recarrega e os cookies `_ga` são apagados.
6. Navegue só com teclado: Tab chega a todos os botões, Esc fecha o painel, foco visível.
