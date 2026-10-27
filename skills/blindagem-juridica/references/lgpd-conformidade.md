# Item 16 — Conformidade LGPD (governança, direitos do titular e segurança)

Os itens 1, 3, 5, 6 e 7 cobrem transparência, cookies e coleta. Este item cobre o restante do
que um projeto digital precisa ter para **demonstrar** conformidade (art. 6º X —
responsabilização e prestação de contas).

**Base:** LGPD arts. 6º, 7º, 11, 14, 15–16, 18–20, 33, 37–41, 46–50; Resoluções CD/ANPD
2/2022, 15/2024, 18/2024, 19/2024; ECA Digital (Lei 15.211/2025).

## Checklist

### Papéis e responsáveis
- [ ] Quem é o **controlador** (empresa dona do site) e quem são os **operadores** (fornecedores
      que tratam dados por ela: hospedagem, banco, e-mail, pagamentos, CRM, IA, analytics).
- [ ] **Encarregado (DPO)** indicado, com nome e contato públicos (art. 41 §1º). Agente de
      pequeno porte pode dispensar, mas **precisa de canal de comunicação** (Res. 2/2022) —
      e não vale para tratamento de alto risco (dados sensíveis em larga escala, vigilância,
      tecnologias emergentes, crianças em larga escala etc.).

### Direitos do titular (art. 18)
- [ ] Canal claro (e-mail dedicado, formulário ou área logada) para: confirmação, acesso,
      correção, anonimização/bloqueio/eliminação, portabilidade, informação sobre
      compartilhamento, revogação do consentimento.
- [ ] Prazo de resposta: imediato no formato simplificado ou até **15 dias** para declaração
      completa (art. 19).
- [ ] **Exclusão de conta** pelo próprio usuário quando houver cadastro (também exigido pela
      Apple App Store e Google Play para apps). Exclua ou anonimize dados que não precisam ser
      mantidos por obrigação legal.
- [ ] **Revogação** do consentimento tão fácil quanto dar (descadastro de e-mail em um clique,
      preferências de cookies no rodapé).
- [ ] **Exportação** (portabilidade) — pode ser JSON/CSV via solicitação.

Se o projeto tem área logada, proponha implementar em "Minha conta": baixar meus dados, editar
dados, preferências de comunicação, excluir conta. Se não tem, um formulário "Solicitação LGPD"
que envia para o e-mail do encarregado já atende.

### Retenção e eliminação (arts. 15 e 16)
Defina prazos e implemente a rotina quando possível (job/cron, política no banco):

| Dado | Prazo sugerido (confirme com o usuário) | Fundamento |
|------|---------------------------------------|-----------|
| Registros de acesso (IP, data/hora) | 6 meses | Marco Civil art. 15 |
| Dados fiscais e de pedidos | 5 anos | Legislação tributária |
| Cadastro de cliente | Enquanto a conta existir + prazo de defesa (ex.: 5 anos após o fim) | Contrato / exercício de direitos |
| Leads e contatos sem conversão | 12 a 24 meses sem interação | Necessidade |
| Newsletter | Até o descadastro | Consentimento |
| Currículos | 6 a 12 meses ou até o fim do processo seletivo | Necessidade |
| Gravações de sessão/analytics | Prazo mínimo da ferramenta (ex.: 2 a 14 meses) | Necessidade |
| Logs de aplicação com dados pessoais | 30 a 90 dias | Segurança + necessidade |

### Segurança (art. 46) — verifique no código
- [ ] HTTPS em todo o site e nas APIs; HSTS se possível.
- [ ] Senhas com **hash forte** (bcrypt, argon2, scrypt) — ou autenticação gerenciada.
- [ ] Segredos fora do código (variáveis de ambiente), `.env` no `.gitignore`, chaves de
      produção nunca em variáveis públicas (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`). Se uma chave
      já foi commitada, **revogar e rotacionar** — removê-la do código não basta.
- [ ] Banco de dados com controle de acesso (ex.: RLS no Supabase, regras do Firestore — **não**
      deixar `allow read, write: if true`).
- [ ] Sem dados pessoais/sensíveis em `localStorage`, logs, URLs (query string), mensagens de
      erro, eventos de analytics.
- [ ] Cartão: nunca trafegar/armazenar dados de cartão no próprio servidor; usar
      tokenização/checkout do gateway (PCI DSS). Nunca armazenar CVV.
- [ ] Uploads: validar tipo/tamanho, armazenar fora da raiz pública ou com URLs assinadas.
- [ ] Rate limiting/antispam em formulários e login; proteção contra enumeração de usuários.
- [ ] Backups e controle de quem tem acesso administrativo.
- [ ] Dependências atualizadas (`npm audit`, `pip-audit`) — vulnerabilidade conhecida não
      corrigida pesa contra o controlador em caso de incidente.

### Incidentes (art. 48; Res. CD/ANPD 15/2024)
- [ ] Plano simples de resposta: quem decide, como conter, como avaliar risco, comunicar ANPD
      e titulares em **3 dias úteis** quando houver risco ou dano relevante, registro do
      incidente (mesmo os não comunicados). Modelo: `templates/plano-resposta-incidentes.md`.

### Documentação (arts. 37 e 38)
- [ ] **Registro das operações de tratamento (ROPA)** — modelo em
      `templates/registro-de-operacoes.md`. Gere preenchido com o mapa de dados da Fase 1.
- [ ] **Relatório de Impacto (RIPD)** quando houver dados sensíveis em escala, crianças,
      monitoramento, decisões automatizadas relevantes, legítimo interesse de alto risco —
      recomende elaboração com apoio jurídico.
- [ ] **Contratos com operadores** (DPA/termos de tratamento de dados): verificar que os
      fornecedores têm termos de processamento de dados e mecanismo de transferência
      internacional (a maioria dos grandes fornecedores publica DPA). Recomendação, não código.

### Transferência internacional (art. 33; Res. 19/2024)
Fornecedores nos EUA/Europa (Vercel, AWS, Google, Meta, Stripe, OpenAI, Anthropic, Supabase,
Firebase, Resend…) implicam transferência. Informe na política e recomende verificar se os
contratos dos fornecedores incorporam cláusulas-padrão ou garantias equivalentes.

### Inteligência artificial
Se o projeto envia dados a modelos de IA (OpenAI, Anthropic, Gemini…):
- informar na política (finalidade, fornecedor, transferência);
- não enviar dados sensíveis ou de crianças sem base adequada;
- verificar se o fornecedor usa os dados para treinamento (configuração da API/contrato);
- decisões automatizadas relevantes → direito de revisão (art. 20) e explicação.

### Crianças e adolescentes
Se o público pode incluir menores de 18 (escola, jogos, conteúdo infantil, apps populares):
- LGPD art. 14 (melhor interesse; consentimento parental para crianças) e Enunciado ANPD 1/2023;
- **ECA Digital (Lei 15.211/2025, em vigor desde 17/03/2026)**: verificação de idade efetiva
  onde houver conteúdo impróprio, supervisão parental, configurações mais protetivas por
  padrão, sem perfilamento para publicidade dirigida. É área de alto risco: recomende revisão
  jurídica específica.

### Perguntas ao usuário (só as que o código não responde)
- Quem é o encarregado ou o canal oficial de privacidade? Esse e-mail é monitorado?
- A empresa se enquadra como agente de pequeno porte?
- Prazos de guarda que quer adotar (ou aceita os sugeridos)?
- Usa outras ferramentas com dados de clientes fora do código (planilhas, CRM, WhatsApp
  Business, ERP)? (vão para o ROPA e a política)
- Atende menores de idade? Atende público da União Europeia?
