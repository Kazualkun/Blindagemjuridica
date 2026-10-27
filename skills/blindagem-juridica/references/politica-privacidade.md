# Item 1 — Política de privacidade

**Base:** LGPD arts. 6º (VI), 9º, 18, 33, 41; Marco Civil art. 7º (VIII e XI); CDC art. 31.
**Quando é obrigatória:** sempre que o site/app tratar qualquer dado pessoal — formulário,
cadastro, compra, newsletter, chat, analytics, pixel, até logs de IP. Na prática, todo site.

## Como auditar

1. **Existe?** Procure rotas/arquivos `privacidade`, `privacy`, `politica-de-privacidade`, `lgpd`,
   textos em CMS/i18n. Se o conteúdo vier de CMS ou banco, pergunte ou peça o texto publicado.
2. **Está acessível?** Link no rodapé de todas as páginas, junto de cada formulário, no
   cadastro, no checkout e dentro do app (menu/configurações). Em apps, URL pública exigida
   pelas lojas.
3. **Está em português claro**, sem juridiquês excessivo, datada e versionada?
4. **Bate com o código?** Este é o teste principal. Compare com o mapa de dados da Fase 1:
   - Todo dado coletado no código aparece na política? (campo `cpf` no checkout → CPF listado).
   - Todo rastreador/embed (GA, Meta Pixel, TikTok, Hotjar, Clarity, YouTube, Maps, reCAPTCHA)
     e todo operador (Stripe, Mercado Pago, Supabase, Firebase, AWS, Vercel, Resend, OpenAI…)
     aparece, ao menos por categoria e com os principais nomeados?
   - A política promete algo que o código não faz? ("não usamos cookies de terceiros" com Meta
     Pixel instalado é publicidade enganosa e quebra de transparência.)
   - Há transferência internacional (serviços nos EUA etc.) e a política fala dela?
5. **Tem o conteúdo mínimo** (checklist abaixo)?
6. **Não é cópia de outro site** (nome de outra empresa, serviços que não existem, "este site
   é regido pelas leis da Califórnia"). Cópia também pode violar direito autoral.

## Conteúdo mínimo (checklist)

- [ ] Identificação do **controlador**: razão social, CNPJ, endereço, contato.
- [ ] **Encarregado (DPO)**: nome e e-mail — ou, para agente de pequeno porte que optou por
      não indicar, o **canal de comunicação** com o titular (Res. CD/ANPD 2/2022).
- [ ] **Quais dados** são tratados, agrupados por contexto (cadastro, compra, navegação,
      atendimento, marketing), incluindo os coletados automaticamente (IP, dispositivo, cookies).
- [ ] **Finalidade de cada grupo** e a **base legal** correspondente (art. 7º; art. 11 se sensível).
- [ ] **Compartilhamento**: categorias de destinatários e principais operadores; autoridades
      quando exigido por lei; nunca "vendemos dados" sem base.
- [ ] **Transferência internacional**: quais serviços, países prováveis, mecanismo (cláusulas-padrão
      da ANPD, garantias contratuais, consentimento).
- [ ] **Cookies e tecnologias semelhantes** (ou link para política de cookies) e como gerenciar.
- [ ] **Prazo de retenção** por tipo de dado e critério de eliminação (ex.: registros de acesso
      6 meses — Marco Civil art. 15; dados fiscais 5 anos; cadastro enquanto a conta existir).
- [ ] **Direitos do titular** (art. 18) e **como exercê-los** (canal, prazo de resposta), direito
      de petição à ANPD.
- [ ] **Segurança**: medidas gerais adotadas (sem detalhes que ajudem atacantes).
- [ ] **Crianças e adolescentes**: se o serviço não é para menores, dizer; se é, regras do art. 14
      e do ECA Digital.
- [ ] **Decisões automatizadas/IA**, se houver (art. 20) — ex.: score, moderação automática,
      chatbot que usa os dados.
- [ ] **Alterações da política** e data da última atualização.

## Bases legais mais comuns (guia rápido)

| Tratamento | Base usual |
|-----------|------------|
| Responder contato, orçamento | Procedimentos preliminares a contrato (art. 7º V) |
| Cadastro e prestação do serviço, entrega, pagamento | Execução de contrato (art. 7º V) |
| Nota fiscal, guarda de registros (Marco Civil art. 15) | Obrigação legal (art. 7º II) |
| Prevenção a fraude, segurança | Legítimo interesse (IX) ou proteção do crédito (X) |
| Newsletter/marketing para quem não é cliente | Consentimento (I) |
| Marketing para cliente sobre produtos semelhantes | Legítimo interesse (IX), com opt-out fácil |
| Cookies de analytics e publicidade | Consentimento (I) |
| Cookies estritamente necessários | Legítimo interesse/execução de contrato |
| Defesa em processos | Exercício regular de direitos (VI) |
| Dados de saúde em clínica | Tutela da saúde (art. 11, II, f) ou consentimento |

Não use "consentimento" para tudo: se o usuário revogar, o tratamento precisa parar. Para o
que é necessário ao contrato, use execução de contrato.

## Como corrigir

1. Parta de `templates/politica-de-privacidade.md`.
2. Preencha com o perfil e o **mapa de dados** do projeto. Remova seções que não se aplicam
   (ex.: "Pagamentos" se nada é vendido). Não deixe placeholders genéricos.
3. Nomeie os operadores e rastreadores detectados, com finalidade e país provável.
4. Crie a página no formato da stack, com o layout do site, títulos navegáveis (h2/h3), índice
   se for longa, e data de atualização visível.
5. Linke: rodapé global, formulários ("Ao enviar, você concorda…" **não** — use "Veja como
   tratamos seus dados na [Política de Privacidade]"), cadastro, checkout, app.
6. Se o projeto tem i18n, crie as versões nos idiomas suportados (a versão pt-BR é a que vale
   no Brasil).

## Erros comuns que você deve corrigir

- Política copiada de outra empresa/país, com "GDPR" e sem LGPD.
- "Ao usar o site você concorda com esta política" como base para tudo — política informa, não
  colhe consentimento.
- Prometer "nunca compartilhamos seus dados" com pixels de publicidade instalados.
- Não mencionar WhatsApp/e-mail marketing/CRM que o negócio usa (pergunte!).
- Encarregado com e-mail que ninguém lê — pergunte quem responde.
- Política só em PDF para baixar (prefira página HTML acessível).
