# Item 14 — Direitos autorais de imagens (e fontes, vídeos, músicas, marcas, código)

**Base:** Lei 9.610/1998 arts. 7º, 22, 24, 28, 29, 79 e 102–110; Código Penal art. 184; Código
Civil art. 20 e Súmula 403 STJ (imagem de pessoas); Lei 9.279/1996 (marcas); Lei 9.609/1998
(software); LGPD (foto de pessoa é dado pessoal).

**Por que é risco real:** bancos de imagem (Getty, Shutterstock, Adobe Stock…) e agências
contratam empresas que rastreiam imagens na web por robôs e enviam **notificações de cobrança**
(frequentemente de milhares de reais por imagem). Fotógrafos processam por uso sem crédito
(dano moral pela falta de indicação de autoria, art. 24 II / 108). Fotos de pessoas sem
autorização geram indenização independentemente de prejuízo (Súmula 403).

## Como auditar

1. **Inventário**: o scanner conta as imagens e aponta sinais. Liste as pastas (`public/`,
   `assets/`, `static/`, `uploads/`, `wp-content/uploads`) e imagens remotas referenciadas no
   código e no CMS.
2. **Sinais de risco** (scanner):
   - nome de arquivo de banco pago (`shutterstock_123.jpg`, `iStock-...`, `AdobeStock_...`,
     `depositphotos_...`, `GettyImages-...`) → confirmar licença ativa, quantidade de usos,
     escopo (web, anúncio, impresso), e se a licença permite o uso feito;
   - metadados (EXIF/XMP/IPTC) com "Getty Images", "Shutterstock", copyright de fotógrafo;
   - URL de comp/preview com marca d'água (`ftcdn.net`, `previews.123rf`), Google Imagens
     (`encrypted-tbn0.gstatic.com`), Pinterest (`pinimg`), Instagram/Facebook CDN → **hotlink
     sem licença**; também consome banda de terceiros;
   - "WhatsApp Image…", "Screenshot", "download (3).jpg", "images.jpg" → origem desconhecida;
   - Freepik/Flaticon gratuitos → exigem atribuição visível no plano free;
   - imagens de pessoas (modelos, clientes, funcionários) → autorização de uso de imagem;
   - logos/personagens de terceiros (marcas, times, Disney, Pokémon) → autorização;
   - imagens geradas por IA → verificar termos da ferramenta; não usar como "foto real de
     cliente/resultado"; cuidado com semelhança com obras/pessoas reais.
3. **Fontes** (`.woff`, `.ttf`, `.otf`): fontes comerciais (Proxima Nova, Gotham, Helvetica,
   Futura, Avenir, Gilroy, SF Pro, Segoe, Arial…) hospedadas no site exigem licença **web**.
   Fontes do Google Fonts/Fontsource (licença OFL) são livres.
4. **Vídeos e músicas**: trilha em vídeo do site (música comercial → precisa de licença; ECAD
   para execução pública), vídeos de terceiros embutidos sem permissão.
5. **Textos copiados** de outros sites (inclusive políticas e termos de outras empresas).
6. **Código**: dependências com licença copyleft (GPL/AGPL) em produto fechado; templates/temas
   pagos usados sem licença (ThemeForest etc.).

## Fontes de imagem seguras (sugira ao usuário)
- Próprias (fotógrafo contratado com contrato de cessão/licença por escrito).
- Unsplash e Pexels (licenças próprias permitem uso comercial sem atribuição, com restrições
  — ex.: não vender a imagem sem modificação; pessoas/marcas na foto ainda podem exigir
  autorização em certos usos).
- Bancos pagos com licença ativa e guardada.
- Ilustrações de bibliotecas com licença clara (ex.: unDraw, Heroicons, Lucide — MIT/ISC).
- Fontes: Google Fonts / Fontsource (OFL).

## Perguntas ao usuário
Monte uma tabela com as imagens suspeitas (arquivo, onde aparece, sinal) e pergunte a origem
de cada uma (ou do grupo): **própria / banco de imagens com licença / gratuita (qual) / gerada
por IA / não sei**. Para pessoas: há autorização de uso de imagem por escrito?

## Como corrigir
- **Hotlinks**: baixar só se houver licença; caso contrário, substituir.
- **Origem desconhecida ou sem licença**: substituir por imagem própria/licenciada; enquanto
  isso, você pode trocar por placeholder neutro **apenas com aprovação** (é mudança visual).
- **Crédito obrigatório**: adicionar crédito ao autor (legenda ou página "Créditos") quando a
  licença exigir ou quando for foto autoral (art. 79 §1º).
- **Fontes comerciais sem licença web**: trocar por equivalente livre (ex.: Proxima Nova →
  Montserrat/Figtree; Gotham → Montserrat; Helvetica → Inter/Arimo; Futura → Jost; Avenir →
  Nunito Sans) — com aprovação, pois muda o visual.
- Registrar no relatório um **inventário de licenças** (`docs/licencas-de-midia.md`, opcional)
  com arquivo, fonte, licença e data — útil para responder notificações.

## Se o usuário já recebeu notificação de cobrança
Não pague nem responda sem orientação: verifique a licença; a notificação pode ser legítima ou
abusiva. Recomende advogado(a). Remover a imagem não apaga o uso passado, mas evita agravar.
