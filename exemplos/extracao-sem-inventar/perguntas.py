"""Perguntas e limiares da extração — o ÚNICO arquivo que um humano precisa revisar.

O Jev nunca gera valor. Três tipos de pergunta, todas numa requisição por mensagem (fan-out):
  1. ESCOLHA   Choice cujas opções SÃO os trechos que a regex achou + `none` (qual o texto pede?).
  2. ESCALA    Choice por número cru ("ofereço 600"): 600 reais, 600 mil ou 600 milhões? O código multiplica.
  3. DATA      Choices por PARTE (modo, dia, mês, ano, âncora, dia da semana, semana); o calendário é código.
Perguntas em inglês sobre mensagem em português (decisão do briefing). O state é {"message": texto}.
Mudar política = editar número aqui, sem nova chamada. Limiares iniciais = 0,60 do cookbook de datas;
afinar SÓ no conjunto de ajuste.
"""

NONE = "none"

# ---------------------------------------------------------------- limiares (política)
CONF_MIN = {  # abaixo disto a resposta vai para REVISÃO (o valor é devolvido, marcado; não é automático)
    "email": 0.60,
    "telefone": 0.60,
    "cpf": 0.60,
    "valor": 0.60,
    "data_visita": 0.60,  # aplicado ao MÍNIMO das partes usadas (uma parte fraca derruba a data)
}
ESCALA_CONF_MIN = 0.60  # número cru: a escala lida entra no mínimo com a confiança da escolha
RECONSTRUIDO_REVISA = True  # e-mail montado pelo código a partir de correção escrita → sempre revisão
MAX_ESCALAS = 6  # teto de perguntas de escala por mensagem (número cru além disso → revisão)

# ---------------------------------------------------------------- 1. escolha entre candidatos
_ESCOLHA = {
    "email": {
        "question": "Which email address should the store use to reach the person who wrote `message`?",
        "focus": "If the writer corrects their address later in the message, the corrected address is the one "
                 "to use. An address of someone else that the writer only mentions is not it.",
    },
    "telefone": {
        "question": "Which phone number should be used to contact the person who wrote `message`?",
        "focus": "If several numbers appear, pick the one the writer asks to be called or messaged on now — "
                 "it may belong to a relative they point to. Not a number they say is off, wrong or old.",
    },
    "cpf": {
        "question": "Which CPF does the writer of `message` give for their registration or for the deal?",
        "focus": "Includes a CPF the writer says should go on the contract, even if it belongs to a relative. "
                 "Not a CPF they say is wrong and then correct.",
    },
    "valor": {
        "question": "Which amount is the price the writer of `message` proposes, offers or asks for "
                    "(their own offer, counter-offer, budget limit, or asking price)?",
        "focus": "Not a price they only quote from the listing or someone else, not an area, an order or "
                 "protocol number, a fee, or an amount they reject.",
    },
}
_NONE_DESC = {
    "email": "The writer gives no email address of their own (or none of these).",
    "telefone": "The writer gives no phone number to contact them (or none of these).",
    "cpf": "The writer gives no CPF for their registration or the deal (or none of these).",
    "valor": "The writer proposes no amount: the numbers are only quoted prices, sizes, order numbers or "
             "other non-proposal numbers.",
}


def escolha(campo: str, candidatos: list[dict]) -> dict:
    """Choice cujas opções são os trechos. Descrição só onde o trecho não está literal na mensagem."""
    criteria = {}
    for c in candidatos:
        if c["origem"] == "reconstruido":
            criteria[c["texto"]] = (f"`{c['base']}` with the correction `{c['correcao']}` that the writer "
                                    f"wrote later in the message applied")
        else:
            criteria[c["texto"]] = None
    criteria[NONE] = _NONE_DESC[campo]
    return {"type": "choice", "instructions": _ESCOLHA[campo], "criteria": criteria}


# ---------------------------------------------------------------- 2. escala de número cru
ESCALA_FATOR = {"as_written": 1, "thousands": 1000, "millions": 1_000_000}


def escala(texto_numero: str) -> dict:
    """'Consigo pagar 600' num papo de imóvel é 600 mil: o Jev lê a escala, o código multiplica."""
    return {
        "type": "choice",
        "instructions": {
            "question": f"In `message`, what amount does the number written as `{texto_numero}` stand for?",
            "focus": "Read the scale the writer means from the context (for example, other prices nearby).",
        },
        "criteria": {
            "as_written": "Exactly that many reais, as written.",
            "thousands": "That many thousand reais — the word 'mil' is left implicit.",
            "millions": "That many million reais — the word 'milhão/milhões' is left implicit.",
        },
    }


# ---------------------------------------------------------------- 3. data da visita por partes
_PAPEL = "the day the writer wants to visit the property (the visit they ask to schedule)"
_AUSENTE = "Not stated for the visit day."
MESES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
         "November", "December"]
DIAS_SEMANA = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def perguntas_data(anos: list[str]) -> dict:
    """Uma Choice por parte (receita de extração de datas, adaptada ao português). Ano só se há ano escrito."""
    q = {
        "visita_modo": {
            "type": "choice",
            "instructions": f"How is {_PAPEL} given in `message`?",
            "criteria": {
                "absolute": "By a day-of-month number, alone or with a month ('dia 15', '15/10', '3 de novembro', "
                            "'sábado dia 12'). If a weekday AND a day number are given, it is this one.",
                "relative": "Relative to today, with no day number: 'hoje', 'amanhã', 'depois de amanhã', or a "
                            "weekday name ('sexta', 'sexta que vem', 'próxima terça', 'sexta da semana que vem').",
                "unclear": "Several possible days, a vague period, or only days to avoid ('sábado ou domingo', "
                           "'semana que vem', 'fim do mês', 'qualquer dia menos segunda').",
                NONE: "The message does not give a visit day (a date may be about something else).",
            },
        },
        "visita_dia": {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given by a day-of-month number, which day of the month is it?",
            "criteria": {**{str(d): None for d in range(1, 32)}, NONE: _AUSENTE},
        },
        "visita_mes": {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given by a day-of-month number, which month is written for it "
                            f"(by name or number, e.g. '15/10' = October)? Pick 'none' if no month is written.",
            "criteria": {**{m: None for m in MESES}, NONE: "No month is written for the visit day."},
        },
        "visita_relativo": {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given relative to today, which is it?",
            "criteria": {"today": "'hoje'", "tomorrow": "'amanhã'", "day_after": "'depois de amanhã'",
                         "weekday": "a weekday name ('sexta', 'terça que vem')", NONE: _AUSENTE},
        },
        "visita_dia_semana": {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given by a weekday name, which weekday?",
            "criteria": {**{d: None for d in DIAS_SEMANA}, NONE: _AUSENTE},
        },
        "visita_semana": {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given by a weekday name, which week does the writer mean?",
            "criteria": {
                "plain": "Just the weekday, or the next one: 'sexta', 'na sexta', 'sexta que vem', 'próxima sexta'.",
                "this_week": "The weekday of the current week: 'esta sexta', 'essa sexta', 'nesta sexta', "
                             "'sexta desta semana'.",
                "next_week": "The weekday of NEXT week: 'sexta da semana que vem', 'sexta da próxima semana', "
                             "'na outra semana, sexta'.",
                NONE: _AUSENTE,
            },
        },
    }
    if anos:
        q["visita_ano"] = {
            "type": "choice",
            "instructions": f"If {_PAPEL} is given by a day-of-month number, which year is written for it? "
                            f"Pick 'none' if no year is written for the visit day.",
            "criteria": {**{a: None for a in anos}, NONE: "No year is written for the visit day."},
        }
    return q
