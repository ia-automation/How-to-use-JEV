# JEV — conhecimento e skills sobre o Jev (TypeSafe)

Base local sobre o **Jev**, o modelo "System One" da TypeSafe: recebe um conteúdo (`state`) e perguntas tipadas
(Choice, Score, Noul) e devolve decisões com probabilidades — não gera texto. Aqui estão o que ele é, quando
usá-lo em vez de código ou de um LLM, como integrar, como avaliar, e o que **medimos** na API real em
2026-09-30. Estudo, medições e consolidação: 2026-09-30 (`jev-1.13.0`, SDK Python 0.7.2, SDK JS 0.6.0).

## Por onde começar
| Preciso de… | Abra |
|---|---|
| O essencial em uma leitura (e as regras deste repositório) | [AGENTS.md](AGENTS.md) — o NÚCLEO |
| Uma nota específica | [conhecimento/INDICE.md](conhecimento/INDICE.md) |
| Decidir código × Jev × LLM | [conhecimento/decidir/jev-llm-codigo.md](conhecimento/decidir/jev-llm-codigo.md) |
| Exemplos medidos na API real | [exemplos/README.md](exemplos/README.md) |
| O que foi medido e o que ainda não | [medições](conhecimento/evidencias/medicoes-2026-09-30.md) · [pendências](conhecimento/evidencias/pendencias.md) |
| Quem estudou o quê | [proveniência](conhecimento/evidencias/proveniencia.md) |

Abrir a pasta como projeto basta: o Codex lê o `AGENTS.md`; o Claude lê o `CLAUDE.md`, que importa o mesmo arquivo.

## Mapa
| Caminho | Conteúdo |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | instruções + núcleo (fonte única) / ponteiro para ele |
| `conhecimento/` | notas: `modelo/`, `decidir/`, `construir/` (+ `padroes/`), `receitas/` (18 + 1 demo + síntese), `avaliar/`, `evidencias/` (+ `videos/`) |
| `skills/` | 4 skills só de procedimento: `jev-desenhar`, `jev-integrar`, `jev-avaliar`, `jev-manter` |
| `exemplos/` | 5 projetos pequenos com dados rotulados e cache das respostas reais |
| `avaliar/` | pt × en sintético, texto real pt-BR (HateBR, B2W) |
| `prova/` | prova de aceite do pacote (fora da cópia fria) |
| `fontes/` | `catalogo/` (URLs, datas, hashes), `skill-oficial/` (MIT); `docs/` e `videos/` = terceiros, fora do Git |
| `ferramentas/` | `validar.py`, `copia_fria.py`, `normalize_youtube_vtt.py` |
| `.local/` | cache, medições brutas, dados locais e `antigos/` (originais superados) — fora do Git |

## Como usar as skills
Peça pelo caminho, por exemplo: "Use `skills/jev-integrar/SKILL.md` para revisar esta integração". Cada skill
é procedimento e aponta para as notas de `conhecimento/`; carregue só a pertinente. A pasta tem
`.claude-plugin/` (plugin e marketplace locais), mas **a instalação não foi validada** em nenhum cliente: a
presença dos arquivos não prova instalação, descoberta automática nem memória permanente.

## Ferramentas
- `ferramentas/validar.py` — confere links relativos, frontmatter das notas (`name` = arquivo), que toda nota
  está no índice, JSON válido, frontmatter das skills, o par requisição/resposta mock e ausência de
  chave/segredo. Rodar antes de encerrar qualquer mudança:
  `python -X utf8 ferramentas/validar.py` (Python 3.12 testado; só biblioteca padrão, sem `.venv`).
- `ferramentas/copia_fria.py` — exporta para `C:\tmp\jev-frio-<AAAAMMDD-HHMMSS>` por **lista permitida**
  (entradas da raiz + extensões; fora `prova/`, `fontes/`, `chat.txt`, `.local/`, `.git/`, `api_key.txt`,
  `.venv/`); entrada não classificada, nome de credencial ou link interrompe. Confere na cópia que a chave não
  aparece e que o validador passa; o manifesto lista cada arquivo com hash. Serve para testar um agente
  "frio"; protocolo e limites em [prova-fria](conhecimento/avaliar/prova-fria.md).
- `ferramentas/normalize_youtube_vtt.py` — normaliza legendas progressivas do YouTube (biblioteca padrão; não
  baixa vídeo nem corrige a transcrição): `python ferramentas/normalize_youtube_vtt.py .local/entrada.vtt
  .local/transcricao.txt`; `--keep-repeats` conserva cues repetidos em legendas convencionais.

## Direitos e licenças
- `fontes/docs/` (documentação da TypeSafe) e `fontes/videos/` (transcrições de vídeos de terceiros) são
  material integral de terceiros para estudo local: **fora do Git** (`.gitignore`). As notas citam a URL
  oficial junto do caminho local.
- `fontes/skill-oficial/` é a skill oficial da TypeSafe, licença MIT (arquivos `LICENSE` preservados).
- `avaliar/publicos/` usa HateBR (CC BY-NC 4.0) e B2W-Reviews01 (CC BY-NC-SA 4.0); no repositório só
  agregados, IDs e hashes, com crédito às fontes; o texto licenciado fica em `.local/`.
- Dados reais do CRM: só anonimizados, e nem texto nem números entram na versão pública (ficam na pasta de
  estudo privada, junto com as propostas internas e a prova).
- Licença: MIT para todo o acervo próprio — código, notas, dados sintéticos e respostas gravadas da API
  ([LICENSE](LICENSE)). Material de terceiros mantém a licença de origem: `fontes/skill-oficial/` (MIT,
  TypeSafe); resumos e citações curtas da documentação da TypeSafe e dos vídeos pertencem aos autores e vêm com
  fonte; HateBR e B2W não são redistribuídos. Dados sintéticos são fictícios (CPFs gerados com dígito válido
  de propósito; e-mails em domínios de exemplo). Contribuições são bem-vindas por PR; merge e publicação só
  pelos mantenedores ([CONTRIBUTING.md](CONTRIBUTING.md)).
- Chave da TypeSafe: variável `TYPESAFE_API_KEY` ou `api_key.txt` local (ignorado pelo Git); nunca em arquivo versionado.

## Estado
Versão pública em `ia-automation/How-to-use-JEV`, gerada da pasta de estudo (privada) por
`python -X utf8 ferramentas/copia_fria.py --publicar <pasta>`. Mocks e casos sintéticos não são resultados do Jev; os
números medidos trazem data, versão e tamanho da amostra. Histórico em [CHANGELOG.md](CHANGELOG.md).
