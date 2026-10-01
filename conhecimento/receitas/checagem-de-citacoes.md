---
name: checagem-de-citacoes
description: Detecta citações erradas ou alucinadas de um LLM com string match + 1 Choice de 3 opções; nas 8 citações de teste pegou as 4 falhas plantadas e as 4 corretas saíram verified com confiança ≥ 0,93.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/citation_check.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 3461–3805
estudado_em: 2026-09-30
---

# Checagem de citações (Double-checking citations)

## Problema
Um LLM responde e anexa citações: para cada afirmação (claim), uma seção do documento-fonte e a frase (quote) em que ela se apoia. Algumas são erradas: (a) a frase não existe no documento (fabricada) ou (b) existe palavra por palavra, mas o contexto diz o oposto do claim, ou não trata do assunto. Conferir à mão é lento (achar documento, achar frase, ler contexto).

Saída do `check_citation()`: um de quatro veredictos (`verified`, `unsupported`, `contradicted`, `fabricated`) + uma confiança que marca o que um humano deve olhar.

## Como o Jev entra
Duas etapas; o Jev só entra na segunda.
1. **Sem modelo:** string match da frase na fonte (após normalização). Não achou = `fabricated`, sem chamar o Jev.
2. **Com Jev:** 1 Choice lê a seção onde a frase foi achada e diz como ela se relaciona com o claim.

- **state:** `{"claim": <texto do claim>, "section": <texto da seção achada>}` (dict).
  - Citação com quote: a seção é a que CONTÉM a frase (achada pelo match, não a que a citação declara).
  - Citação "claim-only" (`quote` = null): não há o que casar; usa-se a seção que a própria citação nomeia (`section`) e vai direto ao modelo (status `section-only`).
- **perguntas:** 1 só, chave `relation`, tipo **Choice**
  - instructions: `"How does the section relate to the claim?"`
  - criteria (opções literais):
    - `supports`: "The section states the claim or directly implies that it is true"
    - `contradicts`: "The section states the opposite of the claim or implies it is false"
    - `says_nothing`: "The section does not address what the claim asserts, either way"
- **chamadas:** 1 `system_one` por citação que sobreviveu ao match (nas 8 do teste: 7 chamadas; a `fabricated` não chama). Nada de paralelismo declarado (loop sequencial no código). Modelo `jev-1.12`, timeout do cliente 120 s.

## O que o código faz com a resposta
- Mapa opção → veredicto: `supports` → `verified`; `contradicts` → `contradicted`; `says_nothing` → `unsupported`.
- `AUTO_ACCEPT = 0.8` sobre `answer.confidence` (campo `confidence` do Choice, não a probabilidade da opção vencedora):
  - confiança ≥ 0,8: veredito vale sozinho (`auto`);
  - < 0,8: humano confirma antes de agir (`review`).
- `fabricated` (match falhou): `confidence = None` (nenhum modelo foi chamado) e `auto = True`.
- Normalização do match: colapsa espaços (`\s+` → " "), troca aspas curvas por retas (“ ” ‘ ’), `strip`; busca como substring; varre as seções em ordem numérica e devolve a primeira que contém a frase.
- Comentário do doc no limiar: "start high for more human review as you build trust in the model" — começar alto e baixar conforme se observa o modelo nos próprios documentos.
- Pré-processamento específico do RFC (não do Jev): remove cabeçalho/rodapé de página, divide em seções numeradas por regex de cabeçalho (45 seções, 58.365 caracteres).

## Resultados medidos
Fonte: RFC 7519 (JWT), 8 citações escritas por um LLM; 4 corretas, 4 editadas para falhar. Modelo `jev-1.12`, 2026-08-16.

| citação | match | relation | conf | veredito | ação |
|---|---|---|---|---|---|
| epoch_seconds | found | supports | 0,93 | verified | auto |
| aud_reject | found | supports | 0,95 | verified | auto |
| sig_reporting | missing | - | - | fabricated | auto |
| clock_skew | found | supports | 0,99 | verified | auto |
| exp_required | found | contradicts | 0,99 | contradicted | auto |
| pii_encryption | found | says_nothing | 0,27 | unsupported | review |
| iat_future | section-only | says_nothing | 0,56 | unsupported | review |
| duplicate_names | found | supports | 0,99 | verified | auto |

- Resumo do doc: 4 verified, 1 fabricated, 1 contradicted, 2 unsupported; as 4 falhas plantadas foram pegas (2 das 4 só com humano, por confiança < 0,8).
- `exp_required` cita a seção 4.1.4 literalmente, e a mesma seção diz "Use of this claim is OPTIONAL" → contradicted a 0,99.
- `pii_encryption` mostra por que o match sozinho não basta: a frase está na fonte literalmente, mas a seção não trata do claim.
- Custo e latência: (não declarado no doc). O código só mede `seconds` e tokens dentro de `ask()`, mas não imprime nenhum.

## Técnicas reutilizáveis
- Tirar do modelo o que uma comparação de strings resolve (existência da frase) → sempre que a verificação for determinística; o modelo só vê o que sobrou.
- Dar ao Choice o CONTEXTO recuperado (a seção) e o claim juntos no state → quando a pergunta é "esta fonte sustenta esta afirmação".
- Escolher as 3 opções como relações mutuamente exclusivas e exaustivas (apoia / contradiz / não diz nada) → cada uma mapeia direto para um veredito de negócio, sem pós-processamento.
- Usar `confidence` como porteiro automático-vs-humano, com limiar único em constante → revisão humana só do que o modelo não tem certeza; limiar começa alto e desce com a confiança construída.
- Mesmo caminho para entrada sem quote (claim-only): pular a etapa 1 e usar a seção declarada → tratar entradas incompletas sem ramificar a lógica do modelo.
- Confiança ausente (`None`) quando nenhum modelo foi chamado → não inventar confiança para decisões tomadas por regra.

## Limites e pegadinhas
- O match é exato após normalização: frase truncada ou levemente reescrita vira `fabricated`; sistema tolerante precisaria de fuzzy matching (admitido pelo doc).
- `load_source()` e `split_sections()` são escritos para o layout de um RFC; outro formato de documento exige parsing próprio.
- `contradicted` e `fabricated` saem `auto`: o desenho manda para humano só o de baixa confiança; um `verified` com confiança ≥ 0,8 também passa sem humano.
- 0,8 é ilustrativo; o doc não calibra nem valida o limiar (8 exemplos).
- O cache `json_cache.json` acompanha o cookbook: reexecutar reproduz os números publicados sem chamar a API; apagar o arquivo roda ao vivo.

## Esqueleto de código
```python
QUESTIONS = {
    "relation": Choice(
        instructions="How does the section relate to the claim?",
        criteria={
            "supports": "The section states the claim or directly implies that it is true",
            "contradicts": "The section states the opposite of the claim or implies it is false",
            "says_nothing": "The section does not address what the claim asserts, either way",
        },
    ),
}
RELATION_TO_VERDICT = {"supports": "verified", "contradicts": "contradicted", "says_nothing": "unsupported"}

def ask(claim, section):
    response = client.system_one(
        state={"claim": claim, "section": section},
        questions=QUESTIONS, model="jev-1.12")
    a = response.answers["relation"]
    return {"choice": a.choice, "probabilities": a.probabilities, "confidence": a.confidence}

def verdict(status, answer):
    if status == "missing":
        return {"verdict": "fabricated", "confidence": None, "auto": True}
    return {"verdict": RELATION_TO_VERDICT[answer["choice"]],
            "confidence": answer["confidence"],
            "auto": answer["confidence"] >= 0.8}   # AUTO_ACCEPT

def check_citation(sections, citation):
    status, section = locate(sections, citation)   # found / missing / section-only
    answer = ask(citation["claim"], section) if section is not None else None
    return {"id": citation["id"], "status": status, "answer": answer, **verdict(status, answer)}
```
