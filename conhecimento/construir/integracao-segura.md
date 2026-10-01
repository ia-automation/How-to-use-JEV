---
name: integracao-segura
description: Regras de operação de uma integração com o Jev — ausência de resposta é erro (não probabilidade 0), validar IDs/tipos/números antes do efeito, efeitos fora da chamada, orçamento único de retentativa, versionar perguntas com o consumidor, nada de campos de chat, chave só no servidor, logs sem corpo, resposta nunca é autorização.
tipo: principio
fonte: recomendações locais do Codex (http-contract, jev-api, sdk-details, 2026-09-30) + agent skill oficial https://docs.typesafe.ai/agent-skill + SDKs https://docs.typesafe.ai/sdk/python e /sdk/javascript + medições de 2026-09-30
estudado_em: 2026-09-30
---

# Integração segura — regras de operação

Rótulos: [doc] documentação · [testado] medido por nós em 2026-09-30 · [local] recomendação nossa de
engenharia (não é exigência do fornecedor). Contrato do endpoint: [api-http](api-http.md).

## 1. A chamada terminar não basta — validar antes do efeito [local]
- Conferir **todos os IDs esperados** em `answers`, o `type` de cada um, que `choice` está entre as opções
  enviadas, que números são **finitos** e estão em [0,1] (`noul`, `confidence`, cada probabilidade), que
  as distribuições somam 1 com tolerância e que o Score cai entre 0 e `len(criteria)-1`.
- **Ausência de resposta é erro, não probabilidade 0.** Timeout, JSON inválido, resposta incompleta,
  tipo inesperado, cancelamento: o consumidor recebe um estado explícito (`erro`/`pendente`), nunca
  `noul=0`, "não" ou a opção padrão. Num lote, itens que falharam ficam **pendentes**, não negativos.
- O SDK Python omite do resultado tipado uma resposta de tipo desconhecido (loga aviso; o corpo segue em
  `raw_http_response`) [doc] → "o SDK não lançou erro" não prova que todos os IDs voltaram.
- A resposta tipada não prova acerto semântico: tipo certo ≠ decisão certa.

## 2. Efeitos fora da chamada [local]
- A chamada ao Jev só **classifica**; efeitos (enviar, cobrar, apagar, consultar dado alheio) ficam no
  código, depois da validação, com a autorização que o processo exigir. Assim uma retentativa não
  duplica efeito.
- **Resposta do Jev nunca é autorização.** Permissão, cálculo e efeito continuam no código mesmo com
  confiança alta [local, a partir de doc: "o código decide"]. Guardrail com Jev "não é fronteira de
  segurança" [doc: receitas guardrails e RAG]; conteúdo adversarial no state move a resposta [doc:
  [limites-jev-1-13](../modelo/limites-jev-1-13.md) #6].
- Registro por item: ligar a resposta ao ID original do registro; a pergunta aponta o registro no state
  ou na instrução (o ID da pergunta não é contexto).

## 3. Retentativa com orçamento único
- Os SDKs já retentam 408/429/5xx: 2 retries (3 tentativas), backoff 0,5 → 5 s, jitter 0,25 [doc,
  [sdk-python](sdk-python.md), [sdk-javascript](sdk-javascript.md)]. Timeout é **por tentativa** (JS 10 s;
  Python 10 s por operação + orçamento total `RetryPolicy.timeout=30` s).
- Retentativa da aplicação por cima da do SDK **multiplica** as tentativas de transporte [local]. Defina
  um orçamento único (tentativas, tempo total, concorrência) e desligue uma das camadas ou dimensione as
  duas juntas. 400/401/422 não se retentam: corrigem-se.
- Fallback (LLM, humano) e o custo das retentativas entram no orçamento do lote [local].

## 4. Contrato do seu lado [local]
- **Versionar perguntas, critérios e limiares junto do consumidor** (arquivo único, hash registrado).
  Mudar um rótulo muda o contrato do aplicativo, mesmo sem mudar a API.
- Registrar em cada resultado: `model` efetivo (o alias muda sozinho [doc]), versão/hash das perguntas,
  `usage`, latência, tentativas, status (`ok`/`erro`/`pendente`) e origem `live` ou `replay` de cache.
- Cache: chave = hash de (state + perguntas/critérios + modelo + provedor); guardar tokens e aplicar preço
  depois; replay de cache não é inferência nova ([licoes-transversais](../licoes-transversais.md) #24).
- **Não enviar campos de chat** (`messages`, `reasoning`, `temperature`, `response_format`) nem campos
  inventados: a API direta responde **400** a campo desconhecido [testado]. O SDK JS encaminha extras e o
  Python aceita `extra_body` → o erro só aparece no servidor.
- Intermediário/gateway: consultar o contrato dele (envelope, ID de modelo, chave); não misturar com a API
  direta. Se `probabilities`/`confidence` chegam intactas via gateway: não medido
  ([pendencias](../evidencias/pendencias.md)).

## 5. Chave e dados
- **Chave só no servidor** [doc: agent skill oficial]. No JS, `dangerouslyAllowBrowser` é `false` por
  padrão; ligá-lo expõe a chave a quem abre a página [doc]. Referenciar por nome (`TYPESAFE_API_KEY`);
  nunca em arquivo versionado, prompt, log ou cache.
- **Log `debug` imprime os corpos** (state e perguntas) nos dois SDKs; só cabeçalhos de credencial são
  redigidos [doc]. Não ligar `debug` com dado real; telemetria separada do conteúdo.
- O 422 pode ecoar `input` (dados enviados) — não logar indiscriminadamente [doc: OpenAPI].
- **State mínimo** [doc]: só o que a pergunta usa. Dado que não pode sair do sistema é filtrado em código
  antes da chamada; para dados sensíveis em avaliações, usar referências ou hashes [local].
- Retenção: o Jev não é treinado com requisições de clientes; ZDR para enterprise [doc,
  [modelos-precos-limites](../modelo/modelos-precos-limites.md)]. O cache/resposta bruta que *você*
  guarda segue as regras de dados do seu projeto [local].

## 6. Honestidade do teste [local]
Ao relatar uma verificação, dizer se foi conferência estática, teste com mock ou inferência real. Mock e
caso sintético não são evidência de desempenho ([metodo](../avaliar/metodo.md)).
