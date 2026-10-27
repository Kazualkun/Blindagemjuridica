# Itens 12 e 13 — Avaliações/depoimentos falsos e promessas enganosas

**Base:** CDC arts. 6º (III, IV), 30, 31, 35, 36, 37, 38, 66, 67; Lei 9.279/96 art. 195
(concorrência desleal); CONAR — Código (arts. 27 e 32) e Anexo Q (testemunhais); Guia CONAR de
influenciadores; normas setoriais (ANVISA, CFM, OAB, CVM…); Código Civil art. 20 / Súmula 403
STJ (uso de imagem).

Consequências típicas: autuação do Procon, ação do MP, ordem do CONAR para retirar anúncio,
indenização a consumidores, **crime** (CDC arts. 66 e 67), bloqueio de anúncios no Google/Meta,
remoção das estrelas nos resultados do Google.

---

## Item 12 — Avaliações e depoimentos

### Sinais de depoimento/avaliação falso ou irregular (o scanner procura vários)
- Fotos de geradores ou bancos: `randomuser.me`, `pravatar.cc`, `thispersondoesnotexist`,
  `ui-avatars`, `dicebear`, fotos de banco de imagens como "cliente".
- `faker` usado em código de produção.
- Array fixo de depoimentos com nomes genéricos ("Maria S.", "João P."), todos 5 estrelas,
  textos parecidos.
- `aggregateRating`/`ratingValue` fixo no JSON-LD (nota que não vem de avaliações reais).
- "+10.000 clientes satisfeitos", "nota 4,9", "98% de aprovação" sem fonte.
- Contadores "37 pessoas vendo agora" / "12 compraram hoje" com `Math.random()`.
- Avaliações compradas, trocadas por brinde sem informar, ou só as positivas exibidas
  (filtrar negativas é omissão enganosa).

### Regras
1. Depoimento precisa ser **real, de cliente real, refletir experiência real e atual**, com
   **autorização** para uso de nome/imagem (direito de imagem + LGPD).
2. Se o depoente recebeu algo (produto grátis, desconto, pagamento), informar.
3. Resultado individual não pode ser apresentado como típico ("perdeu 15 kg") sem aviso claro
   e comprovação; em saúde, muitas vezes é vedado (ver regras do setor).
4. Nota agregada exibida (estrelas) deve vir de sistema de avaliações verificável, incluindo
   as negativas. Os dados estruturados de avaliação não devem ser fabricados.
5. Números de prova social precisam de comprovação guardada (art. 38 — ônus é do anunciante).

### Como corrigir
- **Não remova nem altere sem perguntar.** Pergunte, para cada bloco: "Estes depoimentos são
  de clientes reais, com autorização de uso de nome e foto? Você tem como comprovar?"
  - Sim → mantenha; troque avatar gerado pela foto autorizada ou por iniciais; guarde a
    autorização (sugira formulário/termo de autorização).
  - Não / não sei → remova o bloco ou troque por chamada honesta ("Seja um dos primeiros
    clientes") e, se o usuário quiser, implemente coleta real de avaliações.
- Contador aleatório → remover (ou ligar a dado real do backend, se existir).
- `aggregateRating` fixo → remover ou gerar a partir de avaliações reais.
- Número de clientes → manter apenas se o usuário confirmar o número e tiver comprovação.

---

## Item 13 — Promessas e publicidade enganosa

### Padrões de alto risco
| Padrão | Risco | Correção típica |
|--------|-------|----------------|
| "Resultado garantido", "100% eficaz", "risco zero", "infalível" | Alto | Reescrever sem absoluto; descrever o que de fato é entregue |
| "Lucro/renda garantida", "ganhe R$ X por dia", "fique rico" | Crítico | Remover; incluir aviso de que resultados variam; atenção a pirâmide (Lei 1.521/51) e CVM |
| "Cura", "emagreça X kg", "sem efeitos colaterais", "elimina ansiedade" | Crítico | Remover; produtos sujeitos à ANVISA só podem alegar o que está registrado/permitido |
| "Clinicamente/cientificamente comprovado", "aprovado pela ANVISA", "recomendado por médicos" | Alto | Manter só com estudo/registro citável disponível (art. 36 par. único) |
| "O melhor do Brasil", "nº 1", "líder de mercado", "o mais barato" | Médio | Manter só com fonte (pesquisa, ranking, data); ou trocar por qualidade verificável |
| "Aprovação garantida", "emprego garantido" (cursos) | Alto | Remover/reescrever |
| "Crédito aprovado", "sem consulta ao SPC/Serasa" | Alto | Vedado (CDC art. 54-C) |
| Preço "de R$ 299 por R$ 99" | Info→Alto | "De" precisa ter sido praticado de fato por período razoável; senão é desconto fictício |
| "Últimas unidades", "só hoje", contagem regressiva que reinicia | Médio→Alto | Só se verdadeiro; contador deve ter data real e não reiniciar |
| "Frete grátis" com condição escondida | Médio | Mostrar condições junto da oferta (Decreto 7.962 art. 2º VI) |
| Garantia "dinheiro de volta" sem regras claras | Médio | Explicar regras na política de reembolso e cumprir |
| Comparação depreciativa com concorrente nomeado | Alto | Comparação só objetiva e comprovável (CONAR art. 32; LPI art. 195) |
| Publi/afiliado não identificado | Médio | Identificar como publicidade (CDC art. 36; Guia CONAR) |
| Imagem meramente ilustrativa que difere do produto | Médio | Avisar e mostrar foto real |

### Setores com regras próprias (pergunte se o projeto é desses)
- **Saúde (médicos, dentistas, nutricionistas, psicólogos, clínicas)**: regras de publicidade
  dos conselhos (ex.: Resolução CFM 2.336/2023) — limites para antes/depois, preços,
  promessas, depoimentos de pacientes.
- **Medicamentos, suplementos, cosméticos, alimentos**: ANVISA (alegações permitidas, sem cura).
- **Advocacia**: Provimento OAB 205/2021 (publicidade informativa, sem captação).
- **Investimentos/finanças**: CVM, Banco Central; nada de rentabilidade garantida.
- **Educação**: não prometer aprovação/emprego; reconhecimento MEC quando aplicável.
- **Apostas**: Lei 14.790/2023 (ver `riscos-juridicos.md`).

### Como auditar
1. Leia os textos de marketing (home, landing pages, páginas de produto, e-mails/templates,
   metatags e títulos de SEO, anúncios no repositório, i18n).
2. Liste cada alegação forte com arquivo:linha.
3. Verifique coerência: o que a página promete está nos termos/política? O preço exibido é o
   cobrado no checkout (taxas escondidas = enganoso)?

### Como corrigir
- Proponha reescrita para cada alegação (mostre "antes → depois") e aplique após aprovação.
  Ex.: "Resultados garantidos" → "Método aplicado com mais de 300 alunos desde 2021" (se
  verdadeiro) ou "Veja como funciona o método".
- Inclua avisos quando necessário: "Resultados variam de pessoa para pessoa", "Imagem
  meramente ilustrativa", "Oferta válida até DD/MM/AAAA ou enquanto durarem os estoques
  (N unidades)".
- Peça ao usuário para guardar as comprovações das alegações que permanecerem.
