"""Seleção de skill — perguntas, limiares, variante principal e critério. O arquivo que o humano revisa.

Receita-irmã: `conhecimento/receitas/sugestao-de-skill.md` (cookbook oficial "Skill suggestion"). O que veio de lá
está marcado [receita]; o que é adaptação nossa, [local].

State: `{"request": <pedido>}` — só o pedido. O catálogo NÃO vai no state: vira as opções da Choice e o texto de
cada Noul [receita]. Perguntas em inglês; nome e descrição das skills ficam em português, como estão no catálogo
(são dado, não pergunta — traduzir seria reescrever o catálogo).

Cinco formatos de requisição (cada variante paga só os seus — `selecao.ETAPAS`):
  `ampla`          Choice `which` sobre as 42 skills + `none`, descrição CURTA (nome + 60 caracteres) [receita: o
                   índice truncado em 60; `none` é local — a receita não tem válvula na Choice].
  `fits_vencedor`  um Noul `fits.<id>` só para o vencedor da ampla (variante b).
  `rerank`         Choice `rerank` entre as 3 melhores com a descrição COMPLETA + um Noul `fits.<id>` por candidata +
                   os 3 Nouls de porta da receita [receita; local: as portas vão aqui e não na 1ª requisição, para
                   a ampla ser exatamente o que a Choice única paga — nossa receita faz sempre 2 requisições].
  `todos`          um Noul `fits.<id>` por skill do catálogo, 42 numa requisição (variante e).
  `ampla_completa` a mesma Choice `which` da ampla, com a descrição COMPLETA de cada skill (variante informativa a2:
                   42 descrições inteiras cabem numa requisição — o funil curto → longo é mesmo necessário aqui?).

Política de `null` (dados/LEIA-ME.md, escrita pelo rotulador ANTES dos casos): trivial, fora do catálogo, vago sem
objeto, conversa. Ela está escrita uma vez, no critério `none` da Choice ampla. Os Nouls `fits` perguntam só
adequação absoluta ("esta skill faz o que foi pedido?") e NÃO conhecem a política — é o texto da receita.
"""
from __future__ import annotations

NENHUMA = "none"        # válvula da Choice ampla; nunca é ID de skill (o código confere)
SHORTLIST = 3           # [receita] quantas candidatas a 2ª requisição relê
CURTA = 60              # [receita] caracteres da descrição no índice (padrão do Hermes)
TETO_CARACTERES = 600   # pedido maior que isto não é enviado: sem sugestão (a faixa medida é de 1–3 linhas)
MAX_SKILLS = 254        # Choice aceita ≤ 255 opções; uma é a válvula

# ---------------------------------------------------------------------------------------- textos
# Duas regras de leitura do LEIA-ME ("vale a intenção, não a palavra"; "composto → a primeira etapa"), iguais nas
# duas Choices. Escritas antes de qualquer medição; não foram mexidas na afinação.
_REGRAS = ("Judge by what the user wants done, not by words that merely match a skill's name. If the request has "
           "several steps, pick the skill for the step that has to be done first.")

_NENHUMA = ("No skill should be loaded. Use this when the request is: a small direct task the agent simply does "
            "without a procedure (rename a variable, fix a typo, change a color or a label, run a command such as "
            "tests or lint, make a commit or a local merge); a question answered in prose (what an error message "
            "means, a concept, which skill to use); small talk or thanks; something that no skill in this list "
            "covers; or too vague to tell what the user wants done or on what.")

# [receita] as três portas, texto literal do cookbook; `prose_suffices` aponta ao contrário (entra como 1 − v).
PORTAS = {
    "acts_on_user_system": ("Is the assistant being asked to act on the user's files, accounts, devices, or online "
                            "services, rather than only to explain or advise?"),
    "would_follow_documented_procedure": ("Would a careful expert answering this consult a specific documented "
                                          "procedure or set of commands, rather than answering from general "
                                          "understanding?"),
    "prose_suffices": ("Could a knowledgeable generalist fully satisfy this request in prose, with no tools, no "
                       "documentation, and no access to the user's files or accounts?"),
}
INVERTIDAS = {"prose_suffices"}


def curta(skill: dict) -> str:
    """Linha do índice: nome + descrição cortada em `CURTA` caracteres, em fim de palavra.
    @example curta({"nome": "Abrir PR", "descricao": "Cria o pull request pelo terminal a partir da branch atual, com título"})
             → "Abrir PR: Cria o pull request pelo terminal a partir da branch atual…"
    """
    d = skill["descricao"].strip()
    if len(d) > CURTA:
        d = d[:CURTA + 1].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    return f"{skill['nome']}: {d}"


def completa(skill: dict) -> str:
    return f"{skill['nome']}: {skill['descricao'].strip()}"


def choice_ampla(catalogo: list[dict], inteira: bool = False) -> dict:
    """Choice `which`: as skills com a linha curta (ou a descrição inteira, na variante informativa a2) + a válvula
    `none` com a política de `null` do LEIA-ME. Instrução e válvula são as mesmas nas duas formas."""
    return {
        "type": "choice",
        "instructions": {
            "question": "Which of these skills, if any, is the right one to load to help with the user's request in `request`?",
            "rules": _REGRAS + f" Pick `{NENHUMA}` when no skill should be loaded.",
        },
        "criteria": {**{s["id"]: completa(s) if inteira else curta(s) for s in catalogo}, NENHUMA: _NENHUMA},
    }


def choice_rerank(candidatas: list[dict]) -> dict:
    """Choice `rerank` [receita]: só as candidatas, com o texto completo. Sem válvula, como na receita — quem diz
    "nenhuma" nesta etapa são os Nouls `fits` e as portas."""
    return {
        "type": "choice",
        "instructions": {
            "question": ("Exactly one of these skills is the right one to load for the user's request in `request`. "
                         "Which one? Read what each actually does, not just its name."),
            "rules": _REGRAS,
        },
        "criteria": {s["id"]: completa(s) for s in candidatas},
    }


def noul_fits(skill: dict) -> dict:
    """Noul `fits.<id>` [receita]: adequação absoluta de UMA skill, respondida sozinha — todas podem vir baixas."""
    return {"type": "noul",
            "instructions": (f"Does the skill '{skill['id']}' do the specific thing the user's request in `request` asks "
                             f"for? It is described as: {completa(skill)}")}


def nouls_porta() -> dict:
    return {f"gate.{k}": {"type": "noul", "instructions": texto} for k, texto in PORTAS.items()}


# ---------------------------------------------------------------------------------------- política
# Variantes medidas (o `run.py` compara todas nos mesmos casos; a produção roda só a principal):
#   a   Choice única: o vencedor da ampla (`none` → nenhuma).                                   1 requisição
#   b   a + Noul `fits` do VENCEDOR: portão absoluto no vencedor consumido.                     1–2 requisições
#   c   receita oficial: portas → maior `fits` da shortlist ≥ limiar → vencedor da `rerank`.    2 requisições
#   c2  receita + conferência do vencedor consumido: o `fits` do vencedor da `rerank` ≥ limiar.  2 requisições
#   d   receita corrigida: vencedor = maior `fits` da shortlist, com o portão nele.             2 requisições
#   e   um Noul `fits` por skill: o maior vence, com portão.                                    1 requisição
VARIANTES = ["a", "b", "c", "c2", "d", "e"]
# Informativa, fora do critério: a2 = Choice única com a descrição COMPLETA (1 requisição). Não tem limiar nem texto
# afinado; por orçamento de requisições foi medida só no rascunho (encanamento) e no teste, não no ajuste.
INFORMATIVAS = ["a2"]

# Limiares afinados SÓ no ajuste (36 pedidos; partida = 0,30 da receita em tudo; os textos não foram mexidos).
# Números do ajuste ao lado. Ajuste pequeno não calibra limiar: os platôs são largos e o teste é quem diz.
LIMIAR = {
    # [receita: 0,30] média das 3 portas orientadas < → nenhuma (c, c2, d). A 0,30 a porta fechou 2 pedidos COM skill
    # (tela nova 0,26; planejar feature 0,24) e 3 `null` (≤ 0,16); 0,20 fica no vão entre 0,16 e 0,24.
    "porta": 0.20,
    # [receita: 0,30] `fits` do candidato < → nenhuma (b, c, c2, d). b não muda de 0,1 a 0,6; c/c2/d têm o melhor
    # ponto em 0,4–0,5 (3 indevidas; 4 a 0,30). 0,5 = "sim e não igualmente prováveis", dentro dos dois platôs.
    "fits": 0.50,
    "fits_todos": 0.50,  # maior `fits` entre as 42 < → nenhuma (e). Melhor ponto do ajuste (folgado 0,917; 0,889 a 0,30).
    "baseline": 4.0,     # pontuação BM25 da melhor skill < → nenhuma. Melhor folgado do baseline no ajuste (0,722).
}
LIMIAR_RECEITA = 0.30     # a receita publica 0,30 / 0,30 sem análise de sensibilidade; linha informativa no relatório
# A que o critério julga. Regra de escolha, aplicada ao AJUSTE com os limiares acima: menos skill indevida; empate →
# maior acerto folgado; empate → mais barata. Ajuste: b 1/10 e 0,944 · a 2/10 e 0,917 · c, c2, d, e 3/10 e 0,917.
VARIANTE_PRINCIPAL = "b"

# ---------------------------------------------------------------------------------------- baseline de código
# Sobreposição de palavras (BM25) entre o pedido e id + nome + descrição de cada skill. O que um dev escreve em
# meia hora: minúsculas, sem acento, sem palavras vazias, radical = 5 primeiras letras.
BM25_K1, BM25_B, RADICAL = 1.5, 0.75, 5
VAZIAS = set("""a o as os um uma uns umas de do da dos das em no na nos nas por pra pro para com sem e ou que se
ao aos é ser tem ter foi isso isto esse essa esses essas este esta aqui ai la ja so mais menos muito
me te eu voce ele ela meu minha seu sua como quando onde qual quais quem porque
ta to esta estao vai vou faz fazer preciso quero""".split())

# ---------------------------------------------------------------------------------------- critério
# Critério de continuar/descartar — entra no manifesto `congelamento.json`. Fixado em 2026-10-01, depois do ajuste
# e ANTES de abrir `dados/teste.json`; mudar isto exige congelar de novo. Denominadores pela tabela do LEIA-ME
# (teste: 87 pedidos, 24 `null`, 63 com skill). De onde vêm os limites: a receita oficial mediu, com o agente sozinho,
# 9,8% de carga desnecessária e, com a sugestão, 7,3% de carga errada — um roteador que não fica abaixo disso não paga.
CRITERIO_CONTINUAR = {
    "onde": "no teste (87 pedidos: 24 `null`, 63 com skill), variante principal com os limiares acima",
    "variante_principal": VARIANTE_PRINCIPAL,
    "1_skill_indevida": "carregou skill com gabarito `null` ≤ 2/24",
    "2_acerto_folgado": "escolha ∈ `aceitaveis` (ou nenhuma quando vazio) ≥ baseline de código (BM25) + 0,20",
    "3_contra_choice_unica": "acerto folgado ≥ o da Choice única (a) E skill indevida ≤ a dela",
    "4_null_indevido": "não carregou quando havia skill ≤ 10% (≤ 6/63)",
    "5_skill_errada": "carregou skill fora de `aceitaveis` ≤ 5% (≤ 3/63)",
    "se_falhar": ("1 = a sugestão carrega skill onde não devia: não serve como dica automática; 2 = a sobreposição de "
                  "palavras basta; 3 = o Noul do vencedor não paga a 2ª requisição: a Choice única faz o mesmo; 4 = a "
                  "etapa cala demais (o agente fica sozinho); 5 = sugestão errada e confiante é pior que nenhuma"),
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"indevida_max_fracao": 0.0834, "margem_folgado": 0.20, "null_indevido_max_fracao": 0.10,
                "errada_max_fracao": 0.05},
}
