# Histórico

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
