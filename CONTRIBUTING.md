# Como contribuir

Contribuições são bem-vindas: correção de fato, medição nova, receita, exemplo, melhoria de skill.
**Quem faz merge e publica são só os mantenedores (Inovai).** Este repositório é gerado a partir de um
acervo de estudo: uma contribuição aceita entra primeiro nesse acervo e volta aqui na próxima publicação,
com crédito no PR e no `CHANGELOG.md`.

## Fluxo
1. Abra uma *issue* para dúvida, erro de fato ou proposta maior; para correção pequena, vá direto ao PR.
2. Faça um fork, crie uma branch e abra o PR contra `main`, dizendo o que muda e de onde vem a evidência.
3. Um mantenedor revisa. Se aceitar, incorpora a mudança pela esteira interna e fecha o PR com o link do
   commit publicado; o PR não é mergeado direto.

## Antes de abrir o PR
- `python -X utf8 ferramentas/validar.py` passa (Python 3.12; só biblioteca padrão).
- Toda afirmação tem fonte e rótulo: **[doc]** documentação TypeSafe · **[testado]** medição (com data,
  versão do modelo e tamanho da amostra) · **[terceiro]** vídeo/post · **[local]** conclusão própria.
- Um fato, um lugar: atualize a nota que já trata do assunto; nota nova entra em `conhecimento/INDICE.md`.
- Medição nova segue o protocolo de [conhecimento/avaliar/metodo.md](conhecimento/avaliar/metodo.md)
  (ajuste e teste separados, perguntas congeladas antes do teste, uma rodada no teste).
- Português do Brasil; identificadores em inglês.

## Nunca
- Chave, token ou segredo (use a variável `TYPESAFE_API_KEY`, nunca o valor).
- Dado pessoal real ou dado interno de empresa; exemplos usam dados fictícios.
- Texto integral de material de terceiros (documentação, transcrições, conjuntos de dados com licença
  restritiva) — resumo e citação curta, com fonte.

## Licença
Ao contribuir, você concorda que sua contribuição é licenciada sob a [licença MIT](LICENSE) deste repositório.
