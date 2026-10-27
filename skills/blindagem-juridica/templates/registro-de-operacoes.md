<!--
MODELO — Registro das Operações de Tratamento (ROPA) — LGPD art. 37
Documento INTERNO (não publicar). Gere em docs/lgpd/registro-de-operacoes.md preenchido com o
mapa de dados da auditoria. Agentes de pequeno porte podem usar o formato simplificado
(Res. CD/ANPD 2/2022). Remova os comentários.
-->

# Registro das Operações de Tratamento de Dados Pessoais

- **Controlador:** {{RAZAO_SOCIAL}} — CNPJ {{CNPJ}}
- **Encarregado / canal:** {{ENCARREGADO_OU_CANAL}}
- **Elaborado em:** {{DATA}} · **Revisar a cada:** 12 meses ou a cada nova funcionalidade que trate dados

## Operações

<!-- Uma linha por operação real. Exemplos: -->

| # | Operação | Titulares | Dados pessoais | Sensíveis? | Finalidade | Base legal | Origem (onde no sistema) | Compartilhamento (operadores) | Transferência internacional | Retenção | Medidas de segurança |
|---|----------|-----------|----------------|-----------|-----------|-----------|--------------------------|-------------------------------|-----------------------------|----------|----------------------|
| 1 | Formulário de contato | Visitantes | Nome, e-mail, mensagem | Não | Responder contato | Art. 7º, V | `{{arquivo do formulário}}` → `{{rota de API}}` | {{e-mail transacional}} | {{sim/não, país}} | {{prazo}} | HTTPS, acesso restrito |
| 2 | Cadastro de clientes | Clientes | {{campos}} | {{}} | Prestar o serviço | Art. 7º, V | {{}} | {{banco gerenciado, autenticação}} | {{}} | {{}} | Hash de senha, RLS |
| 3 | Pagamentos | Clientes | Nome, CPF, e-mail, dados de pagamento (tokenizados) | Não | Cobrança e nota fiscal | Art. 7º, V e II | {{}} | {{gateway}} | {{}} | 5 anos | Tokenização no gateway |
| 4 | Estatística de uso | Visitantes que consentiram | Identificadores de cookie, navegação | Não | Melhorar o site | Art. 7º, I | Banner de consentimento | {{Google Analytics}} | EUA | {{14 meses}} | Consent Mode, IP truncado |
| 5 | Publicidade | Visitantes que consentiram | Identificadores, eventos | Não | Medir campanhas | Art. 7º, I | {{}} | {{Meta, Google Ads}} | EUA | {{}} | Consentimento por categoria |
| 6 | Registros de acesso | Usuários | IP, data/hora | Não | Marco Civil art. 15 | Art. 7º, II | Logs do servidor | {{hospedagem}} | {{}} | 6 meses | Acesso restrito |

## Operadores (fornecedores)

| Fornecedor | Serviço | Dados tratados | País | Contrato/DPA verificado? |
|-----------|---------|----------------|------|--------------------------|
| {{}} | {{}} | {{}} | {{}} | {{sim/não/pendente}} |

## Pendências
- {{ex.: confirmar DPA com fornecedor X}}
- {{ex.: definir prazo de retenção de leads}}
