# Briefing — projetos realistas que validam o aprendizado sobre o Jev (2026-09-30)

## O que entrega
Cinco projetos pequenos e realistas em `exemplos/`, cada um resolvendo um problema de verdade com o
Jev e **medido na API real** contra um conjunto rotulado. Servem a dois fins: (1) provar ou derrubar o
que a memória afirma; (2) ficar no repositório como o exemplo de referência que outro Claude/Codex
copia ao projetar. Português do Brasil no domínio (mensagens, anúncios); perguntas ao Jev em inglês,
salvo onde o projeto mede justamente o português.

| # | Pasta | Problema | O que valida |
|---|---|---|---|
| 1 | `triagem-atendimento/` (Python) | tickets de loja online em pt-BR → setor, reembolso, quer humano, ameaça cancelar, frustração, prioridade | fan-out especulativo, Choice/Noul/Score, roteamento por confiança, pontuação composta, **pt × en** |
| 2 | `guardrail-chatbot/` (Python) | toda mensagem que entra e sai de um chatbot de atendimento → passa / revisa / bloqueia | Nouls de perigo + Score de severidade, política por limiares, conteúdo adversarial (limite #6) |
| 3 | `extracao-sem-inventar/` (Python) | de mensagens pt-BR: e-mail, telefone, CPF, valor em R$, data de visita | regex acha candidatos → Choice com `none` escolhe → código normaliza; datas por partes; nada inventado |
| 4 | `busca-imoveis/` (TypeScript, SDK JS) | busca em linguagem natural sobre ~150 anúncios sintéticos ("2 quartos até 600 mil, aceita pet, perto do metrô") | números em código (faixas via Choice), critérios subjetivos via Score por anúncio em lotes, ranking; SDK JS |
| 5 | `roteador-jev-llm/` (Python) | cada pedido de cliente vai para: código (FAQ/status), LLM barato, LLM de raciocínio ou humano | **decisão Jev × LLM × código**; economia estimada contra "tudo no LLM" |

## Critério de aceite (ordenado)
1. **Roda sem chave**: as respostas reais ficam gravadas em `cache/` do projeto (chave = hash de
   modelo + state + perguntas). `python run.py` (ou `npm start`) reproduz os números sem chamar a API.
   Com `JEV_MODO=ao_vivo` refaz as chamadas.
2. **Medido de verdade**: `resultados.md` com acerto por pergunta, cobertura automática × erro por
   limiar, latência (p50/p95), tokens e custo (US$ 0,042/M entrada), versão do modelo que respondeu,
   data, tamanho da amostra. Separar conjunto de AJUSTE (onde se afinam perguntas e limiares) do de
   TESTE (só no fim, uma vez). Reportar os dois.
3. **Desenho explícito**: `README.md` curto — problema, por que cada parte é código/Jev/LLM, o desenho
   (state, perguntas, composição), o que deu certo, o que falhou, a lição.
4. **Perguntas e limiares num arquivo só** (`perguntas.py` / `perguntas.ts`), revisável por humano.
5. Código pequeno e legível; comentário do "porquê" onde divergir do óbvio.

## Aceito por desenho
- Dados sintéticos (escritos por LLM) — são mais fáceis que reais; o README diz isso.
- A parte LLM do projeto 5 é SIMULADA (sem chave de LLM): mede-se a decisão de roteamento e a
  economia estimada com preços públicos declarados como parâmetro, não chamadas reais a LLM.
- Um único modelo (`jev-1.13.0`, versão fixada).

## Onde dói (o que pode sair errado)
- Afinar pergunta olhando o gabarito do teste → número inflado. Afinar só no conjunto de ajuste.
- Pergunta em português × inglês: ninguém sabe o efeito ainda — é para medir, não para supor.
- Números e datas pedidos ao Jev (limites #2 e #3) — o desenho deve contornar e o resultado mostrar.
- Custo escondido: uma requisição por item (anúncio, candidato) multiplica chamadas.
- Chave: nunca impressa, nunca gravada no cache nem em log.

## Quem consome
Agentes que lerem o repositório: a nota `conhecimento/decidir/` e as
skills vão apontar para estes projetos como exemplo canônico de cada padrão.

## O que medir antes de decidir
Acerto por pergunta e por idioma; curva cobertura × erro; latência e custo por item.

## Como provar
`resultados.md` gerado pelo próprio script (não escrito à mão) + cache com as respostas reais.

## Infra comum
`exemplos/_comum/` (Python): cliente com cache e medição (`jevcache.py`) e métricas (`metricas.py`).
Ambiente: `.venv` na raiz (SDK `typesafe-sdk` 0.7.2). Chave: variável `TYPESAFE_API_KEY`; se ausente,
o helper lê `api_key.txt` da raiz sem imprimir. TypeScript: `@typesafe-ai/sdk` com `npm install` na
pasta do projeto (`node_modules/` fora do Git).

## Dados rotulados
Escritos pelo CODEX, sem ver o código, em `exemplos/<projeto>/dados/` (`ajuste.json` e `teste.json`).
Quem constrói NÃO abre `teste.json` antes da rodada final.

## O que NÃO fazer
- Não chamar a API em laço sem cache (rodar de novo não pode gastar de novo).
- Não publicar número sem a amostra e a versão do modelo.
- Não usar o Jev para o que o código faz exato (contagem, soma, comparação de datas e números).
- Não escrever fora da pasta do próprio projeto (exceto `_comum/`, que é do coordenador).
- Varredura da família do defeito: achou um erro de desenho num projeto, conferir se os outros têm.
