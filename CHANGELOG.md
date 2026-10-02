# Histórico

## 2026-10-02 (madrugada, goal 23:00) — casos novos: mais 7 pastas, 30 no total; a lista dos 26 zerou (2 retirados)
- `supervisor-de-automacao` (erro caro 0/14 e 0/7; critério **reprovado** em acerto × regras),
  `triagem-de-documentos` (mapa por seção × documento inteiro: F1 1,000 nos dois; rodada 3 com condições
  compostas "A E B" medidas na API), `sql-semantico`, `comparador-de-propostas` (dado v2 após a revisão: 12 células numéricas rotuladas como
  semânticas), `rerank-publico-ptbr` (**dado público** Quati, CC BY 4.0; texto do corpus fora do Git), `jev-x-llm`
  (**Jev × Haiku 4.5** nos 3 testes congelados), `latencia-interface` (420 chamadas ao vivo: p95 em série 303 ms,
  **não cabe em 300**). Mesmo rito, Codex em cada um (menos a latência, reduzida).
- `ferramentas/reavaliar_versao.py`: arnês que roda os testes congelados ao vivo contra uma versão do modelo e
  compara com o cache congelado; provado contra o próprio `jev-1.13.0` (105 de 13.652 perguntas trocaram de lado;
  veredito de `compactacao-de-contexto` virou). Nota em `conhecimento/evidencias/reavaliacao-jev-1.13.0-2026-10-01.md`.
- Infra comum: `jevcache.py` lê `JEV_MODELO`/`JEV_PASTA_CACHE` (modelo por ambiente exige pasta distinta);
  `llmcache.py` novo (cliente de LLM por `urllib`, cache, orçamento persistido, quarentena).

## 2026-10-01 (tarde) — casos novos: mais 6 fechados, 18 no total

- `triagem-de-alerta`, `requisito-mudou`, `motivo-de-perda`, `compactacao-de-contexto` (critério **reprovado**
  para descarte automático), `compromisso-real` e `roteador-email` (**dado real** do classificador de e-mail em
  produção, anonimizado; texto e cache fora do Git; critério **não passou** por um caso). Mesmo rito.
- Infra comum por achados do Codex: trava do cache por pasta e compartilhada entre instâncias; registro de cache
  com medição fora do contrato vai para quarentena; `congelamento.choice` rejeita Choice cuja opção escolhida não
  é a de maior probabilidade. Síntese em `conhecimento/evidencias/medicoes-2026-10-01.md`.
- Briefing ganhou a onda 5 (6 especificações); faltam rotulador e construtor para esses e para `sql-semantico` e
  `comparador-de-propostas`.

## 2026-10-01 — casos novos: 12 exemplos fechados (ondas 1 a 3)

- Fechados depois da entrada abaixo: `lint-semantico-de-diff`, `auditor-de-evidencia`, `opt-out-lgpd`,
  `proxima-pergunta`, `imovel-duplicado`, `injecao-em-ferramenta`, `selecao-de-skill`, `repeticao-ou-revisao` —
  mesmo rito (rotulador ≠ construtor, rodada 1 cega com manifesto, revisão adversarial do Codex, rodada pós-revisão
  declarada não cega). Critério fixado antes do teste **não passou** em `lint-semantico-de-diff` e
  `selecao-de-skill`, e está dito nos READMEs. Números no índice [exemplos/README.md](exemplos/README.md).
- Infra comum: `_comum/numeros_br.py` (leitor único de número em formato brasileiro, nascido de três exemplos que
  erraram ponto de milhar e "milhão"); `jevcache.py` com gravação atômica, `cache/invalidos/` e `Jev.invalidar()`;
  `congelamento.choice()` confere `type` e a soma da distribuição.
- `repeticao-ou-revisao`: `acao_vigente` sobre o grupo sem reentregas por ID; toda saída leva
  `ids_de_contexto_obrigatorio` e `descartar_anterior: false` (achados do Codex).
- Nota nova `conhecimento/evidencias/medicoes-2026-10-01.md` (síntese dos 12, com limites); lições de método em
  `conhecimento/avaliar/metodo.md` e de desenho em `conhecimento/licoes-transversais.md` (itens 26–37).
- Briefing dos casos novos ganhou a onda 5 (especificação de dados dos 6 exemplos restantes: referências de
  anúncio, supervisor de automação, organizador de downloads, triagem de documentos, rerank em corpus público,
  decisão de interface em 300 ms).

## 2026-10-01 — casos novos: catálogo externo e onda 1 de exemplos (em curso)

- Nota nova `conhecimento/evidencias/casos-externos.md`: 30 casos reais relatados fora daqui (guarda de agente de
  código, juiz de eval, lint de PR, SQL semântico, navegador, SOC, roteador de e-mail…), com número, fonte e o que
  cada relato não prova; onde o LLM ganha. 26 exemplos novos mapeados; briefing da task em
  `exemplos/BRIEFING-2026-10-01-casos-novos.md`.
- Exemplos novos medidos na API real (`jev-1.13.0`): `guarda-tool-call`, `juiz-de-eval`, `imovel-errado`,
  `conferencia-de-promessas` — dados rotulados por Fable (rotulador ≠ construtor; construtor não abre o teste),
  rodada 1 cega, revisão adversarial do Codex em cada um (7+7+6+6 achados, todos aceitos e aplicados), rodada 2
  pós-revisão declarada não cega. Em construção: `lint-semantico-de-diff`, `auditor-de-evidencia`.
- Infra comum: `_comum/congelamento.py` (manifesto auditável com hashes de código, dados e critério; validação de
  probabilidade que rejeita bool/string) e `jevcache.py` guarda a resposta anterior em `cache/historico/` no modo
  `ao_vivo` — ambos nascidos de achados do Codex ("rodada única não era auditável"; `isinstance(True, int)`).
- Pasta de estudo ganhou `.ignore` (chave, `.local/`, `privado/`, `prova/`, `chat.txt`) para a passada do Codex.
- Bloqueio registrado: o held-out de 300 e-mails do F11 foi apagado do disco; `roteador-email` com dado real espera
  extração nova do mail-01 com aval do dono.

## 2026-10-01 — licença MIT única e contribuições

- Todo o acervo próprio sob MIT (sai o CC BY 4.0 dos textos); `CONTRIBUTING.md`: fork + PR, merge e publicação
  só pelos mantenedores; contribuição aceita entra pela pasta de estudo e é republicada.

## 2026-10-01 — versão pública (`ia-automation/How-to-use-JEV`)

- Esta pasta segue como pasta de estudo; a versão pública sai por `copia_fria.py --publicar` (lista permitida;
  inclui `fontes/catalogo` e `fontes/skill-oficial`; nunca `privado/`, `prova/`, `.local/`).
- Dados internos de leads e propostas com casos do CRM movidos para `privado/`; as notas compartilhadas levam
  só a lição qualitativa, sem números. O validador barra link para `privado/`.
- Licenças: código MIT (`LICENSE`), textos CC BY 4.0 (`LICENSE-CONTEUDO.md`); catálogo sem caminhos locais.

## 2026-09-30 — rodada 1 da prova fria

- Codex (contêiner isolado) 120/120; Claude 117/120 com um crítico abaixo do máximo → aceite conjunto não atingido.
- `prova-fria.md`: condições comparáveis definidas antes (ferramentas, modelo, orçamento, saída, ambiente),
  registro da rodada 1 e o contêiner como opção forte. `jev-desenhar`: baseline + critério de continuar/descartar.

## 2026-09-30 — revisão adversarial P11 (Codex) aplicada

- `copia_fria.py` exporta por lista permitida, arquivo a arquivo (inesperado, credencial ou link interrompe);
  manifesto lista cada arquivo. `validar.py` confere âncoras e varre `.env*`; comando portável
  `python -X utf8 ferramentas/validar.py`.
- Nota nova `conhecimento/avaliar/prova-fria.md` (protocolo, decisão de isolamento e limites).
- Núcleo e notas: o Jev não conduz o laço de um agente, mas pode selecionar ação/ferramenta fechada; R4/R5 sem
  "empate" nem "sem rótulos" (perguntas afinadas em 100 rotulados; B2W com diferença não resolvida); leads:
  AUC medido separado da hipótese de priorizar fila; cache com modelo e provedor; 13 Nouls (não 12); preços
  rotulados como premissa informada; duas âncoras corrigidas.

## 2026-09-30 — consolidação numa estrutura única

- `AGENTS.md` passa a ser a fonte única das instruções + o NÚCLEO (o que todo agente precisa saber, com
  rótulos [doc]/[testado]/[terceiro]/[local] e links); `CLAUDE.md` só importa o `AGENTS.md`.
- `memoria/` (Claude) + `memory/`, `sources/` e as referências das skills (Codex) fundidos em `conhecimento/`
  (`modelo/`, `decidir/`, `construir/` + `padroes/`, `receitas/`, `avaliar/`, `evidencias/` + `videos/`), com
  `[[slug]]` convertidos em links relativos e um fato em um lugar. Índice novo: `conhecimento/INDICE.md`.
- Notas novas: `construir/integracao-segura.md`, `receitas/padroes-das-receitas.md`, `avaliar/metodo.md`,
  `avaliar/leitura-critica-das-receitas.md`, `evidencias/contradicoes-da-documentacao.md`, `pendencias.md`,
  `decisoes.md`, `proveniencia.md` (com a tabela de rastreio origem → destino).
- Medições de 2026-09-30 incorporadas: contrato de fronteira (400/422), confiança, escala, estabilidade,
  pt × en; resultados em texto real pt-BR (HateBR, B2W) e em leads reais anonimizados; pendências medidas
  marcadas como fechadas.
- Skills reorganizadas em 4, só procedimento: `jev-desenhar` (funde `jev` + `jev-design`), `jev-integrar`
  (`jev-api`), `jev-avaliar` (`jev-evaluate`), `jev-manter` (`jev-atualizar-memoria`); assets preservados.
- `fontes/catalogo/catalogo.json` junta `sources/catalog.json`, `review-catalog.json` e o manifesto do handoff.
- `ferramentas/validar.py` e `ferramentas/copia_fria.py` novos; `scripts/normalize_youtube_vtt.py` →
  `ferramentas/`. `exemplos/README.md` novo (índice dos 5 projetos). `.gitignore` exclui `fontes/docs/` e `fontes/videos/`.
- Nada apagado: todos os originais (inclusive as versões anteriores dos arquivos reescritos) em
  `.local/antigos/2026-09-30/`, com o caminho relativo de antes.
- Sem commit, remoto ou publicação.

## 2026-09-30 — incorporação do estudo do Claude

- Preservadas `lacunas-fechadas.md`, `absorver-do-codex.md` e captura OpenAPI do
  scratchpad; cópias verificadas por SHA-256. Backup de 60 arquivos antes das edições.
- Acrescentadas referências de cookbooks, SDKs e crítica de benchmarks às skills
  `jev-design`, `jev-api` e `jev-evaluate`.
- Corrigidos instructions opcional, retry Python, legend estruturada, divergências
  de Score/OpenAPI e aproximação de confidence nos dois acervos.
- Ajustadas regras absolutas sobre Choice/none, custo por pergunta e composição;
  manutenção passa a preservar snapshots antigos. Falha de parse da cascata SDE
  confirmada estaticamente e registrada.
- Contagem corrigida: 18 cookbooks + 1 demo, em 19 notas; 112 arquivos de páginas,
  incluindo um retorno Page Not Found. Os números anteriores ficam como histórico.
- Relatório `memory/claude-study-review.md` (hoje em `.local/antigos/2026-09-30/`; conteúdo em
  [proveniência](conhecimento/evidencias/proveniencia.md)) distingue cobertura e pendências.
  Sem nova pesquisa web, inferência, instalação, commit, remoto ou publicação.

## 2026-09-30 — conciliação da colisão entre sessões

- Usuário confirmou que outro agente substituiu o README do Codex e depois parou
  de escrever. O estudo do Codex permanecia em `CODEX-STUDY.md`, `memory/`,
  `sources/` e nas três skills específicas, já escritas e validadas.
- Salvas cópias dos sete arquivos de entrada antes da conciliação em
  `.local/recovery/collision-20260930-175202/`, com hashes no manifesto.
- README passa a apresentar os dois acervos e as cinco skills. `AGENTS.md`,
  `CLAUDE.md`, `CODEX-STUDY.md` e os dois índices foram alinhados à entrada comum.
- Nenhuma nota temática, fonte, skill ou configuração de plugin foi apagada ou
  substituída. A conciliação não é uma nova revisão integral do acervo.
- Sem inferência, benchmark, instalação, commit, remoto ou publicação nesta correção.

## 2026-09-30 — estudo inicial
- Documentação da TypeSafe inteira: snapshot `fontes/docs/llms-full-2026-09-30.txt` (21.111 linhas),
  índice `llms-2026-09-30.txt` e 111 páginas `.md` individuais (`fontes/docs/paginas/`).
- Modelo em vigor: `jev-1.13.0` (aliases `jev-latest` e `jev-preview`). SDK Python 0.7.2, SDK JS 0.6.0.
- Memória: 9 conceitos, 4 padrões, 17 receitas, API HTTP + 2 SDKs, 3 visões externas, lições
  transversais, perguntas abertas.
- Skills: `jev` (desenhar/escrever/revisar) e `jev-atualizar-memoria`.
- Vídeos: vzYKuvD05rE (Max Carrau), VI7r1-BMN8I (QuantBrasil), WLSqQprxai4 (Maestros da IA).
- Achados: link do "migration guide" da skill oficial dá 404; página Primitives e receita divergem no
  ganho do paralelismo (11,5×/9,6× vs 12,2×/10,0×); receitas misturam `jev-1.12` e `jev-1.13.0`.
