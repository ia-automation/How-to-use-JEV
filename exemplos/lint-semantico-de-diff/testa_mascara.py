"""Bateria da máscara de segredo e do teto do diff — roda sem chave e sem rede (`python testa_mascara.py`).

Por que existe (revisão do Codex, 2026-10-01): a máscara estava só no trecho da regra SEG; uma linha com
`console.log(` e um segredo saía inteira pelo trecho de LOG, e o diff ia INTEIRO ao Jev antes de a regex de
SEG rodar. Aqui cada caso põe um segredo num contexto diferente e a bateria prova três coisas:
  1. o state que iria ao Jev (`lint.pedido`) não contém o valor;
  2. nenhum trecho de `lint.compor` nem o comentário de CI contém o valor, venha o trecho pela regra que vier;
  3. diff acima do teto não gera pedido e sai `revisa` com motivo "diff grande" (e nada é truncado).
A resposta do Jev é um dublê (0,9 em tudo, para todo gatilho virar `viola` e o trecho aparecer no comentário):
o que se testa aqui é código nosso, não o modelo.

Os valores são montados em pedaços para este arquivo não carregar literal com cara de segredo (o validador do
repositório varre o pacote). Limite declarado: a máscara tem a recall da regex de SEG — segredo que a regex não
conhece (`"senha": "…"` como chave JSON, valor passado como argumento; LS-T064) passa pelas duas portas.
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import lint as L  # noqa: E402
import perguntas as P  # noqa: E402

REGRAS = [
    {"id": "r1", "tipo": "mecanica", "texto": P.CHAVES["SEG"] + "…"},
    {"id": "r2", "tipo": "mecanica", "texto": P.CHAVES["LOG"] + "…"},
    {"id": "r3", "tipo": "mecanica", "texto": P.CHAVES["TODO"] + "…"},
    {"id": "r4", "tipo": "mecanica", "texto": P.CHAVES["DROP"] + "…"},
    {"id": "r5", "tipo": "semantica", "texto": P.CHAVES["JSDOC"] + "…"},
    {"id": "r6", "tipo": "semantica", "texto": P.CHAVES["DESVIO"] + "…"},
    {"id": "r7", "tipo": "semantica", "texto": P.CHAVES["VALID"] + "…"},
    {"id": "r8", "tipo": "semantica", "texto": P.CHAVES["SQL"] + "…"},
]

# Valores falsos, montados em pedaços (prefixo + corpo): nenhum existe fora deste arquivo.
STRIPE = "sk_" + "live_" + "FAKE9x8w7v6u5t4s"
STRIPE_T = "sk_" + "test_" + "FAKE1a2b3c4d5e6f"
GITHUB = "ghp_" + "FAKEq1w2e3r4t5y6u7"
AWS = "AKIA" + "FAKE7Q2W9E4R6T1Y"
JWT = "eyJ" + "FAKEhbGciOiJIUzI1NiJ9" + "." + "FAKEeyJzdWIiOiIxMjM0NTY3ODkwIn0"
SENHA = "Fake" + "Senha#2026"
SEGREDO = "fake" + "-hmac-" + "segredo-42"

# (nome, caminho, linhas do diff, valores que não podem aparecer na saída)
CASOS = [
    ("LOG com chave na mesma linha", "src/pagamento.ts",
     [f"+  console.log('cobrando', '{STRIPE}');"], [STRIPE]),
    ("TODO sem ticket com token do GitHub", "src/sync.ts",
     [f"+// TODO trocar {GITHUB} por variável de ambiente"], [GITHUB]),
    ("DROP sem marcador com senha no comentário SQL", "drizzle/0042_limpa.sql",
     [f"+DROP TABLE leads_antigos; -- password = '{SENHA}'"], [SENHA]),
    ("gatilho JSDOC: função nova exportada com chave AWS no default", "src/s3.ts",
     [f"+export function assinar(chave = '{AWS}') {{", "+  return chave;", "+}"], [AWS]),
    ("gatilho DESVIO: supressão na linha do segredo", "src/auth.ts",
     [f"+const token = '{JWT}'; // eslint-disable-line no-secrets"], [JWT]),
    ("gatilho VALID: rota nova lendo req.body com segredo literal", "src/rotas/webhook.ts",
     [f"+router.post('/webhook', (req, res) => {{ const secret = '{SEGREDO}'; res.json(req.body); }});"], [SEGREDO]),
    ("gatilho SQL: senha dentro da query crua", "src/repo/usuarios.ts",
     [f"+  await db.execute(sql`ALTER USER app PASSWORD = '{SENHA}'`);"], [SENHA]),
    ("segredo só em linha de CONTEXTO (não é violação, mas não pode ir ao Jev)", "src/config.ts",
     [f" const api_key = '{STRIPE_T}';", "+export function lerConfig() {", "+  return api_key;", "+}"], [STRIPE_T]),
    ("segredo só em linha REMOVIDA", "src/config.ts",
     [f"-const senha = \"{SENHA}\";", "+const senha = process.env.SENHA_DO_BANCO;",
      "+// eslint-disable-next-line no-console", "+console.log('config lida');"], [SENHA]),
    ("Python: noqa na linha do segredo + cursor.execute", "app/db.py",
     [f"+SECRET = \"{SEGREDO}\"  # noqa: S105", "+cur.execute(\"SELECT 1\")"], [SEGREDO]),
    ("arquivo de teste: LOG isento, segredo não", "tests/pagamento.test.ts",
     [f"+  console.log('{GITHUB}');", f"+  const apikey = `{STRIPE_T}`;"], [GITHUB, STRIPE_T]),
    ("dois segredos na mesma linha, com FIXME e console.log", "scripts/carga.ts",
     [f"+console.log('{AWS}', '{STRIPE}'); // FIXME tirar daqui"], [AWS, STRIPE]),
    ("JWT em comentário de documentação acima de função nova", "src/doc.ts",
     [f"+/** exemplo: Authorization com {JWT} */", "+export async function chamar() {}", ], [JWT]),
]


def _diff(caminho: str, linhas: list[str]) -> str:
    cab = [f"diff --git a/{caminho} b/{caminho}", f"--- a/{caminho}", f"+++ b/{caminho}", "@@ -1,3 +1,6 @@"]
    return "\n".join(cab + linhas)


def _resposta_duble(questions: dict) -> dict:
    return {"model": "duble", "answers": {k: {"type": "noul", "noul": 0.9} for k in questions}}


def main() -> None:
    falhas, trechos_vistos = [], 0
    for nome, caminho, linhas, valores in CASOS:
        caso = {"id": nome, "regras": REGRAS, "diff": _diff(caminho, linhas)}
        assert any(v in caso["diff"] for v in valores), f"caso mal montado: {nome}"
        state, questions = L.pedido(caso)
        saida = L.compor(caso, _resposta_duble(questions), desenho="valvula")  # valvula: todo gatilho vira `viola`
        portas = {"state enviado ao Jev": state["diff"], "comentário de CI": saida["comentario"]}
        for r in saida["regras"]:
            trechos_vistos += len(r["trechos"])
            portas[f"trechos de {r['id']} {r['chave']}"] = "\n".join(r["trechos"])
        for porta, texto in portas.items():
            for v in valores:
                if v in texto:
                    falhas.append(f"{nome}: valor bruto em {porta}")
            if P.SEG_RE.search(texto):
                falhas.append(f"{nome}: a regex de SEG ainda casa em {porta}")
        # a máscara não pode comer o diff: mesmas linhas, mesmos prefixos (+/-/contexto)
        antes, depois = caso["diff"].split("\n"), state["diff"].split("\n")
        if len(antes) != len(depois) or any(a[:1] != d[:1] for a, d in zip(antes, depois)):
            falhas.append(f"{nome}: a máscara mudou a estrutura do diff")

    # teto: diff grande não gera pedido, não exige resposta, sai `revisa` com motivo e as mecânicas rodam igual
    for rotulo, corpo in (("linhas", [f"+const linha{i} = {i};" for i in range(P.TETO_LINHAS + 1)]),
                          ("caracteres", ["+const x = '" + "a" * (P.TETO_CARACTERES + 1) + "';"])):
        caso = {"id": f"teto por {rotulo}", "regras": REGRAS,
                "diff": _diff("src/grande.ts", corpo + [f"+console.log('{STRIPE}');"])}
        if L.pedido(caso) is not None:
            falhas.append(f"teto por {rotulo}: gerou pedido ao Jev")
        saida = L.compor(caso, None)
        sem = [r for r in saida["regras"] if r["tipo"] == "semantica"]
        if not saida["diff_grande"] or any(r["veredito"] != "revisa" or r.get("motivo") != P.MOTIVO_DIFF_GRANDE for r in sem):
            falhas.append(f"teto por {rotulo}: semântica não saiu `revisa` com motivo")
        mec = {r["chave"]: r["veredito"] for r in saida["regras"] if r["tipo"] == "mecanica"}
        if mec.get("SEG") != "viola" or mec.get("LOG") != "viola":
            falhas.append(f"teto por {rotulo}: mecânica deixou de rodar")
        if STRIPE in saida["comentario"] or P.MOTIVO_DIFF_GRANDE not in saida["comentario"]:
            falhas.append(f"teto por {rotulo}: comentário com valor bruto ou sem o motivo")
    # dentro do teto e sem resposta continua sendo ERRO (ausência de resposta nunca vira `ok` nem `revisa`)
    try:
        L.compor({"id": "sem resposta", "regras": REGRAS, "diff": _diff("src/a.ts", ["+export function f() {}"])}, None)
        falhas.append("diff dentro do teto sem resposta do Jev não levantou erro")
    except ValueError:
        pass

    if falhas:
        sys.exit("FALHOU:\n  " + "\n  ".join(falhas))
    print(f"ok: {len(CASOS)} contextos de segredo, {trechos_vistos} trechos conferidos, 0 valor bruto no state, "
          f"nos trechos ou no comentário; teto ({P.TETO_LINHAS} linhas / {P.TETO_CARACTERES} caracteres) conferido")


if __name__ == "__main__":
    main()
