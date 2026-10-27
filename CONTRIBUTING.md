# Como contribuir

Obrigado por ajudar a deixar a web brasileira mais segura juridicamente e mais acessível!

## Tipos de contribuição bem-vindos
- **Atualização legal**: nova lei, resolução da ANPD, decisão relevante, mudança de
  entendimento. Inclua a fonte oficial (planalto.gov.br, gov.br/anpd, stf.jus.br) no PR.
- **Novas detecções no scanner** (novo rastreador, novo padrão de promessa enganosa, nova
  stack). Toda regra nova precisa de caso no fixture `loja-problematica` e não pode gerar
  achado grave no `site-limpo`.
- **Falsos positivos**: abra uma issue com um trecho mínimo de código que reproduz.
- **Modelos de documentos**: melhorias de clareza, variantes por setor.
- **Guias por stack** (como integrar o banner, onde criar páginas).

## Regras
1. O scanner usa **apenas a biblioteca padrão** do Python 3.9+.
2. Mensagens e documentos em **português do Brasil**, claros e sem juridiquês desnecessário.
3. Cite a base legal com artigo; não afirme o que não está na fonte.
4. Rode os testes antes do PR:
   ```bash
   python -m unittest discover -s tests -v
   ```
5. Não inclua dados reais de pessoas ou empresas nos fixtures (use CNPJs de exemplo válidos
   apenas no formato, como `11.222.333/0001-81`).

## Estrutura
- `skills/blindagem-juridica/SKILL.md` — fluxo e regras da skill.
- `skills/blindagem-juridica/references/` — um arquivo por grupo de itens.
- `skills/blindagem-juridica/scripts/` — scanner e utilitários.
- `skills/blindagem-juridica/templates/` — modelos e banner de consentimento.
- `tests/` — testes e sites de exemplo.
