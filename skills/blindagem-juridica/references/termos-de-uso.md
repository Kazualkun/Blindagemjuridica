# Item 2 — Termos de uso / termos de serviço

**Base:** CDC arts. 6º, 25, 46, 47, 51, 54 e 101; Decreto 7.962/2013 art. 4º; Marco Civil art. 7º (XI);
Código Civil (contratos); STF Temas 533/987 (conteúdo de terceiros).

**Quando é necessário:**
- **Obrigatório na prática** se há venda, assinatura, cadastro/conta, área logada, marketplace,
  conteúdo enviado por usuários, API pública ou uso de IA pelo usuário.
- **Recomendável** em sites institucionais (regras de uso de conteúdo, limitação razoável de
  responsabilidade por links externos).

## Como auditar

1. Localize (rotas `termos`, `terms`, `condicoes`, `tos`, CMS). Verifique links no rodapé, no
   cadastro e no checkout.
2. **Aceite**: no cadastro/checkout, há caixa **desmarcada** "Li e aceito os [Termos de Uso] e a
   [Política de Privacidade]" (ou botão com texto equivalente e links)? Separado de qualquer
   consentimento de marketing? O sistema guarda **qual versão** foi aceita e quando? (importante
   para provar o aceite).
3. **Conteúdo** (checklist abaixo) coerente com o produto real: planos e preços do código, forma
   de cancelamento que realmente existe, prazos reais.
4. **Cláusulas abusivas** (procure no texto e corrija):
   - "Não nos responsabilizamos por quaisquer danos" / "isenta-se de toda responsabilidade" →
     nulas em relação de consumo (CDC 25 e 51, I). Reescreva como limitação razoável (ex.:
     indisponibilidade por manutenção programada avisada, força maior, conteúdo de sites de
     terceiros) sem afastar responsabilidade por falha do serviço.
   - "Não fazemos reembolso" / "venda final" → conflita com art. 49; remeta à política de
     reembolso conforme o CDC.
   - Arbitragem obrigatória para consumidor → nula (51, VII). Em contrato B2B pode ser válida.
   - Foro exclusivo longe do consumidor → ineficaz contra o consumidor (art. 101, I). Redija:
     "Fica eleito o foro de [cidade], ressalvado o direito do consumidor de propor ação em seu
     domicílio."
   - Alteração unilateral de preço/condições de contrato em vigor sem aviso e sem direito de
     cancelar → abusiva (51, X e XIII). Correto: aviso prévio (ex.: 30 dias) + possibilidade de
     cancelar sem multa.
   - Renúncia a direitos, multa só para o consumidor, renovação automática escondida.
   - Cláusulas limitativas sem destaque (art. 54 §4º) → coloque em **negrito** ou caixa destacada.
5. **Contrato de adesão legível**: fonte não menor que 12pt equivalente (art. 54 §3º); em web
   use pelo menos 16px no corpo.
6. **Assinatura/recorrência**: termos dizem valor, periodicidade, data de cobrança, reajuste,
   como cancelar (pelo mesmo meio da contratação — Decreto 7.962 art. 5º §1º, por analogia) e o
   que acontece com os dados após cancelar.

## Conteúdo mínimo (checklist)

- [ ] Identificação do fornecedor (razão social, CNPJ, endereço, contato).
- [ ] Definições e descrição do serviço/produto.
- [ ] Cadastro: requisitos, idade mínima, veracidade dos dados, segurança da senha.
- [ ] Regras de uso e condutas proibidas; consequências (suspensão, exclusão) com direito de defesa.
- [ ] Preços, pagamento, faturamento, reajuste, inadimplência (se houver venda/assinatura).
- [ ] Cancelamento, arrependimento e reembolso (ou link para a política específica).
- [ ] Propriedade intelectual (do fornecedor e do conteúdo enviado pelo usuário — licença de uso).
- [ ] Conteúdo de usuários: regras, moderação, canal de denúncia, notificação e retirada.
- [ ] Limitação de responsabilidade **válida** (sem afastar o CDC).
- [ ] Disponibilidade, manutenção, suporte e SLA (SaaS).
- [ ] Uso de IA, se houver: limitações, revisão humana, não usar dados do cliente para treinar
      sem informar/consentir conforme o caso.
- [ ] Privacidade: remissão à política de privacidade.
- [ ] Alterações dos termos: como avisa, prazo, direito de cancelar.
- [ ] Lei aplicável (brasileira) e foro com ressalva ao consumidor.
- [ ] Data de vigência/versão.

## Como corrigir

1. Parta de `templates/termos-de-uso.md` e mantenha só as seções aplicáveis ao produto.
2. Use os dados reais (planos, preços, prazos, canais) do código e das respostas do usuário.
3. Crie a página, linke no rodapé, cadastro e checkout.
4. Se o cadastro não tem aceite: adicione caixa desmarcada + links; se possível, grave
   `termsVersion` e `termsAcceptedAt` junto ao usuário (pergunte antes de alterar o banco —
   envolve migração).
5. **B2B (SaaS para empresas)**: o CDC pode não se aplicar; cláusulas de limitação de
   responsabilidade e foro são mais livres. Pergunte se o público é exclusivamente empresarial.
