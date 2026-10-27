# Item 4 — Política de reembolso, trocas e direito de arrependimento

**Base:** CDC arts. 18, 20, 26, 30, 35, 49, 50, 51 (II); Decreto 7.962/2013 arts. 2º e 5º.
**Aplica-se** a qualquer venda a consumidor pela internet, telefone, WhatsApp ou fora do
estabelecimento: produto físico, produto digital (curso, e-book, software), serviço,
assinatura, ingresso. Se o projeto não vende nada → marque ➖ Não se aplica, com motivo.

## O que a lei garante (e a política não pode reduzir)

1. **Arrependimento (art. 49):** 7 dias corridos a partir da contratação ou do recebimento
   (o que for depois), **sem precisar de motivo**, com devolução **integral e imediata** de
   tudo o que foi pago (produto, frete, taxas), atualizado. Custos de devolução do produto
   são do fornecedor.
   - **Produtos digitais/infoprodutos e serviços online:** o entendimento majoritário é que o
     art. 49 se aplica; plataformas (Hotmart, Kiwify, Eduzz) adotam 7 dias. Você pode
     **oferecer mais** (ex.: 15 ou 30 dias de garantia), nunca menos.
   - **Assinaturas:** arrependimento de 7 dias na contratação; depois, cancelamento conforme os
     termos (sem multa abusiva, pelo mesmo canal da contratação).
   - Exceções são debatidas (produto personalizado sob encomenda, conteúdo digital consumido
     integralmente, passagens aéreas — regras da ANAC, hospedagem e eventos com data). Não
     afirme exceção como certa: redija "nos termos da legislação aplicável" e recomende revisão
     jurídica quando o negócio quiser restringir.
2. **Como exercer (Decreto 7.962 art. 5º):** meios claros e ostensivos; pelo menos pela mesma
   ferramenta usada para comprar; confirmação imediata do pedido; estorno comunicado
   imediatamente à operadora do cartão; contratos acessórios (garantia estendida, seguro)
   cancelados junto.
3. **Vício/defeito (arts. 18, 20, 26):** consumidor reclama em 30 dias (não duráveis) ou 90 dias
   (duráveis); o fornecedor tem até 30 dias para resolver; depois, o consumidor escolhe troca,
   devolução do dinheiro ou abatimento. Garantia contratual soma-se à legal (art. 50).
4. **Troca por preferência** (cor, tamanho, "não gostei" após os 7 dias): **não é obrigatória**
   por lei; se a loja oferecer, ela define as condições (prazo, etiqueta, quem paga frete) —
   e passa a ter de cumprir o que anunciou (art. 30).
5. **Garantia anunciada** ("satisfação garantida ou seu dinheiro de volta"): vincula. A política
   precisa ser coerente com o anúncio.

## Como auditar

1. Existe página de trocas/reembolso? Está linkada no rodapé, na página de produto e no checkout?
2. Procure no texto e corrija:
   - prazo menor que 7 dias para arrependimento ("48h", "3 dias");
   - "não fazemos reembolso", "somente vale-compras/crédito" (no arrependimento, a escolha não
     é do fornecedor — o reembolso é em dinheiro/estorno);
   - frete de devolução cobrado no arrependimento;
   - exigência de "produto lacrado" para arrependimento (pode-se exigir que não haja mau uso,
     mas abrir a embalagem para conhecer o produto é direito);
   - taxa de cancelamento/multa no arrependimento;
   - prazo de estorno vago ("em até 90 dias") — prefira prazos concretos e imediatos após
     recebimento da devolução; estorno no cartão depende da operadora (informe isso).
3. O código implementa o que a política promete? (botão "cancelar pedido/assinatura" existe?
   e-mail de confirmação de pedido de arrependimento é enviado?)

## Perguntas ao usuário (se faltar informação)

- O que vende: físico, digital, serviço, assinatura? Por qual meio de pagamento?
- Quer oferecer garantia maior que 7 dias? Quantos dias?
- Aceita troca por preferência após os 7 dias? Em quantos dias, com quais condições e quem
  paga o frete?
- Canal para pedir arrependimento/troca (e-mail, formulário, área do cliente, WhatsApp)?
- Prazo de estorno praticado (Pix, boleto, cartão)?
- Prazo de entrega e transportadoras (para a política de entrega, se houver)?

## Como corrigir

1. Parta de `templates/politica-de-reembolso.md` e escolha as seções da variante certa
   (físico / digital / serviço / assinatura).
2. Crie a página e linke no rodapé, produto e checkout. Em assinaturas, mostre resumo das
   regras de cancelamento antes do pagamento (Decreto 7.962 art. 4º I).
3. Se não houver forma de pedir arrependimento pelo próprio site/app, recomende (e, se o usuário
   aprovar, implemente) um formulário/botão "Desistir da compra" que envia o pedido e confirma
   por e-mail.
4. Reescreva os termos de uso que contradizem a política (veja `termos-de-uso.md`).
