# Itens 5 e 6 — Formulários em conformidade com a LGPD e minimização de dados

**Base:** LGPD arts. 6º (I, II, III, VI), 7º, 8º, 9º, 11, 14, 46; Marco Civil art. 7º (IX).

## Item 5 — O que todo formulário que coleta dado pessoal precisa ter

1. **Aviso de privacidade no ponto de coleta** (camada curta + link): para que os dados serão
   usados e onde ler mais. Ex.: "Usamos seu nome e e-mail para responder a esta mensagem.
   Saiba mais na [Política de Privacidade]."
2. **Consentimentos separados e desmarcados** para finalidades opcionais (newsletter, ofertas,
   WhatsApp, compartilhamento com parceiros). Um checkbox por finalidade. Nunca pré-marcado.
3. **Aceite dos termos separado do marketing.** "Li e aceito os termos **e** aceito receber
   ofertas" na mesma caixa é inválido (art. 8º §4º).
4. **Marketing não é condição** para o serviço: checkbox de marketing nunca `required`.
5. **Campos opcionais sinalizados** como opcionais; obrigatórios só os necessários.
6. **Dados sensíveis** (saúde, religião, origem racial, biometria, vida sexual, opinião
   política, filiação sindical, genética): só com hipótese do art. 11 — normalmente
   consentimento **específico e destacado** (checkbox próprio com texto explicando a
   finalidade) ou outra base do inciso II (ex.: tutela da saúde em clínica).
7. **Menores de idade**: se o formulário pode ser preenchido por crianças, consentimento de
   pai/mãe/responsável (art. 14 §1º); considere o ECA Digital.
8. **Transmissão segura** (HTTPS) e, no backend, validação, rate limit/antispam, armazenamento
   com acesso restrito; não enviar dados do formulário para pixels/analytics.
9. **Acessibilidade** do formulário (rótulos, erros descritivos, foco) — ver `acessibilidade.md`.
10. **Confirmação**: mensagem clara após envio; se houver dupla confirmação (double opt-in) para
    newsletter, melhor ainda — prova o consentimento.

Texto-padrão de consentimento de marketing (adapte):
```html
<label>
  <input type="checkbox" name="consentimento_marketing" value="sim">
  Quero receber novidades e ofertas da [Empresa] por e-mail. Posso cancelar quando quiser.
  (opcional)
</label>
```

Aceite de termos (cadastro/checkout):
```html
<label>
  <input type="checkbox" name="aceite_termos" required>
  Li e aceito os <a href="/termos-de-uso">Termos de Uso</a> e estou ciente da
  <a href="/politica-de-privacidade">Política de Privacidade</a>.
</label>
```
(Note: "estou ciente" da política — a política informa; ela não é "aceita" como base para tudo.)

## Item 6 — Só dados necessários (princípio da necessidade, art. 6º III)

Para cada campo, pergunte: **qual finalidade concreta exige este dado agora?** Se a resposta for
"pode ser útil um dia", remova.

| Campo | Normalmente necessário? | Alternativa |
|------|-------------------------|-------------|
| CPF | Só se emitir nota fiscal, cobrança (boleto/Pix/cartão exigem no gateway), crédito, KYC, serviço regulado | Pedir só no checkout, não no cadastro/lead |
| Data de nascimento | Raramente | Caixa "tenho 18 anos ou mais"; pedir idade só se a lei/serviço exigir |
| RG, CNH, nome da mãe | Quase nunca em site comum | Remover |
| Gênero/sexo | Raramente | Opcional, com "prefiro não informar"; ou remover |
| Endereço completo | Só para entrega/cobrança | Pedir no checkout |
| Telefone | Se houver contato por telefone/WhatsApp | Opcional |
| Estado civil, renda, profissão | Só em crédito/seguros/serviços que dependem disso | Remover |
| Foto/selfie, geolocalização precisa | Só com finalidade clara (ex.: verificação de identidade, entrega) | Localização aproximada; pedir permissão no momento do uso |
| Dados sensíveis | Só em serviços que dependem deles | Remover ou art. 11 com consentimento específico |
| Lead de e-book/newsletter | Nome + e-mail bastam | Remover o resto |

### Como auditar
1. Liste todos os campos de todos os formulários (o scanner faz uma primeira lista) e onde são
   salvos (rota de API, tabela, CRM, planilha, e-mail).
2. Compare com o **uso real** no backend: campo coletado e nunca lido = desnecessário.
3. Verifique coleta invisível: query params com e-mail em URLs (vazam para analytics),
   hidden inputs com dados pessoais, logs com payload completo, envio do formulário inteiro
   para ferramentas de terceiros.
4. Verifique retenção: há rotina de exclusão? Leads antigos ficam para sempre?

### Como corrigir
- **Técnico, aplicar direto:** marcar opcionais, separar consentimentos, desmarcar checkboxes,
  adicionar aviso, trocar `http://` por `https://`, remover dados pessoais de eventos de
  analytics e de logs.
- **Precisa de decisão do usuário:** remover/tornar opcional um campo que o backend usa
  (pergunte a finalidade; mostre o campo e o arquivo onde é usado). Se o usuário decidir
  remover, remova do front **e** do backend/validação/tipos com cuidado (migrations de banco
  só com aprovação explícita).
