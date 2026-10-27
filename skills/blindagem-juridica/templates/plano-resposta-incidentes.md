<!--
MODELO — Plano de Resposta a Incidentes de Segurança com Dados Pessoais
Documento INTERNO. Base: LGPD arts. 46 a 48; Resolução CD/ANPD nº 15/2024.
Gere em docs/lgpd/plano-de-resposta-a-incidentes.md. Remova os comentários.
-->

# Plano de Resposta a Incidentes de Segurança

**Empresa:** {{RAZAO_SOCIAL}} · **Atualizado em:** {{DATA}}

## 1. O que é incidente
Qualquer evento que comprometa a confidencialidade, integridade ou disponibilidade de dados
pessoais: vazamento, acesso indevido, perda, chave/API exposta, banco aberto, ransomware,
e-mail enviado para destinatários errados, dispositivo perdido com dados.

## 2. Responsáveis
| Papel | Pessoa | Contato |
|------|--------|---------|
| Coordenação e decisão | {{}} | {{}} |
| Técnico (contenção) | {{}} | {{}} |
| Encarregado / comunicação com ANPD e titulares | {{}} | {{}} |
| Apoio jurídico | {{}} | {{}} |

## 3. Passo a passo
1. **Detectar e registrar** — data/hora, como foi descoberto, sistemas afetados. Preserve logs e evidências.
2. **Conter (imediato)** — revogar/rotacionar chaves e senhas, fechar acesso, tirar sistema do ar
   se preciso, bloquear contas comprometidas.
3. **Avaliar** — quais dados, quantos titulares, se há dados sensíveis, de crianças, financeiros
   ou de autenticação; se há risco ou dano relevante aos titulares.
4. **Comunicar** — se houver risco ou dano relevante: **ANPD e titulares em até 3 dias úteis**
   (Res. CD/ANPD 15/2024), pelo formulário da ANPD (gov.br/anpd). A comunicação descreve:
   natureza dos dados, titulares envolvidos, medidas de segurança, riscos, motivo de eventual
   demora, medidas adotadas para reverter ou mitigar.
5. **Corrigir a causa** e verificar que não há outros pontos iguais.
6. **Registrar** o incidente (inclusive os não comunicados) e manter o registro por pelo
   menos 5 anos.
7. **Revisar** o plano e os controles (lições aprendidas).

## 4. Contatos úteis
- ANPD — comunicação de incidente: canal oficial em gov.br/anpd
- Hospedagem/infra: {{}}
- Gateway de pagamento: {{}}
- Fornecedores críticos: {{}}

## 5. Modelo de aviso aos titulares
> Assunto: Aviso de incidente de segurança envolvendo seus dados
>
> Em {{data}}, identificamos {{descrição simples}}. Os dados envolvidos foram {{dados}}.
> Já tomamos as seguintes medidas: {{medidas}}. Recomendamos que você {{recomendações, ex.:
> troque sua senha, fique atento a mensagens suspeitas}}. Para dúvidas, fale com
> {{encarregado/canal}}.
