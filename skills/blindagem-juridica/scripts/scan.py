#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan.py - Varredura heurística da skill "blindagem-juridica".

Percorre um projeto (site, loja virtual, SaaS, landing page, app) e aponta
indícios de risco jurídico nos 17 itens auditados pela skill. É uma TRIAGEM:
cada achado precisa ser confirmado lendo o código, e a ausência de achados
não significa conformidade. Usa apenas a biblioteca padrão do Python 3.9+.

Uso:
    python scan.py [RAIZ] [--format md|json] [--max-por-regra N]
                   [--saida ARQUIVO] [--incluir-testes]
"""

import argparse
import bisect
import json
import os
import re
import struct
import sys
from collections import OrderedDict, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contraste import contrast_ratio, parse_color, suggest, to_hex  # noqa: E402

VERSION = "1.0.0"

ITENS = OrderedDict([
    (1, "Política de privacidade"),
    (2, "Termos de uso / serviço"),
    (3, "Aviso e gestão de cookies"),
    (4, "Política de reembolso, trocas e arrependimento"),
    (5, "Formulários e LGPD"),
    (6, "Minimização: só dados necessários"),
    (7, "Scripts de rastreamento"),
    (8, "Acessibilidade geral"),
    (9, "Texto alternativo (alt) nas imagens"),
    (10, "Contraste de cores"),
    (11, "Navegação por teclado"),
    (12, "Avaliações e depoimentos"),
    (13, "Promessas e publicidade enganosa"),
    (14, "Direitos autorais (imagens, fontes, marcas)"),
    (15, "Identificação da empresa"),
    (16, "Conformidade LGPD (governança e segurança)"),
    (17, "Outros riscos jurídicos"),
])
SEVERIDADES = ["critico", "alto", "medio", "baixo", "info"]
ICONE = {"critico": "🔴", "alto": "🟠", "medio": "🟡", "baixo": "🔵", "info": "⚪"}

# --------------------------------------------------------------------------
# Arquivos
# --------------------------------------------------------------------------
IGNORE_DIRS = {
    "node_modules", "vendor", "bower_components", "jspm_packages", ".git", ".hg", ".svn",
    ".next", ".nuxt", ".svelte-kit", ".astro", ".output", ".vercel", ".netlify", ".expo",
    "dist", "build", "out", "coverage", ".nyc_output", "__pycache__", ".venv", "venv",
    "env", ".tox", ".mypy_cache", ".pytest_cache", ".idea", ".vscode", ".cache",
    ".turbo", ".parcel-cache", "target", "obj", ".dart_tool", "Pods", ".gradle",
    "storybook-static", "tmp", "temp", ".claude", "blindagem-juridica", "site-packages",
}
TEST_DIRS = {
    "test", "tests", "__tests__", "__mocks__", "spec", "specs", "e2e", "cypress",
    "playwright", "fixtures", "mocks", "stories", ".storybook",
}
MARKUP_EXT = {
    ".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".mjs", ".cjs", ".vue", ".svelte",
    ".astro", ".php", ".twig", ".liquid", ".erb", ".haml", ".slim", ".hbs",
    ".handlebars", ".ejs", ".pug", ".njk", ".jinja", ".jinja2", ".j2", ".cshtml",
    ".razor", ".jsp", ".mdx",
}
STYLE_EXT = {".css", ".scss", ".sass", ".less", ".styl", ".pcss"}
PROSE_EXT = {".md", ".txt", ".rst"}
CODE_EXT = {".py", ".rb", ".go", ".java", ".kt", ".dart", ".swift", ".cs", ".rs",
            ".prisma", ".sql", ".graphql", ".gql"}
CONFIG_EXT = {".json", ".yml", ".yaml", ".toml", ".xml", ".ini", ".conf", ".env"}
TEXT_EXT = MARKUP_EXT | STYLE_EXT | PROSE_EXT | CODE_EXT | CONFIG_EXT
IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".bmp",
           ".tif", ".tiff", ".heic", ".ico"}
FONT_EXT = {".ttf", ".otf", ".woff", ".woff2", ".eot"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock",
              "gemfile.lock", "poetry.lock", "cargo.lock", "bun.lockb"}
MAX_BYTES = 1_500_000

# Tags HTML/JSX: aceita "=>" de arrow functions dentro dos atributos.
TAG = r"(?:=>|[^>]){0,3000}?"


# --------------------------------------------------------------------------
# Catálogos
# --------------------------------------------------------------------------
# (nome, regex, categoria, palavra-chave para conferir menção na política)
TRACKERS = [
    ("Google Tag Manager", r"googletagmanager\.com/gtm\.js|['\"]GTM-[A-Z0-9]{4,10}['\"]|GoogleTagManager", "marketing", r"google"),
    ("Google Analytics", r"googletagmanager\.com/gtag/js|gtag\(\s*['\"]config['\"]\s*,\s*['\"]G-|google-analytics\.com|['\"]G-[A-Z0-9]{8,12}['\"]|['\"]UA-\d{4,10}-\d+['\"]|react-ga4?|GoogleAnalytics|vue-gtag|@nuxtjs/google-analytics", "analytics", r"google\s*analytics|google"),
    ("Google Ads / DoubleClick", r"['\"]AW-\d{6,12}|googleadservices\.com|googlesyndication\.com|doubleclick\.net|adsbygoogle", "publicidade", r"google"),
    ("Meta Pixel (Facebook/Instagram)", r"connect\.facebook\.net/[^\"'\s]*fbevents|\bfbq\s*\(|react-facebook-pixel", "publicidade", r"meta|facebook"),
    ("TikTok Pixel", r"analytics\.tiktok\.com|\bttq\.(load|track|page)\b", "publicidade", r"tiktok"),
    ("LinkedIn Insight Tag", r"snap\.licdn\.com|_linkedin_partner_id", "publicidade", r"linkedin"),
    ("Pinterest Tag", r"s\.pinimg\.com/ct/|\bpintrk\s*\(", "publicidade", r"pinterest"),
    ("X/Twitter Pixel", r"static\.ads-twitter\.com|\btwq\s*\(", "publicidade", r"twitter|\bx\b"),
    ("Kwai Pixel", r"kwai[^\n]{0,40}pixel|s\d?\.kwai\.net", "publicidade", r"kwai"),
    ("Taboola", r"cdn\.taboola\.com|_tfa\.push", "publicidade", r"taboola"),
    ("Criteo", r"static\.criteo\.net|criteo_q", "publicidade", r"criteo"),
    ("Hotjar", r"static\.hotjar\.com|hotjar\.com/c/hotjar|@hotjar/browser|\bhj\(\s*['\"]", "gravacao", r"hotjar"),
    ("Microsoft Clarity", r"clarity\.ms|\bclarity\s*\(\s*['\"]|@microsoft/clarity", "gravacao", r"clarity|microsoft"),
    ("FullStory", r"fullstory\.com|_fs_org", "gravacao", r"fullstory"),
    ("Smartlook", r"smartlook", "gravacao", r"smartlook"),
    ("Mouseflow", r"mouseflow", "gravacao", r"mouseflow"),
    ("Lucky Orange", r"luckyorange", "gravacao", r"lucky\s*orange"),
    ("Sentry Session Replay", r"replayIntegration|new\s+Replay\s*\(|Sentry\.Replay", "gravacao", r"sentry"),
    ("Yandex Metrica", r"mc\.yandex\.ru", "analytics", r"yandex"),
    ("Segment", r"cdn\.segment\.com|@segment/analytics", "analytics", r"segment"),
    ("Mixpanel", r"cdn\.mxpnl\.com|mixpanel\.(init|track)\b|mixpanel-browser", "analytics", r"mixpanel"),
    ("Amplitude", r"cdn\.amplitude\.com|amplitude\.(init|getInstance)\b|@amplitude/", "analytics", r"amplitude"),
    ("PostHog", r"posthog\.(init|capture)\b|posthog-js|i\.posthog\.com", "analytics", r"posthog"),
    ("Heap", r"cdn\.heapanalytics\.com|heap\.load\(", "analytics", r"heap"),
    ("HubSpot", r"js\.hs-scripts\.com|js\.hsforms\.net|js\.hs-analytics\.net", "marketing", r"hubspot"),
    ("RD Station", r"d335luupugsy2\.cloudfront\.net|rdstation|rd-station", "marketing", r"rd\s*station"),
    ("ActiveCampaign", r"trackcmp\.net|activecampaign", "marketing", r"activecampaign"),
    ("Intercom", r"widget\.intercom\.io|\bIntercom\s*\(\s*['\"]boot", "chat", r"intercom"),
    ("Crisp", r"client\.crisp\.chat|\$crisp", "chat", r"crisp"),
    ("Tawk.to", r"embed\.tawk\.to", "chat", r"tawk"),
    ("Zendesk Chat", r"static\.zdassets\.com|zopim", "chat", r"zendesk"),
    ("JivoChat", r"code\.jivosite\.com|jivosite", "chat", r"jivo"),
    ("Vercel Analytics", r"@vercel/analytics|@vercel/speed-insights", "sem_cookies", r"vercel"),
    ("Plausible", r"plausible\.io/js", "sem_cookies", r"plausible"),
    ("Umami", r"umami\.is|cloud\.umami|umami\.js", "sem_cookies", r"umami"),
    ("Google reCAPTCHA", r"google\.com/recaptcha|recaptcha/api\.js|grecaptcha|react-google-recaptcha", "seguranca", r"recaptcha|google"),
    ("hCaptcha", r"hcaptcha\.com|@hcaptcha", "seguranca", r"hcaptcha"),
    ("Cloudflare Turnstile", r"challenges\.cloudflare\.com/turnstile", "seguranca", r"cloudflare|turnstile"),
    ("YouTube (embed com cookies)", r"youtube\.com/embed/|react-youtube|youtube\.com/iframe_api", "embed", r"youtube|google"),
    ("Vimeo", r"player\.vimeo\.com", "embed", r"vimeo"),
    ("Google Maps", r"google\.com/maps/embed|maps\.googleapis\.com|@react-google-maps", "embed", r"google\s*maps|google"),
    ("Google Fonts (servidor do Google)", r"fonts\.googleapis\.com|fonts\.gstatic\.com", "fontes", r"google"),
    ("Facebook SDK / plugins sociais", r"connect\.facebook\.net/[^\"'\s]*sdk\.js|facebook\.com/plugins/", "social", r"facebook|meta"),
    ("Instagram embed", r"instagram\.com/embed\.js", "social", r"instagram|meta"),
    ("AddThis / ShareThis", r"addthis\.com|sharethis\.com", "social", r"addthis|sharethis"),
]
CONSENT_CATS = {"publicidade", "marketing", "analytics", "gravacao", "embed", "social"}
CAT_LABEL = {
    "publicidade": "publicidade/remarketing", "marketing": "marketing", "analytics": "estatística",
    "gravacao": "gravação de sessão", "embed": "conteúdo incorporado de terceiro",
    "social": "rede social", "chat": "chat/atendimento", "sem_cookies": "estatística sem cookies",
    "seguranca": "segurança/antifraude", "fontes": "fonte remota (envia IP)",
}

CMP_RE = re.compile(
    r"cookieconsent|cookie-consent|vanilla-cookieconsent|onetrust|optanon|cookiebot|usercentrics|"
    r"klaro|tarteaucitron|complianz|cookieyes|cookie-law-info|iubenda|termly|osano|didomi|"
    r"consentmanager|goadopt|adopt\.js|tag\.goadopt|privacytools|react-cookie-consent|"
    r"cookie-notice|blindagemConsent|data-consent-category|data-categoria-consentimento|"
    r"gtag\(\s*['\"]consent['\"]", re.I)
CONSENT_DEFAULT_RE = re.compile(r"gtag\(\s*['\"]consent['\"]\s*,\s*['\"]default['\"][^)]{0,400}denied", re.I | re.S)
BANNER_RE = re.compile(
    r"usamos\s+cookies|utilizamos\s+cookies|este\s+site\s+(usa|utiliza)\s+cookies|we\s+use\s+cookies|"
    r"aceitar\s+(todos\s+)?(os\s+)?cookies|accept\s+(all\s+)?cookies|aceito\s+os\s+cookies", re.I)
REJECT_RE = re.compile(
    r"rejeitar|recusar|reject|decline|negar|n[aã]o\s+aceito|apenas\s+(os\s+)?(necess[aá]rios|essenciais)|"
    r"somente\s+(os\s+)?(necess[aá]rios|essenciais)|only\s+(necessary|essential)", re.I)
TACIT_RE = re.compile(
    r"ao\s+(continuar|prosseguir)\s+(navegando|a\s+navegar|no\s+site|usando|utilizando)|"
    r"continuing\s+to\s+(browse|use)|by\s+(using|continuing)\s+(this|our)\s+(site|website)|"
    r"ao\s+(usar|utilizar|navegar\s+(n|em))\s*(este|nosso|o)\s+site,?\s+voc[eê]\s+(concorda|aceita)", re.I)

# Serviços de terceiros (operadores) detectados por dependência
SERVICES = [
    (r"^stripe$|^@stripe/", "Stripe", "pagamentos", True),
    (r"mercadopago|@mercadopago", "Mercado Pago", "pagamentos", False),
    (r"pagarme|pagar\.me|@pagarme", "Pagar.me", "pagamentos", False),
    (r"pagseguro|pagbank", "PagBank/PagSeguro", "pagamentos", False),
    (r"asaas", "Asaas", "pagamentos", False),
    (r"iugu", "Iugu", "pagamentos", False),
    (r"paypal", "PayPal", "pagamentos", True),
    (r"gerencianet|sdk-node-apis-efi|efipay", "Efí (Gerencianet)", "pagamentos", False),
    (r"^firebase$|^firebase-admin$|@firebase/|@react-native-firebase", "Google Firebase", "infraestrutura/banco/autenticação", True),
    (r"@supabase/", "Supabase", "infraestrutura/banco/autenticação", True),
    (r"@clerk/", "Clerk", "autenticação", True),
    (r"auth0", "Auth0", "autenticação", True),
    (r"aws-sdk|@aws-sdk/|^boto3$", "Amazon Web Services", "infraestrutura", True),
    (r"@google-cloud/", "Google Cloud", "infraestrutura", True),
    (r"@vercel/blob|@vercel/postgres|@vercel/kv", "Vercel", "infraestrutura", True),
    (r"@neondatabase|@planetscale|@upstash", "Banco gerenciado (Neon/PlanetScale/Upstash)", "infraestrutura", True),
    (r"cloudinary", "Cloudinary", "armazenamento de mídia", True),
    (r"uploadthing", "UploadThing", "armazenamento de arquivos", True),
    (r"^resend$", "Resend", "envio de e-mails", True),
    (r"@sendgrid|^sendgrid$", "SendGrid (Twilio)", "envio de e-mails", True),
    (r"mailchimp", "Mailchimp", "e-mail marketing", True),
    (r"postmark", "Postmark", "envio de e-mails", True),
    (r"brevo|sib-api|sendinblue", "Brevo", "e-mail marketing", True),
    (r"twilio", "Twilio", "SMS/WhatsApp", True),
    (r"zenvia", "Zenvia", "SMS/WhatsApp", False),
    (r"whatsapp-web\.js|baileys|venom-bot|wppconnect", "WhatsApp não oficial (biblioteca de automação)", "mensageria", True),
    (r"onesignal", "OneSignal", "notificações push", True),
    (r"@sentry/|^sentry-sdk$", "Sentry", "monitoramento de erros", True),
    (r"^openai$", "OpenAI", "inteligência artificial", True),
    (r"@anthropic-ai/|^anthropic$", "Anthropic (Claude)", "inteligência artificial", True),
    (r"@google/generative-ai|@google/genai|google-generativeai", "Google Gemini", "inteligência artificial", True),
    (r"replicate|@huggingface", "Replicate/Hugging Face", "inteligência artificial", True),
    (r"algolia", "Algolia", "busca", True),
    (r"pusher", "Pusher", "tempo real", True),
    (r"crisp-sdk-web", "Crisp", "chat", True),
    (r"@intercom", "Intercom", "chat", True),
]
AI_SERVICES = {"OpenAI", "Anthropic (Claude)", "Google Gemini", "Replicate/Hugging Face"}
PAYMENT_DEPS = re.compile(r"stripe|mercadopago|pagarme|pagseguro|pagbank|asaas|iugu|paypal|gerencianet|efipay|"
                          r"woocommerce|shopify|medusa|saleor|vtex|nuvemshop|@lemonsqueezy|paddle", re.I)
HASH_DEPS = re.compile(r"bcrypt|argon2|scrypt|pbkdf2|passlib|@node-rs/argon2|@node-rs/bcrypt", re.I)
MANAGED_AUTH = re.compile(r"firebase|@supabase|@clerk|auth0|cognito|amplify|next-auth|@auth/|lucia|better-auth|"
                          r"django|laravel|devise|rails|keycloak|@kinde|stack-auth|appwrite|pocketbase", re.I)
BACKEND_DEPS = re.compile(r"^(express|fastify|koa|hono|@nestjs/core|next|nuxt|@sveltejs/kit|@remix-run/node|"
                          r"django|flask|fastapi|laravel/framework|rails|sinatra|astro)$", re.I)


def _fp(p):
    return re.compile(r"(?<![a-z])(?:" + p + r")(?![a-z])")


# (rótulo, nível, regex) - níveis: comum | atencao | sensivel (art. 11 LGPD)
FIELD_PATTERNS = [
    ("nome", "comum", _fp(r"nome|name|full_name|first_name|last_name|sobrenome|surname")),
    ("e-mail", "comum", _fp(r"e[_\- ]?mail")),
    ("telefone/WhatsApp", "comum", _fp(r"telefone|fone|phone|celular|whats_?app|tel")),
    ("endereço", "comum", _fp(r"endere[cç]o|address|cep|zip_?code|zip|logradouro|bairro|street")),
    ("CPF", "atencao", _fp(r"cpf")),
    ("RG", "atencao", _fp(r"rg|identidade")),
    ("CNH", "atencao", _fp(r"cnh")),
    ("data de nascimento/idade", "atencao", _fp(r"nascimento|data_nasc|dt_nasc|birth_?date|birthday|birth|dob|idade|age")),
    ("gênero/sexo", "atencao", _fp(r"g[eê]nero|gender|sexo|sex")),
    ("estado civil", "atencao", _fp(r"estado_civil|marital_status|marital")),
    ("renda/salário", "atencao", _fp(r"renda|sal[aá]rio|income|salary|faixa_salarial")),
    ("nome da mãe", "atencao", _fp(r"nome_da_m[aã]e|nome_mae|mother_name|mother")),
    ("foto/selfie", "atencao", _fp(r"selfie|foto|photo|foto_perfil")),
    ("geolocalização", "atencao", _fp(r"geolocation|geolocaliza[cç][aã]o|latitude|longitude|get_current_position")),
    ("dados de cartão", "atencao", _fp(r"card_?number|cc_number|cc_csc|numero_cartao|numero_do_cartao|cvv|cvc")),
    ("origem racial/étnica", "sensivel", _fp(r"ra[cç]a|etnia|race|ethnicity|cor_da_pele|skin_color")),
    ("convicção religiosa", "sensivel", _fp(r"religi[aã]o|religion|cren[cç]a_religiosa")),
    ("opinião política/filiação", "sensivel", _fp(r"partido|filia[cç][aã]o_partid[aá]ria|sindicato|opini[aã]o_pol[ií]tica|political")),
    ("saúde", "sensivel", _fp(r"sa[uú]de|health|doen[cç]as?|diagn[oó]stico|medicamentos?|alergias?|prontu[aá]rio|"
                              r"defici[eê]ncia|disability|gestante|gravidez|pregnan\w*|cid|tipo_sangu[ií]neo|blood_type|medical")),
    ("vida sexual/orientação", "sensivel", _fp(r"orienta[cç][aã]o_sexual|sexual_orientation|vida_sexual")),
    ("biometria/genética", "sensivel", _fp(r"biometria|biometric|fingerprint|impress[aã]o_digital|face_id|"
                                            r"reconhecimento_facial|facial_recognition|gen[eé]tico|genetic")),
]

DOCS = OrderedDict([
    ("privacidade", (r"privac|privacidade|privacy|lgpd|protecao-de-dados|data-protection",
                     r"pol[ií]tica\s+de\s+privacidade|aviso\s+de\s+privacidade|privacy\s+policy|privacy\s+notice")),
    ("termos", (r"termos|terms|(^|[/_-])tos([/_.-]|$)|condicoes|conditions|eula|contrato",
                r"termos\s+(de\s+)?(uso|servi[cç]os?)|termos\s+e\s+condi[cç][oõ]es|terms\s+(of\s+)?(use|service)|terms\s+and\s+conditions")),
    ("cookies", (r"cookie", r"pol[ií]tica\s+de\s+cookies|cookie\s+policy|aviso\s+de\s+cookies")),
    ("reembolso", (r"reembolso|refund|devolu|troca|cancelamento|returns|arrependimento",
                   r"pol[ií]tica\s+de\s+(reembolso|trocas?|devolu[cç])|trocas\s+e\s+devolu|direito\s+de\s+arrependimento|refund\s+policy|return\s+policy")),
    ("acessibilidade", (r"acessibilidade|accessibility",
                        r"declara[cç][aã]o\s+de\s+acessibilidade|accessibility\s+statement|compromisso\s+com\s+a\s+acessibilidade")),
])
DOC_LINK = {
    "privacidade": r"privac|privacidade|privacy",
    "termos": r"termos|terms|condicoes",
    "cookies": r"cookie",
    "reembolso": r"reembolso|refund|devolu|troca|arrependimento",
    "acessibilidade": r"acessibilidade|accessibility",
}
PRIVACY_REQ = [
    ("identificação do controlador (razão social/CNPJ)", r"controlador|cnpj|raz[aã]o\s+social"),
    ("dados coletados", r"dados\s+(pessoais\s+)?(que\s+)?(coletamos|coletados|tratados|tratamos)|quais\s+dados|informa[cç][oõ]es\s+(que\s+)?coletamos"),
    ("finalidades", r"finalidade"),
    ("bases legais (art. 7º/11)", r"bases?\s+lega(l|is)|hip[oó]teses?\s+lega|art(igo)?\.?\s*7"),
    ("compartilhamento com terceiros", r"compartilh"),
    ("direitos do titular (art. 18)", r"direitos\s+do\s+titular|seus\s+direitos|art(igo)?\.?\s*18|portabilidade"),
    ("encarregado/DPO e canal de contato (art. 41)", r"encarregad|\bdpo\b|data\s+protection\s+officer"),
    ("prazo de retenção", r"reten[cç][aã]o|por\s+quanto\s+tempo|prazo\s+de\s+(armazenamento|guarda|conserva)|armazenad[oa]s?\s+(por|pelo|durante)"),
    ("cookies", r"cookie"),
    ("segurança", r"seguran[cç]a"),
    ("data de atualização", r"atualiza|vig[eê]ncia|[uú]ltima\s+(revis|altera)"),
    ("menção à LGPD", r"lgpd|13\.709"),
]
TERMS_REQ = [
    ("identificação do fornecedor", r"cnpj|raz[aã]o\s+social|inscrit[oa]\s+no"),
    ("descrição do serviço/objeto", r"objeto|servi[cç]os?\s+oferecid|produtos\s+(vendidos|oferecidos|comercializados)|o\s+que\s+(é|oferecemos)|descri[cç][aã]o"),
    ("regras de uso/condutas proibidas", r"proibid|vedad|n[aã]o\s+(é\s+)?permitid|conduta"),
    ("cancelamento/rescisão", r"cancel|rescis|encerramento"),
    ("alterações dos termos", r"altera[cç][oõ]es|alterar|alterad|modifica[cç][oõ]es|modificar|atualiza"),
    ("propriedade intelectual", r"propriedade\s+intelectual|direitos\s+autorais|marca"),
    ("lei aplicável e foro", r"foro|legisla[cç][aã]o\s+(aplic|brasileira)|leis\s+(da\s+)?rep[uú]blica"),
    ("referência à política de privacidade", r"pol[ií]tica\s+de\s+privacidade"),
]
ABUSIVE_CLAUSES = [
    (r"n[aã]o\s+nos\s+responsabilizamos\s+por\s+(nenhum|qualquer)|isent[ao]-?se\s+de\s+(toda|qualquer)\s+responsabilidade|"
     r"n[aã]o\s+se\s+responsabiliza\s+por\s+(nenhum|qualquer)|sem\s+qualquer\s+responsabilidade", "alto",
     "Cláusula de exoneração total de responsabilidade - nula em relação de consumo (CDC art. 25 e 51, I)"),
    (r"sem\s+direito\s+a\s+(reembolso|devolu|estorno)|n[aã]o\s+(fazemos|realizamos|aceitamos|efetuamos)\s+(reembolso|devolu|troca|estorno)|"
     r"n[aã]o\s+h[aá]\s+(reembolso|devolu)|venda\s+final|todas\s+as\s+vendas\s+s[aã]o\s+finais|n[aã]o\s+(é|e)\s+reembols[aá]vel|"
     r"no\s+refunds?|non-refundable", "alto",
     "Negativa genérica de reembolso - conflita com o direito de arrependimento (CDC art. 49) e com o art. 51, II"),
    (r"arbitragem", "alto", "Arbitragem compulsória é nula em contrato de consumo (CDC art. 51, VII) - confirme o contexto"),
    (r"foro\s+(da\s+comarca\s+de|eleito|exclusivo)|elegem\s+o\s+foro", "medio",
     "Foro de eleição: em relação de consumo o consumidor pode demandar no próprio domicílio (CDC art. 101, I) - "
     "redija ressalvando esse direito"),
    (r"podemos\s+alterar\s+(os\s+)?pre[cç]os?\s+a\s+qualquer\s+momento[^.]{0,80}(contrat|assinatur|j[aá]\s+pag)|"
     r"pre[cç]os\s+podem\s+ser\s+alterados\s+a\s+qualquer\s+momento[^.]{0,80}(contrat|assinatur|j[aá]\s+pag)|reajust\w+\s+unilateral", "medio",
     "Alteração unilateral de preço/condição de contrato vigente (CDC art. 51, X e XIII)"),
]

PROMISES = [
    (r"lucro\s+garantido|renda\s+(extra\s+)?garantida|retorno\s+garantido|rentabilidade\s+garantida|dinheiro\s+f[aá]cil|"
     r"fique\s+rico|ganhe\s+R?\$?\s?[\d.]+\s*(mil\s+)?(por|ao)\s+(dia|m[eê]s|semana)|ganhos?\s+garantidos?", "critico",
     "Promessa de ganho financeiro - publicidade enganosa (CDC art. 37 e 67) e possível crime contra a economia popular"),
    (r"\bcura\b|\bcuram\b|curar\s+(a|o|sua|seu)|emagre[çc]a\s+\d+\s*(kg|quilos)|perca\s+\d+\s*(kg|quilos)|"
     r"sem\s+efeitos?\s+colaterais|elimina\s+(a\s+|o\s+)?(diabetes|ansiedade|depress|c[aâ]ncer|calv[ií]cie)", "critico",
     "Alegação de cura/resultado de saúde - vedada sem comprovação e registro (CDC art. 37; Lei 6.437/77; normas ANVISA/conselhos)"),
    (r"resultados?\s+garantid[oa]s?|garantimos\s+(o\s+|seu\s+)?resultado|100\s*%\s+(garantido|eficaz|eficiente|seguro)|"
     r"risco\s+zero|sem\s+riscos?\b|infal[ií]vel|milagros[oa]", "alto",
     "Promessa absoluta/resultado garantido - a oferta vincula (CDC art. 30) e o ônus da prova é do anunciante (art. 38)"),
    (r"clinicamente\s+comprovad|cientificamente\s+comprovad|comprovad[oa]\s+(pela|pela\s+)?ci[eê]ncia|"
     r"aprovad[oa]\s+pela\s+anvisa|recomendad[oa]\s+por\s+(m[eé]dicos|dentistas|especialistas)", "alto",
     "Alegação científica/regulatória - exige comprovação documental disponível (CDC art. 36, par. único, e 38)"),
    (r"aprova[çc][aã]o\s+garantida|emprego\s+garantido|vaga\s+garantida|passe\s+(no|em|na)\s[^.\n]{0,40}garantid", "alto",
     "Promessa de aprovação/emprego garantido"),
    (r"cr[eé]dito\s+(pr[eé]-?)?aprovado|cr[eé]dito\s+garantido|sem\s+consulta\s+(ao\s+)?(spc|serasa)|libera[cç][aã]o\s+imediata", "alto",
     "Oferta de crédito com apelo vedado - Lei 14.181/2021 (superendividamento), CDC art. 54-C"),
    (r"\bo\s+melhor\s+(do|da)\s+(brasil|mercado|mundo|cidade)|\ba\s+melhor\s+(do|da)\s+(brasil|mercado|mundo|cidade)|"
     r"n[uú]mero\s+1\s+(do|no|em)|\bn[ºo°]\s*1\s+(do|no|em)|l[ií]der\s+(de|do|no)\s+mercado|o\s+mais\s+barato", "medio",
     "Superlativo/comparativo - precisa de comprovação objetiva (CONAR arts. 27 e 32; CDC art. 38)"),
    (r"satisfa[çc][aã]o\s+garantida|seu\s+dinheiro\s+de\s+volta|garantia\s+incondicional|devolvemos\s+(100\s*%|todo)", "info",
     "Garantia anunciada - vincula (CDC art. 30) e deve bater com a política de reembolso"),
    (r"frete\s+gr[aá]tis", "info",
     "Frete grátis - condições e restrições devem estar claras e ostensivas (Decreto 7.962/2013, art. 2º, VI)"),
]
SCARCITY_RE = re.compile(
    r"[uú]ltimas?\s+(unidades|vagas|pe[cç]as)|apenas\s+\d+\s+(unidades|vagas|itens|pe[cç]as)|restam\s+(apenas\s+|s[oó]\s+)?\d+|"
    r"s[oó]\s+hoje|somente\s+hoje|oferta\s+(termina|acaba|expira|encerra)|\d+\s+pessoas\s+(est[aã]o\s+)?(vendo|comprando|olhando)", re.I)
PRICE_ANCHOR_RE = re.compile(r"\bde\s*:?\s*R\$\s*[\d.,]+\s*(por|→|->|para)\s*:?\s*(apenas\s+)?R\$", re.I)
SOCIAL_PROOF_RE = re.compile(
    r"\+\s?\d{1,3}(?:[.,]\d{3})+\s*(clientes|alunos|usu[aá]rios|vendas|pessoas|empresas)|"
    r"milhares\s+de\s+(clientes|alunos|pessoas)\s+satisfeit|\b[45][.,]\d\s*(/\s*5|estrelas|de\s+5)\b|"
    r"avalia[cç][aã]o\s+m[eé]dia|nota\s+[45][.,]\d", re.I)
FAKE_AVATAR_RE = re.compile(
    r"randomuser\.me|pravatar\.cc|thispersondoesnotexist|generated\.photos|xsgames\.co/randomusers|"
    r"api\.dicebear\.com|i\.pravatar|ui-avatars\.com|robohash\.org|this-person-does-not-exist", re.I)
TESTIMONIAL_RE = re.compile(r"depoimento|testimonial|review|avalia[cç]|feedback|o\s+que\s+(nossos\s+)?clientes\s+dizem", re.I)
RATING_KEY_RE = re.compile(r"\b(rating|stars|estrelas|nota|score)\s*[:=]\s*['\"]?[1-5](?:[.,]\d)?\b", re.I)

STOCK_NAME_RE = re.compile(r"shutterstock|istock|istockphoto|getty|gettyimages|depositphotos|adobestock|adobe[_-]stock|"
                           r"123rf|dreamstime|alamy|vecteezy|envato|stocksy|bigstock|canstock|pond5", re.I)
FREEPIK_RE = re.compile(r"freepik|flaticon", re.I)
UNKNOWN_ORIGIN_RE = re.compile(r"whatsapp[ _-]?image|screenshot|captura[ _-]de[ _-]tela|^images?(\s?\(\d+\))?\.|"
                               r"^download(\s?\(\d+\))?\.|^unnamed|^imagem[ _-]?\d*\.|^img[-_]?\d{4,}|^pexels-|^unsplash", re.I)
AI_IMAGE_RE = re.compile(r"midjourney|dall[-_ ]?e|stable[-_ ]?diffusion|firefly|ai[-_]generated|gerad[ao][-_]por[-_]ia|leonardo[-_]ai", re.I)
HOTLINK_RE = re.compile(
    r"https?://(encrypted-tbn\d\.gstatic\.com|i\.pinimg\.com|[\w-]+\.pinimg\.com|lookaside\.fbsbx\.com|"
    r"scontent[\w.-]*\.(?:fbcdn|cdninstagram)\.net|[\w.-]*cdninstagram\.com|media\.gettyimages\.com|"
    r"t\d\.ftcdn\.net|as\d\.ftcdn\.net|image\.shutterstock\.com|thumbs\.dreamstime\.com|st\d\.depositphotos\.com|"
    r"previews\.123rf\.com|media\.istockphoto\.com|img\.freepik\.com|i\.ytimg\.com)[^\s\"')]*", re.I)
BRAND_FILE_RE = re.compile(r"(?<![a-z])(nike|adidas|netflix|disney|marvel|coca[-_]?cola|mcdonalds|spotify|starbucks|"
                           r"pokemon|nintendo|playstation|xbox|ferrari|louis[-_]?vuitton|gucci|chanel|globo|fifa|"
                           r"cbf|flamengo|corinthians|palmeiras|harry[-_]?potter|star[-_]?wars)(?![a-z])", re.I)
COMMERCIAL_FONT_RE = re.compile(r"helvetica|gotham|futura|avenir|proxima[-_ ]?nova|sf[-_ ]?pro|san[-_ ]?francisco|"
                                r"circular|graphik|brandon|gilroy|museo|din[-_ ]?pro|frutiger|univers|myriad|segoe|"
                                r"trade[-_ ]?gothic|akzidenz|neue[-_ ]?haas|calibri|arial|cera[-_ ]?pro|sofia[-_ ]?pro|"
                                r"aeonik|gt[-_ ]?walsheim|tt[-_ ]?norms", re.I)
STOCK_BYTES_RE = re.compile(rb"Getty Images|iStock|Shutterstock|Adobe Stock|Depositphotos|Dreamstime|123RF|Alamy|"
                            rb"gettyimages|shutterstock\.com|stock\.adobe\.com|Freepik", re.I)

SECRET_PATTERNS = [
    ("Chave secreta do Stripe (produção)", r"sk_live_[0-9a-zA-Z]{20,}", "critico"),
    ("Chave restrita do Stripe (produção)", r"rk_live_[0-9a-zA-Z]{20,}", "critico"),
    ("Chave de acesso AWS", r"AKIA[0-9A-Z]{16}", "critico"),
    ("Chave privada", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "critico"),
    ("Token do GitHub", r"gh[pousr]_[A-Za-z0-9]{36,}", "critico"),
    ("Token do Slack", r"xox[baprs]-[A-Za-z0-9-]{10,}", "critico"),
    ("Chave da Anthropic", r"sk-ant-[A-Za-z0-9_-]{32,}", "critico"),
    ("Chave da OpenAI", r"sk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}", "critico"),
    ("Access token do Mercado Pago (produção)", r"APP_USR-\d{6,}-\d{6}-[a-f0-9]{32}-\d{6,}", "critico"),
    ("service_role do Supabase exposta em variável pública", r"(?:NEXT_PUBLIC|VITE|REACT_APP|PUBLIC|NUXT_PUBLIC|EXPO_PUBLIC)_[A-Z_]*SERVICE_ROLE", "critico"),
    ("Senha de banco de dados em URL", r"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^:\s/'\"]+:[^@\s'\"]{3,}@(?!localhost|127\.0\.0\.1|host|db\b|postgres\b)", "critico"),
    ("Chave de API do Google", r"AIza[0-9A-Za-z_-]{35}", "baixo"),
]

COPYLEFT_RE = re.compile(r"AGPL|SSPL|(?<!L)GPL", re.I)


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def camel_to_snake(s):
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def strip_tags(text):
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def get_attr(tag, name):
    m = re.search(r"(?<![\w:-])" + name + r"\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{([^}]*)\}|([^\s>]+))", tag, re.I)
    if not m:
        return None
    return next((g for g in m.groups() if g is not None), "")


def has_attr(tag, name):
    return re.search(r"(?<![\w:-])" + name + r"(?=[\s=>/]|$)", tag, re.I) is not None


def mask(secret):
    if len(secret) <= 10:
        return secret[:2] + "…"
    return secret[:6] + "…" + secret[-2:]


def cnpj_valid(raw):
    """Valida CNPJ numérico ou alfanumérico (IN RFB 2.229/2024)."""
    s = re.sub(r"[.\-/\s]", "", raw.upper())
    if not re.fullmatch(r"[0-9A-Z]{12}\d{2}", s) or len(set(s)) == 1:
        return False
    vals = [ord(c) - 48 for c in s]

    def dv(nums):
        weights = list(range(len(nums) - 7, 1, -1)) + list(range(9, 1, -1))
        total = sum(n * w for n, w in zip(nums, weights))
        r = total % 11
        return 0 if r < 2 else 11 - r

    return dv(vals[:12]) == vals[12] and dv(vals[:13]) == vals[13]


def exif_text(data):
    """Extrai Artist/Copyright do EXIF de um JPEG (melhor esforço)."""
    out = {}
    try:
        i = data.find(b"Exif\x00\x00")
        if i < 0:
            return out
        tiff = data[i + 6:]
        end = "<" if tiff[:2] == b"II" else ">" if tiff[:2] == b"MM" else None
        if not end:
            return out
        off = struct.unpack(end + "I", tiff[4:8])[0]
        n = struct.unpack(end + "H", tiff[off:off + 2])[0]
        for k in range(min(n, 200)):
            e = off + 2 + k * 12
            tag, typ, cnt = struct.unpack(end + "HHI", tiff[e:e + 8])
            if tag in (0x013B, 0x8298) and typ == 2 and cnt < 1000:
                if cnt <= 4:
                    raw = tiff[e + 8:e + 8 + cnt]
                else:
                    vo = struct.unpack(end + "I", tiff[e + 8:e + 12])[0]
                    raw = tiff[vo:vo + cnt]
                val = raw.rstrip(b"\x00").decode("latin-1", "replace").strip()
                if val:
                    out["artista" if tag == 0x013B else "copyright"] = val
    except Exception:
        pass
    return out


# Paleta padrão do Tailwind (v3; a v4 usa OKLCH com valores próximos) - tons 50..950
TW_SHADES = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
TW_PALETTE = {
    "slate": "f8fafc f1f5f9 e2e8f0 cbd5e1 94a3b8 64748b 475569 334155 1e293b 0f172a 020617",
    "gray": "f9fafb f3f4f6 e5e7eb d1d5db 9ca3af 6b7280 4b5563 374151 1f2937 111827 030712",
    "zinc": "fafafa f4f4f5 e4e4e7 d4d4d8 a1a1aa 71717a 52525b 3f3f46 27272a 18181b 09090b",
    "neutral": "fafafa f5f5f5 e5e5e5 d4d4d4 a3a3a3 737373 525252 404040 262626 171717 0a0a0a",
    "stone": "fafaf9 f5f5f4 e7e5e4 d6d3d1 a8a29e 78716c 57534e 44403c 292524 1c1917 0c0a09",
    "red": "fef2f2 fee2e2 fecaca fca5a5 f87171 ef4444 dc2626 b91c1c 991b1b 7f1d1d 450a0a",
    "orange": "fff7ed ffedd5 fed7aa fdba74 fb923c f97316 ea580c c2410c 9a3412 7c2d12 431407",
    "amber": "fffbeb fef3c7 fde68a fcd34d fbbf24 f59e0b d97706 b45309 92400e 78350f 451a03",
    "yellow": "fefce8 fef9c3 fef08a fde047 facc15 eab308 ca8a04 a16207 854d0e 713f12 422006",
    "lime": "f7fee7 ecfccb d9f99d bef264 a3e635 84cc16 65a30d 4d7c0f 3f6212 365314 1a2e05",
    "green": "f0fdf4 dcfce7 bbf7d0 86efac 4ade80 22c55e 16a34a 15803d 166534 14532d 052e16",
    "emerald": "ecfdf5 d1fae5 a7f3d0 6ee7b7 34d399 10b981 059669 047857 065f46 064e3b 022c22",
    "teal": "f0fdfa ccfbf1 99f6e4 5eead4 2dd4bf 14b8a6 0d9488 0f766e 115e59 134e4a 042f2e",
    "cyan": "ecfeff cffafe a5f3fc 67e8f9 22d3ee 06b6d4 0891b2 0e7490 155e75 164e63 083344",
    "sky": "f0f9ff e0f2fe bae6fd 7dd3fc 38bdf8 0ea5e9 0284c7 0369a1 075985 0c4a6e 082f49",
    "blue": "eff6ff dbeafe bfdbfe 93c5fd 60a5fa 3b82f6 2563eb 1d4ed8 1e40af 1e3a8a 172554",
    "indigo": "eef2ff e0e7ff c7d2fe a5b4fc 818cf8 6366f1 4f46e5 4338ca 3730a3 312e81 1e1b4b",
    "violet": "f5f3ff ede9fe ddd6fe c4b5fd a78bfa 8b5cf6 7c3aed 6d28d9 5b21b6 4c1d95 2e1065",
    "purple": "faf5ff f3e8ff e9d5ff d8b4fe c084fc a855f7 9333ea 7e22ce 6b21a8 581c87 3b0764",
    "fuchsia": "fdf4ff fae8ff f5d0fe f0abfc e879f9 d946ef c026d3 a21caf 86198f 701a75 4a044e",
    "pink": "fdf2f8 fce7f3 fbcfe8 f9a8d4 f472b6 ec4899 db2777 be185d 9d174d 831843 500724",
    "rose": "fff1f2 ffe4e6 fecdd3 fda4af fb7185 f43f5e e11d48 be123c 9f1239 881337 4c0519",
}
TW = {"white": "#ffffff", "black": "#000000"}
for _name, _hexes in TW_PALETTE.items():
    for _shade, _hex in zip(TW_SHADES, _hexes.split()):
        TW["{}-{}".format(_name, _shade)] = "#" + _hex


def tw_color(token, prefix):
    """'text-gray-400' -> '#9ca3af'; aceita text-[#999] e bg-white."""
    if not token.startswith(prefix + "-"):
        return None
    rest = token[len(prefix) + 1:]
    if "/" in rest:  # opacidade -> não calculável
        return None
    m = re.fullmatch(r"\[(#[0-9a-fA-F]{3,8}|rgb\([^\]]+\))\]", rest)
    if m:
        return m.group(1)
    return TW.get(rest)


# --------------------------------------------------------------------------
# Scanner
# --------------------------------------------------------------------------
class Scanner:
    def __init__(self, root, max_per_rule=15, include_tests=False):
        self.root = os.path.abspath(root)
        self.max_per_rule = max_per_rule
        self.include_tests = include_tests
        self.files = []          # dicts: rel, ext, text, name
        self.images = []         # (rel, size)
        self.fonts = []
        self.env_files = []
        self.findings = []
        self.rule_counts = defaultdict(int)
        self.deps = {}           # nome -> arquivo de manifesto
        self.doc_candidates = defaultdict(list)
        self.doc_files = set()
        self.p = OrderedDict()   # perfil
        self.p["stack"] = []
        self.p["sinais"] = OrderedDict()
        self.p["servicos_terceiros"] = []
        self.p["rastreadores"] = OrderedDict()
        self.p["cmp"] = []
        self.p["documentos_legais"] = OrderedDict()
        self.p["dados_em_formularios"] = defaultdict(set)
        self.p["dados_em_modelos"] = defaultdict(set)
        self.p["empresa"] = OrderedDict()
        self.p["imagens"] = 0
        self.p["fontes_locais"] = 0

    # ---------------------------------------------------------------- base
    def add(self, item, sev, rule, msg, f=None, pos=None, trecho=None, linha=None):
        self.rule_counts[rule] += 1
        if self.rule_counts[rule] > self.max_per_rule:
            return
        entry = OrderedDict([("item", item), ("severidade", sev), ("regra", rule), ("mensagem", msg)])
        if f is not None:
            entry["arquivo"] = f["rel"] if isinstance(f, dict) else f
            if isinstance(f, dict) and pos is not None:
                entry["linha"] = self.line_of(f, pos)
                entry["trecho"] = trecho if trecho is not None else self.snippet(f, pos)
            elif linha is not None:
                entry["linha"] = linha
        if trecho is not None and "trecho" not in entry:
            entry["trecho"] = trecho
        self.findings.append(entry)

    @staticmethod
    def _loc(ocorrencia):
        """'arquivo:12' -> {"f": "arquivo", "linha": 12} para add()."""
        m = re.fullmatch(r"(.+):(\d+)", ocorrencia)
        if m:
            return {"f": m.group(1), "linha": int(m.group(2))}
        return {}

    def line_of(self, f, pos):
        if f.get("_nl") is None:
            f["_nl"] = [m.start() for m in re.finditer("\n", f["text"])]
        return bisect.bisect_right(f["_nl"], pos) + 1

    def snippet(self, f, pos):
        text = f["text"]
        start = text.rfind("\n", 0, pos) + 1
        end = text.find("\n", pos)
        end = len(text) if end < 0 else end
        line = text[start:end].strip()
        if len(line) > 180:
            rel = pos - start
            line = ("…" if rel > 80 else "") + line[max(0, rel - 80):rel + 100] + "…"
        return line

    def sel(self, exts, skip_docs=False):
        for f in self.files:
            if f["ext"] in exts and not (skip_docs and f["rel"] in self.doc_files):
                yield f

    def walk(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORE_DIRS
                and not (d.startswith(".") and d not in {".well-known", ".github"})
                and (self.include_tests or d.lower() not in TEST_DIRS)
            ]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, self.root).replace("\\", "/")
                low = fn.lower()
                ext = os.path.splitext(low)[1]
                if low.startswith(".env"):
                    self.env_files.append(rel)
                    ext = ".env"
                try:
                    size = os.path.getsize(full)
                except OSError:
                    continue
                if ext in IMG_EXT:
                    self.images.append((rel, size, full))
                    continue
                if ext in FONT_EXT:
                    self.fonts.append(rel)
                    continue
                if ext not in TEXT_EXT and low not in {"gemfile", "requirements.txt", "dockerfile"}:
                    continue
                if low in SKIP_FILES or ".min." in low or low.endswith(".map") or size > MAX_BYTES:
                    continue
                if not self.include_tests and re.search(r"\.(test|spec|stories|cy)\.", low):
                    continue
                try:
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        text = fh.read()
                except OSError:
                    continue
                if len(text) > 200_000 and text.count("\n") < len(text) / 2000:
                    continue  # bundle minificado
                self.files.append({"rel": rel, "ext": ext, "text": text, "name": low, "_nl": None})

    # ------------------------------------------------------------ perfil
    def profile(self):
        stack = set()
        for f in self.files:
            name = f["name"]
            if name == "package.json":
                try:
                    data = json.loads(f["text"])
                except ValueError:
                    continue
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    for dep in (data.get(key) or {}):
                        self.deps.setdefault(dep, f["rel"])
            elif name in ("requirements.txt", "pyproject.toml", "pipfile", "composer.json", "gemfile",
                          "pubspec.yaml", "go.mod", "build.gradle", "pom.xml"):
                for m in re.finditer(r"[\"']?([A-Za-z0-9_.@/\-]+)[\"']?\s*(?:[=<>~^:]|$)", f["text"], re.M):
                    self.deps.setdefault(m.group(1).lower(), f["rel"])
        d = {k.lower() for k in self.deps}
        rels = {f["rel"].lower() for f in self.files}

        def has(*names):
            return any(n in d for n in names)

        if has("next"):
            stack.add("Next.js")
        if has("nuxt", "nuxt3"):
            stack.add("Nuxt")
        if has("react", "react-dom") and "Next.js" not in stack:
            stack.add("React")
        if has("vue") and "Nuxt" not in stack:
            stack.add("Vue")
        if has("svelte", "@sveltejs/kit"):
            stack.add("Svelte/SvelteKit")
        if has("astro"):
            stack.add("Astro")
        if has("@angular/core"):
            stack.add("Angular")
        if has("@remix-run/react", "@remix-run/node"):
            stack.add("Remix")
        if has("gatsby"):
            stack.add("Gatsby")
        if has("react-native", "expo"):
            stack.add("React Native/Expo")
        if has("express", "fastify", "koa", "hono", "@nestjs/core"):
            stack.add("Node.js (servidor)")
        if has("tailwindcss", "@tailwindcss/vite", "@tailwindcss/postcss"):
            stack.add("Tailwind CSS")
        if has("django"):
            stack.add("Django")
        if has("flask"):
            stack.add("Flask")
        if has("fastapi"):
            stack.add("FastAPI")
        if has("laravel/framework"):
            stack.add("Laravel")
        if has("rails"):
            stack.add("Ruby on Rails")
        if has("flutter") or any(r.endswith("pubspec.yaml") for r in rels):
            stack.add("Flutter")
        if any("wp-content/" in r or r.endswith("wp-config.php") for r in rels) or \
                any(r.endswith("style.css") and "theme name:" in f["text"].lower()[:2000]
                    for f in self.files for r in [f["rel"].lower()]):
            stack.add("WordPress")
        if any(r.endswith(".liquid") for r in rels):
            stack.add("Shopify (Liquid)")
        if not stack and any(r.endswith((".html", ".htm")) for r in rels):
            stack.add("HTML estático")
        self.p["stack"] = sorted(stack)

        for dep in sorted(self.deps):
            for pat, label, cat, foreign in SERVICES:
                if re.search(pat, dep, re.I):
                    if not any(s["nome"] == label for s in self.p["servicos_terceiros"]):
                        self.p["servicos_terceiros"].append(OrderedDict([
                            ("nome", label), ("finalidade", cat), ("exterior_provavel", foreign),
                            ("evidencia", "{} ({})".format(dep, self.deps[dep]))]))
                    break

        markup = [f for f in self.files if f["ext"] in MARKUP_EXT | PROSE_EXT]

        def count(rx):
            r = re.compile(rx, re.I)
            hits, where = 0, []
            for f in markup:
                n = len(r.findall(f["text"]))
                if n:
                    hits += n
                    if len(where) < 3:
                        where.append(f["rel"])
            return hits, where

        signals = OrderedDict()
        pay = [dep for dep in self.deps if PAYMENT_DEPS.search(dep)]
        sell_hits, sell_where = count(r"checkout|carrinho|add[-_ ]?to[-_ ]?cart|adicionar\s+ao\s+carrinho|comprar\s+agora|"
                                      r"finalizar\s+compra|assine\s+j[aá]|quero\s+comprar|\bR\$\s?\d")
        signals["vende_online"] = bool(pay) or sell_hits >= 3
        signals["vende_online_evidencias"] = (pay[:3] + sell_where)[:4]
        sub_hits, _ = count(r"assinatura|subscription|plano\s+(mensal|anual|pro|premium)|/m[eê]s\b|por\s+m[eê]s|per\s+month|renova[cç][aã]o")
        signals["assinatura_recorrente"] = sub_hits >= 2
        dig_hits, _ = count(r"\bcurso\b|e-?book|mentoria|infoproduto|hotmart|kiwify|eduzz|monetizze|videoaula|\baulas?\b|download\s+imediato")
        signals["produto_digital"] = dig_hits >= 3
        auth_hits, _ = count(r"type\s*=\s*[\"'{]?password|criar\s+conta|cadastre-se|sign\s*up|registr(ar|e-se)|esqueci\s+(a\s+)?senha")
        signals["login_cadastro"] = auth_hits > 0 or has("next-auth", "@clerk/nextjs", "passport", "@supabase/supabase-js",
                                                          "firebase", "@auth/core", "better-auth", "lucia")
        ugc_hits, _ = count(r"type\s*=\s*[\"'{]?file|coment[aá]rios?\b|deixe\s+(seu|um)\s+coment|publicar\s+(post|an[uú]ncio)|"
                            r"enviar\s+arquivo|upload")
        signals["conteudo_de_usuario"] = ugc_hits >= 2
        kid_hits, kid_where = count(r"crian[cç]as?|infantil|\bkids?\b|menores\s+de\s+(idade|1[2-8])|\bbeb[eê]s?\b|"
                                    r"educa[cç][aã]o\s+infantil|ensino\s+fundamental|brinquedos?|\bteens?\b|adolescentes?")
        signals["publico_infantil_ou_adolescente"] = kid_hits >= 2
        signals["publico_infantil_evidencias"] = kid_where
        health_hits, _ = count(r"pacientes?|cl[ií]nica|consult[oó]rio|prontu[aá]rio|agendar\s+consulta|\bm[eé]dic[oa]s?\b|"
                               r"psic[oó]log|nutricionist|odonto|fisioterap|telemedicina|exames?\b")
        signals["setor_saude"] = health_hits >= 3
        fin_hits, _ = count(r"empr[eé]stimo|cr[eé]dito\s+pessoal|investimentos?|cripto|consignado|financiamento|"
                            r"renda\s+fixa|day\s*trade|trader|op[cç][oõ]es\s+bin[aá]rias")
        signals["setor_financeiro"] = fin_hits >= 3
        pt_hits, _ = count(r"\b(voc[eê]|n[aã]o|p[aá]gina|pol[ií]tica|servi[cç]os|in[ií]cio|contato|sobre\s+n[oó]s|entrar)\b")
        en_hits, _ = count(r"\b(the|your|privacy|about\s+us|sign\s+in|contact\s+us|learn\s+more)\b")
        signals["idioma_principal"] = "pt-BR" if pt_hits >= en_hits else "en"
        signals["publico_estrangeiro_provavel"] = en_hits > 30 and any(
            re.search(r"(^|/)(locales?|i18n|lang|messages)/(en|es|fr|de)", f["rel"]) for f in self.files)
        signals["tem_backend"] = any(BACKEND_DEPS.match(dep) for dep in self.deps) or any(
            re.search(r"(^|/)(api|server|backend|routes|controllers)/", f["rel"]) for f in self.files)
        self.p["sinais"] = signals

    # ------------------------------------------------------- documentos
    def find_docs(self):
        """Localiza documentos legais antes das demais checagens, para que o
        texto deles (que cita Google Analytics, garantia etc.) não gere
        falsos positivos de rastreador ou promessa."""
        candidates_text = defaultdict(str)
        for f in self.sel(MARKUP_EXT | PROSE_EXT | {".json"}):
            rel_low = f["rel"].lower()
            if re.search(r"(^|/)(readme|changelog|contributing|license|code_of_conduct)", rel_low):
                continue
            plain = None
            for key, (path_rx, content_rx) in DOCS.items():
                path_hit = re.search(path_rx, rel_low) is not None
                hits = len(re.findall(content_rx, f["text"], re.I))
                if not path_hit and hits < 2:
                    continue
                if plain is None:
                    plain = strip_tags(f["text"]) if f["ext"] != ".json" else f["text"]
                if len(plain) >= 1000:
                    self.doc_candidates[key].append(f["rel"])
                    self.doc_files.add(f["rel"])
                    candidates_text[key] += "\n" + plain
                elif path_hit and re.search(r"(^|/)(pages?|app|routes|views|templates|src/pages)/|\.html?$", rel_low):
                    self.doc_candidates[key + "_curta"].append(f["rel"])

        links = defaultdict(list)
        for f in self.sel(MARKUP_EXT, skip_docs=True):
            for key, rx in DOC_LINK.items():
                m = re.search(r"(?:href|to|path|url|link|route)\s*[=:]\s*[{\"'`(\[]\s*[\"'`]?[^\"'`\n]{0,120}?(?:" + rx + r")", f["text"], re.I)
                if m and len(links[key]) < 3:
                    links[key].append(f["rel"])
        self.candidates_text = candidates_text
        self.links = links

    def check_docs(self):
        candidates_text, links = self.candidates_text, self.links
        sig = self.p["sinais"]
        collects = sig.get("login_cadastro") or bool(self.p["dados_em_formularios"]) or bool(self.p["rastreadores"])
        for key in DOCS:
            self.p["documentos_legais"][key] = OrderedDict([
                ("arquivos", self.doc_candidates.get(key, [])),
                ("paginas_curtas_ou_dinamicas", self.doc_candidates.get(key + "_curta", [])),
                ("linkado_em", links.get(key, [])),
            ])

        # 1 - privacidade
        priv = candidates_text.get("privacidade", "")
        if not priv:
            short = self.doc_candidates.get("privacidade_curta")
            if short:
                self.add(1, "alto", "privacidade-curta-ou-dinamica",
                         "Há rota de política de privacidade, mas com pouco texto no código (conteúdo vem de CMS/arquivo externo?) - confirme o conteúdo publicado",
                         short[0])
            else:
                self.add(1, "critico" if collects else "alto", "privacidade-ausente",
                         "Política de privacidade não encontrada. Exigida pela LGPD (arts. 6º VI, 9º) e Marco Civil (art. 7º, VIII e XI)"
                         + (" - o projeto coleta dados pessoais." if collects else "."))
        else:
            missing = [label for label, rx in PRIVACY_REQ if not re.search(rx, priv, re.I)]
            if missing:
                self.add(1, "alto" if len(missing) > 3 else "medio", "privacidade-incompleta",
                         "Política de privacidade sem: " + "; ".join(missing), self.doc_candidates["privacidade"][0])
            if re.search(r"\[(nome|empresa|cnpj|endere[cç]o|e-?mail)[^\]]*\]|nome\s+da\s+(sua\s+)?empresa|seu\s+site\s+aqui|"
                         r"example\.com|lorem\s+ipsum|xx\.xxx\.xxx|\[\[PREENCHER", priv, re.I):
                self.add(1, "alto", "privacidade-modelo-nao-preenchido",
                         "Política de privacidade contém marcadores de modelo não preenchidos", self.doc_candidates["privacidade"][0])
            if sig.get("idioma_principal") == "pt-BR" and not re.search(r"\b(dados|pessoais|voc[eê])\b", priv, re.I):
                self.add(1, "alto", "privacidade-idioma",
                         "Política de privacidade não está em português (CDC art. 31; LGPD art. 9º exige informação clara)",
                         self.doc_candidates["privacidade"][0])
            mentioned_missing = []
            for name, info in self.p["rastreadores"].items():
                if not re.search(info["kw"], priv, re.I):
                    mentioned_missing.append(name)
            for svc in self.p["servicos_terceiros"]:
                first = re.escape(svc["nome"].split(" ")[0].split("(")[0])
                if first and not re.search(first, priv, re.I) and not re.search(svc["finalidade"].split("/")[0], priv, re.I):
                    mentioned_missing.append(svc["nome"])
            if mentioned_missing:
                self.add(1, "alto", "privacidade-nao-bate-com-codigo",
                         "A política não menciona serviços/rastreadores que estão no código: " + ", ".join(sorted(set(mentioned_missing))),
                         self.doc_candidates["privacidade"][0])
            foreign = [s["nome"] for s in self.p["servicos_terceiros"] if s["exterior_provavel"]] + \
                [n for n, i in self.p["rastreadores"].items() if i["categoria"] != "sem_cookies"]
            if foreign and not re.search(r"transfer[eê]ncia\s+internacional|fora\s+do\s+brasil|outros\s+pa[ií]ses|no\s+exterior|servidores\s+localizados", priv, re.I):
                self.add(1, "alto", "privacidade-sem-transferencia-internacional",
                         "Há serviços com servidores provavelmente no exterior ({}) e a política não trata de transferência internacional (LGPD art. 33; Res. CD/ANPD 19/2024)".format(
                             ", ".join(foreign[:5])), self.doc_candidates["privacidade"][0])
            if not links.get("privacidade"):
                self.add(1, "medio", "privacidade-sem-link",
                         "Política existe mas não encontrei link para ela (rodapé, formulários, cadastro)", self.doc_candidates["privacidade"][0])

        # 2 - termos
        terms = candidates_text.get("termos", "")
        needs_terms = sig.get("vende_online") or sig.get("login_cadastro") or sig.get("conteudo_de_usuario")
        if not terms:
            if self.doc_candidates.get("termos_curta"):
                self.add(2, "medio", "termos-curto-ou-dinamico",
                         "Rota de termos com pouco texto no código - confirme o conteúdo publicado", self.doc_candidates["termos_curta"][0])
            else:
                self.add(2, "alto" if needs_terms else "baixo", "termos-ausente",
                         "Termos de uso/serviço não encontrados" + (" - o projeto tem venda, cadastro ou conteúdo de usuário (CDC arts. 46 e 54; Decreto 7.962/2013 art. 4º)" if needs_terms else " (recomendável)"))
        else:
            missing = [label for label, rx in TERMS_REQ if not re.search(rx, terms, re.I)]
            if missing:
                self.add(2, "medio", "termos-incompletos", "Termos sem: " + "; ".join(missing), self.doc_candidates["termos"][0])
            if not links.get("termos"):
                self.add(2, "medio", "termos-sem-link", "Termos existem mas não encontrei link para eles", self.doc_candidates["termos"][0])

        # cláusulas abusivas em qualquer documento
        for key in ("termos", "reembolso", "privacidade"):
            for rel in self.doc_candidates.get(key, []):
                f = next(x for x in self.files if x["rel"] == rel)
                for rx, sev, msg in ABUSIVE_CLAUSES:
                    for m in re.finditer(rx, f["text"], re.I):
                        self.add(4 if key == "reembolso" else 2, sev, "clausula-abusiva", msg, f, m.start())
                        break

        # 4 - reembolso
        refund = candidates_text.get("reembolso", "")
        if sig.get("vende_online"):
            if not refund and not re.search(r"arrependimento|7\s*\(?sete\)?\s*dias|sete\s+dias", terms, re.I):
                self.add(4, "alto", "reembolso-ausente",
                         "Projeto vende online e não há política de reembolso/arrependimento (CDC art. 49; Decreto 7.962/2013 art. 5º)")
            elif refund:
                ref_file = self.doc_candidates["reembolso"][0]
                if not re.search(r"arrependimento|7\s*\(?sete\)?\s*dias|sete\s+dias|7\s+dias\s+corridos", refund, re.I):
                    self.add(4, "alto", "reembolso-sem-arrependimento",
                             "Política de reembolso não menciona o direito de arrependimento de 7 dias (CDC art. 49)", ref_file)
                if not re.search(r"estorno|reembols|devolu[cç][aã]o\s+(do|dos)\s+valor", refund, re.I):
                    self.add(4, "medio", "reembolso-sem-forma-de-devolucao",
                             "Não explica como e em quanto tempo o valor é devolvido (CDC art. 49, par. único; Decreto 7.962 art. 5º §3º)", ref_file)
                if not re.search(r"v[ií]cio|defeito|garantia\s+legal|30\s*\(?trinta\)?\s*dias|90\s*\(?noventa\)?\s*dias", refund, re.I):
                    self.add(4, "medio", "reembolso-sem-vicio",
                             "Não trata de produto/serviço com defeito e garantia legal (CDC arts. 18, 20 e 26)", ref_file)
                f = next(x for x in self.files if x["rel"] == ref_file)
                m = re.search(r"(frete|custos?\s+de\s+(envio|devolu[cç][aã]o|postagem))[^.]{0,120}(por\s+conta|[ée]\s+de\s+responsabilidade|pago|arcad)\s+(do|pelo)\s+(cliente|comprador|consumidor)", f["text"], re.I)
                if m:
                    self.add(4, "alto", "reembolso-frete-consumidor",
                             "Atribui frete/devolução ao consumidor - no arrependimento (art. 49) o fornecedor arca com tudo; só é válido para trocas por mera preferência fora do prazo de 7 dias",
                             f, m.start())
                m = re.search(r"(\b[1-6]\s*\(?(um|dois|tr[eê]s|quatro|cinco|seis)?\)?\s*dias|\b(24|48|72)\s*h(oras)?)[^.]{0,80}(arrepend|desist|cancel|reembols)|"
                              r"(arrepend|desist|reembols)[^.]{0,80}(\b[1-6]\s*\(?(um|dois|tr[eê]s|quatro|cinco|seis)?\)?\s*dias|\b(24|48|72)\s*h(oras)?)", f["text"], re.I)
                if m:
                    self.add(4, "alto", "reembolso-prazo-menor",
                             "Prazo de arrependimento/cancelamento possivelmente menor que 7 dias (CDC art. 49 é piso)", f, m.start())
                if not links.get("reembolso"):
                    self.add(4, "medio", "reembolso-sem-link", "Política de reembolso sem link visível (checkout/rodapé)", ref_file)
        elif not refund:
            self.add(4, "info", "reembolso-nao-aplicavel", "Não detectei venda online - política de reembolso provavelmente não se aplica (confirmar)")

        if not candidates_text.get("acessibilidade"):
            self.add(8, "baixo", "declaracao-acessibilidade-ausente",
                     "Sem declaração de acessibilidade (boa prática; LBI art. 63 e ABNT NBR 17225)")

    # ------------------------------------------------- rastreadores/cookies
    def check_trackers(self):
        exts = MARKUP_EXT | CODE_EXT | {".json", ".env", ".yml", ".yaml"}
        compiled = [(n, re.compile(rx), c, kw) for n, rx, c, kw in TRACKERS]
        for f in self.sel(exts, skip_docs=True):
            if f["name"] == "package.json":
                continue
            for name, rx, cat, kw in compiled:
                m = rx.search(f["text"])
                if m:
                    info = self.p["rastreadores"].setdefault(name, OrderedDict([
                        ("categoria", cat), ("kw", kw), ("ocorrencias", [])]))
                    if len(info["ocorrencias"]) < 5:
                        info["ocorrencias"].append("{}:{}".format(f["rel"], self.line_of(f, m.start())))
            m = CMP_RE.search(f["text"])
            if m and len(self.p["cmp"]) < 5:
                self.p["cmp"].append("{}:{} ({})".format(f["rel"], self.line_of(f, m.start()), m.group(0)))
        for dep in self.deps:
            for name, rx, cat, kw in compiled:
                if rx.search(dep) and name not in self.p["rastreadores"]:
                    self.p["rastreadores"][name] = OrderedDict([("categoria", cat), ("kw", kw),
                                                                ("ocorrencias", ["dependência " + dep])])
            if CMP_RE.search(dep) and len(self.p["cmp"]) < 5:
                self.p["cmp"].append("dependência " + dep)

        needs = OrderedDict((n, i) for n, i in self.p["rastreadores"].items() if i["categoria"] in CONSENT_CATS)
        has_cmp = bool(self.p["cmp"])
        if needs and not has_cmp:
            self.add(3, "critico", "cookies-sem-consentimento",
                     "Rastreadores/cookies não essenciais sem gestão de consentimento: {}. Precisam ser bloqueados até o aceite "
                     "(LGPD arts. 7º I e 8º; Marco Civil art. 7º IX; Guia de Cookies da ANPD)".format(", ".join(needs)))
        for name, info in needs.items():
            sev = "alto" if info["categoria"] in {"publicidade", "gravacao", "marketing"} else "medio"
            self.add(7, sev if not has_cmp else "medio", "rastreador-" + info["categoria"],
                     "{} ({}) - {}".format(name, CAT_LABEL[info["categoria"]],
                                           "confirme que só carrega após consentimento" if has_cmp else "carrega sem consentimento"),
                     **self._loc(info["ocorrencias"][0]),
                     trecho=("também em: " + "; ".join(info["ocorrencias"][1:])) if len(info["ocorrencias"]) > 1 else None)
        if any(n in self.p["rastreadores"] for n in ("Google Analytics", "Google Tag Manager", "Google Ads / DoubleClick")):
            if not any(CONSENT_DEFAULT_RE.search(f["text"]) for f in self.sel(MARKUP_EXT)):
                self.add(7, "alto" if has_cmp else "medio", "consent-mode-ausente",
                         "Google Consent Mode v2 sem estado padrão 'denied' (gtag('consent','default',{...:'denied'})) - "
                         "exigido pelo Google para medição/anúncios com consentimento e evita coleta antes do aceite")
        for name in ("Hotjar", "Microsoft Clarity", "FullStory", "Smartlook", "Mouseflow", "Lucky Orange", "Sentry Session Replay"):
            if name in self.p["rastreadores"]:
                self.add(7, "alto", "gravacao-sessao",
                         "{} grava a sessão do usuário: exija consentimento, mascare campos de formulário e cite na política".format(name),
                         trecho="; ".join(self.p["rastreadores"][name]["ocorrencias"]))
        for f in self.sel(MARKUP_EXT, skip_docs=True):
            m = re.search(r"fbq\(\s*['\"]init['\"]\s*,\s*['\"]?\d+['\"]?\s*,\s*\{", f["text"])
            if m:
                self.add(7, "alto", "pixel-advanced-matching",
                         "Meta Pixel com correspondência avançada (envia e-mail/telefone ao Meta) - requer consentimento e transparência", f, m.start())
            m = BANNER_RE.search(f["text"])
            if m:
                if not REJECT_RE.search(f["text"]):
                    self.add(3, "alto", "banner-sem-rejeitar",
                             "Banner de cookies sem opção de rejeitar com a mesma facilidade de aceitar (Guia de Cookies ANPD)", f, m.start())
                if not re.search(r"prefer[eê]ncias|personalizar|configurar|gerenciar|customize|manage|settings", f["text"], re.I):
                    self.add(3, "medio", "banner-sem-granularidade",
                             "Banner de cookies sem opção de escolher por categoria", f, m.start())
            m = TACIT_RE.search(f["text"])
            if m:
                self.add(3, "alto", "consentimento-tacito",
                         "Consentimento tácito ('ao continuar navegando…') não é válido - consentimento deve ser inequívoco (LGPD art. 5º XII e 8º)", f, m.start())
            m = re.search(r"type\s*=\s*[\"']checkbox[\"'][^>]{0,200}(checked|defaultChecked)[^>]{0,200}>[^<]{0,200}(marketing|publicidade|an[uú]ncios|estat[ií]stic|analytics)", f["text"], re.I)
            if m:
                self.add(3, "alto", "cookies-pre-marcados", "Categorias de cookies não essenciais pré-marcadas", f, m.start())
        if needs and has_cmp:
            self.add(3, "info", "cmp-detectada",
                     "Gestão de consentimento detectada ({}) - confirme manualmente que os scripts só disparam após o aceite".format(self.p["cmp"][0]))
        if not candidates_any(self.doc_candidates, "cookies") and needs:
            self.add(3, "medio", "politica-cookies-ausente",
                     "Sem política/seção de cookies listando cada cookie, finalidade, duração e fornecedor (confira se a política de privacidade cobre)")
        if "YouTube (embed com cookies)" in self.p["rastreadores"]:
            self.add(7, "medio", "youtube-nocookie",
                     "Embeds do YouTube definem cookies - use youtube-nocookie.com e/ou carregue só após consentimento",
                     trecho="; ".join(self.p["rastreadores"]["YouTube (embed com cookies)"]["ocorrencias"]))
        if "Google Fonts (servidor do Google)" in self.p["rastreadores"]:
            self.add(7, "baixo", "google-fonts-remoto",
                     "Google Fonts carregado do servidor do Google (envia IP do visitante) - prefira hospedar as fontes localmente")

    # ----------------------------------------------------------- formulários
    def check_forms(self):
        input_re = re.compile(r"<(input|select|textarea|Input|Select|Textarea|TextField|Field)\b(" + TAG + r")/?>", re.S)
        val_re = re.compile(r"(?:name|id|placeholder|aria-label|autocomplete|autoComplete|v-model|formControlName|ng-model|"
                            r"label|bind:value)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{\s*[`'\"]?([^}`'\"]*)[`'\"]?\s*\})")
        register_re = re.compile(r"register\(\s*[\"'`]([\w.]+)")
        for f in self.sel(MARKUP_EXT, skip_docs=True):
            text = f["text"]
            file_fields = set()
            for m in input_re.finditer(text):
                tag = m.group(0)
                ttype = (get_attr(tag, "type") or "").lower().strip("'\"")
                if ttype in ("hidden", "submit", "button", "reset", "image"):
                    continue
                vals = " ".join(next((g for g in vm.groups() if g), "") for vm in val_re.finditer(tag))
                vals += " " + " ".join(register_re.findall(tag))
                if ttype in ("email", "tel", "password", "date", "file"):
                    vals += " " + {"email": "email", "tel": "tel", "password": "", "date": "", "file": "foto"}[ttype]
                norm = camel_to_snake(vals)
                for label, level, rx in FIELD_PATTERNS:
                    if rx.search(norm):
                        file_fields.add(label)
                        self.p["dados_em_formularios"][label].add(f["rel"])
                        if level == "sensivel":
                            self.add(6, "alto", "dado-sensivel-formulario",
                                     "Coleta de dado pessoal sensível ({}) - exige hipótese do art. 11 da LGPD, finalidade específica e, em regra, consentimento destacado".format(label),
                                     f, m.start())
                        elif level == "atencao":
                            self.add(6, "medio", "dado-verificar-necessidade",
                                     "Campo '{}' - confirme se é indispensável à finalidade (LGPD art. 6º, III - necessidade)".format(label),
                                     f, m.start())
                if ttype == "checkbox" and re.search(r"(?<![\w-])(checked|defaultChecked)(\s*=\s*(\{?\s*true\s*\}?|[\"']checked[\"']|[\"']true[\"']))?(?=[\s/>])", tag):
                    ctx = text[max(0, m.start() - 250):m.end() + 300].lower()
                    if re.search(r"newsletter|marketing|ofertas|promo|novidades|comunica[cç]|whats|sms|parceir|autorizo|concordo|aceito|termos|pol[ií]tica", ctx):
                        self.add(5, "alto", "checkbox-pre-marcado",
                                 "Caixa de consentimento/aceite pré-marcada - consentimento deve ser ação afirmativa (LGPD art. 8º; ANPD)", f, m.start())
                    if re.search(r"seguro|garantia\s+estendida|doa[cç][aã]o|gorjeta|prote[cç][aã]o|assinatura|frete\s+expresso", ctx):
                        self.add(17, "alto", "adicional-pre-marcado",
                                 "Serviço adicional pré-selecionado no fluxo de compra - venda casada/prática abusiva (CDC art. 39, I e III)", f, m.start())
                if ttype == "checkbox" and has_attr(tag, "required"):
                    ctx = text[max(0, m.start() - 250):m.end() + 300].lower()
                    if re.search(r"newsletter|marketing|ofertas|promo|novidades|receber\s+(e-?mails|comunica)|whats|sms|parceir", ctx) and not re.search(r"termos|pol[ií]tica\s+de\s+privacidade", ctx):
                        self.add(5, "alto", "marketing-obrigatorio",
                                 "Consentimento de marketing marcado como obrigatório - não pode ser condição para o serviço (LGPD art. 8º e 9º §3º)", f, m.start())
            if file_fields and re.search(r"<form\b|onSubmit|handleSubmit|@submit|v-on:submit|\(ngSubmit\)|action\s*=", text):
                if not re.search(r"privacidade|privacy|privacid", text, re.I):
                    m = re.search(r"<form\b|onSubmit|handleSubmit|@submit|\(ngSubmit\)", text)
                    self.add(5, "medio", "formulario-sem-aviso",
                             "Formulário coleta {} sem link/aviso de privacidade neste arquivo (LGPD art. 9º - informar finalidade no momento da coleta)".format(
                                 ", ".join(sorted(file_fields))), f, m.start() if m else 0)
            m = re.search(r"(li|aceito|concordo|declaro)[^<\n]{0,140}(termos|pol[ií]tica)[^<\n]{0,140}(e\s+(aceito|desejo|quero|autorizo)\s+receber|newsletter|ofertas|comunica[cç][oõ]es\s+de\s+marketing)", text, re.I)
            if m:
                self.add(5, "alto", "consentimento-agrupado",
                         "Aceite de termos agrupado com consentimento de marketing - separe em caixas distintas (LGPD art. 8º §4º - finalidades determinadas)", f, m.start())
            for m in re.finditer(r"<form\b" + TAG + r"action\s*=\s*[\"']http://(?!localhost|127\.)", text, re.I):
                self.add(16, "alto", "form-http", "Formulário envia dados sem HTTPS (LGPD art. 46)", f, m.start())

    def check_models(self):
        sensitive_levels = {"atencao", "sensivel"}
        for f in self.files:
            rel = f["rel"].lower()
            if not (f["ext"] in {".prisma", ".sql"} or re.search(r"(^|/)(models?|schemas?|entit(y|ies)|migrations?|database/migrations|db)/", rel)):
                continue
            if f["ext"] not in CODE_EXT | MARKUP_EXT | {".php", ".rb"}:
                continue
            norm = camel_to_snake(f["text"])
            for label, level, rx in FIELD_PATTERNS:
                if level in sensitive_levels and rx.search(norm):
                    self.p["dados_em_modelos"][label].add(f["rel"])
                    if level == "sensivel":
                        self.add(16, "alto", "dado-sensivel-armazenado",
                                 "Dado sensível ({}) armazenado - exige base do art. 11, controles de acesso, e avaliar Relatório de Impacto (art. 38)".format(label),
                                 f["rel"])

    # -------------------------------------------------------- acessibilidade
    def check_a11y(self):
        any_skip = False
        pt = self.p["sinais"].get("idioma_principal") == "pt-BR"
        for f in self.sel(MARKUP_EXT, skip_docs=False):
            text = f["text"]
            if re.search(r"pular\s+para\s+(o\s+)?(conte[uú]do|principal)|skip\s+to\s+(main\s+)?content|skip-link|skip-to|#main-?content|#conteudo", text, re.I):
                any_skip = True

            for m in re.finditer(r"<html\b(" + TAG + r")>", text, re.I):
                lang = get_attr(m.group(0), "lang")
                if lang is None:
                    self.add(8, "medio", "html-sem-lang", "<html> sem atributo lang (WCAG 3.1.1)", f, m.start())
                elif pt and lang.lower().strip("'\" ").startswith("en"):
                    self.add(8, "medio", "html-lang-errado",
                             "Site em português com lang=\"{}\" - leitores de tela pronunciam errado (WCAG 3.1.1). Use pt-BR".format(lang), f, m.start())
            m = re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?(?![\d.])|userScalable\s*:\s*false|maximumScale\s*:\s*1(?![\d.])", text)
            if m:
                self.add(8, "medio", "zoom-bloqueado", "Zoom bloqueado na viewport (WCAG 1.4.4 - redimensionar texto)", f, m.start())

            # 9 - alt
            for m in re.finditer(r"<(img|Image|NextImage|amp-img|area)\b(" + TAG + r")/?>", text):
                tag = m.group(0)
                if re.search(r"\{\s*\.\.\.", tag):
                    continue
                alt = get_attr(tag, "alt")
                if alt is None and not has_attr(tag, "alt"):
                    if re.search(r"aria-hidden\s*=\s*[\"{]?\s*true|role\s*=\s*[\"'](presentation|none)", tag):
                        continue
                    self.add(9, "alto", "img-sem-alt",
                             "Imagem sem atributo alt (WCAG 1.1.1; LBI art. 63). Use alt descritivo ou alt=\"\" se decorativa", f, m.start())
                elif alt is not None:
                    a = alt.strip().strip("'\"`")
                    if re.fullmatch(r"(img|image|imagem|foto|photo|picture|figura|banner|icon|[ií]cone|untitled|sem\s+t[ií]tulo|alt|"
                                    r"[\w\-]+\.(png|jpe?g|gif|webp|svg|avif))", a, re.I):
                        self.add(9, "baixo", "alt-generico", "alt genérico/nome de arquivo (\"{}\") não descreve a imagem".format(a), f, m.start())
            for m in re.finditer(r"<input\b(" + TAG + r")>", text, re.I):
                if (get_attr(m.group(0), "type") or "").lower() == "image" and get_attr(m.group(0), "alt") is None:
                    self.add(9, "alto", "input-image-sem-alt", "<input type=image> sem alt", f, m.start())
            if f["ext"] in {".mdx"}:
                for m in re.finditer(r"!\[\s*\]\(", text):
                    self.add(9, "baixo", "markdown-img-sem-alt", "Imagem em Markdown sem texto alternativo", f, m.start())

            # 8 - rótulos de campos
            label_for = set(re.findall(r"(?<![\w-])(?:for|htmlFor)\s*=\s*[{\"']?\s*[\"'`]?([\w\-:]+)", text))
            for m in re.finditer(r"<(input|select|textarea)\b(" + TAG + r")/?>", text):
                tag = m.group(0)
                ttype = (get_attr(tag, "type") or "text").lower().strip("'\"")
                if ttype in ("hidden", "submit", "button", "reset", "image") or re.search(r"\{\s*\.\.\.", tag):
                    continue
                if re.search(r"aria-label|aria-labelledby|(?<![\w-])title\s*=", tag):
                    continue
                id_ = get_attr(tag, "id")
                if id_ and id_.strip("'\"` ") in label_for:
                    continue
                before = text[max(0, m.start() - 400):m.start()]
                if before.rfind("<label") > before.rfind("</label>"):
                    continue
                self.add(8, "medio", "campo-sem-rotulo",
                         "Campo sem rótulo acessível{} (WCAG 1.3.1, 3.3.2, 4.1.2)".format(
                             " - placeholder não substitui label" if has_attr(tag, "placeholder") else ""), f, m.start())

            # 8 - botões e links só com ícone
            for m in re.finditer(r"<(button|a)\b(" + TAG + r")>(.{0,1500}?)</\1>", text, re.S):
                attrs, inner = m.group(2), m.group(3)
                if re.search(r"aria-label|aria-labelledby|(?<![\w-])title\s*=|\{\s*\.\.\.", attrs):
                    continue
                if re.search(r"sr-only|visually-hidden|screen-reader|visuallyhidden|aria-label", inner):
                    continue
                visible = re.sub(r"<[^>]*>", "", re.sub(r"<svg\b.*?</svg>", "", inner, flags=re.S))
                if not visible.strip() and re.search(r"<svg|<i\b|<img|<[A-Z]\w*(Icon|Svg)\b|<Icon|<span\s+class=[\"'][^\"']*icon", inner):
                    if m.group(1) == "a" and not has_attr(attrs, "href"):
                        continue
                    self.add(8, "medio", "botao-icone-sem-nome",
                             "<{}> só com ícone e sem nome acessível (aria-label) (WCAG 4.1.2, 2.4.4)".format(m.group(1)), f, m.start())
                if m.group(1) == "a" and re.fullmatch(r"\s*(clique\s+aqui|aqui|saiba\s+mais|leia\s+mais|veja\s+mais|click\s+here|read\s+more|learn\s+more)\s*", visible, re.I):
                    self.add(8, "baixo", "link-generico", "Texto de link genérico (\"{}\") - descreva o destino (WCAG 2.4.4)".format(visible.strip()), f, m.start())

            # 8 - mídia
            for m in re.finditer(r"<video\b(" + TAG + r")>(.{0,2000}?)</video>", text, re.S | re.I):
                attrs, inner = m.group(1), m.group(2)
                if has_attr(attrs, "autoplay") and has_attr(attrs, "muted"):
                    if has_attr(attrs, "loop") and not has_attr(attrs, "controls"):
                        self.add(8, "baixo", "video-sem-pausa",
                                 "Vídeo em loop automático sem controle de pausa (WCAG 2.2.2 se durar > 5s)", f, m.start())
                elif "<track" not in inner.lower():
                    self.add(8, "medio", "video-sem-legenda", "Vídeo sem legendas (<track kind=\"captions\">) (WCAG 1.2.2)", f, m.start())
            for m in re.finditer(r"<audio\b(" + TAG + r")>", text, re.I):
                if has_attr(m.group(1), "autoplay"):
                    self.add(8, "medio", "audio-autoplay", "Áudio com reprodução automática (WCAG 1.4.2)", f, m.start())
            for m in re.finditer(r"<iframe\b(" + TAG + r")>", text, re.I):
                if not re.search(r"(?<![\w-])title\s*=", m.group(0)):
                    self.add(8, "baixo", "iframe-sem-title", "<iframe> sem title (WCAG 4.1.2)", f, m.start())
            m = re.search(r"accessibe|acsbapp|userway|equalweb|audioeye", text, re.I)
            if m:
                self.add(8, "info", "overlay-acessibilidade",
                         "Overlay de acessibilidade detectado - não substitui correções no código (há processos nos EUA contra sites que dependiam só dele)", f, m.start())

            # 11 - teclado
            for m in re.finditer(r"<(div|span|li|p|section|article|td|tr|img|i|svg|figure|header|footer)\b(" + TAG + r")>", text):
                tag = m.group(0)
                if not re.search(r"(?<![\w-])(onClick|onclick|@click|v-on:click|on:click|\(click\))\s*=", tag):
                    continue
                missing = []
                if not re.search(r"role\s*=", tag):
                    missing.append("role")
                if not re.search(r"tab[iI]ndex\s*=", tag):
                    missing.append("tabIndex")
                if not re.search(r"onKey(Down|Up|Press)|onkey(down|up|press)|@key(down|up)|v-on:key|on:key|\(key(down|up)", tag):
                    missing.append("tratador de teclado (Enter/Espaço)")
                if missing:
                    self.add(11, "alto", "clique-sem-teclado",
                             "<{}> clicável sem {} - inacessível por teclado (WCAG 2.1.1). Prefira <button>".format(m.group(1), ", ".join(missing)),
                             f, m.start())
            for m in re.finditer(r"<a\b(" + TAG + r")>", text):
                tag = m.group(0)
                if re.search(r"(?<![\w-])(onClick|onclick|@click|v-on:click)\s*=", tag) and not has_attr(tag, "href") and not re.search(r"\{\s*\.\.\.", tag):
                    self.add(11, "medio", "link-sem-href", "<a> com clique e sem href não recebe foco - use <button> (WCAG 2.1.1)", f, m.start())
            for m in re.finditer(r"tab[iI]ndex\s*=\s*[\"'{]?\s*([1-9]\d*)", text):
                self.add(11, "baixo", "tabindex-positivo", "tabindex positivo altera a ordem natural de foco (WCAG 2.4.3)", f, m.start())
            for m in re.finditer(r"class(?:Name)?\s*=\s*[{\"'`]+([^\"'`}]{0,800})", text):
                tokens = m.group(1).split()
                if any(t in ("outline-none", "focus:outline-none", "focus-visible:outline-none", "outline-0") for t in tokens):
                    if not any(re.match(r"(focus(-visible|-within)?|group-focus|peer-focus):(ring|outline-(?!none)|border|shadow|bg|underline|text)", t) or t.startswith("ring") for t in tokens):
                        self.add(11, "medio", "foco-removido-tailwind",
                                 "outline removido sem indicador de foco alternativo (WCAG 2.4.7 - foco visível)", f, m.start())

        for f in self.sel(STYLE_EXT | MARKUP_EXT):
            text = f["text"]
            if f["ext"] in MARKUP_EXT and "<style" not in text and "styled." not in text and "css`" not in text:
                continue
            for m in re.finditer(r"outline\s*:\s*(none|0)(?![.\d])", text):
                if not re.search(r":focus-visible|:focus\s*\{[^}]*(outline\s*:\s*(?!none|0)|box-shadow|border)", text):
                    self.add(11, "medio", "foco-removido-css",
                             "outline removido sem estilo :focus-visible alternativo no mesmo arquivo (WCAG 2.4.7)", f, m.start())
                    break
        if not any_skip and any(f["ext"] in MARKUP_EXT for f in self.files):
            self.add(11, "baixo", "sem-skip-link", "Sem link \"Pular para o conteúdo\" (WCAG 2.4.1 - bypass blocks)")

    # ------------------------------------------------------------ contraste
    def check_contrast(self):
        css_vars = {}
        style_sources = []
        for f in self.files:
            if f["ext"] in STYLE_EXT:
                style_sources.append((f, f["text"], 0))
            elif f["ext"] in MARKUP_EXT:
                for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", f["text"], re.S | re.I):
                    style_sources.append((f, m.group(1), m.start(1)))
        for _, css, _ in style_sources:
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}{]+)", css):
                css_vars.setdefault(m.group(1), m.group(2).strip())

        def resolve(v, depth=0):
            if v is None or depth > 5:
                return None
            v = v.strip()
            m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,\s*(.+))?\)", v)
            if m:
                inner = css_vars.get(m.group(1)) or m.group(2)
                return resolve(inner, depth + 1)
            if re.fullmatch(r"[\d.]+\s+[\d.]+%\s+[\d.]+%", v):  # convenção shadcn: "0 0% 45%"
                return "hsl({})".format(v.replace(" ", ", "))
            return v

        def evaluate(f, pos, fg_raw, bg_raw, large, where):
            fg, bg = parse_color(resolve(fg_raw)), parse_color(resolve(bg_raw))
            if not fg or not bg:
                return
            ratio = contrast_ratio(fg, bg)
            need = 3.0 if large else 4.5
            if ratio < need:
                sug = suggest(fg, bg, need)
                self.add(10, "alto" if ratio < 3 else "medio", "contraste-insuficiente",
                         "Contraste {:.2f}:1 ({} sobre {}) abaixo de {}:1 (WCAG 1.4.3){}{}".format(
                             ratio, to_hex(fg), to_hex(bg), need, " - " + where if where else "",
                             " | sugestão: {} ({:.2f}:1)".format(to_hex(sug), contrast_ratio(sug, bg)) if sug else ""),
                         f, pos)

        for f, css, base in style_sources:
            for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
                body = m.group(2)
                fgm = re.search(r"(?<![-\w])color\s*:\s*([^;!}]+)", body)
                bgm = re.search(r"background(?:-color)?\s*:\s*([^;!}]+)", body)
                if not fgm or not bgm:
                    continue
                bg_val = bgm.group(1).strip()
                if not parse_color(resolve(bg_val)):
                    cm = re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|var\(--[\w-]+\)", bg_val)
                    if not cm or "gradient" in bg_val or "url(" in bg_val:
                        continue
                    bg_val = cm.group(0)
                size = re.search(r"font-size\s*:\s*([\d.]+)(px|rem|em)", body)
                bold = re.search(r"font-weight\s*:\s*(bold|[7-9]00)", body)
                px = float(size.group(1)) * (16 if size and size.group(2) != "px" else 1) if size else 16
                large = px >= 24 or (px >= 18.66 and bold)
                lead = len(m.group(1)) - len(m.group(1).lstrip())
                evaluate(f, base + m.start() + lead, fgm.group(1), bg_val, large, "seletor " + m.group(1).strip()[:60])

        for f in self.sel(MARKUP_EXT):
            text = f["text"]
            for m in re.finditer(r"style\s*=\s*\"([^\"]*)\"", text):
                body = m.group(1)
                fgm = re.search(r"(?<![-\w])color\s*:\s*([^;]+)", body)
                bgm = re.search(r"background(?:-color)?\s*:\s*([^;]+)", body)
                if fgm and bgm:
                    evaluate(f, m.start(), fgm.group(1), bgm.group(1), False, "estilo inline")
            for m in re.finditer(r"style\s*=\s*\{\{([^}]*)\}\}", text):
                body = m.group(1)
                fgm = re.search(r"(?<![\w])color\s*:\s*['\"]([^'\"]+)['\"]", body)
                bgm = re.search(r"background(?:Color)?\s*:\s*['\"]([^'\"]+)['\"]", body)
                if fgm and bgm:
                    evaluate(f, m.start(), fgm.group(1), bgm.group(1), False, "estilo inline")
            for m in re.finditer(r"class(?:Name)?\s*=\s*[{\"'`]+([^\"'`}]{0,800})", text):
                tokens = [t for t in m.group(1).split() if ":" not in t]
                fg = next((c for c in (tw_color(t, "text") for t in tokens) if c), None)
                bg = next((c for c in (tw_color(t, "bg") for t in tokens) if c), None)
                large = any(t in tokens for t in ("text-2xl", "text-3xl", "text-4xl", "text-5xl", "text-6xl", "text-7xl", "text-8xl", "text-9xl")) or \
                    ("text-xl" in tokens and any(t in tokens for t in ("font-bold", "font-extrabold", "font-black")))
                if fg and bg:
                    evaluate(f, m.start(), fg, bg, large, "classes Tailwind")
                elif fg and not bg and not large:
                    rgb = parse_color(fg)
                    if rgb and contrast_ratio(rgb, (255, 255, 255)) < 3.0 and contrast_ratio(rgb, (0, 0, 0)) > 7:
                        self.add(10, "baixo", "contraste-texto-claro",
                                 "Texto claro ({}, {:.2f}:1 sobre branco) - se o fundo for claro, o contraste é insuficiente".format(
                                     to_hex(rgb), contrast_ratio(rgb, (255, 255, 255))), f, m.start())

    # ------------------------------------------------ avaliações e promessas
    def check_claims(self):
        exts = MARKUP_EXT | PROSE_EXT | {".json"}
        for f in self.sel(exts, skip_docs=True):
            text = f["text"]
            if f["name"] in ("package.json", "tsconfig.json", "composer.json") or f["rel"].lower().startswith(("docs/",)):
                continue
            m = FAKE_AVATAR_RE.search(text)
            if m:
                ctx = TESTIMONIAL_RE.search(text)
                self.add(12, "critico" if ctx else "alto", "avatar-gerado",
                         "Foto gerada/aleatória ({}) {}- depoimento com pessoa inexistente é publicidade enganosa (CDC art. 37 e 67; CONAR Anexo Q)".format(
                             m.group(0), "em seção de depoimentos " if ctx else ""), f, m.start())
            if f["ext"] in MARKUP_EXT and re.search(r"@faker-js/faker|from\s+['\"]faker['\"]|require\(['\"]faker", text):
                m = re.search(r"faker", text)
                self.add(12, "alto", "faker-em-producao", "Dados falsos (faker) usados em código de produção - confirme que não aparecem como clientes/avaliações reais", f, m.start())
            if TESTIMONIAL_RE.search(text):
                m = RATING_KEY_RE.search(text)
                if m:
                    self.add(12, "medio", "depoimentos-hardcoded",
                             "Depoimentos/avaliações fixos no código - confirme que são reais, autorizados (uso de nome/imagem) e representativos", f, m.start())
            m = re.search(r"[\"']?aggregateRating[\"']?\s*:", text)
            if m:
                self.add(12, "alto", "aggregate-rating-fixo",
                         "Nota agregada (schema.org aggregateRating) no código - precisa vir de avaliações reais e verificáveis", f, m.start())
            for m in SOCIAL_PROOF_RE.finditer(text):
                self.add(12, "medio", "prova-social-numerica",
                         "Número de prova social (\"{}\") - mantenha comprovação (CDC art. 38)".format(m.group(0).strip()[:60]), f, m.start())
                break

            for rx, sev, msg in PROMISES:
                for m in re.finditer(rx, text, re.I):
                    self.add(13, sev, "promessa-" + sev, msg + " - \"{}\"".format(m.group(0)[:60]), f, m.start())
                    break
            m = SCARCITY_RE.search(text)
            if m:
                self.add(13, "medio", "escassez", "Gatilho de escassez/urgência (\"{}\") - precisa ser verdadeiro (CDC art. 37 §1º)".format(m.group(0)[:50]), f, m.start())
            for m in re.finditer(r"Math\.random\(\)", text):
                ctx = text[max(0, m.start() - 400):m.end() + 400]
                if re.search(r"vendo|comprando|compraram|online\s+agora|visitantes|pessoas|estoque|unidades|vagas|restam|viewers|bought", ctx, re.I):
                    self.add(13, "critico", "prova-social-aleatoria",
                             "Contador de pessoas/estoque/vagas gerado com Math.random() - informação falsa ao consumidor (CDC art. 37 e 66)", f, m.start())
                    break
            if re.search(r"setInterval|setTimeout|countdown|useCountdown", text) and re.search(r"countdown|contagem\s+regressiva|cron[oô]metro|timer", text, re.I) \
                    and re.search(r"oferta|promo|desconto|pre[cç]o|black\s*friday", text, re.I):
                m = re.search(r"countdown|contagem\s+regressiva|cron[oô]metro|timer", text, re.I)
                self.add(13, "medio", "contador-regressivo",
                         "Contagem regressiva de oferta - confirme que o prazo é real e não reinicia a cada visita", f, m.start())
            m = PRICE_ANCHOR_RE.search(text) or re.search(r"line-through[^\n]{0,200}R\$|<(s|del|strike)\b[^>]*>\s*R\$", text)
            if m:
                self.add(13, "info", "preco-de-por",
                         "Preço \"de/por\" - o preço anterior precisa ter sido praticado de fato (desconto fictício é publicidade enganosa)", f, m.start())

    # -------------------------------------------------------------- imagens
    def check_images(self):
        self.p["imagens"] = len(self.images)
        self.p["fontes_locais"] = len(self.fonts)
        exif_found = 0
        for rel, size, full in self.images:
            name = os.path.basename(rel)
            if STOCK_NAME_RE.search(name):
                self.add(14, "alto", "imagem-banco-pago",
                         "Nome indica imagem de banco pago ({}) - confirme licença ativa e escopo (Lei 9.610/98 arts. 29 e 79)".format(STOCK_NAME_RE.search(name).group(0)), rel)
            elif FREEPIK_RE.search(name):
                self.add(14, "medio", "imagem-freepik", "Imagem do Freepik/Flaticon - licença gratuita exige atribuição; confirme o plano", rel)
            elif UNKNOWN_ORIGIN_RE.search(name):
                self.add(14, "medio", "imagem-origem-desconhecida",
                         "Nome sugere origem incerta (download, print, WhatsApp, banco gratuito) - confirme a licença/autoria", rel)
            if AI_IMAGE_RE.search(name):
                self.add(14, "info", "imagem-ia", "Imagem gerada por IA - verifique os termos da ferramenta e não a use como foto real de cliente/resultado", rel)
            if BRAND_FILE_RE.search(name):
                self.add(14, "baixo", "marca-terceiro",
                         "Possível marca/personagem de terceiro ({}) - uso comercial exige autorização (Lei 9.279/96)".format(BRAND_FILE_RE.search(name).group(0)), rel)
            if name.lower().endswith((".jpg", ".jpeg", ".tif", ".tiff", ".png", ".webp")) and size < 40_000_000:
                try:
                    with open(full, "rb") as fh:
                        head = fh.read(262144)
                except OSError:
                    continue
                m = STOCK_BYTES_RE.search(head)
                if m:
                    self.add(14, "alto", "metadado-banco-imagem",
                             "Metadados da imagem citam \"{}\" - confirme a licença (imagens de banco são rastreadas por robôs de cobrança)".format(
                                 m.group(0).decode("latin-1")), rel)
                    continue
                ex = exif_text(head)
                if ex.get("copyright") or ex.get("artista"):
                    exif_found += 1
                    self.add(14, "medio", "exif-copyright",
                             "EXIF indica autoria ({}) - precisa de licença e crédito ao fotógrafo (Lei 9.610/98 art. 79 §1º)".format(
                                 "; ".join("{}: {}".format(k, v) for k, v in ex.items())[:120]), rel)
        for rel in self.fonts:
            m = COMMERCIAL_FONT_RE.search(os.path.basename(rel))
            if m:
                self.add(14, "medio", "fonte-comercial",
                         "Arquivo de fonte comercial/de sistema ({}) distribuído pelo site - requer licença de uso web".format(m.group(0)), rel)
        for f in self.sel(MARKUP_EXT | STYLE_EXT | {".json", ".md"}, skip_docs=True):
            for m in HOTLINK_RE.finditer(f["text"]):
                self.add(14, "alto", "imagem-hotlink",
                         "Imagem carregada de Google Imagens/Pinterest/redes/banco de imagens - não há licença implícita", f, m.start())
        if self.images:
            self.add(14, "info", "imagens-confirmar-origem",
                     "{} arquivo(s) de imagem no projeto - a origem/licença precisa ser confirmada pelo responsável".format(len(self.images)))

    # -------------------------------------------------------------- empresa
    def check_company(self):
        emp = self.p["empresa"]
        emp["cnpj_validos"], emp["cnpj_invalidos"], emp["cnpj_locais"] = [], [], []
        emp["emails"], emp["telefones"], emp["enderecos"], emp["razao_social"] = [], [], [], []
        placeholder = None
        for f in self.sel(MARKUP_EXT | PROSE_EXT | {".json", ".yml", ".yaml"}):
            text = f["text"]
            for m in re.finditer(r"(?<![\w.])([0-9A-Z]{2}\.[0-9A-Z]{3}\.[0-9A-Z]{3}/[0-9A-Z]{4}-\d{2}|\d{14})(?![\w])", text):
                raw = m.group(1)
                if len(raw) == 14 and not re.search(r"cnpj", text[max(0, m.start() - 40):m.start()], re.I):
                    continue
                if re.fullmatch(r"0{2}\.?0{3}\.?0{3}/?0{4}-?0{2}", raw):
                    placeholder = (f, m.start())
                    continue
                target = emp["cnpj_validos"] if cnpj_valid(raw) else emp["cnpj_invalidos"]
                if raw not in target:
                    target.append(raw)
                    emp["cnpj_locais"].append("{}:{}".format(f["rel"], self.line_of(f, m.start())))
                if target is emp["cnpj_invalidos"]:
                    self.add(15, "alto", "cnpj-invalido", "CNPJ {} com dígitos verificadores inválidos".format(raw), f, m.start())
            m = re.search(r"xx\.xxx\.xxx/xxxx-xx|\[\s*cnpj\s*\]|seu\s+cnpj|cnpj\s+aqui|\[\[PREENCHER", text, re.I)
            if m:
                placeholder = (f, m.start())
            for m in re.finditer(r"(?<![\w.+-])[\w.+-]+@[\w-]+\.[\w.-]+", text):
                e = m.group(0).rstrip(".")
                if re.search(r"example\.|exemplo\.|seu-?email|email@|user@|@email\.|@dominio|\.(png|jpe?g|svg|webp)$|@\d|noreply|no-reply|sentry|@types|@vercel", e, re.I):
                    continue
                if e not in emp["emails"] and len(emp["emails"]) < 5:
                    emp["emails"].append(e)
            for m in re.finditer(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]\d{4}(?!\d)", text):
                if len(emp["telefones"]) < 3 and m.group(0) not in emp["telefones"]:
                    emp["telefones"].append(m.group(0))
            for m in re.finditer(r"\b(rua|r\.|av\.|avenida|alameda|al\.|rodovia|travessa|pra[cç]a|estrada)\s+[A-ZÀ-Úa-zà-ú0-9][^<\n\"]{3,80}?(\d{5}-\d{3}|,\s*\d+)", text, re.I):
                if len(emp["enderecos"]) < 3:
                    emp["enderecos"].append(m.group(0).strip()[:100])
            for m in re.finditer(r"\b[A-ZÀ-Ú][\w&.\- ]{2,60}?\s(LTDA|Ltda\.?|S\.A\.|S/A|EIRELI|EPP)\b", text):
                if len(emp["razao_social"]) < 3 and m.group(0) not in emp["razao_social"]:
                    emp["razao_social"].append(m.group(0).strip())
        sig = self.p["sinais"]
        if placeholder:
            self.add(15, "alto", "dados-empresa-placeholder", "Dados da empresa com marcador de modelo (CNPJ fictício/[CNPJ])", placeholder[0], placeholder[1])
        if sig.get("vende_online"):
            has_cpf = any(re.search(r"CPF\s*(n[ºo°.]*)?\s*:?\s*\d{3}\.\d{3}\.\d{3}-\d{2}", f["text"])
                          for f in self.sel(MARKUP_EXT | PROSE_EXT))
            if not emp["cnpj_validos"] and not has_cpf:
                self.add(15, "alto", "empresa-sem-cnpj",
                         "Loja/serviço pago sem nome empresarial e CNPJ válido (ou CPF) visíveis - Decreto 7.962/2013, art. 2º, I")
            if not emp["enderecos"]:
                self.add(15, "medio", "empresa-sem-endereco",
                         "Endereço físico não encontrado - Decreto 7.962/2013, art. 2º, II")
            if not emp["emails"] and not emp["telefones"]:
                self.add(15, "medio", "empresa-sem-contato",
                         "Sem canal de atendimento (e-mail/telefone) visível - Decreto 7.962/2013, arts. 2º II e 4º V")
            if emp["cnpj_validos"] and not any(re.search(r"footer|rodape|layout|base|_app|app\.(vue|svelte|tsx|jsx)|index\.html?$", loc, re.I)
                                               for loc in emp["cnpj_locais"]):
                self.add(15, "baixo", "cnpj-fora-do-rodape",
                         "CNPJ aparece só em páginas internas - o decreto pede local de destaque e fácil visualização (ex.: rodapé de todas as páginas)")
        elif not emp["emails"] and not emp["telefones"]:
            self.add(15, "baixo", "sem-contato", "Nenhum canal de contato encontrado no site")

    # ------------------------------------------------------- LGPD/segurança
    def check_lgpd(self):
        sig = self.p["sinais"]
        all_text_files = list(self.sel(MARKUP_EXT | PROSE_EXT | {".json"}))
        rights = any(re.search(r"direitos\s+do\s+titular|exercer\s+(os\s+)?seus\s+direitos|privacidade@|dpo@|encarregado@|lgpd@|"
                               r"solicita[cç][aã]o\s+(de\s+)?(exclus|acesso)\s+(de|aos)\s+dados", f["text"], re.I) for f in all_text_files)
        if not rights:
            self.add(16, "alto", "sem-canal-titular",
                     "Sem canal para o titular exercer direitos (acesso, correção, exclusão, portabilidade) - LGPD arts. 18 e 41; até agente de pequeno porte deve ter canal (Res. CD/ANPD 2/2022)")
        if not any(re.search(r"encarregad|\bdpo\b|data\s+protection\s+officer", f["text"], re.I) for f in all_text_files):
            self.add(16, "medio", "sem-encarregado",
                     "Encarregado (DPO) não identificado publicamente - LGPD art. 41 §1º (dispensa só para agente de pequeno porte, Res. CD/ANPD 2/2022)")

        code = [f for f in self.files if f["ext"] in MARKUP_EXT | CODE_EXT | CONFIG_EXT]
        dep_names = " ".join(self.deps)
        has_password = any(re.search(r"type\s*=\s*[\"'{]?\s*[\"']?password", f["text"]) for f in self.files if f["ext"] in MARKUP_EXT)
        if sig.get("login_cadastro"):
            if not any(re.search(r"(delete|excluir|apagar|deletar|remover|encerrar|destroy)[\s_\-]?(minha[\s_\-])?(account|conta|usu[aá]rio|user|perfil|profile|me)\b|deleteUser|account/delete",
                                 f["text"], re.I) for f in code):
                self.add(16, "medio", "sem-exclusao-conta",
                         "Não encontrei fluxo de exclusão de conta/dados - LGPD art. 18, VI (e exigência da App Store/Google Play para apps)")
            if has_password and sig.get("tem_backend") and not HASH_DEPS.search(dep_names) and not MANAGED_AUTH.search(dep_names) \
                    and not any(re.search(r"password_hash\(|Hash::make|bcrypt|argon2|scrypt|pbkdf2|has_secure_password|make_password|generate_password_hash", f["text"]) for f in code):
                self.add(16, "alto", "senha-sem-hash",
                         "Há senha no cadastro e não encontrei hash de senha (bcrypt/argon2/scrypt) nem autenticação gerenciada - LGPD art. 46")
        for f in code:
            text = f["text"]
            for label, rx, sev in SECRET_PATTERNS:
                for m in re.finditer(rx, text):
                    is_env = f["ext"] == ".env"
                    if is_env and re.search(r"\.env(\.(example|sample|template|dist))$", f["rel"]):
                        continue
                    if is_env and sev == "critico":
                        sev_use = "medio"
                        msg = "{} em arquivo .env - confirme que não está versionado no Git".format(label)
                    else:
                        sev_use = sev
                        msg = "{} exposta no código-fonte - revogue/rotacione e mova para variável de ambiente (LGPD art. 46)".format(label)
                    self.add(16, sev_use, "segredo-exposto", msg, f, m.start(), trecho=mask(m.group(0)))
                    break
            m = re.search(r"console\.(log|info|debug)\([^)\n]{0,200}\b(cpf|senha|password|card(Number)?|cartao|cvv)\b", text, re.I)
            if m:
                self.add(16, "medio", "log-dado-pessoal", "Log de dado pessoal/sensível no console", f, m.start())
            m = re.search(r"(localStorage|sessionStorage)\.setItem\(\s*[\"'`][^\"'`]*(cpf|senha|password|card|cartao|cvv|rg)\b", text, re.I)
            if m:
                self.add(16, "alto", "storage-dado-pessoal", "Dado pessoal/sensível gravado no localStorage (acessível a qualquer script da página)", f, m.start())
            m = re.search(r"fetch\(\s*[\"'`]http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)|axios\.\w+\(\s*[\"'`]http://(?!localhost|127\.)", text)
            if m:
                self.add(16, "medio", "requisicao-http", "Requisição sem HTTPS para servidor externo", f, m.start())
        env_real = [e for e in self.env_files if not re.search(r"\.(example|sample|template|dist)$", e)]
        if env_real:
            gi = os.path.join(self.root, ".gitignore")
            ignored = False
            if os.path.exists(gi):
                with open(gi, encoding="utf-8", errors="replace") as fh:
                    ignored = re.search(r"^\s*\*?\.env", fh.read(), re.M) is not None
            if not ignored:
                self.add(16, "alto", "env-nao-ignorado", ".env presente e não listado no .gitignore - risco de vazar credenciais", env_real[0])
        if self.p["dados_em_formularios"].get("dados de cartão"):
            if not re.search(r"stripe|mercadopago|pagarme|pagseguro|asaas|iugu|adyen|cielo|getnet|braintree|efipay|gerencianet", dep_names, re.I):
                self.add(16, "alto", "cartao-sem-tokenizacao",
                         "Formulário próprio de cartão sem SDK de tokenização do gateway - risco PCI DSS e de vazamento")
        ais = [s["nome"] for s in self.p["servicos_terceiros"] if s["nome"] in AI_SERVICES]
        if ais:
            self.add(16, "info", "ia-terceiro",
                     "Dados podem ser enviados a provedor de IA ({}) - informe na política, avalie dados sensíveis e transferência internacional".format(", ".join(ais)))
        if sig.get("publico_infantil_ou_adolescente"):
            self.add(16, "alto", "publico-infantil",
                     "Sinais de público infantil/adolescente ({}) - LGPD art. 14 e ECA Digital (Lei 15.211/2025, em vigor desde 17/03/2026): "
                     "melhor interesse, consentimento parental, sem perfilamento para publicidade, verificação etária quando aplicável".format(
                         ", ".join(sig.get("publico_infantil_evidencias", [])[:2])))
        if sig.get("setor_saude"):
            self.add(16, "medio", "setor-saude",
                     "Projeto da área da saúde - dados de saúde são sensíveis (art. 11) e há regras de publicidade dos conselhos profissionais (CFM, CFO, CFN, CFP…)")
        if sig.get("setor_financeiro"):
            self.add(16, "medio", "setor-financeiro",
                     "Projeto financeiro/crédito/investimentos - regras do Banco Central/CVM, Lei 14.181/2021 e sigilo bancário podem se aplicar")
        foreign = [s["nome"] for s in self.p["servicos_terceiros"] if s["exterior_provavel"]]
        if foreign:
            self.add(16, "info", "transferencia-internacional",
                     "Operadores com servidores provavelmente fora do Brasil: {} - transferência internacional (LGPD art. 33; Res. CD/ANPD 19/2024)".format(", ".join(foreign)))

    # ---------------------------------------------------------------- outros
    def check_other(self):
        for f in self.sel(MARKUP_EXT | PROSE_EXT | {".json"}, skip_docs=True):
            text = f["text"]
            m = re.search(r"\bsorteio|\bsortear|giveaway|concorra\s+a|cupom\s+premiado|raspadinha|roleta\s+(da\s+sorte|de\s+(pr[eê]mios|descontos))|"
                          r"spin\s+(to|the)\s+win|gire\s+a\s+roleta|ganhe\s+pr[eê]mios", text, re.I)
            if m:
                self.add(17, "alto", "promocao-sorteio",
                         "Sorteio/roleta/promoção com prêmio - em regra exige autorização prévia da SPA/Ministério da Fazenda (Lei 5.768/71); "
                         "\"concurso cultural\" só é isento sem vínculo com compra", f, m.start())
            m = re.search(r"\b(apostas?\s+esportiv|cassino|casino|\bodds\b|tigrinho|bet\s*365|fortune\s+tiger|quota\s+fixa)", text, re.I)
            if m:
                self.add(17, "alto", "apostas",
                         "Conteúdo de apostas - só operadores autorizados (Lei 14.790/2023) e publicidade com restrições; afiliados também respondem", f, m.start())
            m = re.search(r"n[aã]o,?\s+(obrigad[oa],?\s+)?(eu\s+)?(n[aã]o\s+)?(quero|gosto\s+de)\s+(economizar|ganhar|perder|pagar\s+mais|aprender)|prefiro\s+(pagar\s+mais|perder)", text, re.I)
            if m:
                self.add(17, "medio", "confirmshaming", "Botão de recusa constrangedor (dark pattern) - prática comercial desleal (CDC art. 6º IV e 39)", f, m.start())
            m = re.search(r"renova[cç][aã]o\s+autom[aá]tica|renovad[oa]\s+automaticamente|cobran[cç]a\s+recorrente|auto-?renew", text, re.I)
            if m and not re.search(r"cancel", text, re.I):
                self.add(17, "medio", "renovacao-sem-cancelamento",
                         "Renovação automática sem informação de como cancelar no mesmo lugar - Decreto 7.962 art. 4º V; cancelamento tão fácil quanto a contratação", f, m.start())
            m = re.search(r"lorem\s+ipsum", text, re.I)
            if m and f["ext"] != ".json":
                self.add(17, "baixo", "lorem-ipsum", "Texto de preenchimento (lorem ipsum) - não publique páginas incompletas", f, m.start())
            m = re.search(r"#publi\b|publicidade\s+paga|conte[uú]do\s+patrocinado|parceria\s+paga|link\s+de\s+afiliado|afiliad[oa]s?\b", text, re.I)
            if m:
                self.add(17, "info", "publicidade-identificada",
                         "Conteúdo patrocinado/afiliado - deve estar claramente identificado como publicidade (CDC art. 36; Guia CONAR de influenciadores)", f, m.start())
        dep_names = " ".join(self.deps)
        mail = re.search(r"nodemailer|resend|sendgrid|mailchimp|@aws-sdk/client-ses|postmark|brevo|mailgun", dep_names, re.I)
        if mail and any(re.search(r"newsletter|e-?mail\s+marketing|campanha", f["text"], re.I) for f in self.files if f["ext"] in MARKUP_EXT) \
                and not any(re.search(r"unsubscribe|descadastr|cancelar\s+(a\s+)?inscri|opt-?out|n[aã]o\s+quero\s+mais\s+receber", f["text"], re.I) for f in self.files):
            self.add(17, "medio", "email-sem-descadastro",
                     "Envio de e-mail marketing sem link de descadastro encontrado (LGPD art. 8º §5º - revogação fácil; boas práticas CAPEM)")
        if self.p["sinais"].get("conteudo_de_usuario"):
            self.add(17, "info", "conteudo-usuario",
                     "Há conteúdo/arquivos enviados por usuários - termos precisam de regras de uso e canal de denúncia; após o STF (Temas 533 e 987, jun/2025) "
                     "a plataforma pode responder após notificação extrajudicial em vários casos")
        nm = os.path.join(self.root, "node_modules")
        if os.path.isdir(nm):
            for dep in list(self.deps)[:400]:
                pj = os.path.join(nm, *dep.split("/"), "package.json")
                try:
                    with open(pj, encoding="utf-8") as fh:
                        lic = json.load(fh).get("license")
                except (OSError, ValueError):
                    continue
                if isinstance(lic, dict):
                    lic = lic.get("type")
                if isinstance(lic, str) and COPYLEFT_RE.search(lic):
                    self.add(17, "medio", "licenca-copyleft",
                             "Dependência {} com licença {} - copyleft pode obrigar a abrir o código; confirme o uso".format(dep, lic))

    # ------------------------------------------------------------------ run
    def run(self):
        self.walk()
        self.profile()
        self.find_docs()
        self.check_trackers()
        self.check_forms()
        self.check_models()
        self.check_docs()
        self.check_a11y()
        self.check_contrast()
        self.check_claims()
        self.check_images()
        self.check_company()
        self.check_lgpd()
        self.check_other()
        order = {s: i for i, s in enumerate(SEVERIDADES)}
        self.findings.sort(key=lambda x: (x["item"], order[x["severidade"]]))
        return self

    # --------------------------------------------------------------- saída
    def to_json(self):
        prof = json.loads(json.dumps(self.p, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))
        for info in prof["rastreadores"].values():
            info.pop("kw", None)
        return OrderedDict([
            ("versao", VERSION), ("raiz", self.root),
            ("arquivos_texto", len(self.files)), ("perfil", prof),
            ("resumo", self.summary()), ("achados", self.findings),
            ("omitidos_por_regra", {r: c - self.max_per_rule for r, c in self.rule_counts.items() if c > self.max_per_rule}),
        ])

    def summary(self):
        s = OrderedDict()
        for item, name in ITENS.items():
            counts = OrderedDict((sev, 0) for sev in SEVERIDADES)
            for fnd in self.findings:
                if fnd["item"] == item:
                    counts[fnd["severidade"]] += 1
            s[item] = OrderedDict([("item", name), ("contagem", counts)])
        return s

    def to_markdown(self):
        p = self.p
        sig = p["sinais"]
        out = ["# Varredura heurística - blindagem-juridica v{}".format(VERSION), "",
               "Raiz: `{}` · {} arquivos de texto · {} imagens · {} fontes locais".format(
                   self.root, len(self.files), p["imagens"], p["fontes_locais"]), "",
               "> Triagem automática. Confirme cada achado no código; ausência de achado não é conformidade.", "",
               "## Perfil detectado", ""]

        def yn(v):
            return "sim" if v else "não"

        out.append("- **Stack:** {}".format(", ".join(p["stack"]) or "não identificada"))
        out.append("- **Vende online:** {}{}".format(yn(sig.get("vende_online")),
                                                     " ({})".format(", ".join(sig.get("vende_online_evidencias", []))) if sig.get("vende_online") else ""))
        out.append("- **Assinatura recorrente:** {} · **Produto digital:** {}".format(yn(sig.get("assinatura_recorrente")), yn(sig.get("produto_digital"))))
        out.append("- **Login/cadastro:** {} · **Conteúdo de usuário/upload:** {} · **Backend:** {}".format(
            yn(sig.get("login_cadastro")), yn(sig.get("conteudo_de_usuario")), yn(sig.get("tem_backend"))))
        out.append("- **Público infantil/adolescente (sinais):** {} · **Saúde:** {} · **Financeiro:** {}".format(
            yn(sig.get("publico_infantil_ou_adolescente")), yn(sig.get("setor_saude")), yn(sig.get("setor_financeiro"))))
        out.append("- **Idioma principal:** {} · **Público estrangeiro provável:** {}".format(
            sig.get("idioma_principal"), yn(sig.get("publico_estrangeiro_provavel"))))
        out.append("- **Serviços de terceiros (operadores):** " + (", ".join(
            "{} ({}{})".format(s["nome"], s["finalidade"], ", exterior" if s["exterior_provavel"] else "") for s in p["servicos_terceiros"]) or "nenhum detectado"))
        out.append("- **Rastreadores/embeds:** " + (", ".join(
            "{} [{}] em {}".format(n, CAT_LABEL[i["categoria"]], i["ocorrencias"][0]) for n, i in p["rastreadores"].items()) or "nenhum detectado"))
        out.append("- **Gestão de consentimento (CMP):** " + (", ".join(p["cmp"]) or "nenhuma"))
        docs = []
        for k, v in p["documentos_legais"].items():
            loc = v["arquivos"] or v["paginas_curtas_ou_dinamicas"]
            docs.append("{}: {}".format(k, ", ".join(loc[:2]) if loc else "-"))
        out.append("- **Documentos legais:** " + " · ".join(docs))
        out.append("- **Dados pessoais em formulários:** " + (", ".join(
            "{} ({})".format(k, len(v)) for k, v in sorted(p["dados_em_formularios"].items())) or "nenhum detectado"))
        out.append("- **Dados de atenção/sensíveis em modelos/banco:** " + (", ".join(
            "{} ({})".format(k, ", ".join(sorted(v)[:2])) for k, v in sorted(p["dados_em_modelos"].items())) or "nenhum detectado"))
        emp = p["empresa"]
        out.append("- **Empresa:** CNPJ válido: {} · inválido: {} · razão social: {} · e-mails: {} · telefones: {} · endereço: {}".format(
            ", ".join(emp.get("cnpj_validos", [])) or "-", ", ".join(emp.get("cnpj_invalidos", [])) or "-",
            ", ".join(emp.get("razao_social", [])) or "-", ", ".join(emp.get("emails", [])) or "-",
            ", ".join(emp.get("telefones", [])) or "-", "; ".join(emp.get("enderecos", [])) or "-"))
        out += ["", "## Resumo por item", "", "| # | Item | 🔴 | 🟠 | 🟡 | 🔵 | ⚪ |", "|---|---|---|---|---|---|---|"]
        for item, data in self.summary().items():
            c = data["contagem"]
            out.append("| {} | {} | {} | {} | {} | {} | {} |".format(item, data["item"], *[c[s] or "" for s in SEVERIDADES]))
        out += ["", "## Achados", ""]
        for item, name in ITENS.items():
            items = [x for x in self.findings if x["item"] == item]
            if not items:
                continue
            out.append("### {}. {}".format(item, name))
            out.append("")
            for x in items:
                loc = ""
                if x.get("arquivo"):
                    loc = " - `{}{}`".format(x["arquivo"], ":{}".format(x["linha"]) if x.get("linha") else "")
                out.append("- {} **{}** {}{}".format(ICONE[x["severidade"]], x["regra"], x["mensagem"], loc))
                if x.get("trecho"):
                    out.append("  > `{}`".format(x["trecho"].replace("`", "'")[:200]))
            omitted = [(r, c - self.max_per_rule) for r, c in self.rule_counts.items()
                       if c > self.max_per_rule and any(x["regra"] == r for x in items)]
            for r, n in omitted:
                out.append("- … mais {} ocorrência(s) de **{}** omitidas (use --max-por-regra)".format(n, r))
            out.append("")
        return "\n".join(out)


def candidates_any(cands, key):
    return bool(cands.get(key) or cands.get(key + "_curta"))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Varredura heurística de riscos jurídicos (blindagem-juridica).")
    ap.add_argument("raiz", nargs="?", default=".", help="raiz do projeto (padrão: diretório atual)")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--max-por-regra", type=int, default=15, help="máximo de ocorrências listadas por regra (padrão 15)")
    ap.add_argument("--saida", help="grava o resultado neste arquivo em vez de imprimir")
    ap.add_argument("--incluir-testes", action="store_true", help="inclui pastas de teste/fixtures/stories")
    args = ap.parse_args()
    if not os.path.isdir(args.raiz):
        print("Diretório não encontrado: " + args.raiz, file=sys.stderr)
        sys.exit(2)
    sc = Scanner(args.raiz, args.max_por_regra, args.incluir_testes).run()
    result = json.dumps(sc.to_json(), ensure_ascii=False, indent=2) if args.format == "json" else sc.to_markdown()
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as fh:
            fh.write(result)
        print("Resultado gravado em " + args.saida)
    else:
        print(result)


if __name__ == "__main__":
    main()
