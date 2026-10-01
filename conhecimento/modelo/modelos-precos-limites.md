---
name: modelos-precos-limites
description: jev-1.13.0 — US$ 0,042 por milhão de tokens de ENTRADA, saída grátis; 100K tok/s e 40 req/s; contexto 64k (32k state+maior pergunta); aliases jev-latest/jev-preview; sem fine-tuning; inglês é o idioma principal.
tipo: referencia
fonte: https://docs.typesafe.ai/models · /legal
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 12995–13098 e 12824–12838
estudado_em: 2026-09-30
---

# Modelos, preço e limites (estado em 2026-09-30)

## Modelo atual
| Jev 1.13 | `jev-1.13.0` |
|---|---|
| Preço | **US$ 42 por bilhão / US$ 0,042 por milhão de tokens — só entrada; saída grátis** |
| Limites de taxa | 100K tokens/s e 40 requisições/s (acima de qualquer um → `429`) |
| Contexto | 64k tokens por requisição (state + todas as perguntas); 32k para state + a maior pergunta |
| Entrada | só texto: string, objeto JSON ou array de texto |

- Limites de taxa **mudam sem aviso** ("demanda muito grande, contratos de GPU chegando"); planos
  custom/enterprise têm limites maiores (sales@typesafe.ai).
- SDKs retentam com backoff e respeitam `retry-after` por padrão.
- A resposta traz `usage.output_tokens`, mas saída não é cobrada.
- Ordem de grandeza: 1 milhão de requisições de ~1.000 tokens de entrada ≈ US$ 42.
- Custo e latência medidos por nós (tokens por pergunta, 1 → 100 perguntas, paralelismo, p95):
  [medicoes](../evidencias/medicoes-2026-09-30.md#escala-latência-custo) [testado].
- Cookbooks de ago/2026 usam `jev-1.12` com a mesma tarifa histórica (0,042/0); outras rodaram em
  `jev-latest` → `jev-1.13.0`. Números entre versões não são comparáveis.

## Aliases
| Alias | Aponta para | Significado |
|---|---|---|
| `jev-latest` | `jev-1.13.0` | última versão estável oficial; padrão dos SDKs e dos exemplos |
| `jev-preview` | `jev-1.13.0` | última versão, oficial ou não (hoje não há build de preview) |

- Alias **se move** quando sai versão nova → respostas mudam sem você mudar nada. O campo `model` da
  resposta traz o ID versionado que respondeu: **logar sempre**.
- Medido em 2026-09-30: `jev-1.13.0`, `jev-latest` e `jev-preview` responderam todos `jev-1.13.0`;
  modelo inexistente → 400 `Unknown model` [testado, [medicoes](../evidencias/medicoes-2026-09-30.md)].
  Via gateway o ID pode vir em outra grafia (vídeo 3, 43:57: `typesafe/jev-1.13-20260917`) [terceiro].
- Limiar afinado contra uma versão → fixar o ID versionado e migrar no seu ritmo.
- `GET /v1/models` lista os nomes da conta (hoje só os aliases; IDs versionados são aceitos mesmo sem
  aparecer). Campos: `name`, `description`, `release_date`.

## Customização
Não há fine-tuning nem LoRA por cliente — mesmos pesos para todos. Adapta-se pelo pedido:
conteúdo proprietário no `state`; regras e casos de fronteira em `instructions`/`criteria`;
decomposição + composição em código (ou modelo clássico treinado sobre as probabilidades).
Enviar dados no `state` não constitui "treinamento" privado do Jev.

## Idioma
Inglês é o idioma principal de treino e onde a acurácia é melhor. Outros idiomas (inclusive CJK)
são aceitos com acurácia menor — **testar no próprio conteúdo antes** e olhar a confiança ao rotear.
Para nós (português): o que medimos está em [medicoes-2026-09-30](../evidencias/medicoes-2026-09-30.md#idioma) [testado].

## Dados
- O Jev não é treinado com requisições/respostas de clientes (Privacy Policy; DPA; Master Customer Agreement).
- ZDR (retenção zero) para enterprise.

## Onde acessar
- API própria: `POST https://api.typesafe.ai/v1/systemone` com chave do console
  (https://console.typesafe.ai/keys). Playground: https://console.typesafe.ai/playground.
- Acesso passou por lista de espera (vídeo 2: liberado em ~1 dia).
- **Gateways** (declarados na página do SDK Python; o SDK aponta para eles via `base_url`):
  | Gateway | `base_url` | `model` | chave |
  |---|---|---|---|
  | OpenRouter | `https://openrouter.ai/api` | `~typesafe/jev-latest` | `OPENROUTER_API_KEY` |
  | Vercel AI Gateway | `https://ai-gateway.vercel.sh/typesafe` | `typesafe-ai/jev` | `AI_GATEWAY_API_KEY` |
  | Pydantic AI Gateway | `https://gateway-us.pydantic.dev/proxy/typesafe` | `jev-latest` | `PYDANTIC_AI_GATEWAY_API_KEY` |
  Vídeo 2: OpenRouter com o mesmo preço; Vercel grátis por tempo limitado (não confirmado no doc).
  Contrato, preço, limites e integridade de `probabilities`/`confidence` via gateway: não medidos
  ([pendencias](../evidencias/pendencias.md)).
- SDKs: Python ≥ 3.10 (quickstart), Node.js ≥ 20 (página JS); ver [sdk-python](../construir/sdk-python.md)
  e [sdk-javascript](../construir/sdk-javascript.md).
- Skill oficial da TypeSafe: repositório https://github.com/typesafe-ai/skills, instalação anunciada em
  https://docs.typesafe.ai/agent-skill com `npx skills add typesafe-ai/skills --skill typesafe-ai`
  (referência, não executada por nós; evitar instalar várias cópias por métodos diferentes). Cópia
  local MIT em `fontes/skill-oficial/` (fora da cópia fria; ver README).

## Relacionados
[api-http](../construir/api-http.md) · [limites-jev-1-13](limites-jev-1-13.md) · [python](../construir/sdk-python.md) · [javascript](../construir/sdk-javascript.md)
