"""Perguntas, faixas e política do imóvel duplicado — o ÚNICO arquivo que um humano precisa revisar.

Um PAR de anúncios (dois portais/corretores, pt-BR) vira UM state `{"a", "b", "numeric_checks"}` e UMA requisição
ao Jev. O código calcula o que é número (bairro/cidade, quartos, vagas, área ±3%, preço ±5%) e entrega como fato
pronto; o Jev julga só o que é TEXTO; `duplicado.py` compõe a ação (`unir` / `revisar` / `manter_separados`) com os
números daqui. Mudar política = editar número, sem chamar a API de novo. Nada é apagado: `unir` é uma PROPOSTA.

Desenho (regras de rotulagem em dados/LEIA-ME.md; receita-irmã: conhecimento/receitas/alinhamento-de-entidades.md):
- `same_listing` (Score, 3 níveis: diferentes / não dá para saber / a mesma unidade) — a leitura inteira do par,
  como na receita. Aqui é SEGUNDA leitura do lado caro: só pode tirar um `unir`, nunca criar um.
- Nouls atômicos (absolutos, mesma requisição — pergunta extra ≈ 20–100 tokens):
  `same_building_or_street` — os dois citam o mesmo prédio ou a mesma rua (diagnóstico; mede `mesmo_endereco`);
  `address_conflict`        — citam prédios ou ruas DIFERENTES (endereço ausente não é endereço diferente);
  `layout_contradiction`    — um diz que TEM sacada/varanda/dependência e o outro diz que NÃO tem (planta);
  `fixed_contradiction`     — detalhe permanente incompatível: vista, face/sol, frente × fundos, lareira, pé-direito;
  `state_contradiction`     — estado/mobília opostos (mobiliado × vazio, reformado × original): não prova unidade
                              diferente nem a mesma → humano. O "só" de "só o estado difere" é do CÓDIGO
                              (estado alto E contradição fixa baixa): uma condição por pergunta;
  `shared_distinctive_details` — os dois citam o MESMO detalhe da unidade (o sinal forte que autoriza `unir`).
- Número nenhum é pedido ao Jev (limite #2): área, preço, quartos e vagas NÃO vão no state como valor, só como
  fato calculado em `numeric_checks`; o texto do anúncio pode citar "68 m²", e o `false` das perguntas diz que
  diferença de área ou preço não é contradição.

Perguntas em inglês sobre anúncios em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%).

Afinação (só no ajuste, 2026-10-01, duas passadas de 36 requisições — 4 dos 40 pares o código decide sem chamada):
- 1ª passada (as perguntas deste arquivo): ação 40/40 com os Nouls; vetos reais 0,86–0,98 e ≤ 0,16 nos pares sem
  aquele veto; sinal forte ≥ 0,92 nas 20 duplicatas e ≤ 0,15 nos 3 "sem detalhe distintivo"; Score 1,83–1,99 nas
  duplicatas, 0,01–0,24 nos diferentes e 1,24–1,57 nos 4 indecidíveis (dois ACIMA do corte de arredondamento 1,5).
- 2ª passada: tentei escrever nas duas perguntas de endereço o caso "um cita só o prédio, o outro só a rua → nada
  a comparar" (regra do LEIA-ME que o ajuste não exercita). Nenhuma decisão mudou, mas `address_conflict` caiu de
  0,95 para 0,81 num par de ruas diferentes (ID-A002, "Avenida…" × "Rua…"). Mudança sem caso que a sustente e com
  efeito colateral medido → REVERTIDA; vale a redação da 1ª passada. Fica como limite conhecido no README.
- Limiares: o ajuste não discrimina dentro dos vãos (todos largos); ficam os de partida, com dois ajustes
  explicados junto das constantes (`sim` dos vetos 0,7; Score mínimo para unir 1,7).
Nenhuma pergunta foi alargada para consertar um caso.
"""

NIVEIS = [
    "They advertise different apartments: they name different buildings or different streets, or the "
    "descriptions state incompatible permanent features of the unit (one has a park view and the other faces the "
    "back with no view; north face versus south face; fireplace versus no fireplace; double-height versus "
    "standard ceiling; balcony versus no balcony).",
    "It cannot be told: they could be the same unit or an identical neighbouring unit of the same building. "
    "Neither description gives details of the unit that match, or one listing names no building or street and "
    "both are generic, or one says the unit is furnished and the other says it is empty.",
    "They advertise one and the same apartment unit: the same building or street (or one of them omits the "
    "address) and the details of the unit that are described coincide (same view, same sun orientation, same "
    "fireplace, same floor material, same balcony features). Different wording, a different asking price, an area "
    "gap that `numeric_checks` says is explained by a second area figure, or furniture mentioned in only one "
    "listing do not make them different.",
]


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"a": {"title", "description"}, "b": {...}, "numeric_checks": {...}} — só pares que o código já viu com
# mesmo bairro/cidade, mesmos quartos e mesmas vagas (o resto o código decide sem chamada).
PERGUNTAS = {
    "same_listing": {
        "type": "score",
        "instructions": "`a` and `b` are two real-estate listings (Brazilian Portuguese) for apartments in the same "
                        "neighborhood, with the same number of bedrooms and parking spaces (checked by code, see "
                        "`numeric_checks`). Judging by what their titles and descriptions say, are they listings "
                        "of one and the same apartment unit?",
        "criteria": NIVEIS,
    },
    "same_building_or_street": _noul(
        "Listings `a` and `b` (title and description) both say where the apartment is, and it is the same place: "
        "the same building or condominium name, or, when they do not both name a building, the same street.",
        "Both name the same building or condominium (wording may differ), or at least one of them names no "
        "building and both name the same street.",
        "They name different buildings or condominiums (even on the same street), or different streets; or one "
        "of the two listings names neither a building nor a street, so there is nothing to compare. The "
        "neighborhood or the city alone does not count as an address.",
    ),
    "address_conflict": _noul(
        "Listings `a` and `b` (title and description) name different places: different building or condominium "
        "names, or different streets.",
        "Both name a building or condominium and the names differ (even if the street is the same); or they do "
        "not both name a building, both name a street, and the streets differ.",
        "They name the same building or the same street; or one of the listings names neither a building nor a "
        "street (a missing address is not a different address).",
    ),
    "layout_contradiction": _noul(
        "One of the two descriptions says the apartment HAS a structural room or space, such as a balcony or "
        "veranda ('sacada', 'varanda') or a maid's room ('dependência'), and the other description says the "
        "apartment does NOT have it.",
        "One states the space exists and the other explicitly states it does not: 'sala com sacada' versus "
        "'sala sem sacada'; 'varanda' versus 'sem varanda'.",
        "There are no such opposite statements: both have it, neither mentions it, or only one mentions it (an "
        "omission is not a contradiction). A different kitchen style (open or closed), flooring, cabinets, "
        "barbecue, furniture or renovation is not a structural room.",
    ),
    "fixed_contradiction": _noul(
        "The descriptions of `a` and `b` state incompatible permanent features of the apartment unit itself.",
        "They make opposite statements about a feature that renovation or furniture cannot change: the view "
        "(park or mountain view versus no view or an internal courtyard; pool view versus facing the street), the "
        "sun orientation or face (north versus south; morning sun versus no direct sun), front versus back "
        "position, fireplace versus no fireplace, double-height versus standard ceiling.",
        "No permanent feature is contradicted: the descriptions agree; or a feature appears in only one of them "
        "(an omission is not a contradiction); or they differ only in wording, price, area figures, or in the "
        "condition of the unit, such as renovated versus original, furnished versus empty, with versus without "
        "cabinets, kitchen style or flooring.",
    ),
    "state_contradiction": _noul(
        "The descriptions of `a` and `b` make opposite statements about the current condition or contents of "
        "the apartment, something that can change over time in the same unit.",
        "One says it is delivered furnished and the other says it is delivered empty, without furniture; one "
        "says renovated and the other says original condition or needing renovation; one says the kitchen has "
        "cabinets and the other says it has none; open kitchen versus closed kitchen; different flooring in the "
        "same room.",
        "There are no opposite statements about condition or contents: both agree, or furniture, renovation, "
        "cabinets or flooring are mentioned in only one of the descriptions (an omission is not a contradiction).",
    ),
    "shared_distinctive_details": _noul(
        "Both descriptions mention the same detail of the apartment unit itself, beyond the address, the number "
        "of bedrooms, suites and parking spaces, the area, the price and the building's common areas.",
        "At least one detail of the unit appears in both descriptions: a balcony or its type (gourmet, glazed, "
        "with barbecue), the same view, the same sun orientation, a fireplace, a double-height ceiling, the same "
        "floor material, the kitchen type or its cabinets, a closet, custom furniture, acoustic windows, air "
        "conditioning, a recent renovation.",
        "They share only generic facts: neighborhood, building or street, bedrooms, suites, parking spaces, "
        "area, price, doorman, elevator, pool, gym, 'good location', 'paperwork in order', 'living room and "
        "kitchen'; or at least one of the descriptions gives no detail of the unit beyond those.",
    ),
}

NOULS = [q for q, p in PERGUNTAS.items() if p["type"] == "noul"]
SCORE = "same_listing"

# ---------------------------------------------------------------------------------------- fatos do código
# Tolerâncias do LEIA-ME (são do CÓDIGO; o run.py confere 100% contra `sinais.mesma_area` / `sinais.mesmo_preco`).
TOLERANCIA_AREA = 0.03
TOLERANCIA_PRECO = 0.05

# ---------------------------------------------------------------------------------------- política
# Noul em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida. Partida 0,2–0,8 (NÚCLEO §6).
# Política ASSIMÉTRICA: unir errado apaga um imóvel; não unir só deixa duplicata. Por isso:
#   - os três VETOS (endereço em conflito, planta, detalhe fixo) com `sim` → `manter_separados`; em DÚVIDA →
#     `revisar`; só com os três em `nao` o par pode ser unido;
#   - `unir` exige ainda estado sem contradição, área conciliada (código) e o sinal forte
#     (`shared_distinctive_details` sim), confirmado pelo Score;
#   - tudo que não fecha nem para um lado nem para o outro → `revisar` (é onde o gabarito `null` tem de cair).
# Vetos: no ajuste os reais ficaram em 0,86–0,98 (detalhe fixo: 0,86–0,90, n = 4) e os pares sem aquele veto em
# ≤ 0,16. O `sim` de partida (0,8) ficava a 0,06 do grupo dos reais — a mesma ordem da variação entre chamadas
# idênticas (p95 ~0,05, NÚCLEO §6) — então desce para 0,7. O `nao` (o lado caro: abaixo dele o par pode ser unido)
# fica em 0,2: as duplicatas do ajuste têm os três vetos ≤ 0,08.
FAIXA = {
    "address_conflict": (0.2, 0.7),
    "layout_contradiction": (0.2, 0.7),
    "fixed_contradiction": (0.2, 0.7),
    "state_contradiction": (0.2, 0.8),         # só o `nao` é consumido: acima dele o par não é unido
    "shared_distinctive_details": (0.2, 0.8),  # só o `sim` é consumido: abaixo dele o par não é unido
    "same_building_or_street": (0.2, 0.8),     # diagnóstico; na decisão só segura um veto de endereço (`sim`)
}
VETOS = ["address_conflict", "layout_contradiction", "fixed_contradiction"]
# Score. `SCORE_ARREDONDA` = cortes do arredondamento da receita (0,5 e 1,5), usados SÓ na variante "só Score"
# (medição). Na política o Score é segunda leitura da união: no ajuste as duplicatas deram 1,83–1,99 e os
# indecidíveis 1,24–1,57 — o corte de arredondamento (1,5) deixaria passar dois indecidíveis; o mínimo para unir
# fica no vão, em 1,7. No ajuste o Score não mudou nenhuma decisão dos Nouls (fica ligado por desenho, como
# segunda leitura do erro caro; o relatório mede a política com e sem ele).
SCORE_ARREDONDA = (0.5, 1.5)
SCORE_UNIR_MIN = 1.7
USAR_SCORE = True        # False = política só com Nouls
# Faixa validada: descrições dos dados têm até ~350 caracteres. Acima do teto o par NÃO vai ao Jev: `revisar`,
# motivo "anúncio longo" (família do achado 6 do imovel-errado). Não é limiar afinado.
TETO_CARACTERES = 4000

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, antes de abrir `dados/teste.json`. Denominadores pela tabela do LEIA-ME (teste: 80 pares =
# 40 duplicatas, 32 diferentes, 8 indecidíveis). Baseline no ajuste: 0,550.
CRITERIO_CONTINUAR = {
    "onde": "no teste (80 pares: 40 duplicatas, 32 diferentes, 8 indecidíveis), com a política acima",
    "1_diferente_unido": "par de imóveis diferentes (gabarito false) que saiu `unir` = 0",
    "2_indecidivel_unido": "par indecidível (gabarito null) que saiu `unir` ≤ 1 (de 8)",
    "3_duplicata_separada": "duplicata real (gabarito true) que saiu `manter_separados` ≤ 5% (≤ 2 de 40)",
    "4_acerto_acao": "ação (3 classes) ≥ baseline + 0,15",
    "secundario_nao_decide": "todo nulo → `revisar`; revisou sem necessidade ≤ 15% dos decidíveis; sinais numéricos do código = 100% (senão é bug)",
    "se_falhar": "1 ou 2 falhando = não serve para propor união sem humano conferir cada uma; 3 falhando = os vetos separam demais; 4 falhando = a regra de código basta",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"diferente_unido_max": 0, "indecidivel_unido_max": 1, "duplicata_separada_max_fracao": 0.05,
                "margem_acao": 0.15, "revisou_sem_necessidade_max": 0.15},
}
