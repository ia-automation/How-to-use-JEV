/**
 * Roda a busca nos conjuntos rotulados e gera `resultados.md` sozinho.
 *
 *   npm start               ajuste + teste numa execução; recusa se perguntas.ts/busca.ts mudaram desde o congelamento
 *   npm run ajuste          afinação (só o ajuste; o teste nem é lido)
 *   npm run congelar        roda o ajuste e grava o hash de perguntas.ts e busca.ts em congelamento.json
 *   npm run rascunho        consultas do construtor: só a leitura da consulta (encanamento, não é métrica)
 *   JEV_MODO=gravado npm start   reproduz tudo do cache/, sem chave
 */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { Jev, MODELO, PRECO_US_POR_MILHAO_ENTRADA } from "./jev.js";
import { BAIRROS, CIDADES, CONCORRENCIA, TIPOS } from "./perguntas.js";
import { bm25, falhas, julgarEOrdenar, lerConsulta, type Anuncio, type Filtro, type Julgado, type LeituraConsulta } from "./busca.js";

const AQUI = resolve(import.meta.dirname, "..");
const DADOS = join(AQUI, "dados");
const CONGELAMENTO = join(AQUI, "congelamento.json");
const ler = (arq: string) => JSON.parse(readFileSync(join(DADOS, arq), "utf8"));

interface Consulta { id: string; consulta: string; relevancia: Record<string, number> }
const SISTEMAS = ["jev", "filtro_so", "palavras", "filtro_palavras", "teto"] as const;
type Sistema = (typeof SISTEMAS)[number];
const DESCRICAO_SISTEMA: Record<Sistema, string> = {
  jev: "filtro (Jev lê a consulta) + ranking pelo ganho esperado (Jev lê cada anúncio)",
  filtro_so: "mesmo filtro, ordem do catálogo (sem ranking)",
  palavras: "linha de base SEM Jev: BM25 sobre título+descrição+tipo+bairro+cidade, catálogo inteiro, sem filtro",
  filtro_palavras: "mesmo filtro, ranking por BM25 na descrição (isola o valor do Jev no anúncio)",
  teto: "mesmo filtro, recuperados na ordem do gabarito (só a perda da recuperação limita)",
};

// ---------------------------------------------------------------- métricas

const dcg = (rels: number[], k: number) => rels.slice(0, k).reduce((s, r, i) => s + (2 ** r - 1) / Math.log2(i + 2), 0);
/** NDCG@k com o ideal tirado do GABARITO INTEIRO (não da lista devolvida): anúncio perdido na recuperação pesa. */
function ndcg(ordem: string[], rel: Record<string, number>, k = 10): number {
  const ideal = dcg(Object.values(rel).sort((a, b) => b - a), k);
  return ideal ? dcg(ordem.map((id) => rel[id] ?? 0), k) / ideal : 0;
}
const precisao = (ordem: string[], rel: Record<string, number>, k = 5) => ordem.slice(0, k).filter((id) => (rel[id] ?? 0) >= 1).length / k;
const conta = (ids: string[], rel: Record<string, number>, f: (r: number) => boolean) => ids.filter((id) => f(rel[id] ?? 0)).length;
const media = (xs: number[]) => xs.reduce((s, x) => s + x, 0) / (xs.length || 1);
const quantil = (xs: number[], q: number) => { const s = [...xs].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };

/** Latência por consulta: leitura da consulta + fila de CONCORRENCIA vagas com os ms MEDIDOS de cada anúncio. */
function latenciaConsulta(msLeitura: number, msAnuncios: number[]): number {
  const vagas = new Array(CONCORRENCIA).fill(0);
  for (const ms of msAnuncios) { const i = vagas.indexOf(Math.min(...vagas)); vagas[i] += ms; }
  return msLeitura + Math.max(0, ...vagas);
}

// ---------------------------------------------------------------- execução

interface Resultado {
  c: Consulta; leitura: LeituraConsulta; recuperados: Anuncio[]; julgados: Julgado[];
  ordens: Record<Sistema, string[]>; perdidos: { id: string; rel: number; causas: string[] }[];
  requisicoes: number; tokens: number; latencia: number;
}

async function rodarConjunto(consultas: Consulta[], anuncios: Anuncio[]): Promise<{ res: Resultado[]; jev: Jev }> {
  const jev = new Jev(join(AQUI, "cache")); // uma instância por conjunto: custo e latência separados
  const res: Resultado[] = [];
  for (const c of consultas) {
    const antes = jev.chamadas.length;
    const leitura = await lerConsulta(jev, c.consulta);
    const recuperados = anuncios.filter((a) => falhas(a, leitura.filtro).length === 0);
    const julgados = await julgarEOrdenar(jev, recuperados, leitura.pedidos);
    const chamadas = jev.chamadas.slice(antes);
    const kw = bm25(anuncios.map((a) => ({ id: a.id, texto: `${a.titulo} ${a.descricao} ${a.tipo} ${a.bairro} ${a.cidade}` })), c.consulta);
    const kwDesc = bm25(anuncios.map((a) => ({ id: a.id, texto: a.descricao })), c.consulta);
    const ids = recuperados.map((a) => a.id);
    const porPontos = (m: Map<string, number>) => (x: string, y: string) => m.get(y)! - m.get(x)! || x.localeCompare(y);
    res.push({
      c, leitura, recuperados, julgados,
      ordens: {
        jev: julgados.map((j) => j.id),
        filtro_so: ids,
        palavras: anuncios.map((a) => a.id).sort(porPontos(kw)),
        filtro_palavras: [...ids].sort(porPontos(kwDesc)),
        teto: [...ids].sort((x, y) => (c.relevancia[y] ?? 0) - (c.relevancia[x] ?? 0) || x.localeCompare(y)),
      },
      perdidos: Object.entries(c.relevancia).filter(([id]) => !ids.includes(id))
        .map(([id, rel]) => ({ id, rel, causas: falhas(anuncios.find((a) => a.id === id)!, leitura.filtro) })),
      requisicoes: chamadas.length,
      tokens: chamadas.reduce((s, x) => s + x.input_tokens, 0),
      latencia: latenciaConsulta(chamadas[0].ms, chamadas.slice(1).map((x) => x.ms)),
    });
  }
  return { res, jev };
}

// ---------------------------------------------------------------- relatório

const f3 = (x: number) => (Number.isFinite(x) ? x.toFixed(3) : "—");
const pct = (a: number, b: number) => `${a}/${b} (${b ? ((100 * a) / b).toFixed(0) : "—"}%)`;
function tabela(linhas: Record<string, string | number>[]): string {
  if (!linhas.length) return "_(vazio)_\n";
  const cols = Object.keys(linhas[0]);
  return `| ${cols.join(" | ")} |\n|${"---|".repeat(cols.length)}\n` +
    linhas.map((l) => `| ${cols.map((k) => (typeof l[k] === "number" ? f3(l[k] as number) : l[k])).join(" | ")} |`).join("\n") + "\n";
}
function textoFiltro(f: Filtro): string {
  const p = [f.tipos?.join("/") ?? "qualquer tipo", f.cidades?.join("/") ?? "qualquer cidade"];
  if (f.bairros) p.push(f.bairros.join("/"));
  if (f.quartosMin) p.push(`≥${f.quartosMin} quartos`);
  if (f.vagasMin) p.push(`≥${f.vagasMin} vagas`);
  if (f.precoMin !== null) p.push(`≥ R$ ${f.precoMin / 1000} mil`);
  if (f.precoMax !== null) p.push(`≤ R$ ${f.precoMax / 1000} mil`);
  return p.join(" · ");
}

function resumoConjunto(nome: string, res: Resultado[], jev: Jev) {
  const soma = (f: (r: Resultado) => number) => res.reduce((s, r) => s + f(r), 0);
  const rel1 = soma((r) => conta(Object.keys(r.c.relevancia), r.c.relevancia, (x) => x >= 1));
  const rel3 = soma((r) => conta(Object.keys(r.c.relevancia), r.c.relevancia, (x) => x === 3));
  const rec1 = soma((r) => conta(r.recuperados.map((a) => a.id), r.c.relevancia, (x) => x >= 1));
  const rec3 = soma((r) => conta(r.recuperados.map((a) => a.id), r.c.relevancia, (x) => x === 3));
  const teto1 = soma((r) => Math.min(10, conta(Object.keys(r.c.relevancia), r.c.relevancia, (x) => x >= 1)));
  const teto3 = soma((r) => Math.min(10, conta(Object.keys(r.c.relevancia), r.c.relevancia, (x) => x === 3)));
  const top = (s: Sistema, f: (x: number) => boolean) => soma((r) => conta(r.ordens[s].slice(0, 10), r.c.relevancia, f));
  const pares = res.flatMap((r) => r.julgados.map((j) => [j.relPrevista, r.c.relevancia[j.id] ?? 0]));
  const custo = jev.resumo();
  const lat = res.map((r) => r.latencia);
  const pedidosP = res.flatMap((r) => r.leitura.pedidos.map((c) => r.leitura.probPedido[c]));
  const naoPedidosP = res.flatMap((r) => Object.entries(r.leitura.probPedido).filter(([c]) => !r.leitura.pedidos.includes(c as never)).map(([, p]) => p));
  const topos = res.flatMap((r) => r.julgados.flatMap((j) => Object.values(j.leituras).map((t) => Math.max(t!.afirma, t!.nega, t!.omite))));
  return {
    nome, n: res.length, custo,
    ndcg: Object.fromEntries(SISTEMAS.map((s) => [s, media(res.map((r) => ndcg(r.ordens[s], r.c.relevancia)))])) as Record<Sistema, number>,
    p5: Object.fromEntries(SISTEMAS.map((s) => [s, media(res.map((r) => precisao(r.ordens[s], r.c.relevancia)))])) as Record<Sistema, number>,
    rel1, rel3, rec1, rec3, teto1, teto3,
    top1: Object.fromEntries(SISTEMAS.map((s) => [s, top(s, (x) => x >= 1)])) as Record<Sistema, number>,
    top3: Object.fromEntries(SISTEMAS.map((s) => [s, top(s, (x) => x === 3)])) as Record<Sistema, number>,
    acertoRel: pares.filter(([p, g]) => p === g).length, nPares: pares.length,
    matriz: [0, 1, 2, 3].map((g) => [0, 1, 2, 3].map((p) => pares.filter(([pp, gg]) => gg === g && pp === p).length)),
    reqPorConsulta: custo.requisicoes / res.length,
    tokensPorConsulta: custo.input_tokens / res.length,
    usPorConsulta: custo.custo_us / res.length,
    latP50: quantil(lat, 0.5), latP95: quantil(lat, 0.95),
    margem: {
      minPedido: Math.min(...pedidosP), maxNaoPedido: Math.max(...naoPedidosP),
      minConfDura: Math.min(...res.flatMap((r) => Object.values(r.leitura.confianca))),
      toposAbaixo09: topos.filter((x) => x < 0.9).length, nLeituras: topos.length, minTopo: Math.min(...topos),
    },
  };
}
type Resumo = ReturnType<typeof resumoConjunto>;

function secaoConjunto(nome: string, dados: { versao: string; autor: string }, res: Resultado[], rs: Resumo, anuncios: Anuncio[]): string {
  const out: string[] = [`## Conjunto \`${nome}\` — ${res.length} consultas (arquivo versão ${dados.versao}, autor ${dados.autor})\n`];
  out.push("### Por consulta\n");
  out.push(tabela(res.map((r) => {
    const rel = r.c.relevancia;
    const n1 = conta(Object.keys(rel), rel, (x) => x >= 1), n3 = conta(Object.keys(rel), rel, (x) => x === 3);
    return {
      consulta: r.c.id, recuperados: String(r.recuperados.length), requisicoes: String(r.requisicoes),
      "rel≥1 recuperados": `${n1 - r.perdidos.length}/${n1}`,
      "rel=3 recuperados": `${n3 - r.perdidos.filter((p) => p.rel === 3).length}/${n3}`,
      "NDCG@10 jev": ndcg(r.ordens.jev, rel), "filtro_so": ndcg(r.ordens.filtro_so, rel),
      "palavras": ndcg(r.ordens.palavras, rel), "filtro_palavras": ndcg(r.ordens.filtro_palavras, rel),
      "teto": ndcg(r.ordens.teto, rel), "P@5 jev": precisao(r.ordens.jev, rel),
      "ms (simulado)": String(r.latencia),
    };
  })));
  out.push("\n### Leitura da consulta (Jev) → filtro (código)\n");
  out.push("Critério pedido = Noul ≥ limiar (valor entre parênteses). `conf mín` = menor confiança entre as 7 Choices duras.\n");
  out.push(tabela(res.map((r) => ({
    consulta: r.c.id, texto: r.c.consulta, filtro: textoFiltro(r.leitura.filtro),
    pedidos: r.leitura.pedidos.map((c) => `${c} (${r.leitura.probPedido[c].toFixed(2)})`).join(", ") || "—",
    "quase pedidos (0,2–0,5)": Object.entries(r.leitura.probPedido).filter(([, p]) => p >= 0.2 && p < 0.5).map(([c, p]) => `${c} (${p.toFixed(2)})`).join(", ") || "—",
    "conf mín": Math.min(...Object.values(r.leitura.confianca)),
  }))));
  const perdidos = res.flatMap((r) => r.perdidos.map((p) => ({ consulta: r.c.id, anuncio: p.id, rel: String(p.rel), "restrição que descartou": p.causas.join(", ") })));
  out.push(`\n### Perda da recuperação (relevantes descartados pelo filtro ANTES do Jev): ${perdidos.length}\n`);
  if (perdidos.length) out.push(tabela(perdidos));
  const erros = res.flatMap((r) => r.julgados.filter((j) => j.relPrevista !== (r.c.relevancia[j.id] ?? 0)).map((j) => ({
    consulta: r.c.id, anuncio: j.id, gabarito: String(r.c.relevancia[j.id] ?? 0), previsto: String(j.relPrevista),
    posicao: String(r.ordens.jev.indexOf(j.id) + 1),
    "leitura do Jev (afirma/nega/omite)": Object.entries(j.leituras).map(([c, t]) => `${c} ${t!.afirma.toFixed(2)}/${t!.nega.toFixed(2)}/${t!.omite.toFixed(2)}`).join("; "),
  })));
  out.push(`\n### Leitura do anúncio: relevância prevista ≠ gabarito (${erros.length} de ${rs.nPares} recuperados)\n`);
  out.push("A ordem usa o ganho esperado, não a prevista; a prevista (argmax) mede a leitura. Recortes da descrição ao lado.\n");
  if (erros.length) out.push(tabela(erros.slice(0, 25).map((e) => ({ ...e, descricao: anuncios.find((a) => a.id === e.anuncio)!.descricao }))));
  return out.join("\n");
}

function relatorio(resumos: Resumo[], secoes: string[], linhaCongelada: string): string {
  const modo = process.env.JEV_MODO || "auto";
  const hoje = new Date().toISOString().slice(0, 10);
  const o: string[] = [
    "# Resultados — busca-imoveis\n",
    `Gerado por \`src/run.ts\` em ${hoje} (modo \`${modo}\`). Modelo pedido \`${MODELO}\`; preço US$ ${PRECO_US_POR_MILHAO_ENTRADA} por milhão de tokens de entrada. Perguntas, limiares e pesos: \`src/perguntas.ts\`.\n`,
    `${linhaCongelada}\n`,
    "> **Demonstração de mecanismo, não desempenho em portal real.** Catálogo sintético e controlado (Codex): cada anúncio tem 8 fatos ternários " +
      "(afirma / nega / omite) escritos com um de três enunciados fixos; o gabarito foi DERIVADO desses fatos de autoria pela escala congelada, " +
      "não anotado por humano sobre anúncios reais. O teste mede consultas novas sobre o MESMO catálogo.\n",
    "## Lado a lado\n",
    "Sistemas: " + SISTEMAS.map((s) => `\`${s}\` = ${DESCRICAO_SISTEMA[s]}`).join("; ") + ".\n",
    "**Qualidade do ranking (média por consulta)**\n",
    tabela(resumos.flatMap((r) => [
      { conjunto: r.nome, métrica: "NDCG@10", ...Object.fromEntries(SISTEMAS.map((s) => [s, r.ndcg[s]])) },
      { conjunto: r.nome, métrica: "P@5 (rel≥1)", ...Object.fromEntries(SISTEMAS.map((s) => [s, r.p5[s]])) },
    ])),
    "\n**Recuperação (o filtro, antes do Jev ler anúncio) e ranking (top-10)** — somas sobre as consultas. " +
      "`teto top-10` = Σ min(10, relevantes da consulta).\n",
    tabela(resumos.map((r) => ({
      conjunto: r.nome, n: String(r.n),
      "rel≥1 após recuperação": pct(r.rec1, r.rel1), "rel=3 após recuperação": pct(r.rec3, r.rel3),
      "PERDA da recuperação rel≥1 · rel=3": `${r.rel1 - r.rec1} · ${r.rel3 - r.rec3}`,
      "rel≥1 no top-10 jev · filtro_palavras · palavras": `${pct(r.top1.jev, r.teto1)} · ${r.top1.filtro_palavras} · ${r.top1.palavras}`,
      "rel=3 no top-10 jev · filtro_palavras · palavras": `${pct(r.top3.jev, r.teto3)} · ${r.top3.filtro_palavras} · ${r.top3.palavras}`,
    }))),
    "\n**Leitura do anúncio (relevância prevista = argmax da distribuição, entre os recuperados)** — matriz linhas = gabarito 0..3, colunas = previsto 0..3\n",
    tabela(resumos.map((r) => ({
      conjunto: r.nome, "acerto da relevância prevista": pct(r.acertoRel, r.nPares),
      matriz: r.matriz.map((l, g) => `${g}: ${l.join("/")}`).join(" · "),
    }))),
    "\n**Margem das leituras** — quão longe dos limiares tudo caiu. Limiar que nenhuma leitura chegou perto de cruzar NÃO foi calibrado.\n",
    tabela(resumos.map((r) => ({
      conjunto: r.nome,
      "consulta: menor Noul pedido · maior Noul não pedido (limiar 0,5)": `${r.margem.minPedido.toFixed(2)} · ${r.margem.maxNaoPedido.toFixed(2)}`,
      "consulta: menor confiança das Choices duras": r.margem.minConfDura,
      "anúncio: leituras ternárias com prob. máxima < 0,9": `${r.margem.toposAbaixo09}/${r.margem.nLeituras}`,
      "anúncio: menor prob. máxima": r.margem.minTopo,
    }))),
    "\n**Custo e latência** (latência por requisição = medida na chamada real, 8 em paralelo; por consulta = leitura + fila de 8 vagas com os ms medidos)\n",
    tabela(resumos.map((r) => ({
      conjunto: r.nome, "requisições/consulta": r.reqPorConsulta.toFixed(1), "tokens/consulta": Math.round(r.tokensPorConsulta).toString(),
      "US$/consulta": r.usPorConsulta.toFixed(6), "US$/1000 consultas": (1000 * r.usPorConsulta).toFixed(3),
      "p50/p95 por requisição (ms)": `${r.custo.p50_ms} / ${r.custo.p95_ms}`, "p50/p95 por consulta (ms)": `${r.latP50} / ${r.latP95}`,
      "requisições (do cache)": `${r.custo.requisicoes} (${r.custo.do_cache})`, "retentativas do SDK nesta execução": String(r.custo.retentativas),
      modelo: r.custo.modelos.join(", "),
    }))),
    "",
    ...secoes,
  ];
  return o.join("\n");
}

// ---------------------------------------------------------------- congelamento e modos

const hashes = () => Object.fromEntries(["perguntas.ts", "busca.ts"].map((n) =>
  [n, createHash("sha256").update(readFileSync(join(AQUI, "src", n))).digest("hex").slice(0, 16)]));

const RASCUNHO = [ // escritas pelo construtor para ver o encanamento e a grade de preço; NÃO são métrica
  "Apê até 620 mil com 2 dorms em Cidade Aurora",
  "Casa ou sobrado em Cidade Horizonte, orçamento de meio milhão, 3 quartos",
  "Entre 400 e 550 mil, qualquer tipo, precisa ter jardim e não pode ser barulhento",
  "Imóvel com 2 vagas a partir de 700 mil no Centro, aceita cachorro",
  "Até R$ 1,1 milhão, 4 quartos, sol da manhã; vista não importa",
  "Não me importo com pet. Apartamento 1 quarto perto do metrô até 350k",
];

async function main() {
  const modo = process.argv[2] ?? "final";
  const anuncios: Anuncio[] = ler("anuncios.json").casos;
  // As Choices de tipo/cidade/bairro listam o catálogo: valor novo no catálogo exige pergunta nova.
  for (const [campo, mapa] of [["tipo", TIPOS], ["cidade", CIDADES], ["bairro", BAIRROS]] as const) {
    const fora = anuncios.filter((a) => !Object.values(mapa).includes(a[campo] as never));
    if (fora.length) throw new Error(`catálogo tem ${campo} fora das opções da pergunta: ${fora[0][campo]}`);
  }

  if (modo === "rascunho") {
    const jev = new Jev(join(AQUI, "cache"));
    for (const t of RASCUNHO) {
      const l = await lerConsulta(jev, t);
      console.log(`${t}\n  → ${textoFiltro(l.filtro)} | pede: ${Object.entries(l.probPedido).map(([k, v]) => `${k} ${v.toFixed(2)}`).join(" ")} | ` +
        `conf ${Object.entries(l.confianca).map(([k, v]) => `${k} ${v.toFixed(2)}`).join(" ")}`);
    }
    console.log(jev.resumo());
    return;
  }

  let linha: string;
  const conjuntos: [string, string][] = [["ajuste", "consultas_ajuste.json"]];
  if (modo === "final") {
    const gravado = existsSync(CONGELAMENTO) ? JSON.parse(readFileSync(CONGELAMENTO, "utf8")) : null;
    // O teste só roda com perguntas e composição congeladas: o hash gravado ANTES tem de bater com os arquivos.
    if (!gravado || JSON.stringify(gravado.sha256) !== JSON.stringify(hashes()))
      throw new Error("teste recusado: perguntas.ts/busca.ts não batem com congelamento.json (rode `npm run congelar`)");
    linha = `Versão congelada (gravada em ${gravado.gravado_em}, antes de abrir o teste): ` +
      Object.entries(gravado.sha256).map(([n, h]) => `\`${n}\` sha256 ${h}…`).join(" · ");
    conjuntos.push(["teste", "consultas_teste.json"]);
  } else if (modo === "congelar") {
    const gravado_em = new Date().toISOString().replace("T", " ").slice(0, 16) + " UTC";
    writeFileSync(CONGELAMENTO, JSON.stringify({ gravado_em, sha256: hashes() }, null, 1) + "\n", "utf8");
    linha = `Versão congelada agora (${gravado_em}); só o ajuste rodou.`;
  } else if (modo === "ajuste") {
    linha = `Versão em afinação (NÃO congelada): ${JSON.stringify(hashes())}`;
  } else throw new Error(`modo desconhecido: ${modo}`);

  const resumos: Resumo[] = [], secoes: string[] = [];
  for (const [nome, arq] of conjuntos) {
    const dados = ler(arq);
    const { res, jev } = await rodarConjunto(dados.casos, anuncios);
    const rs = resumoConjunto(nome, res, jev);
    resumos.push(rs);
    secoes.push(secaoConjunto(nome, dados, res, rs, anuncios));
    console.log(`${nome}: NDCG@10 ${f3(rs.ndcg.jev)} (palavras ${f3(rs.ndcg.palavras)}, filtro_palavras ${f3(rs.ndcg.filtro_palavras)}) · ` +
      `perda rel≥1 ${rs.rel1 - rs.rec1}/${rs.rel1} · US$/consulta ${rs.usPorConsulta.toFixed(6)} · ${rs.custo.requisicoes} req (${rs.custo.do_cache} do cache)`);
  }
  writeFileSync(join(AQUI, "resultados.md"), relatorio(resumos, secoes, linha), "utf8");
}

main().catch((e) => { console.error(e instanceof Error ? `${e.name}: ${e.message}` : e); process.exit(1); });
