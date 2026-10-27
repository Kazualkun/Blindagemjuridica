# Item 15 — Dados da empresa (identificação do fornecedor)

**Base:** Decreto 7.962/2013 arts. 2º (I e II) e 4º; CDC arts. 6º III, 31 e 33; LGPD arts. 9º
(II, III) e 41 (identificação do controlador e encarregado).

## O que precisa aparecer

Em **local de destaque e de fácil visualização** — na prática, no **rodapé de todas as páginas**
(e, em apps, numa tela "Sobre/Informações legais"):

- **Nome empresarial (razão social)** e nome fantasia, se houver.
- **CNPJ** — ou **CPF** se a venda for feita por pessoa física (avaliar exposição: MEI tem CNPJ
  próprio e é preferível).
- **Endereço físico** completo (onde a empresa pode ser encontrada/notificada). Negócio 100%
  online sem sede aberta ao público: use o endereço do registro (pode ser endereço fiscal ou
  escritório virtual, desde que seja o do CNPJ).
- **Endereço eletrônico** e demais canais de contato (e-mail, telefone/WhatsApp, horário de
  atendimento).
- Para lojas: canal de atendimento que resolva dúvidas, reclamações, cancelamento
  (Decreto 7.962 art. 4º V), com resposta em até 5 dias.
- Para marketplaces: identificação de cada vendedor parceiro na página do produto/checkout.

Exemplo de rodapé:
```html
<footer>
  <p>
    [Razão Social] — CNPJ [00.000.000/0000-00]<br>
    [Logradouro, número, complemento], [Bairro], [Cidade]/[UF], CEP [00000-000]<br>
    Atendimento: <a href="mailto:[email]">[email]</a> · <a href="tel:+55[número]">[telefone]</a>
    · [dias e horários]
  </p>
  <nav aria-label="Informações legais">
    <a href="/politica-de-privacidade">Política de Privacidade</a> ·
    <a href="/termos-de-uso">Termos de Uso</a> ·
    <a href="/trocas-e-devolucoes">Trocas e Devoluções</a> ·
    <a href="/politica-de-cookies">Cookies</a> ·
    <button type="button" data-abrir-preferencias-cookies>Preferências de cookies</button> ·
    <a href="/acessibilidade">Acessibilidade</a>
  </nav>
</footer>
```

## Como auditar
1. O scanner extrai CNPJs (e **valida dígitos verificadores**, inclusive do CNPJ alfanumérico
   — formato emitido a partir de julho de 2026 pela Receita Federal, com 12 caracteres
   alfanuméricos + 2 dígitos), razão social, endereços, e-mails e telefones.
2. Confirme: os dados estão em todas as páginas (layout global), não só em "Sobre"?
3. CNPJ inválido, placeholder (`00.000.000/0000-00`), de outra empresa (modelo copiado)?
4. Os dados batem entre site, política de privacidade, termos e nota fiscal? Divergência
   confunde o consumidor e enfraquece a defesa.
5. Opcional: o usuário pode conferir o CNPJ e a razão social no comprovante de inscrição da
   Receita Federal. **Não** faça consultas externas com dados do usuário sem pedir.

## Como corrigir
- Pergunte os dados que faltam (nunca invente). Se o usuário não quiser publicar endereço
  residencial (MEI que trabalha em casa), explique o risco (descumprimento do decreto em loja
  online) e as alternativas (endereço comercial/escritório virtual vinculado ao CNPJ).
- Insira no componente de rodapé global (ex.: `components/Footer.tsx`, `footer.php`,
  `layouts/default.vue`, `theme.liquid`). Mantenha o estilo do site e contraste adequado.
- Use os mesmos dados nos documentos legais.
- Inclua link `mailto:`/`tel:` e, se houver WhatsApp, `https://wa.me/55...`.
