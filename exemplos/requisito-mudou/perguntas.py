"""Perguntas, faixas, política e critério do `requisito-mudou` — o ÚNICO arquivo que um humano precisa revisar.

Uma história (requisitos registrados + turnos novos de WhatsApp) vira UM state `{"previous_requirements",
"new_turns"}` e UMA requisição ao Jev com as perguntas de TODOS os requisitos. O Jev julga, por requisito, se o
cliente continua com a mesma restrição; o código (`requisitos.py`) lê os candidatos de valor, copia o escolhido
literalmente, aplica a política e recalcula a shortlist (`reavaliar`) com comparação numérica própria.

Desenho (regras de rotulagem em dados/LEIA-ME.md):
- Variante PRINCIPAL `choice`: uma Choice por requisito, `kept | replaced | denied | uncertain`, com a descrição
  completa de cada classe (lição 37: catálogo que cabe numa Choice começa pela Choice única). Política: vence a
  maior probabilidade; vencedor abaixo de `P_MIN_VENCEDOR` → `incerto` (o lado barato: não mexe na shortlist e
  manda o corretor perguntar).
- Variante INFORMATIVA `nouls`: três Nouls atômicos por requisito — `changed` (o cliente decidiu mudar ou tirar),
  `dropped` (tirou e nada entrou no lugar), `open` (ficou em aberto: hipótese, terceiro, sem valor) — combinados em
  código por `FAIXA`. Vai na MESMA requisição (perguntas isoladas; custo ≈ 20–100 tokens cada) e é só comparação.
- `new_value` (Choice por requisito, só quando o código acha candidatos): o valor novo é escolhido entre
  CANDIDATOS lidos pelo código — números do texto normalizados (`_comum/numeros_br.py`), bairros do dicionário,
  meses, `mobiliado`/`sem mobília`, a faixa inteira para quartos/vagas — mais `none`. O Jev escolhe, o código
  copia literal; consumido SÓ quando a Choice de status diz `replaced`. Sem candidato (ou `none`) com `replaced`
  → `incerto` ("sem valor não há substituição", LEIA-ME). Atributos sim/indiferente não têm pergunta de valor:
  o único valor novo possível é `sim` (regra de código).
- O estado inicial vem do CADASTRO (`previous_requirements`), nunca do texto; só os turnos novos entram.

Perguntas em inglês sobre conversa em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%).

Afinação (só rascunho + ajuste; o que cada passada mudou está registrado abaixo e no README):
- 1ª passada (texto escrito a partir do LEIA-ME antes de qualquer chamada): rascunho 19/19; ajuste 92/95 na Choice,
  zero erro caro, `reavaliar` 22/22. Os 3 erros eram UMA família: `mantido` que saiu `uncertain` (0,62–0,70) porque a
  hipótese era sobre OUTRO atributo (promoção → teto, e o `financiamento` ficou em aberto, RM-A004; ajuda do pai →
  teto, idem RM-A007; "mais uma vaga mudaria o valor?" → `orcamento`, RM-A021). O LEIA-ME já diz que o fato não
  contamina os outros atributos.
- 2ª passada: a regra do LEIA-ME entrou em `_REGRAS` ("a hypothesis, a question or a fact that concerns a different
  attribute leaves this attribute as it was") e no `not_for` de `uncertain`. Nada foi escrito para um caso só.
"""

# ---------------------------------------------------------------------------------------- vocabulário
# Atributo do cadastro → o que ele significa (vai na pergunta, em inglês) e como o código trata o valor novo.
# `tipo`: dinheiro (candidatos = números do texto) · contagem (candidatos = faixa inteira menos o atual) ·
# bairro (candidatos = bairros do dicionário citados, sozinhos e somados ao atual) · mobilia · prazo (meses) ·
# sim_ou_nada (sem pergunta de valor: o único valor novo possível é "sim").
ATRIBUTOS = {
    "orcamento": {"tipo": "dinheiro",
                  "gloss": "the maximum price the client will pay — a purchase price, or a monthly rent when the "
                           "registered value ends in '/mês'"},
    "quartos": {"tipo": "contagem", "faixa": (1, 5), "gloss": "the minimum number of bedrooms"},
    "vagas": {"tipo": "contagem", "faixa": (0, 4),
              "gloss": "the minimum number of parking spaces ('0' = the client did not need one)"},
    "bairro": {"tipo": "bairro", "gloss": "the neighbourhood(s) the property must be in ('A ou B' = either)"},
    "elevador": {"tipo": "sim_ou_nada",
                 "gloss": "'sim' = access without stairs is required (an elevator, a ground floor or a single-storey "
                          "house); 'indiferente' = the client did not care"},
    "pet": {"tipo": "sim_ou_nada",
            "gloss": "'sim' = the property must accept pets because the client has one; 'não' = the client had no pet "
                     "and no such requirement"},
    "mobilia": {"tipo": "mobilia",
                "gloss": "'mobiliado' = must be furnished; 'sem mobília' = must be unfurnished; 'indiferente' = either"},
    "andar_baixo": {"tipo": "sim_ou_nada",
                    "gloss": "'sim' = must be on a low floor (ground to 3rd) or a single-storey house; 'indiferente' = "
                             "the client did not care"},
    "financiamento": {"tipo": "sim_ou_nada",
                      "gloss": "'sim' = the client needs bank financing, so the seller must accept it; 'não' = pays "
                               "cash, no such requirement"},
    "prazo": {"tipo": "prazo", "gloss": "the latest month to move in ('mudança até MM/AAAA')"},
}
STATUS = ["kept", "replaced", "denied", "uncertain"]
# Opção da Choice → rótulo do gabarito (dados em pt).
ROTULO_DA_OPCAO = {"kept": "mantido", "replaced": "substituido", "denied": "negado", "uncertain": "incerto"}

# Regras comuns às perguntas de status e de valor: quem decide, última fala, correção, mudança indireta.
_REGRAS = (
    "Only the client decides: count what the client states or confirms in these turns. A number first said by "
    "the broker counts only when the client confirms it ('isso', 'fechou'). The client's LAST statement about this "
    "attribute wins; a message starting with '*' corrects the previous one. A fact of the client's life whose "
    "consequence for this attribute is stated or inescapable counts as the client's decision (a relative who "
    "cannot climb stairs will live there → access without stairs; a second car that cannot stay on the street → "
    "two spaces; a pet adopted → must accept pets; moving in with no furniture at all → furnished only if the client "
    "says so). Talk about OTHER attributes, visits, schedules or the properties already sent does not touch this one: "
    "a hypothesis, a question or a fact that concerns a different attribute (money that may come in concerns the "
    "budget, not the financing; the cost of one more parking space concerns parking, not the rent ceiling) leaves this "
    "attribute as it was — judge only what is said about this attribute itself."
)


def pergunta_status(req: dict) -> dict:
    """Choice `kept | replaced | denied | uncertain` para UM requisito registrado; o texto cita o id, o atributo, o
    significado e o valor registrado (o ID da pergunta não vai ao modelo). Exemplos escritos à mão."""
    atr = req["atributo"]
    gloss = ATRIBUTOS[atr]["gloss"]
    return {
        "type": "choice",
        "instructions": {
            "question": f"`new_turns` are the latest WhatsApp messages between a property-hunting client (`from` = "
                        f"`client`) and the broker (`from` = `broker`), in Brazilian Portuguese. Requirement "
                        f"`{req['id']}` in `previous_requirements` is the attribute `{atr}` ({gloss}), registered "
                        f"BEFORE these turns as `{req['valor']}`. After these turns, does the client still have the "
                        f"same restriction on `{atr}`?",
            "rules": _REGRAS,
        },
        "criteria": {
            "kept": {
                "what": f"The restriction on `{atr}` is unchanged: nothing in these turns touches this attribute; "
                        "or the client reaffirms the registered value, rejects a change the broker or a relative "
                        "proposed, corrects the broker back to the registered value, only asks a question about a "
                        "property's attribute, or mentions a value that belongs to someone else's purchase or is "
                        "plainly ironic; or the client names a conditional exception but keeps the limit "
                        "('my limit is 600, 650 only for something exceptional').",
                "not_for": "A preference of a spouse, parent or friend reported WITHOUT the client's decision "
                           "(that is uncertain); a decided new value, even a looser one (replaced); the restriction "
                           "dropped (denied); a hypothesis or a change without value (uncertain).",
                "examples": ["meu teto continua 600, não mudou nada", "o segundo tem elevador?",
                             "ela queria 3 quartos mas quem decide sou eu, fica 2"],
            },
            "replaced": {
                "what": f"The client now has a DIFFERENT restriction on `{atr}`, decided and with a value stated or "
                        "inescapable: a new number or ceiling (tighter or looser), a neighbourhood added or swapped, "
                        "a requirement that did not exist before ('indiferente', 'não' or '0' becomes a real "
                        "requirement), the broker's suggestion accepted, or a number said by the broker and confirmed "
                        "by the client.",
                "not_for": "A value that depends on something that has not happened yet; a value only the broker "
                           "said; a relative's wish the client did not adopt; a change announced without a value; "
                           "the restriction removed with nothing in its place (denied).",
                "examples": ["agora preciso de 2 vagas, compramos outro carro", "pode incluir a Lapa também",
                             "minha mãe vem morar comigo e não sobe escada"],
            },
            "denied": {
                "what": f"The client no longer wants or needs any restriction on `{atr}` and nothing replaces it: "
                        "'não preciso mais de vaga', 'pode ser com ou sem mobília', 'vou pagar à vista' (financing "
                        "no longer needed), 'tanto faz o bairro', 'nunca pedi isso'; or the wish moved to something "
                        "this attribute cannot hold ('agora quero andar alto' for a low-floor requirement).",
                "not_for": "A different value for the same attribute, including a looser one (replaced); a "
                           "restriction the client keeps or reaffirms (kept); a removal still under consideration "
                           "(uncertain).",
                "examples": ["vendi o carro, não preciso mais de vaga", "pode ser mobiliado ou não, tanto faz"],
            },
            "uncertain": {
                "what": f"A change on `{atr}` is in the air but not decided: a hypothesis about the future ('se eu "
                        "for promovida subo pra 800', 'vamos ver', 'depois te falo'); a preference or opinion of a "
                        "spouse, parent or friend that the client neither adopts nor rejects; help from a relative "
                        "that is still a 'maybe'; a change announced without a value ('dá pra esticar um pouco'); a "
                        "fact of life whose consequence for this attribute the client leaves open ('tô grávida' "
                        "with nothing about bedrooms); a broker's suggestion left with 'deixa eu ver'.",
                "not_for": "The client reaffirming, rejecting or ignoring the change (kept); the client deciding a "
                           "value (replaced) or dropping the restriction (denied); a hypothesis that concerns a "
                           "DIFFERENT attribute (kept for this one).",
                "examples": ["talvez meu pai ajude com uns 50 mil, ainda vai ver", "minha esposa prefere a Lapa, "
                             "vamos conversar", "meu prazo apertou, ainda não sei quanto"],
            },
        },
    }


def pergunta_valor(req: dict, candidatos: list[str]) -> dict:
    """Choice do valor novo entre candidatos LIDOS PELO CÓDIGO (+ `none`). O Jev escolhe; o código copia literal.
    Consumida só quando o status é `replaced`."""
    atr = req["atributo"]
    gloss = ATRIBUTOS[atr]["gloss"]
    return {
        "type": "choice",
        "instructions": {
            "question": f"Requirement `{req['id']}` (`{atr}`: {gloss}) was registered as `{req['valor']}`. If after "
                        f"`new_turns` the client has a NEW value for `{atr}` — decided by the client, not a hypothesis, "
                        "not someone else's — which of these candidates is it? The candidates were read from the "
                        "text by code; pick the one the client's last statement supports.",
            "rules": _REGRAS + " Choose `none` when the requirement was not replaced by a new value, when the only "
                               "value mentioned is hypothetical or belongs to another person, or when the real new "
                               "value is not among the candidates.",
        },
        "criteria": {
            **{c: f"The client's new requirement on `{atr}` is exactly `{c}`." for c in candidatos},
            "none": "No decided new value for this attribute in these turns, or the new value is not listed.",
        },
    }


def perguntas_nouls(req: dict) -> dict:
    """Variante informativa: três Nouls atômicos por requisito, combinados em código (`requisitos.status_por_nouls`)."""
    atr, rid, val = req["atributo"], req["id"], req["valor"]
    gloss = ATRIBUTOS[atr]["gloss"]
    cab = (f"`new_turns` are the latest WhatsApp messages between a property-hunting client (`client`) and the "
           f"broker (`broker`), in Brazilian Portuguese. Requirement `{rid}` in `previous_requirements` is `{atr}` "
           f"({gloss}), registered before these turns as `{val}`. ")
    return {
        f"{rid}_changed": {
            "type": "noul",
            "instructions": cab + f"In these turns the client DECIDES to change or to drop the restriction on `{atr}`: "
                                  "states a new value, accepts a suggested one, confirms a number the broker said, or "
                                  "says the restriction no longer applies. " + _REGRAS,
            "criteria": {"true": "The client decided: a new value for this attribute, or its removal, is stated or "
                                 "inescapable in the client's own words.",
                         "false": "Not decided: the attribute is not touched, is reaffirmed, the change is a "
                                  "hypothesis, a question, irony, someone else's wish not adopted, someone else's "
                                  "money, or a change announced without a value."},
        },
        f"{rid}_dropped": {
            "type": "noul",
            "instructions": cab + f"The client says the restriction on `{atr}` no longer applies AT ALL and gives no "
                                  "other value for it ('não preciso mais', 'pode ser com ou sem', 'tanto faz', 'vou "
                                  "pagar à vista' for financing, 'nunca pedi isso'). " + _REGRAS,
            "criteria": {"true": "The restriction is removed and nothing replaces it.",
                         "false": "The client keeps a restriction on this attribute (the same or a different value), "
                                  "or the removal is only considered, or the attribute is not touched."},
        },
        f"{rid}_open": {
            "type": "noul",
            "instructions": cab + f"These turns leave the restriction on `{atr}` IN THE AIR: a hypothesis about the "
                                  "future, a preference of a spouse, parent or friend the client neither adopts nor "
                                  "rejects, help from a relative still unconfirmed, a change announced without a "
                                  "value, a 'vamos ver' / 'depois te falo' / 'deixa eu ver'. " + _REGRAS,
            "criteria": {"true": "A possible change on this attribute is mentioned and the client leaves it undecided.",
                         "false": "Nothing about this attribute is left open: it is not mentioned, or the client "
                                  "decided (new value, removal), or reaffirmed or rejected the change."},
        },
    }


# ---------------------------------------------------------------------------------------- política
# Variante principal declarada ANTES do teste (entra no manifesto via CRITERIO_CONTINUAR); a outra é informativa.
VARIANTE_PRINCIPAL = "choice"
# Choice de status: vence a maior probabilidade; vencedor abaixo deste piso → `incerto` (não mexe na shortlist e
# pede confirmação). Partida = piso global das notas (NÚCLEO §6: ~0,5–0,6); afinado só no ajuste.
P_MIN_VENCEDOR = 0.5
# Choice de valor: consumida só com status `replaced`; `none` ou vencedor abaixo do piso → `incerto`.
P_MIN_VALOR = 0.5
# Nouls da variante informativa: ≤ nao → não; ≥ sim → sim; meio = dúvida (→ `incerto`). Partida 0,3–0,7.
FAIXA = {"changed": (0.3, 0.7), "dropped": (0.3, 0.7), "open": (0.3, 0.7)}
# Faixa validada: histórias de 3–5 turnos curtos e 3–6 requisitos. Acima do teto a história NÃO vai ao Jev: tudo
# `incerto`, origem `longa` (contada à parte). Não é limiar afinado.
TETO_CARACTERES = 4000
TETO_REQUISITOS = 12

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01 ~19h, depois da 2ª passada do ajuste e ANTES de abrir `dados/teste.json`, com os denominadores
# da tabela do LEIA-ME (teste: 44 histórias, 181 requisitos; 22 `substituido`, 6 `negado`, 12 `incerto`; 141
# `mantido`). Limites ABSOLUTOS no erro caro + piso de acerto; o baseline fica informativo (margem sobre baseline é
# critério frágil: metodo.md 2026-10-01). "Sempre mantido" acerta 141/181 = 0,779 dos requisitos: o piso 5 fica
# acima disso. O ajuste fechou em 95/95 (fácil demais para calibrar): os pisos 3 e 5 ficam abaixo do ajuste de
# propósito, porque o teste tem 93% de difíceis e duas famílias sem caso no ajuste (ambíguo, ironia).
CRITERIO_CONTINUAR = {
    "onde": "no teste (44 histórias, 181 requisitos), variante principal `choice` com a política acima",
    "variante_principal": VARIANTE_PRINCIPAL,
    "1_mudanca_perdida": "requisito `substituido` ou `negado` no gabarito que saiu `mantido` ≤ 2 de 28 (a dor: shortlist velha continua valendo)",
    "2_troca_indevida": "requisito `incerto` (hipótese/terceiro) ou `mantido` no gabarito que saiu `substituido` ou `negado` ≤ 4 de 153",
    "3_acerto_mudados": "rótulo exato nos 40 requisitos mudados (`substituido`/`negado`/`incerto`) ≥ 0,75",
    "4_reavaliar": "`reavaliar` exato (conjunto e ordem) ≥ 0,85 das 44 histórias",
    "5_acerto_total": "rótulo exato nos 181 requisitos ≥ 0,90 (sempre-mantido = 0,779)",
    "secundario_nao_decide": "`novo_valor` certo ≥ 0,85 dos `substituido` acertados; detectou que algo mudou ≥ 0,85 das 34 histórias com mudança; baseline informativo",
    "se_falhar": "1 ou 2 falhando = o desenho não serve para atualizar o cadastro sem humano; 3, 4 ou 5 falhando = volta ao ajuste com dados novos",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"mudanca_perdida_max": 2, "troca_indevida_max": 4, "acerto_mudados_min": 0.75, "reavaliar_min": 0.85,
                "acerto_total_min": 0.90, "novo_valor_min": 0.85, "detectou_min": 0.85},
}

# ---------------------------------------------------------------------------------------- dicionário de bairros
# Candidatos de `bairro` vêm daqui (mais os bairros já registrados e os da shortlist). Um CRM tem a tabela de bairros
# da cidade; esta lista, escrita à mão, faz esse papel. Sem acento e em minúsculas no casamento.
BAIRROS = [
    # São Paulo
    "Moema", "Pinheiros", "Vila Madalena", "Vila Mariana", "Saúde", "Perdizes", "Pompeia", "Lapa", "Tatuapé", "Mooca",
    "Santana", "Tucuruvi", "Butantã", "Itaim Bibi", "Jardins", "Jardim Paulista", "Paraíso", "Bela Vista", "Consolação",
    "Higienópolis", "Brooklin", "Campo Belo", "Vila Olímpia", "Morumbi", "Ipiranga", "Aclimação", "Cambuci", "Liberdade",
    "Vila Leopoldina", "Alto da Lapa", "Alto de Pinheiros", "Sumaré", "Barra Funda", "Água Branca", "Freguesia do Ó",
    "Jabaquara", "Santo Amaro", "Chácara Klabin", "Vila Clementino", "Vila Prudente", "Anália Franco", "Penha",
    "Carrão", "Vila Formosa", "Belém", "Brás", "Pari", "Mandaqui", "Casa Verde", "Vila Guilherme", "Jaçanã",
    "Vila Sônia", "Rio Pequeno", "Jaguaré", "Interlagos", "Socorro", "Guarapiranga", "Vila Andrade", "Panamby",
    # Curitiba
    "Batel", "Água Verde", "Portão", "Bigorrilho", "Centro Cívico", "Juvevê", "Cabral", "Alto da XV", "Cristo Rei",
    "Jardim das Américas", "Rebouças", "Mercês", "Bacacheri", "Boa Vista", "Santa Felicidade", "Ecoville", "Mossunguê",
    "Campo Comprido", "Ahú", "Hugo Lange", "Jardim Social", "Guabirotuba", "Novo Mundo", "Capão Raso", "Pinheirinho",
    # Porto Alegre
    "Bom Fim", "Menino Deus", "Petrópolis", "Moinhos de Vento", "Cidade Baixa", "Auxiliadora", "Mont'Serrat",
    "Bela Vista", "Rio Branco", "Santana", "Floresta", "Independência", "Três Figueiras", "Tristeza", "Cristal",
    "Jardim Botânico", "Partenon", "Santa Cecília", "Boa Vista", "Chácara das Pedras", "Higienópolis", "São João",
    # Belo Horizonte
    "Buritis", "Savassi", "Funcionários", "Lourdes", "Sion", "Belvedere", "Santo Agostinho", "Serra", "Cidade Nova",
    "Castelo", "Santo Antônio", "Anchieta", "Carmo", "Cruzeiro", "Gutierrez", "Luxemburgo", "Mangabeiras", "Estoril",
    "Ouro Preto", "Pampulha", "Jaraguá", "Santa Efigênia", "Floresta", "Padre Eustáquio", "Prado", "Caiçara",
    # Recife
    "Boa Viagem", "Graças", "Casa Forte", "Espinheiro", "Aflitos", "Parnamirim", "Pina", "Madalena", "Torre",
    "Derby", "Jaqueira", "Tamarineira", "Rosarinho", "Encruzilhada", "Poço da Panela", "Candeias", "Piedade",
    "Setúbal", "Imbiribeira", "Boa Vista", "Santo Amaro", "Cordeiro", "Várzea", "Casa Amarela",
    # Campinas
    "Cambuí", "Taquaral", "Nova Campinas", "Guanabara", "Jardim Chapadão", "Barão Geraldo", "Mansões Santo Antônio",
    "Vila Itapura", "Botafogo", "Bosque", "Jardim Proença", "Jardim Flamboyant", "Alphaville", "Swiss Park",
    "Jardim Guanabara", "Castelo", "Vila Brandina", "Parque Prado", "Sousas",
    # Rio de Janeiro
    "Copacabana", "Ipanema", "Leblon", "Botafogo", "Flamengo", "Laranjeiras", "Tijuca", "Barra da Tijuca",
    "Recreio", "Jardim Botânico", "Gávea", "Humaitá", "Catete", "Glória", "Méier", "Vila Isabel", "Grajaú",
    "Jacarepaguá", "Freguesia", "Taquara", "Lagoa", "Urca", "Leme", "Niterói", "Icaraí",
    # Florianópolis, Salvador, Fortaleza, Goiânia, Brasília
    "Trindade", "Centro", "Agronômica", "Córrego Grande", "Itacorubi", "Campeche", "Coqueiros", "Estreito",
    "Pituba", "Barra", "Graça", "Rio Vermelho", "Caminho das Árvores", "Horto Florestal", "Itaigara", "Ondina",
    "Meireles", "Aldeota", "Cocó", "Dionísio Torres", "Papicu", "Varjota", "Fátima", "Benfica",
    "Setor Bueno", "Setor Marista", "Setor Oeste", "Jardim Goiás", "Setor Sul", "Asa Sul", "Asa Norte",
    "Águas Claras", "Sudoeste", "Noroeste", "Lago Sul", "Lago Norte", "Guará", "Taguatinga",
]

# ---------------------------------------------------------------------------------------- baseline de código
# Palavras-chave por atributo (sem acento, minúsculas; só turnos do CLIENTE) — o que um dev escreveria em meia hora.
# Precedência no código: negação → `negado`; número novo diferente → `substituido`; "agora/preciso/tem que" →
# `substituido`; palavra de hipótese → `incerto`; senão `mantido`.
BASELINE_ATRIBUTO = {
    "orcamento": r"\bteto\b|or[c]amento|\bvalor\b|\bmil\b|r\$|\blimite\b|\bpagar\b|\bgastar\b|\baluguel\b|\bfaixa\b",
    "quartos": r"\bquartos?\b|\bdormit|\bfilh[oa]s?\b|\bbeb[e]\b",
    "vagas": r"\bvagas?\b|\bcarros?\b|\bgaragem\b|\bestacion",
    "bairro": r"\bbairro\b|\bregi[a]o\b|\bzona\b",
    "elevador": r"\belevador\b|\bescadas?\b|\bt[e]rreo\b|\bcadeira\b|\bmobilidade\b",
    "pet": r"\bpets?\b|\bcachorr|\bgat[oa]s?\b|\banimal|\bcaozinho\b",
    "mobilia": r"\bmobili|\bm[o]ve(l|is)\b",
    "andar_baixo": r"\bandar\b|\bt[e]rreo\b",
    "financiamento": r"\bfinanc|\b[a] vista\b|\bentrada\b|\bbanco\b",
    "prazo": r"\bprazo\b|\bmudan[c]a\b|\bmudar\b|\bentrega\b|\d{1,2}/\d{4}|\bcontrato\b",
}
BASELINE_NEGACAO = [r"n[a]o (preciso|precisa|precisamos|quero|queremos|vou|vamos|faz|faco|fazemos) mais",
                    r"n[a]o (faco|faz|fazemos) quest[a]o", r"tanto faz", r"com ou sem", r"pode tirar", r"nunca pedi",
                    r"n[a]o [e] (mais )?requisito", r"deixa de ser"]
BASELINE_NEGACAO_POR_ATRIBUTO = {"financiamento": [r"\b[a] vista\b"]}  # "pagar à vista" nega o financiamento, não o teto
BASELINE_MUDANCA = [r"\bagora\b", r"\bpreciso de\b", r"\bprecisamos de\b", r"\bvou precisar\b", r"\btem que ser\b",
                    r"\bno m[i]nimo\b", r"\bpassou a ser\b", r"\bmudou\b", r"\bsubiu\b", r"\bcaiu\b", r"\binclui",
                    r"\bpode ser\b", r"\bfechou\b"]
BASELINE_HIPOTESE = [r"\btalvez\b", r"\bse (eu|a gente|ele|ela|sair|der)\b", r"\bvamos ver\b", r"\bdepende\b",
                     r"\bainda n[a]o sei\b", r"\bdepois te falo\b", r"\bdeixa eu\b", r"\bquem sabe\b", r"\bpode ser que\b"]
