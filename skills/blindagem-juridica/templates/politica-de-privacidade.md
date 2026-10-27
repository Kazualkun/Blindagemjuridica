<!--
MODELO — Política de Privacidade (LGPD)

Instruções para o Claude (remova todos os comentários no documento final):
- {{CHAVES}} são preenchidas com dados do projeto (mapa de dados da Fase 1) ou do usuário.
- Seções marcadas [SE ...] só entram se a condição for verdadeira no projeto. Apague as demais.
- Liste SOMENTE dados, finalidades, cookies e fornecedores que existem de fato no código ou que
  o usuário confirmou. Nada genérico "por via das dúvidas".
- Linguagem: clara, direta, segunda pessoa ("você"). Evite juridiquês. Use títulos navegáveis.
- Converta para o formato da stack (página TSX/Vue/HTML/Markdown do CMS) mantendo os títulos.
-->

# Política de Privacidade

**Última atualização:** {{DATA_ATUALIZACAO}} · **Versão:** {{VERSAO}}

Esta Política explica como **{{RAZAO_SOCIAL}}** ("{{NOME_FANTASIA}}", "nós"), inscrita no CNPJ
**{{CNPJ}}**, com sede em {{ENDERECO_COMPLETO}}, trata os dados pessoais de quem usa
{{NOME_DO_SITE_OU_APP}} ({{URL}}), conforme a Lei Geral de Proteção de Dados Pessoais
(Lei nº 13.709/2018 — LGPD) e o Marco Civil da Internet (Lei nº 12.965/2014).

Se tiver dúvidas, fale com a gente pelo canal indicado em [Como falar conosco](#contato).

## Resumo

<!-- 4 a 6 tópicos curtos com o essencial. Ex.: -->
- Coletamos {{RESUMO_DADOS}} para {{RESUMO_FINALIDADES}}.
- Não vendemos seus dados.
- [SE houver cookies não essenciais] Cookies de estatística e publicidade só são usados com sua
  autorização, que você pode mudar a qualquer momento em "Preferências de cookies", no rodapé.
- Você pode acessar, corrigir, excluir ou levar seus dados para outro serviço — veja
  [Seus direitos](#direitos).

## 1. Quem é o responsável pelos seus dados

O controlador é **{{RAZAO_SOCIAL}}**, CNPJ {{CNPJ}}.
<!-- [SE houver encarregado] -->
Nosso encarregado pelo tratamento de dados pessoais (DPO) é **{{NOME_ENCARREGADO}}**, que pode
ser contatado pelo e-mail **{{EMAIL_ENCARREGADO}}**.
<!-- [SE agente de pequeno porte sem encarregado] -->
<!-- Para assuntos de privacidade, use o canal **{{EMAIL_PRIVACIDADE}}**, que é atendido por
nossa equipe responsável. -->

## 2. Quais dados tratamos, para quê e com qual base legal

<!-- Uma linha por contexto real do projeto. Exemplos — mantenha só os que existem. -->

| Quando | Dados | Para quê | Base legal (LGPD) |
|--------|-------|----------|-------------------|
| [SE formulário de contato] Você nos envia uma mensagem | Nome, e-mail, {{OUTROS_CAMPOS_CONTATO}}, conteúdo da mensagem | Responder ao seu contato | Procedimentos preliminares a contrato (art. 7º, V) ou legítimo interesse (art. 7º, IX) |
| [SE cadastro] Você cria uma conta | {{CAMPOS_CADASTRO}} | Criar e manter sua conta e prestar o serviço | Execução de contrato (art. 7º, V) |
| [SE compra] Você faz uma compra | {{CAMPOS_CHECKOUT}} | Processar pagamento, emitir nota fiscal, entregar, atender trocas e devoluções | Execução de contrato (art. 7º, V) e obrigação legal (art. 7º, II) |
| [SE newsletter] Você se inscreve para receber novidades | E-mail{{, NOME}} | Enviar comunicações de marketing | Consentimento (art. 7º, I) — revogável a qualquer momento |
| Você navega no site | Endereço IP, data e hora de acesso, navegador, dispositivo, páginas acessadas | Segurança, prevenção a fraudes e cumprimento do Marco Civil (guarda de registros de acesso) | Obrigação legal (art. 7º, II) e legítimo interesse (art. 7º, IX) |
| [SE analytics com consentimento] Você aceita cookies de estatística | Identificadores de cookie, páginas visitadas, interações, localização aproximada | Entender o uso do site e melhorá-lo | Consentimento (art. 7º, I) |
| [SE pixels de publicidade] Você aceita cookies de marketing | Identificadores de cookie e de dispositivo, eventos (visita, cadastro, compra) | Medir campanhas e exibir anúncios relevantes em outras plataformas | Consentimento (art. 7º, I) |
| [SE dado sensível] {{CONTEXTO}} | {{DADO_SENSIVEL}} | {{FINALIDADE_ESPECIFICA}} | {{BASE_ART_11}} (art. 11) |
| [SE atendimento por WhatsApp/chat] Você fala conosco pelo {{CANAL}} | Nome, telefone, conteúdo das mensagens | Atendimento | Execução de contrato ou legítimo interesse |
| [SE IA] Você usa {{FUNCIONALIDADE_IA}} | {{DADOS_ENVIADOS_IA}} | {{FINALIDADE_IA}} | {{BASE}} |

Coletamos apenas os dados necessários para essas finalidades. Campos opcionais estão
identificados como tal nos formulários.

<!-- [SE houver decisão automatizada relevante] -->
<!-- ### Decisões automatizadas
{{DESCRICAO}}. Você pode pedir revisão dessas decisões e informações sobre os critérios
usados (art. 20 da LGPD). -->

## 3. Com quem compartilhamos

Não vendemos seus dados pessoais. Compartilhamos apenas o necessário com:

<!-- Liste os operadores detectados no código e confirmados pelo usuário. -->
- **Fornecedores que operam o serviço para nós**, sob contrato e com dever de confidencialidade:
  {{LISTA_OPERADORES}}
  <!-- ex.: hospedagem (Vercel), banco de dados (Supabase), envio de e-mails (Resend),
  pagamentos (Stripe / Mercado Pago), atendimento (Crisp). -->
- [SE pixels/analytics] **Plataformas de estatística e publicidade**, somente se você autorizar:
  {{LISTA_RASTREADORES}}.
- [SE entregas] **Transportadoras e Correios**, para entregar seu pedido.
- **Autoridades públicas**, quando exigido por lei ou ordem judicial.
- **Em caso de reorganização societária** (fusão, aquisição), mantidas as garantias desta Política.

## 4. Transferência internacional

<!-- [SE algum fornecedor estiver fora do Brasil] -->
Alguns fornecedores armazenam ou processam dados fora do Brasil, principalmente nos
{{PAISES}} ({{FORNECEDORES_EXTERIOR}}). Nesses casos, adotamos as garantias previstas no art. 33
da LGPD, como cláusulas contratuais e fornecedores com padrões de proteção compatíveis.
<!-- [SE nenhum] Seus dados são armazenados em servidores localizados no Brasil. -->

## 5. Cookies e tecnologias semelhantes

Usamos cookies estritamente necessários para o funcionamento do site.
[SE houver não essenciais] Cookies de estatística, marketing e conteúdos de terceiros só são
ativados se você autorizar no aviso de cookies. Você pode mudar sua escolha a qualquer momento
em **Preferências de cookies**, no rodapé. Detalhes em nossa
[Política de Cookies]({{URL_POLITICA_COOKIES}}).

## 6. Por quanto tempo guardamos

| Dado | Prazo |
|------|-------|
| Registros de acesso (IP, data e hora) | 6 meses (Marco Civil da Internet, art. 15) |
| [SE compra] Dados de pedidos e fiscais | 5 anos (legislação tributária) |
| [SE cadastro] Dados da conta | Enquanto a conta existir e, após o encerramento, pelo prazo necessário para cumprir obrigações legais ou defender direitos |
| [SE contato] Mensagens de contato | {{PRAZO_CONTATO}} |
| [SE newsletter] E-mail de newsletter | Até você cancelar a inscrição |
| {{OUTROS}} | {{PRAZO}} |

Após esses prazos, os dados são eliminados ou anonimizados.

## 7. Seus direitos {#direitos}

Pela LGPD (art. 18), você pode, a qualquer momento e gratuitamente:

- confirmar se tratamos seus dados e **acessá-los**;
- **corrigir** dados incompletos, inexatos ou desatualizados;
- pedir **anonimização, bloqueio ou eliminação** de dados desnecessários ou tratados em
  desconformidade;
- pedir a **portabilidade** dos dados a outro fornecedor;
- pedir a **eliminação** dos dados tratados com base no seu consentimento;
- saber **com quem compartilhamos** seus dados;
- ser informado sobre a possibilidade de **não consentir** e suas consequências;
- **revogar o consentimento**;
- pedir **revisão de decisões automatizadas**;
- apresentar reclamação à **Autoridade Nacional de Proteção de Dados (ANPD)**.

**Como exercer:** {{COMO_EXERCER}}
<!-- ex.: envie um e-mail para {{EMAIL_PRIVACIDADE}} ou use a opção "Meus dados" em Minha Conta.
Podemos pedir informações para confirmar sua identidade. Respondemos em até 15 dias. -->

## 8. Segurança

Adotamos medidas técnicas e administrativas para proteger seus dados, como conexão criptografada
(HTTPS), controle de acesso, {{OUTRAS_MEDIDAS}}. Nenhum sistema é totalmente imune a incidentes;
se ocorrer um incidente que possa trazer risco ou dano relevante, comunicaremos você e a ANPD
nos termos da lei.

## 9. Crianças e adolescentes

<!-- [SE o serviço NÃO é para menores] -->
{{NOME_DO_SITE_OU_APP}} não é direcionado a menores de 18 anos e não coletamos
intencionalmente dados de crianças. Se você acredita que coletamos dados de uma criança, fale
conosco para que sejam excluídos.
<!-- [SE o serviço é para menores] Descreva: melhor interesse, consentimento de um dos pais ou
responsável para crianças (art. 14 §1º), dados mínimos, sem publicidade direcionada por
perfilamento, ferramentas de supervisão (ECA Digital — Lei 15.211/2025). Recomende revisão
jurídica. -->

## 10. Alterações desta Política

Podemos atualizar esta Política para refletir mudanças no serviço ou na lei. A data da última
atualização fica no topo. Mudanças relevantes serão comunicadas {{COMO_COMUNICA}}
<!-- ex.: por e-mail ou aviso no site -->.

## 11. Como falar conosco {#contato}

- **Privacidade e direitos do titular:** {{EMAIL_PRIVACIDADE_OU_ENCARREGADO}}
- **Atendimento geral:** {{EMAIL_ATENDIMENTO}} · {{TELEFONE}}
- **Endereço:** {{ENDERECO_COMPLETO}}
