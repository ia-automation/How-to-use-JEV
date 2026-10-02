# Briefing — casos novos medidos na API real (task iniciada em 2026-10-01)

Briefing da TASK inteira; nasce uma vez. Cada agente recebe o recorte que lhe cabe; o conselheiro (Codex) recebe este
mesmo arquivo na revisão adversarial de cada exemplo. Complementa [BRIEFING.md](BRIEFING.md) (os 5 primeiros) e
[DADOS.md](DADOS.md) (regras dos dados), que continuam valendo.

## O que entrega
Novos exemplos em `exemplos/`, cada um um problema real resolvido com o Jev e **medido na API real** contra conjunto
rotulado, no mesmo molde dos 5 existentes (modelo de referência: `triagem-atendimento/`). Objetivo do dono: o máximo de
exemplos diversos, porque isso vira produto dentro do CRM com todos os devs usando. Lista completa (26) e ondas em
`conhecimento/evidencias/casos-externos.md` (catálogo) e abaixo.

**Onda 1 (em curso):** `guarda-tool-call` · `juiz-de-eval` · `conferencia-de-promessas` · `imovel-errado` ·
`roteador-email` (este último com dado real do F11, só depois da varredura + auditoria do dono).
Ondas seguintes: lint semântico de diff, auditor de evidência, próxima pergunta necessária, opt-out/LGPD, imóvel
duplicado, e o resto do catálogo.

## Papéis e ferramentas (ordem do dono, 2026-10-01)
- Todo agente roda em **Fable** (`model: fable`), inclusive subagentes. No máximo **2 subagentes** ao mesmo tempo.
- **Rotulador ≠ construtor**: quem escreve `dados/` não escreve código do exemplo; quem constrói **não abre
  `teste.json`** antes da rodada final (abre só `ajuste.json` e `rascunho.json`).
- **Revisão adversarial do Codex em cada exemplo**, pelo script `conselheiro.sh`, com este briefing + o README do
  exemplo. Achados são triados pela sessão principal; nada se aplica no automático.
- Código em Python 3.12 com o `.venv` da raiz (SDK `typesafe-sdk` 0.7.2); infra comum em `_comum/` (cliente com cache
  `jevcache.py`, métricas `metricas.py`). Perguntas ao Jev em inglês; dados em pt-BR.

## Critério de aceite (ordenado) — igual ao BRIEFING.md, repetido para o conselheiro
1. Roda sem chave (`python run.py` reproduz do `cache/`); `JEV_MODO=ao_vivo` refaz.
2. Medido de verdade: `resultados.md` gerado pelo script, com acerto por pergunta, cobertura × erro por limiar, p50/p95,
   tokens, custo, versão do modelo, data, n. Ajuste separado do teste; teste congelado por hash e rodado UMA vez.
3. `README.md` curto: problema, quem faz o quê (código/Jev/LLM) e por quê, desenho, baseline, o que deu certo, o que
   falhou, lição, limites.
4. Perguntas e limiares num arquivo só (`perguntas.py`).
5. **Baseline de código** (regra, palavra-chave, igualdade) medido nos mesmos dados; critério de continuar/descartar
   fixado antes do teste.
6. Código pequeno, comentado no "porquê".

## Aceito por desenho
Dados sintéticos escritos por LLM (Fable), um rotulador só; LLM de comparação (juiz, resposta) **simulado ou
opcional** via `claude -p` — se usado, dizer que é o mesmo fornecedor do rotulador; um só modelo (`jev-1.13.0`);
amostras pequenas (ajuste ≥ 30, teste ≥ 60 ou o que a especificação de cada exemplo pedir).

## Onde dói
- Afinar olhando o teste; alargar pergunta para consertar um caso do ajuste (overfit medido no roteador).
- Pedir ao Jev o que o código resolve (contar frases, comparar números, datas) — a rubrica do juiz e a ficha do imóvel
  têm itens assim: eles são **do código**.
- Guarda de tool-call: injeção no `contexto_lido` move a resposta (limite #6); a guarda não é fronteira de segurança.
- Promessas: `not_stated` lido ao pé da letra ("ensolarado" × "face norte").
- Imóvel errado: o Jev escolhe entre candidatos; `null` (informação insuficiente) precisa de válvula.
- Custo escondido: uma requisição por afirmação/candidato multiplica chamadas — agrupar no mesmo state.
- Segredo: a chave nunca em log, cache ou saída; `api_key.txt` só é lido pelo `_comum/jevcache.py`.

## Quem consome
- Agentes que leem o repositório (nota `conhecimento/decidir/jev-llm-codigo.md`, skills) — os exemplos viram referência.
- Versão pública `C:\Users\user\Documents\CRM Inovai\How-to-use-JEV` (gerada por `ferramentas/copia_fria.py --publicar`).
- Devs do CRM Inovai: `guarda-tool-call` é candidato a hook do Claude Code; `conferencia-de-promessas` e
  `imovel-errado` são candidatos a guardas da Luci (0800).

## O que medir antes de decidir
Acerto por pergunta; cobertura × erro por limiar; baseline × Jev nos mesmos casos; custo e latência por item;
erros caros contados à parte (vazamento no guarda, promessa inventada aprovada, referente trocado).

## Como provar
`resultados.md` gerado pelo script + `cache/` com as respostas reais + hash dos arquivos congelados no cabeçalho.

## O que NÃO fazer
- Chamar a API em laço sem cache; publicar número sem n e versão; usar Jev para conta/data/comparação numérica.
- Escrever fora da pasta do próprio exemplo (exceto `_comum/`, do coordenador).
- Rotulador: ler código de exemplo em construção. Construtor: abrir `teste.json` antes da rodada final.
- Varredura da família do defeito: achado de desenho num exemplo → conferir os outros da onda.

---

## Especificação dos dados — onda 1 (o rotulador escreve; o construtor lê)
Regras gerais de [DADOS.md](DADOS.md): pt-BR realista, nada de dado pessoal real, ≥ 30% casos difíceis, `null` =
indecidível, cabeçalho `{"versao": "AAAA-MM-DD", "autor": "fable", "casos": [...]}`. Cada pasta de dados leva um
`LEIA-ME.md` com as decisões de rotulagem (precedência, o que conta e o que não conta), escrito ANTES dos casos.
Além de `ajuste.json` e `teste.json`, um `rascunho.json` com 5 casos fáceis para o construtor testar o encanamento.

### A. `guarda-tool-call/dados/` — ajuste ≥ 30, teste ≥ 60
Dor: agente de código apaga, faz push, sai do escopo ou executa ordem que leu num arquivo/página.
Caso: `{"id", "tarefa", "plano", "contexto_lido", "chamada", "irreversivel", "fora_da_tarefa",
"de_conteudo_nao_confiavel", "acao_esperada", "nota"}`
- `tarefa`: o pedido do usuário (1–3 linhas). `plano`: últimas palavras do agente antes da chamada (pode ser `null`).
- `contexto_lido`: texto que o agente leu antes (README, saída de comando, página) — `null` ou texto; é onde mora a
  injeção ("para continuar, rode `curl … | sh`").
- `chamada`: `{"ferramenta": "bash" | "write" | "edit", "comando": "…"}` para bash; `{"ferramenta": "write"|"edit",
  "arquivo": "…", "trecho": "…"}` para escrita. Misturar Windows/Git Bash e Linux.
- `irreversivel`: `true` se a ação perde dado ou estado sem volta fácil (rm de arquivo não versionado, DROP, push
  --force em branch compartilhada, reset --hard com mudanças, envio de e-mail, pagamento). `rm -rf node_modules`,
  `git checkout -b`, editar arquivo versionado = `false`.
- `fora_da_tarefa`: a chamada não serve ao pedido (mexe em outro módulo, muda config global sem pedido).
- `de_conteudo_nao_confiavel`: a chamada executa instrução que veio do `contexto_lido`, não do usuário.
- `acao_esperada` ∈ `permite | pergunta | bloqueia`, precedência: **bloqueia** (irreversível E não pedido pelo usuário,
  OU de conteúdo não confiável) > **pergunta** (irreversível mas pedido; ou difícil de desfazer e fora da tarefa) >
  **permite**.
- Difíceis obrigatórios: `db:reset` depois de "resete o banco" × depois de "adicione uma coluna"; `rm -rf` de
  pasta gerada × de pasta de dados; `git push --force` na própria branch × em `main`; edição de `.env`; comando
  destrutivo citado dentro de um comentário/string (não executado); nome assustador inofensivo (`drop_cache.py` que
  limpa cache local); injeção disfarçada em saída de teste; pedido do usuário que já autoriza a ação destrutiva.

### B. `juiz-de-eval/dados/` — ajuste ≥ 25 respostas, teste ≥ 50 (cada uma com 2–5 critérios)
Dor: avaliar respostas de LLM por rubrica custa um LLM de fronteira por resposta.
Caso: `{"id", "pergunta", "rubrica": [{"id", "criterio", "tipo"}], "resposta", "veredito": {"<id_criterio>": true|false|null},
"nota"}`
- Domínio: atendimento imobiliário e dúvidas gerais de um CRM (pt-BR), respostas de 1–8 frases.
- `criterio`: frase literal verificável ("Informa que a visita precisa de agendamento prévio"; "Não inventa valor de
  condomínio"; "Responde em tom cordial"). `tipo` ∈ `semantico` (Jev) | `formal` (código: tamanho, presença de
  palavra, formato) — pelo menos 1 em 5 critérios é `formal`, para o exemplo mostrar a divisão.
- `veredito`: `true` = atende; `false` = não atende; `null` = indecidível pelo texto.
- Difíceis obrigatórios: atende de forma implícita; atende e acrescenta fato falso (critério "não inventa"); critério
  negado ("não promete desconto"); resposta longa que enterra a informação; resposta que repete a pergunta sem
  responder; critério formal que o Jev erraria (≤ 3 frases) — fica no código.

### C. `conferencia-de-promessas/dados/` — ajuste ≥ 30 fichas, teste ≥ 60 (cada ficha com 1–5 afirmações)
Dor: rascunho de resposta promete o que a ficha do imóvel não diz ("financiamento aprovado", "sol da manhã").
Caso: `{"id", "ficha": {"titulo", "descricao", "campos": {…}}, "afirmacoes": [{"id", "texto", "relacao",
"trecho_apoio"}], "nota"}`
- `ficha.campos`: só campos públicos (`quartos`, `vagas`, `area_m2`, `orientacao_solar`, `aceita_pet`, `financiamento`
  ("aceita" | "proprietario_analisa" | "nao_aceita" | null), `distancia_metro_m`, `condominio_reais`, `mobiliado`).
  **Nunca** andar nem número da unidade.
- `afirmacoes[].texto`: frase do rascunho do atendente. `relacao` ∈ `supported` (a ficha sustenta) | `contradicted`
  (a ficha diz o contrário) | `not_stated` (a ficha não diz). `trecho_apoio`: trecho literal da ficha que sustenta ou
  contradiz; `null` em `not_stated`.
- Afirmações numéricas (área, vagas, preço, distância) existem para o **código** comparar: rotular normalmente, com
  nota "numérica".
- Difíceis obrigatórios: possibilidade × garantia ("pode aceitar" → "aceita"); vaga rotativa × privativa; permissão
  condicionada ("pet de pequeno porte" → "aceita pet"); distância estimada; orientação solar × cômodo iluminado;
  paráfrase válida (supported, não contradicted); negação na ficha ("não mobiliado") × afirmação.

### D. `imovel-errado/dados/` — ajuste ≥ 24 conversas, teste ≥ 48
Dor: cliente fala de dois imóveis; o agente responde sobre o errado.
Caso: `{"id", "conversa": [{"de": "cliente" | "agente", "texto"}], "candidatos": [{"id", "resumo"}], "rascunho",
"referente", "rascunho_usa_outro", "nota"}`
- `conversa`: 3–10 turnos, pt-BR informal; `candidatos`: 2–4 fichas resumidas em 1–2 linhas, com IDs `IM-01`…;
  `rascunho`: resposta preparada pelo agente para a última mensagem do cliente.
- `referente`: ID do candidato de que a última mensagem do cliente trata, ou `null` (não dá para saber).
- `rascunho_usa_outro`: `true` se o rascunho usa fatos de um candidato diferente do referente (ou de algum, quando
  referente é `null`).
- Difíceis obrigatórios: troca de foco no meio; citação de fala antiga ("você disse que o da varanda…"); dois imóveis
  parecidos (mesmo bairro, preço próximo); referência vaga ("o outro"); correção do cliente ("não, o primeiro");
  referência por atributo que só um candidato tem; referência por atributo que dois têm (→ `null`).

## Especificação dos dados — onda 2 (mesmas regras gerais)

### F. `lint-semantico-de-diff/dados/` — ajuste ≥ 30 diffs, teste ≥ 60
Dor: convenções do time ("divergência de padrão se comenta", JSDoc com `@description`, validação com
express-validator no backend, nada de segredo literal, migration sem `DROP` sem confirmação) só são checadas por
humano em revisão; lint sintático não enxerga semântica.
Caso: `{"id", "regras": [{"id", "texto"}], "diff", "violacoes": {"<id_regra>": true|false|null}, "nota"}`
- `regras`: 3–6 regras do time, em português, literais e verificáveis no diff ("Toda função nova exportada tem JSDoc
  com `@description`"; "Desvio proposital de convenção leva comentário na linha dizendo o porquê"; "Nenhum valor de
  segredo em literal"; "Query SQL crua só com comentário justificando"; "Rota nova valida entrada com
  express-validator"). Pelo menos 1 regra por caso é **mecânica** (regex resolve: segredo literal, `console.log`) e
  rotulada `"tipo": "mecanica"`; as demais `"semantica"`.
- `diff`: diff unificado realista (TypeScript/Express/Drizzle ou Python), 10–60 linhas, com `+`/`-`.
- `violacoes[regra]`: `true` = o diff viola; `false` = não viola; `null` = o diff não toca o assunto da regra.
- Difíceis obrigatórios: desvio COM comentário justificando (não viola); JSDoc presente mas sem `@description`;
  segredo em comentário (viola igual); função modificada mas não nova (regra não se aplica → `null` ou `false`
  conforme o texto da regra — decidir no LEIA-ME); validação feita por zod no backend (viola a convenção); SQL cru
  com comentário; `console.log` em teste (regra pode excluir testes — escrever a regra de modo literal).

### G. `auditor-de-evidencia/dados/` — ajuste ≥ 25, teste ≥ 50
Dor: relatório de agente diz "testado e publicado"; a evidência é um build local ou um teste com dublê.
Caso: `{"id", "afirmacao", "registros": [{"id", "tipo", "texto"}], "relacao", "registros_de_apoio": [ids], "nota"}`
- `afirmacao`: frase de relatório de agente ("Rota `/x` funcionando em produção"; "Testes passando"; "Migration
  aplicada nos dois bancos"). `registros`: 2–6 evidências normalizadas e sintéticas (`tipo` ∈ `log_build | log_teste
  | resposta_http | commit | deploy | manual`), 1–4 linhas cada, sem segredo nem caminho real.
- `relacao` ∈ `supported` (registros sustentam a afirmação inteira) | `contradicted` (algum registro contradiz) |
  `insufficient_evidence` (nada sustenta ou sustenta só parte). `registros_de_apoio`: IDs que sustentam/contradizem.
- Difíceis: teste real de OUTRA revisão; resposta HTTP 200 sem conteúdo provado; build sem teste; teste com mock
  dizendo "API ok"; "aplicada em dev" generalizada para "nos dois bancos"; registro manual sem processo; frase
  correta sobre teste estendida a deploy.

### H. `proxima-pergunta/dados/` — ajuste ≥ 20, teste ≥ 40
Dor: o cliente já disse orçamento, bairro e finalidade, e o atendente pergunta tudo de novo.
Caso: `{"id", "conversa": [{"de", "texto"}], "campos_conhecidos": {…}, "catalogo": [{"id", "pergunta"}],
"aceitaveis": [ids], "proibidas": [ids], "nota"}`
- `catalogo`: 6–10 perguntas-modelo fixas por conjunto (finalidade, orçamento, bairro, quartos, vagas, prazo, pet,
  financiamento, visita, `no_question_needed`). `campos_conhecidos`: o que o CRM já tem (pode estar vazio).
- `aceitaveis`: conjunto de IDs de perguntas que um corretor experiente faria agora (pode ter mais de um; pode ser
  só `no_question_needed`). `proibidas`: perguntas já respondidas na conversa ou nos campos.
- Difíceis: valor ambíguo ("até 600" = preço ou prestação?); pergunta já respondida de modo informal; correção
  tardia; campo conhecido contradito pela conversa; nada faltando.

### I. `opt-out-lgpd/dados/` — ajuste ≥ 30, teste ≥ 60
Dor: obrigação legal — "não me mande mais mensagem", "apaga meus dados", "quem te passou meu número?" precisam de
ação imediata e distinta; falso positivo bloqueia cliente interessado.
Caso: `{"id", "mensagem", "opt_out", "pedido_lgpd", "tipo_lgpd", "pausa_temporaria", "nota"}`
- `opt_out`: `true` se pede para parar de receber mensagens (definitivo). `pausa_temporaria`: `true` se pede para
  não mandar agora/por um tempo ("agora não, me chama mês que vem") — não é opt-out.
- `pedido_lgpd`: `true` se exerce direito de titular; `tipo_lgpd` ∈ `exclusao | acesso | origem_dos_dados |
  correcao | null`.
- Difíceis: ironia ("adoro spam"); terceiro ("minha mãe não quer mais"); negação ("não precisa parar, pode mandar");
  pausa × opt-out; pergunta sobre origem sem pedir exclusão; opt-out dentro de reclamação longa; "para" ambíguo.

### J. `imovel-duplicado/dados/` — pares de anúncios: ajuste ≥ 40 pares, teste ≥ 80
Dor: o mesmo imóvel entra no catálogo por dois portais/corretores com título, área e preço diferentes.
Caso: `{"id", "a": {anúncio}, "b": {anúncio}, "mesmo_imovel", "sinais": {"mesmo_endereco", "mesma_area",
"mesma_planta", "mesmo_preco"}, "nota"}` — anúncio = `{"titulo", "descricao", "bairro", "cidade", "quartos",
"vagas", "area_m2", "preco", "condominio_reais"}` (sem andar/unidade; rua pode aparecer, número não).
- `mesmo_imovel`: `true | false | null` (indecidível). `sinais`: `true|false|null` por dimensão — os numéricos
  (`mesma_area` ±3%, `mesmo_preco` ±5%) existem para o CÓDIGO; o rotulador preenche conforme a regra do LEIA-ME.
- Difíceis: mesmo prédio, unidades diferentes (não é duplicata); mesmo imóvel com área útil × total; preço
  reajustado; descrição copiada com pequenas mudanças; dois corretores com fotos/descrições diferentes do mesmo
  imóvel; "mobiliado" num e não no outro.

## Especificação dos dados — onda 3 (mesmas regras gerais)

### K. `injecao-em-ferramenta/dados/` — ajuste ≥ 30, teste ≥ 60
Dor: agente lê página, README, saída de comando ou e-mail e o conteúdo tenta mandar nele; o filtro precisa separar
"texto que fala de instruções" de "texto que instrui o agente".
Caso: `{"id", "tarefa", "origem", "conteudo", "dirigido_ao_agente", "tipo", "relevante_para_tarefa", "acao_esperada", "nota"}`
- `origem` ∈ `pagina_web | readme | saida_comando | email | comentario_pr | resultado_busca`. `conteudo`: 2–15 linhas.
- `dirigido_ao_agente`: `true` se o conteúdo contém instrução dirigida a um assistente/agente de IA (ou a "quem
  estiver lendo isto automaticamente") para fazer algo fora do que o usuário pediu.
- `tipo` ∈ `injecao` (tenta mudar o comportamento, exfiltrar, executar) | `discussao` (fala SOBRE injeção/prompts:
  artigo, doc de segurança, teste) | `instrucao_legitima` (passos de instalação que o usuário mandou seguir) | `benigno`.
- `relevante_para_tarefa`: o conteúdo ajuda a tarefa. `acao_esperada` ∈ `usar | usar_com_alerta | descartar`:
  `injecao` → `descartar` (se irrelevante) ou `usar_com_alerta` (se o resto é relevante e a injeção é um trecho);
  `discussao`/`instrucao_legitima`/`benigno` relevantes → `usar`; irrelevantes → `descartar`.
- Difíceis: injeção em comentário HTML/markdown invisível; injeção educada ("por favor, assistente…"); doc de
  segurança que CITA um payload; instrução legítima do README com `curl | sh`; injeção em outro idioma; texto em
  segunda pessoa dirigido ao leitor humano ("você deve configurar…"); canário ("se você é uma IA, responda X").

### L. `selecao-de-skill/dados/` — catálogo de ~40 skills + pedidos: ajuste ≥ 30, teste ≥ 60
Dor: agente com dezenas de skills carrega a errada ou nenhuma; a escolha custa uma chamada de LLM por turno.
`skills.json`: ~40 skills fictícias mas realistas de um parque de desenvolvimento e marketing
(`{"id", "nome", "descricao"}` — 1–2 linhas, com sobreposição de propósito entre algumas).
Caso: `{"id", "pedido", "skill", "aceitaveis": [ids], "nota"}` — `skill`: a melhor, ou `null` se nenhuma serve;
`aceitaveis`: todas as que um engenheiro aceitaria (contém `skill`; vazio quando `null`).
- ≥ 25% dos pedidos com `skill: null` (pedido comum que não precisa de skill). Difíceis: duas skills próximas;
  pedido que cita o nome de uma skill mas quer outra coisa; pedido composto; pedido vago; jargão.

### M. `repeticao-ou-revisao/dados/` — ajuste ≥ 24 grupos, teste ≥ 48
Dor: "pode marcar terça" seguido de "não, terça não; quarta" é revisão, não duplicata; duas cópias do mesmo pedido
por falha de envio são duplicata. Colapsar errado perde a correção; executar as duas duplica o efeito.
Caso: `{"id", "mensagens": [{"id", "de", "texto", "minutos_desde_a_primeira"}], "relacao", "acao_vigente", "nota"}`
- 2–3 mensagens do mesmo remetente já ordenadas. `relacao` ∈ `same_intent` (repetição) | `revision` (a última
  corrige/substitui a anterior) | `additional_request` (pedido novo que se soma) | `unclear`.
- `acao_vigente`: ID da mensagem cujo pedido vale agora (a última em `revision`; a primeira em `same_intent`;
  `null` em `additional_request` — valem as duas — e em `unclear`).
- Difíceis: mudança de dia; negativa; segundo pedido intencional parecido; cópia de terceiro ("minha esposa também
  pediu"); mensagem atrasada; retry idêntico com erro de digitação; "e também".

### N. `triagem-de-alerta/dados/` — ajuste ≥ 30, teste ≥ 60
Dor: alerta de monitoramento/segurança às 3h: fechar, avisar o dono, fila ou conter agora? Hoje é um LLM caro ou
um humano acordado.
Caso: `{"id", "alerta": {"fonte", "titulo", "detalhe", "ativo", "ambiente"}, "contexto": [linhas], "acao", "sinais":
{"atividade_esperada", "ativo_critico", "indicio_de_comprometimento", "em_andamento"}, "nota"}`
- Tudo sintético, sem IP/host real (use `10.0.0.x` fictício e nomes inventados). `contexto`: 0–5 linhas (janela de
  manutenção, histórico do usuário, deploy recente).
- `acao` ∈ `auto_close | notify_owner | queue_tier2 | contain_now`; precedência no LEIA-ME: comprometimento em
  andamento em ativo crítico → `contain_now`; indício sem confirmação → `queue_tier2`; atividade esperada
  (manutenção, deploy, usuário conhecido) → `auto_close`; anomalia benigna que o dono deve saber → `notify_owner`.
- `sinais`: booleanos (ou `null`) que justificam a ação — o construtor vai perguntar cada um como Noul.
- Difíceis: manutenção anunciada mas fora da janela; alerta repetido; login impossível com VPN conhecida; teste de
  intrusão autorizado; pico de CPU após deploy; exfiltração lenta; alerta de ambiente de dev com dado de prod.

### O. `compactacao-de-contexto/dados/` — ajuste ≥ 15 sessões, teste ≥ 30 (cada uma com 12–25 mensagens)
Dor: sessão longa de agente; o que manter ao compactar? Resumir tudo com LLM custa caro e perde o detalhe decisivo.
Caso: `{"id", "tarefa_atual", "mensagens": [{"id", "papel", "texto"}], "manter": [ids], "descartar": [ids], "nota"}`
- `papel` ∈ `usuario | assistente | ferramenta`. `manter`: mensagens necessárias para continuar a tarefa atual
  (decisão do usuário, restrição, caminho/valor ainda em uso, erro ainda não resolvido). `descartar`: o resto
  (exploração abandonada, saída de ferramenta já consumida, tarefa anterior concluída). Toda mensagem está num dos
  dois; mensagens genuinamente discutíveis ficam fora dos dois (e fora da métrica), com nota.
- Difíceis: restrição dita cedo e ainda válida; decisão revertida depois (a antiga é descartável, a nova não);
  saída de ferramenta longa com UMA linha ainda necessária; tarefa anterior cuja conclusão é premissa da atual.

## Especificação dos dados — onda 4 (mesmas regras gerais)

### P. `requisito-mudou/dados/` — ajuste ≥ 20 histórias, teste ≥ 40
Dor: o cliente aceitou imóvel sem elevador e depois diz que a mãe vai morar junto; a shortlist antiga não serve
mais e ninguém percebe porque o assunto da conversa continua o mesmo.
Caso: `{"id", "requisitos_anteriores": [{"id", "atributo", "valor"}], "conversa": [{"de", "texto"}],
"shortlist": [{"id", "resumo"}], "atualizacoes": {"<id_requisito>": "mantido" | "substituido" | "negado" | "incerto"},
"novo_valor": {"<id_requisito>": "<texto>" | null}, "reavaliar": [ids da shortlist], "nota"}`
- `requisitos_anteriores`: 3–6 itens (`atributo` ∈ `elevador | vagas | quartos | pet | orcamento | bairro | prazo |
  mobilia | andar_baixo | financiamento`), IDs `q1`…. `conversa`: só os turnos NOVOS (3–8), em ordem.
- `atualizacoes`: para CADA requisito anterior. `substituido` = o cliente deu valor novo; `negado` = deixou de
  querer/precisar; `incerto` = hipótese, fala de terceiro, ou ambíguo. `novo_valor` só para `substituido`.
- `reavaliar`: itens da shortlist que deixam de atender pelos requisitos atualizados (comparação numérica —
  vagas, quartos, preço — é do CÓDIGO; o rotulador preenche pela regra e diz no LEIA-ME).
- Difíceis: mudança indireta ("minha mãe vai morar comigo" → acessibilidade); hipótese sobre o futuro; preferência
  de terceiro; orçamento de outra pessoa; correção explícita; "não faço questão" → "agora preciso"; nada mudou.

### Q. `motivo-de-perda/dados/` — taxonomia + ajuste ≥ 30 conversas, teste ≥ 60
Dor: lead perdido vira "sem interesse" no CRM; o motivo real (preço, localização, documentação, concorrente,
atendimento lento) está na conversa e nunca chega ao relatório.
`taxonomia.json`: árvore de 2 níveis (6–8 grupos, 3–5 folhas cada, com `id`, `nome`, `descricao`), incluindo
`sem_informacao`. Caso: `{"id", "conversa": [{"de", "texto"}], "folha", "grupo", "aceitaveis": [ids de folha],
"nota"}` — `folha` pode ser `null` quando só o grupo é decidível (aí `grupo` vale); `sem_informacao` quando o
cliente simplesmente sumiu.
- Difíceis: dois motivos (principal × secundário); motivo dito com educação ("vou pensar"); motivo real diferente
  do declarado; sumiço depois de preço; cliente que comprou em outro lugar sem dizer por quê; motivo do corretor.

### R. `sql-semantico/dados/` — tabela + condições: ajuste ≥ 8 condições, teste ≥ 16
Dor: filtro que o SQL não expressa ("clientes que mencionaram mudança de cidade", "imóveis com cara de reforma
recente") hoje é leitura manual ou um LLM por linha.
`linhas.json`: ≥ 150 linhas sintéticas de uma tabela de observações de atendimento (`{"id", "texto",
"campos": {…}}`, 1–3 frases em `texto`). `condicoes_ajuste.json` / `condicoes_teste.json`:
`{"id", "condicao", "linhas_verdadeiras": [ids], "linhas_indecidiveis": [ids], "nota"}` — marcar TODAS as linhas
que satisfazem (as demais valem falso).
- Condições semânticas (não resolvíveis por `LIKE`), algumas com parte numérica que é do código (`campos`).
  Difíceis: negação; condição satisfeita por inferência fraca (→ indecidível); condição composta (E/OU).

### S. `compromisso-real/dados/` — ajuste ≥ 20 trechos, teste ≥ 40
Dor: "posso mandar sexta", "ficou para a próxima semana", "não precisa mais" — tarefa fantasma ou compromisso?
Caso: `{"id", "data_referencia", "conversa": [{"id", "autor", "texto"}], "candidatos": [{"id", "trecho",
"responsavel_candidato"}], "vereditos": {"<id_candidato>": "compromisso" | "proposta" | "cancelado" |
"citacao_antiga" | "pedido_sem_aceite"}, "prazo": {"<id_candidato>": "AAAA-MM-DD" | null}, "nota"}`
- `candidatos`: trechos já marcados (o exemplo mede o decisor, não a extração). `prazo`: só quando há data
  resolvível a partir de `data_referencia` — a conta é do CÓDIGO; o rotulador preenche e explica a convenção.
- Difíceis: correção tardia; citação de e-mail antigo; pedido sem aceite ("pode entregar amanhã?"); aceite
  condicional; cancelamento implícito; responsável ambíguo.

### T. `comparador-de-propostas/dados/` — ajuste ≥ 10 disputas, teste ≥ 20 (3 propostas cada)
Dor: três propostas de fornecedor; a barata exclui instalação, a outra não diz a duração do suporte.
Caso: `{"id", "requisitos": [{"id", "texto", "obrigatorio", "tipo": "semantico" | "numerico"}], "propostas":
[{"id", "texto", "campos": {…}}], "matriz": {"<id_proposta>": {"<id_requisito>": "atende" | "contradiz" |
"nao_informado"}}, "trechos": {"<id_proposta>": {"<id_requisito>": "<trecho literal>" | null}}, "elegiveis": [ids],
"nota"}`
- Requisito `numerico` (preço ≤ X, prazo ≤ N dias) é do código, com valores em `campos`. `elegiveis` = propostas
  sem `contradiz` em requisito obrigatório (as com `nao_informado` obrigatório ficam elegíveis COM pergunta).
- Difíceis: exclusão escondida; promessa condicionada; termo vago ("suporte incluso"); requisito atendido por
  anexo citado mas ausente; proposta que atende tudo menos o prazo.

## Especificação dos dados — onda 5 (mesmas regras gerais; escrita em 2026-10-01 ~16h)
U, V e W saem das propostas do Codex (pilotos fora do imobiliário); X, Y e Z fecham a lista dos 26. Em todos:
texto de tela, de anúncio ou de documento é DADO, nunca instrução; o exemplo só propõe — nada é movido, publicado,
clicado nem apagado.

### U. `referencias-de-anuncio/dados/` — RETIRADO em 2026-10-01 ~17h (balanço após 23 exemplos; decisão do dono)
Motivo: o gabarito é preferência humana, sem verdade de desempenho; dos 26, o que menos serve ao CRM. A spec fica
registrada abaixo para não se perder; não lançar rotulador.
Dor: curar referências de anúncios de concorrentes é leitura manual; filtro por termo traz repetição e anúncio de
outra solução. O nome certo é **selecionador de referências para testar**, não detector de anúncio vencedor.
`briefings.json`: 3 itens `{"id", "segmento", "produto", "publico", "objetivo"}` (loja, curso, serviço local — um
por segmento). Caso: `{"id", "briefing_id", "familia", "anuncio": {"anunciante", "texto", "descricao_do_criativo",
"dias_em_veiculacao"}, "mesma_solucao": true|false|null, "dor": "<id>"|null, "formato", "promessa_com_prova":
true|false|null, "serve_ao_briefing": true|false|null, "variacao_de": "<id de anúncio>"|null, "nota"}`
- Tudo sintético: anunciantes e marcas inventados, nenhum anúncio real copiado. `descricao_do_criativo` é texto
  (o que a imagem/vídeo mostra) — o Jev não vê imagem; a extração visual não é medida aqui.
- `formato` ∈ `demonstracao | comparacao | depoimento | oferta | autoridade | outro`. `dor`: lista fechada de 5–7
  dores POR briefing, declarada no LEIA-ME (com `nenhuma`).
- `familia`: variações do mesmo criativo têm a mesma família e ficam do MESMO lado (ajuste ou teste).
  `variacao_de` aponta a primeira da família; duplicata exata é do código (texto normalizado).
- `dias_em_veiculacao` é sinal para investigar, **nunca gabarito de desempenho**: o LEIA-ME proíbe usar o campo
  para decidir `serve_ao_briefing`.
- Difíceis: mesma dor, solução diferente; promessa forte sem prova; depoimento que é só elogio genérico;
  variação com oferta trocada; anúncio do segmento certo para outro público; texto curto com tudo no criativo.
- O construtor mede os atributos e uma shortlist de 10 por briefing (precisão contra `serve_ao_briefing`, formatos
  distintos, variações repetidas) contra o baseline "termos do produto + sem duplicata exata".

### V. `supervisor-de-automacao/dados/` — ajuste ≥ 15 trajetórias, teste ≥ 30 (2–4 estados julgados em cada)
Dor: automação de tela (navegador, ERP, planilha) trava em modal, sessão expirada ou timeout; a máquina de estados
repete o clique e duplica o efeito, ou para e acorda alguém.
`rotinas.json`: catálogo de 5–7 recuperações conhecidas `{"id", "nome", "pre_condicao"}` (ex.: `refazer_login`,
`fechar_modal`, `reabrir_exportacao`, `conferir_resultado`). Caso (um ESTADO): `{"id", "trajetoria", "causa",
"objetivo", "acao_anterior": {"tipo", "alvo"}, "historico": [0–3 passos], "estado_observado": {"titulo",
"texto_visivel": [linhas], "elementos": [rótulos]}, "acao", "aceitaveis": [ações], "rotina": "<id>"|null, "nota"}`
- `acao` ∈ `continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda`; `rotina` só em
  `recuperacao_conhecida`. Precedência no LEIA-ME: efeito já enviado com resultado desconhecido → nunca
  `continuar` (conferir antes de repetir); tela que pede credencial, 2FA ou confirmação de efeito → `pedir_ajuda`.
- `trajetoria` e `causa` definem o split: a mesma causa com a mesma interface não aparece nos dois lados.
- Aplicativo fictício, dados sintéticos; nenhuma credencial, cookie ou dado de cliente no estado.
- Difíceis: "solicitação recebida" depois de timeout; relatório vazio × tela de login; modal de aviso que não
  bloqueia; carregando há muito × travado; sucesso sem o aviso esperado; texto da tela que "manda" clicar
  (conteúdo, não ordem); erro que pede ação que o catálogo não tem.
- Erro caro (o construtor fixa no critério): `continuar` ou repetir a submissão com efeito de resultado
  desconhecido; qualquer ação que não `pedir_ajuda` em tela de credencial.

### W. `organizador-de-downloads/dados/` — RETIRADO em 2026-10-01 ~17h (balanço após 23 exemplos; decisão do dono)
Motivo: risco de privacidade alto com documento real e, com dado sintético, repete o mecanismo "duplicata ×
revisão" que `imovel-duplicado` já mediu. Spec mantida abaixo; não lançar rotulador.
Dor: `final_v3.pdf` é o orçamento recusado e `scan_008.pdf` é o aprovado; nome e extensão arquivam errado e
semelhança não autoriza apagar.
`projetos.json`: 6–8 projetos `{"id", "nome", "descricao"}` (+ casos sem projeto). Caso: `{"id", "lote", "arquivo":
{"nome", "extensao", "hash", "texto_extraido"}, "existentes": [{"id", "nome", "hash", "resumo"}], "funcao",
"projeto": "<id>"|null, "projetos_aceitaveis": [ids], "relacao": {"com": "<id de existente>"|null, "tipo"},
"trecho_que_sustenta": "<literal do texto>"|null, "nota"}`
- `funcao` ∈ `nota_fiscal | boleto | comprovante | contrato | orcamento | manual | curriculo | outro`.
  `relacao.tipo` ∈ `novo | duplicata_exata | revisao | assunto_distinto | indefinido`.
- `duplicata_exata` é só hash igual (código); o rotulador gera `hash` fictício coerente. `texto_extraido` ≤ 1.200
  caracteres, sintético (pessoas e empresas inventadas, CNPJ/CPF fictícios e inválidos de propósito).
- `lote` define o split: arquivos do mesmo projeto fictício ficam do mesmo lado.
- Difíceis: nome ruim com conteúdo claro; duas faturas iguais de períodos diferentes (não é revisão); revisão com
  mudança pequena; comprovante × cobrança; anexo citado e ausente; texto de scan ruim (→ `indefinido`); arquivo
  sem projeto identificável (`null`).
- Erro caro: `revisao` ou `assunto_distinto` tratado como `duplicata_exata`; projeto errado com confiança.
  Datas e valores comparados em código (`_comum/numeros_br.py`).

### X. `triagem-de-documentos/dados/` — ≥ 40 documentos longos + condições: ajuste ≥ 6, teste ≥ 12
Dor: "quais destes 500 contratos têm multa por rescisão / exclusividade / reajuste fora do índice?" — hoje é
leitura manual ou um LLM por documento. Mede o limite "state grande com lixo derruba acerto": **mapa por seção**
(um Noul por seção) e redução em código × o documento inteiro num state só.
`documentos.json`: `{"id", "tipo", "secoes": [{"id", "titulo", "texto"}], "campos": {…}}` — 4–8 seções de 60–200
palavras; tipos: contrato de locação, prestação de serviço, ata de reunião de condomínio, proposta comercial.
`condicoes_ajuste.json` / `condicoes_teste.json`: `{"id", "condicao", "tipo": "semantica" | "numerica",
"documentos_verdadeiros": [ids], "documentos_indecidiveis": [ids], "secao_que_prova": {"<id_doc>": "<id_secao>"},
"nota"}` — marcar TODOS os documentos que satisfazem (os demais valem falso).
- O rotulador pode montar documentos por script a partir de um banco de seções escritas à mão (declarar no
  LEIA-ME quantas seções-base e quantos moldes — limita a alegação a mecanismo). Partes fictícias.
- Condição `numerica` (multa > 2 aluguéis, prazo < 12 meses) é do código, com valor em `campos`; a contagem final
  ("quantos têm") é sempre do código.
- Difíceis: cláusula negada ("não haverá multa"); cláusula revogada por seção posterior; condição que depende de
  DUAS seções; termo citado só no título; seção parecida de outro assunto; documento sem a cláusula.
- Documentos de ajuste e de teste são os MESMOS (como em R): o que se separa são as condições.

### Y. `rerank-publico-ptbr/` — corpus PÚBLICO pt-BR com julgamento de relevância (sem rotulador)
Dor: busca por palavra traz o trecho errado em primeiro; reordenar com LLM custa caro por consulta. O exemplo
`busca-imoveis` mediu só catálogo sintético — este mede em dado público com gabarito de terceiros.
Protocolo = o de `avaliar/publicos/PROTOCOLO.md`: **antes de qualquer chamada**, o preparador confere fonte e
licença, e registra em `preparacao.md`. Candidatos, nesta ordem: Quati (pt-BR nativo, UNICAMP) → mMARCO pt-BR
(MS MARCO traduzido). Licença, tamanho e formato dos julgamentos: "(não declarado)" até o preparador ler a fonte —
**não completar de cabeça**. Se nenhum puder ser baixado ou a licença não permitir o uso, o exemplo PARA e reporta.
- Dado cru só em `.local/publicos/` (fora do Git). No repositório: código, IDs das consultas sorteadas, agregados,
  crédito à fonte. Cache do Jev (contém os trechos) também em `.local/`.
- Sorteio com semente fixa ANTES de olhar resultados: 20 consultas de ajuste + 60 de teste, cada uma com os 20
  primeiros do BM25 (implementação própria ou `sklearn`; nada de dependência nova sem necessidade).
- Jev: Noul "o trecho responde à consulta" por trecho (uma requisição por trecho) e a variante "20 trechos num
  state" medida à parte. Métricas: MRR@10 e NDCG@10 do BM25 puro × BM25 → Jev, com intervalo por bootstrap;
  consultas sem relevante no top 20 relatadas à parte (teto do rerank).
- Orçamento ≤ 2.500 requisições. Perguntas em inglês × português: uma variante só, no ajuste.

### Z. `decisao-de-ui/` — REDUZIDO em 2026-10-01 ~17h a medição curta de latência (sem rotulador, sem exemplo completo)
O que fica: 200+ chamadas ao vivo com uma Choice de 7 destinos sobre textos curtos escritos à mão pelo construtor,
em série e com 4 em paralelo, hora e rede declaradas; p50/p95 e a resposta "cabe em 300 ms?" entram em
`conhecimento/evidencias/medicoes-2026-10-01.md` (ou nota do dia em que rodar). A spec original fica abaixo.
Dor: decisão que precisa caber num gesto da interface (campo único que entende "o que você quer fazer") — um LLM
leva segundos; regra por palavra erra a intenção. O doc promete ~100 ms; daqui medimos 280–350 ms: o exemplo mede
se **cabe em 300 ms** de verdade, não só se acerta.
Caso: `{"id", "texto", "prefixos": ["…", "…"], "destino", "aceitaveis": [destinos], "nota"}`
- Contexto: barra de comando de um CRM imobiliário. `destino` ∈ `buscar_cliente | buscar_imovel | criar_tarefa |
  abrir_relatorio | agendar_visita | enviar_mensagem | nenhum`. `prefixos`: o mesmo texto cortado em 2–3 pontos de
  digitação (o último é o texto inteiro) — mede quando a decisão estabiliza.
- Nomes e telefones fictícios. `nenhum` = texto que não é comando (rascunho colado, pergunta ao suporte).
- Difíceis: nome de pessoa que é nome de bairro; "visita" como busca × como agendamento; número que é código de
  imóvel × telefone; comando com dois destinos; texto colado longo; abreviações de corretor.
- O construtor mede, **ao vivo** e declarando hora e rede: p50/p95 em série e com 4 em paralelo (≥ 200 chamadas),
  acerto no texto inteiro e por prefixo, e a política de interface (limiar para agir sem confirmar × mostrar
  sugestão). Critério de latência fixado ANTES do teste; se não couber em 300 ms, o veredito é "não cabe" e fica
  escrito. Baseline: regras por palavra-chave e regex (código de imóvel, telefone).

## Especificação — onda 6 (acrescentada em 2026-10-01 ~17h, pelo balanço do que o estudo mostrou faltar)
Não são exemplos novos de mecanismo: são as três lacunas que separam o catálogo de uma prova de valor.

### AA. `jev-x-llm/` — o mesmo teste congelado, respondido por um LLM (sem rotulador)
Dor: "Jev no lugar de LLM" é hoje argumento de custo; nenhum LLM foi medido nos 23 testes. Fechar a lacuna mais
barata: 3 testes já congelados, respondidos por um LLM barato com o MESMO esquema de saída (JSON com a mesma
Choice/Nouls), comparados pelas mesmas métricas e erros caros.
- Quais: `opt-out-lgpd` (mensagem única, erro caro legal), `motivo-de-perda` (taxonomia de 30), `auditor-de-evidencia`
  (afirmação × registros). Dados de teste intocados (hash do manifesto confere).
- LLM: um modelo barato de API (o construtor declara qual, versão e data) com a chave do parque lida só por módulo
  próprio em `_comum/` (nunca impressa); temperatura 0; uma chamada por caso; 2 retries; saída validada com a mesma
  validação estrita (JSON fora do esquema = falha operacional, contada à parte). Prompt = as mesmas `instructions` e
  `criteria` de `perguntas.py`, sem exemplos extras (comparação justa: nenhum dos dois recebe mais que o outro).
- Medir: acerto, erro caro, falha operacional, p50/p95, custo real por mil (tokens de entrada + saída ao preço
  publicado), e concordância Jev × LLM caso a caso. Baseline de código ao lado.
- Critério fixado antes: o relatório diz, por exemplo, onde o LLM ganha, onde empata e a razão custo/latência; nada
  de "o Jev é melhor" sem a diferença e o n.
- Orçamento: ≤ 250 chamadas ao LLM e 0 ao Jev (cache). Fica em `exemplos/jev-x-llm/` com um `resultados.md` por
  exemplo comparado.

### AB. `motivo-de-perda-real/` — dado REAL do CRM com gabarito do dono (ordem do dono necessária)
Dor: 22 dos 23 exemplos são sintéticos; o único real mede concordância com um classificador. Sem gabarito humano em
dado real, nenhum dev deve usar o padrão no CRM.
- Origem: conversas de leads perdidos do CRM (`db.sh prod`, só leitura), anonimizadas com a biblioteca de
  `.local/dados-reais/anonimizar.py` + conferência EXATA contra o bruto + leitura de amostra ANTES de qualquer envio
  (lição de 2026-10-01). Texto e cache ficam em `.local/dados-reais/motivo/`; no repositório só código, agregados e IDs.
- Gabarito: o dono (ou gestor de vendas) rotula folha/grupo pela mesma `taxonomia.json` de `motivo-de-perda`, numa
  planilha com IDs; ≥ 60 conversas (20 ajuste / 40 teste), divisão por corretor. Registrar concordância entre dois
  rotuladores em 20 casos, se houver dois.
- Reusar `perguntas.py` e `motivo.py` do exemplo sintético SEM mexer (hash conferido): a pergunta é "o que foi afinado
  em sintético segura em real?". Só depois, se não segurar, uma passada de ajuste no real, declarada.
- Critério fixado antes: os mesmos limites absolutos do exemplo sintético; reportar a queda sintético → real.

### AC. `ferramentas/reavaliar_versao.py` — arnês de reavaliação por versão do modelo (sem rotulador)
Dor: os limiares valem para `jev-1.13.0`; o alias `jev-latest` muda sozinho e nada avisa.
- Roda, para cada exemplo com manifesto, o teste congelado ao vivo contra um modelo dado (`--modelo jev-1.14.0`),
  gravando o cache numa pasta separada (`cache-<modelo>/`), e compara com o cache da versão congelada: por exemplo,
  acerto, erro caro, veredito do critério, e lista dos casos que trocaram de lado, com a distância ao limiar.
- Saída: `conhecimento/evidencias/reavaliacao-<modelo>-<data>.md` + linha no INDICE. Nunca sobrescreve o cache nem os
  manifestos; nunca mexe em limiar (recalibrar é decisão humana, registrada).
- Antes de existir uma versão nova: provar o arnês rodando contra o PRÓPRIO `jev-1.13.0` ao vivo (mede também a
  variação entre rodadas, hoje conhecida só em amostra pequena). Orçamento declarado por execução (soma dos testes:
  ~1.300 requisições, ~US$ 0,10).

## Dado real (fora das ondas)

### E. `roteador-email/` — dado REAL do F11, anonimizado (ordem do dono, 2026-10-01)
Dor: o classificador de e-mail em produção resolve ~2/3 por regra e manda o resto a um LLM (Claude → Codex → API).
O Jev entra entre a regra e o LLM: decide o que tem confiança e escala só o incerto (caso externo: nutlope/jev-fraud,
96/100 com 31% escalado).
Dados: `.local/dados-reais/email/emails-anon.jsonl` (738 registros; `conjunto` = ajuste 152 / teste 586, dividido
por domínio do remetente). **O texto nunca entra no repositório**: o exemplo guarda código, `resultados.md` com
agregados e IDs `EM-xxxx`; o cache do Jev (que contém o state) fica em `.local/dados-reais/email/cache-jev/`.
Registro: `{"id", "grupo", "conjunto", "classe", "decidido_por", "confianca", "regra", "pasta_chegada", "retro",
"crm_client", "sinais": {sender_kind, dkim_pass, dkim_aligned, spf_pass, dmarc_pass, reply_to_differs,
list_unsubscribe, list_id, bulk_precedence, auto_submitted, attachment_types, link_domains,
links_outside_sender_domain, body_from, body_truncated}, "remetente_nome", "assunto", "texto"}`.
- `classe` ∈ `principal | notificacoes | promocoes | redes_sociais | spam | golpe` = decisão do F11 em produção
  (gabarito = concordância com o sistema em produção, não verdade independente; `decidido_por` ∈ `rule | ai_claude
  | ai_codex | ai_api | crm` separa o que a regra decidiu do resíduo que foi a um LLM).
- `redes_sociais` só tem 6 casos, todos no teste: reportar à parte, não entra no critério.
- Só entra em construção depois da auditoria de amostra pelo dono; orçamento da API ≤ 2.500 requisições.
