/**
 * Busca em linguagem natural — composição (código) em volta das leituras do Jev (`perguntas.ts`).
 *
 * Funil: (1) o Jev LÊ a consulta → (2) o CÓDIGO filtra o catálogo pelas restrições duras (recuperação)
 *        → (3) o Jev LÊ cada anúncio recuperado, só nos critérios pedidos → (4) o CÓDIGO aplica a escala
 *        congelada em probabilidade e ordena pelo ganho esperado.
 * O ranking só reordena o que a recuperação trouxe: anúncio que o filtro descarta não volta (medido em run.ts).
 * Também aqui, congelada junto: a linha de base de palavras-chave (BM25, sem Jev).
 */
import type { ChoiceResponse, NoulQuestion } from "@typesafe-ai/sdk";
import { emParalelo, type Jev } from "./jev.js";
import {
  BAIRROS, CIDADES, CONCORRENCIA, GANHO, LIMIAR_PEDIDO, NOMES_CRITERIOS, P_ACEITA, PERGUNTAS_CONSULTA, TIPOS,
  perguntaAnuncio, perguntaPede, type NomeCriterio,
} from "./perguntas.js";

export interface Anuncio {
  id: string; titulo: string; descricao: string; tipo: string; bairro: string; cidade: string;
  quartos: number; vagas: number; preco: number; condominio: number; area_m2: number;
}

/** Restrições duras já em valores do catálogo; `null` = sem restrição. */
export interface Filtro {
  tipos: string[] | null; cidades: string[] | null; bairros: string[] | null;
  quartosMin: number; vagasMin: number; precoMax: number | null; precoMin: number | null;
}

export interface LeituraConsulta {
  filtro: Filtro;
  pedidos: NomeCriterio[];
  probPedido: Record<NomeCriterio, number>;
  confianca: Record<string, number>; // confiança da Choice de cada campo duro (diagnóstico)
}

type Ternaria = { afirma: number; nega: number; omite: number };
export interface Julgado {
  id: string;
  leituras: Partial<Record<NomeCriterio, Ternaria>>;
  dist: [number, number, number, number]; // P(rel = 0..3)
  ganho: number; // Σ GANHO[r]·P(r)
  relPrevista: number; // argmax da distribuição (diagnóstico, não ordena)
}

/** Opções com probabilidade ≥ P_ACEITA; a mais provável entra sempre (a Choice de 28 opções pode ficar abaixo). */
function aceitos(probs: Record<string, number>): string[] {
  const topo = Object.entries(probs).sort((a, b) => b[1] - a[1])[0][0];
  return [...new Set([topo, ...Object.keys(probs).filter((k) => probs[k] >= P_ACEITA)])];
}

const conjunto = (probs: Record<string, number>, mapa: Record<string, string>): string[] | null => {
  const a = aceitos(probs);
  return a.includes("qualquer") ? null : a.map((k) => mapa[k]);
};
const minimo = (probs: Record<string, number>, livre: string): number => {
  const a = aceitos(probs);
  return a.includes(livre) ? 0 : Math.min(...a.map((k) => Number(k.slice(1))));
};
const preco = (probs: Record<string, number>, livre: string, lado: "max" | "min"): number | null => {
  const a = aceitos(probs);
  if (a.includes(livre)) return null;
  const valores = a.map((k) => Number(k.slice(1)) * 1000); // "p600" → 600000
  return lado === "max" ? Math.max(...valores) : Math.min(...valores);
};

/**
 * @description Etapa 1 — uma requisição por consulta: 7 Choices de restrição dura + 8 Nouls "pede X?".
 * @returns o filtro (na dúvida, largo) e os critérios subjetivos pedidos
 */
export async function lerConsulta(jev: Jev, texto: string): Promise<LeituraConsulta> {
  const pede = Object.fromEntries(NOMES_CRITERIOS.map((c) => [`pede_${c}`, perguntaPede(c)])) as
    Record<`pede_${NomeCriterio}`, NoulQuestion>;
  const { answers: r } = await jev.perguntar({ buyer_request: texto }, { ...PERGUNTAS_CONSULTA, ...pede });
  const probPedido = Object.fromEntries(NOMES_CRITERIOS.map((c) => [c, r[`pede_${c}`].noul])) as Record<NomeCriterio, number>;
  return {
    filtro: {
      tipos: conjunto(r.tipo.probabilities, TIPOS),
      cidades: conjunto(r.cidade.probabilities, CIDADES),
      bairros: conjunto(r.bairro.probabilities, BAIRROS),
      quartosMin: minimo(r.quartos_min.probabilities, "sem_minimo"),
      vagasMin: minimo(r.vagas_min.probabilities, "sem_minimo"),
      precoMax: preco(r.preco_max.probabilities, "sem_limite", "max"),
      precoMin: preco(r.preco_min.probabilities, "sem_minimo", "min"),
    },
    pedidos: NOMES_CRITERIOS.filter((c) => probPedido[c] >= LIMIAR_PEDIDO),
    probPedido,
    confianca: Object.fromEntries(Object.keys(PERGUNTAS_CONSULTA).map((k) => [k, (r as unknown as Record<string, ChoiceResponse>)[k].confidence])),
  };
}

/** @description Restrições duras que o anúncio viola (vazio = passa). Limites inclusivos. É comparação exata: código. */
export function falhas(a: Anuncio, f: Filtro): string[] {
  const x: string[] = [];
  if (f.tipos && !f.tipos.includes(a.tipo)) x.push("tipo");
  if (f.cidades && !f.cidades.includes(a.cidade)) x.push("cidade");
  if (f.bairros && !f.bairros.includes(a.bairro)) x.push("bairro");
  if (a.quartos < f.quartosMin) x.push("quartos");
  if (a.vagas < f.vagasMin) x.push("vagas");
  if (f.precoMax !== null && a.preco > f.precoMax) x.push("preco_max");
  if (f.precoMin !== null && a.preco < f.precoMin) x.push("preco_min");
  return x;
}

/**
 * @description Escala congelada (DADOS.md, decisão 5) em probabilidade, supondo critérios independentes:
 * P(0) = algum negado · P(3) = todos afirmados · P(1) = todos omitidos · P(2) = sem negação e nem 3 nem 1.
 * Sem critério pedido, o anúncio que passou no filtro "atende tudo" (3).
 */
export function distribuicao(leituras: Ternaria[]): [number, number, number, number] {
  if (leituras.length === 0) return [0, 0, 0, 1];
  const norm = leituras.map((t) => { const s = t.afirma + t.nega + t.omite || 1; return { a: t.afirma / s, n: t.nega / s, o: t.omite / s }; });
  const semNegar = norm.reduce((p, t) => p * (1 - t.n), 1);
  const todosA = norm.reduce((p, t) => p * t.a, 1);
  const todosO = norm.reduce((p, t) => p * t.o, 1);
  // Com um critério só, "sem negação" = afirma ou omite: P(2) sai 0 pela conta (max protege do arredondamento).
  return [1 - semNegar, todosO, Math.max(0, semNegar - todosA - todosO), todosA];
}

/** @description Etapa 3+4 — uma requisição por anúncio recuperado (só os critérios pedidos), depois ordena. */
export async function julgarEOrdenar(jev: Jev, recuperados: Anuncio[], pedidos: NomeCriterio[]): Promise<Julgado[]> {
  const julgados = await emParalelo(recuperados, CONCORRENCIA, async (a): Promise<Julgado> => {
    let leituras: Partial<Record<NomeCriterio, Ternaria>> = {};
    if (pedidos.length) { // sem critério subjetivo não há o que perguntar: nenhuma chamada
      const perguntas = Object.fromEntries(pedidos.map((c) => [c, perguntaAnuncio(c)])) as
        Record<NomeCriterio, ReturnType<typeof perguntaAnuncio>>;
      const { answers } = await jev.perguntar({ listing_description: a.descricao }, perguntas);
      leituras = Object.fromEntries(pedidos.map((c) => [c, answers[c].probabilities as Ternaria]));
    }
    const dist = distribuicao(pedidos.map((c) => leituras[c]!));
    return {
      id: a.id, leituras, dist,
      ganho: dist.reduce((s, p, r) => s + GANHO[r] * p, 0),
      relPrevista: dist.indexOf(Math.max(...dist)),
    };
  });
  return julgados.sort((x, y) => y.ganho - x.ganho || x.id.localeCompare(y.id));
}

// ---------------------------------------------------------------- linha de base: palavras-chave (sem Jev)

const PARADAS = new Set(("a o as os um uma uns umas de da do das dos em no na nos nas com para por pelo pela que e ou " +
  "se ao aos mais menos ate r mil quero procuro preciso imovel sao seja fique tem ter").split(" "));

/** Minúsculas, sem acento, sem palavra vazia; plural simples cortado ("quartos" → "quarto"). */
export function tokens(texto: string): string[] {
  return texto.toLowerCase().normalize("NFD").replace(/\p{M}/gu, "").split(/[^a-z0-9]+/)
    .filter((w) => w.length > 1 && !PARADAS.has(w))
    .map((w) => (w.length > 3 && w.endsWith("s") ? w.slice(0, -1) : w));
}

/** @description BM25 clássico (k1 = 1,2, b = 0,75) sobre um corpus fixo; devolve a pontuação de cada documento. */
export function bm25(corpus: { id: string; texto: string }[], consulta: string): Map<string, number> {
  const docs = corpus.map((d) => ({ id: d.id, t: tokens(d.texto) }));
  const media = docs.reduce((s, d) => s + d.t.length, 0) / docs.length;
  const df = new Map<string, number>();
  for (const d of docs) for (const w of new Set(d.t)) df.set(w, (df.get(w) ?? 0) + 1);
  const q = [...new Set(tokens(consulta))];
  return new Map(docs.map((d) => {
    let s = 0;
    for (const w of q) {
      const tf = d.t.filter((x) => x === w).length;
      if (!tf) continue;
      const idf = Math.log(1 + (docs.length - df.get(w)! + 0.5) / (df.get(w)! + 0.5));
      s += (idf * tf * 2.2) / (tf + 1.2 * (0.25 + (0.75 * d.t.length) / media));
    }
    return [d.id, s];
  }));
}
