# Item 17 — Outros riscos jurídicos

Riscos frequentes em produtos digitais que não cabem nos itens anteriores. Para cada um: o
sinal no código, por que é risco e a correção.

## Práticas comerciais e dark patterns (CDC arts. 6º IV, 39 e 51)
| Sinal | Risco | Correção |
|------|------|---------|
| Item adicional pré-selecionado no carrinho (seguro, garantia estendida, doação, assinatura) | Venda casada / prática abusiva (art. 39, I e III) | Desmarcado por padrão |
| Renovação automática pouco visível, cancelamento só por telefone/e-mail | Abusivo; Decreto 7.962 art. 4º V | Informar antes do pagamento; botão de cancelar na conta |
| Taxas reveladas só no último passo (drip pricing) | Publicidade enganosa por omissão; art. 2º IV do decreto | Mostrar custo total cedo |
| "Não, prefiro pagar mais caro" (confirmshaming) | Prática desleal | Texto neutro ("Não, obrigado") |
| Pop-up que impede fechar / botão de fechar escondido | Desleal + acessibilidade | Botão de fechar visível e acessível |
| Preço diferente por meio de pagamento sem aviso | Lei 13.455/2017 exige informar | Informar diferença |
| Período grátis que vira cobrança sem aviso | Abusivo | Avisar antes da primeira cobrança |

## Promoções, sorteios e apostas
- **Sorteio, vale-brinde, roleta de prêmios, "comente e concorra", cupom premiado**: em regra
  exigem **autorização prévia** da Secretaria de Prêmios e Apostas do Ministério da Fazenda
  (Lei 5.768/71). **Concurso cultural** puro (critério de mérito, sem sorteio, sem vínculo com
  compra) é dispensado — mas precisa de regulamento. Pergunte se há autorização; se não houver,
  recomende suspender ou converter em concurso cultural com regulamento, e revisão jurídica.
- **Roleta de desconto ("gire e ganhe")**: se o prêmio depende de sorte, pode ser enquadrada
  como promoção; prefira cupom fixo.
- **Apostas e cassino online / afiliados de bets**: só operadores autorizados (Lei 14.790/2023);
  publicidade com restrições (sem apelo a menores, sem promessa de ganho). Afiliado também
  responde.

## Comunicação e marketing
- **E-mail marketing**: opt-in, link de descadastro em todas as mensagens, remetente
  identificado (CAPEM + LGPD art. 8º §5º). Sem lista comprada.
- **WhatsApp/SMS**: consentimento para marketing; respeitar opt-out; bibliotecas não oficiais
  de automação de WhatsApp violam os termos do WhatsApp (risco de banimento e de
  responsabilidade) — prefira a API oficial (Cloud API/BSP).
- **Telemarketing**: respeitar o "Não Me Perturbe" quando aplicável.
- **Influenciadores/afiliados**: publicidade identificada (#publi, "conteúdo patrocinado").

## Conteúdo de usuários e plataformas
- Comentários, avaliações, perfis, uploads, fóruns, marketplaces: termos com regras de
  conduta, canal de denúncia, processo de remoção com devido processo, e logs (Marco Civil
  art. 15). Após o **STF (Temas 533 e 987, jun/2025)**, a plataforma pode responder após
  notificação extrajudicial em várias situações — tenha fluxo de análise de denúncias.
- Remoção de conteúdo por direitos autorais: canal de notificação.
- Marketplace: identificar vendedores; responsabilidade solidária pode recair sobre a
  plataforma em relação de consumo.

## Propriedade intelectual além de imagens
- Nome/domínio parecido com marca registrada de terceiro (pesquisar no INPI antes de investir).
- Uso de marcas de terceiros em anúncios, metatags ou palavras-chave de concorrentes.
- Código copiado sem licença; tema/plugin pago "nulled"; dependências GPL/AGPL em produto
  fechado distribuído; fontes sem licença web.
- Conteúdo gerado por IA: revisar termos da ferramenta; não presumir originalidade.

## Contratação e cobrança
- Contrato não disponibilizado para download/guarda após a compra (Decreto 7.962 art. 4º IV).
- Falta de confirmação imediata da compra por e-mail (art. 4º III).
- Boleto/Pix sem identificação do beneficiário correto (risco de fraude e de reclamação).
- Cobrança de inadimplentes com exposição ao ridículo ou ameaça (CDC art. 42) — mensagens
  automáticas de cobrança devem ser respeitosas.

## Setores regulados (pergunte se é o caso; recomende revisão especializada)
Saúde e telemedicina (CFM, ANVISA, prontuário), farmácia, alimentos e suplementos, bebidas
alcoólicas (aviso "Beba com moderação", restrição a menores), tabaco/vape (venda proibida),
armas, finanças/crédito/investimentos (BACEN, CVM), seguros (SUSEP), educação (MEC), turismo
(Cadastur), imobiliário (CRECI), advocacia (OAB), transporte, telecom (Anatel), energia,
loterias/apostas, criptoativos (Lei 14.478/2022).

## Segurança como risco jurídico
Vulnerabilidades que levam a vazamento viram responsabilidade civil (LGPD art. 42 e 44) e
sanção (art. 52). Pontos de código: segredos expostos, regras de banco abertas, rotas de API
sem autenticação/autorização (IDOR: `/api/pedidos/123` acessível por outro usuário), upload
sem validação, dependências vulneráveis, logs com dados pessoais. Aponte e corrija o que for
técnico; para auditoria de segurança profunda, recomende pentest.

## Internacional
- Atende a UE? GDPR (base legal, consentimento de cookies, DPA, representante na UE em certos
  casos). Califórnia? CCPA/CPRA. Público dos EUA? Acessibilidade (ADA).
- Preços em moeda estrangeira, impostos e regras de consumo locais.

## Documentos e práticas recomendadas (não são código)
- Registro do aceite de termos (versão + data) e do consentimento.
- Guarda das comprovações de alegações publicitárias.
- Contratos com fornecedores (DPA), com fotógrafos (cessão/licença), com influenciadores.
- Registro de marca no INPI.
- Revisão periódica (a cada nova feature que colete dados ou novo script de terceiro, rodar
  esta skill de novo).
