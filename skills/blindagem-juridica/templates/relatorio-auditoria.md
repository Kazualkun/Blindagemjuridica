<!--
MODELO — Relatório final (gravar como AUDITORIA-JURIDICA.md na raiz do projeto).
Seja específico: arquivos, linhas, o que mudou. Remova os comentários.
-->

# Auditoria Jurídica — {{NOME_DO_PROJETO}}

**Data:** {{DATA}} · **Gerado com:** skill blindagem-juridica · **Modo:** {{auditar|corrigir}}

> ⚖️ Este relatório é uma auditoria técnica automatizada e **não constitui parecer jurídico**.
> Ele reduz riscos, mas não garante ausência de questionamentos. Documentos contratuais e
> pontos marcados como alto risco devem ser revisados por advogado(a).

## Placar

| # | Item | Antes | Depois | Observação |
|---|------|-------|--------|-----------|
| 1 | Política de privacidade | ❌ | ✅ | {{}} |
| 2 | Termos de uso | | | |
| 3 | Aviso de cookies | | | |
| 4 | Política de reembolso | | | |
| 5 | Formulários (LGPD) | | | |
| 6 | Só dados necessários | | | |
| 7 | Scripts de rastreamento | | | |
| 8 | Acessibilidade geral | | | |
| 9 | Alt nas imagens | | | |
| 10 | Contraste | | | |
| 11 | Navegação por teclado | | | |
| 12 | Avaliações e depoimentos | | | |
| 13 | Promessas e publicidade | | | |
| 14 | Direitos autorais | | | |
| 15 | Dados da empresa | | | |
| 16 | Conformidade LGPD | | | |
| 17 | Outros riscos jurídicos | | | |

Legenda: ✅ Conforme · ⚠️ Parcial · ❌ Não conforme · ➖ Não se aplica

**Riscos restantes mais importantes:**
1. {{}}
2. {{}}
3. {{}}

## O que foi corrigido

<!-- Agrupe por item. Para cada mudança: o problema, a base legal e os arquivos alterados/criados. -->

### {{N}}. {{Item}}
- **Problema:** {{}} — `{{arquivo:linha}}` — {{base legal}}
- **Correção:** {{}} — arquivos: `{{}}`

## Documentos criados

| Documento | Arquivo | URL/rota | Linkado em |
|-----------|---------|----------|-----------|
| Política de Privacidade | `{{}}` | `{{}}` | rodapé, formulários, cadastro, checkout |

## O que depende de você

<!-- Ações que o código não resolve, em ordem de prioridade. -->
- [ ] 🔴 {{ex.: revogar a chave X que estava no código e gerar nova}}
- [ ] 🟠 {{ex.: confirmar licença das imagens listadas abaixo ou substituí-las}}
- [ ] 🟠 {{ex.: guardar comprovação da alegação "Y" ou aprovar a reescrita}}
- [ ] 🟡 {{ex.: verificar DPA dos fornecedores}}
- [ ] Revisão por advogado(a) dos termos de uso e da política de reembolso.

### Marcadores pendentes `[[PREENCHER]]`
| Arquivo | Linha | O que falta |
|---------|-------|-------------|

### Itens que exigem decisão (não alterados)
| Arquivo | Conteúdo | Por que é risco | Opções |
|---------|----------|-----------------|--------|

## Perfil e respostas (usado na próxima execução)

- **Tipo de negócio:** {{}}
- **Stack:** {{}}
- **Empresa:** {{razão social}} · CNPJ {{}} · {{endereço}} · {{contatos}}
- **Encarregado/canal:** {{}}
- **Público:** {{B2C/B2B}} · menores: {{sim/não}} · exterior: {{}}
- **Prazos (entrega, troca, estorno, retenção):** {{}}
- **Mapa de dados:**

| Dado | Onde é coletado | Finalidade | Base legal | Onde fica | Compartilhado com |
|------|-----------------|-----------|-----------|-----------|-------------------|

- **Rastreadores e categoria:** {{}}
- **Decisões do usuário:** {{ex.: depoimentos confirmados como reais em DD/MM; campo CPF mantido para nota fiscal}}

## Como manter
- Rode a skill novamente ao adicionar formulários, scripts de terceiros, novos fornecedores ou
  páginas de venda.
- Atualize a data das políticas sempre que mudar o tratamento de dados.
- Revise este relatório a cada 12 meses.
