/**
 * Cliente do Jev com cache em disco e medição — porte para TypeScript de `exemplos/_comum/jevcache.py`.
 *
 * Por que cache: rodar de novo não pode gastar de novo, e o exemplo precisa rodar sem chave (o cache é a
 * resposta gravada da API real). Chave do cache = sha256(modelo + state + perguntas), com as chaves do JSON
 * ordenadas (o JSON.stringify do JS não ordena; sem isso a mesma pergunta viraria dois arquivos).
 *
 * Modos (variável JEV_MODO):
 *   auto     (padrão) usa o cache; se faltar, chama a API e grava.
 *   gravado  só o cache; resposta faltando = erro (modo de quem não tem chave).
 *   ao_vivo  sempre chama a API e regrava o cache.
 *
 * A chave vem de TYPESAFE_API_KEY; se ausente, de `api_key.txt` na raiz do repositório. Nunca é impressa,
 * logada nem gravada (o cache guarda só resposta e medição).
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { TypeSafeClient, type EntryType, type Questions, type SystemOneResult } from "@typesafe-ai/sdk";

export const MODELO = "jev-1.13.0"; // versão fixada: limiares afinados valem para esta versão, não para o alias
export const PRECO_US_POR_MILHAO_ENTRADA = 0.042; // saída não é cobrada (docs.typesafe.ai/models, 2026-09-30)
const RAIZ = resolve(import.meta.dirname, "..", "..", ".."); // src → busca-imoveis → exemplos → raiz do repositório

type Modo = "auto" | "gravado" | "ao_vivo";
export interface Medicao { ms: number; input_tokens: number; modelo: string; perguntas: number; cache: boolean }

/** @description JSON com chaves ordenadas em todos os níveis — base estável para o hash do cache. */
const ordenado = (v: unknown): unknown =>
  Array.isArray(v) ? v.map(ordenado)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, ordenado((v as Record<string, unknown>)[k])]))
      : v;

function chaveApi(): string {
  const doAmbiente = (process.env.TYPESAFE_API_KEY ?? "").trim();
  if (doAmbiente) return doAmbiente;
  const arquivo = join(RAIZ, "api_key.txt");
  return existsSync(arquivo) ? readFileSync(arquivo, "utf8").trim() : "";
}

/** Uma instância por conjunto medido (latência e tokens separados); a pasta de cache é do projeto e vai ao Git. */
export class Jev {
  readonly chamadas: Medicao[] = [];
  readonly modo: Modo;
  retentativas = 0; // contadas pelo logger do SDK (ele só as anuncia no nível "info")
  private cliente?: TypeSafeClient;

  constructor(private readonly pasta: string, private readonly modelo = MODELO) {
    mkdirSync(pasta, { recursive: true });
    this.modo = (process.env.JEV_MODO as Modo) || "auto";
  }

  private cli(): TypeSafeClient {
    if (!this.cliente) {
      const apiKey = chaveApi();
      if (!apiKey) throw new Error("sem chave: defina TYPESAFE_API_KEY ou rode com JEV_MODO=gravado");
      const quieto = () => {};
      this.cliente = new TypeSafeClient({
        apiKey,
        defaultModel: this.modelo,
        // "info" só para contar retentativas; o resto é descartado. Nunca "debug": ele imprime os corpos.
        logLevel: "info",
        logger: {
          debug: quieto,
          info: (m: string) => { if (m.includes("retrying")) this.retentativas++; },
          warn: (m: string) => console.warn(`[sdk] ${m}`),
          error: (m: string) => console.error(`[sdk] ${m}`),
        },
      });
    }
    return this.cliente;
  }

  /**
   * @description Uma requisição: um state, várias perguntas. Devolve a resposta tipada pelo SDK (as chaves
   * dos critérios viram tipos: `answers.x.choice` é a união dos rótulos declarados).
   * @param state texto ou objeto JSON que o Jev lê
   * @param questions dicionário nome → pergunta (choice/noul/score)
   * @returns o mesmo formato da API — do cache ou da chamada real
   */
  async perguntar<Q extends Questions>(state: EntryType, questions: Q): Promise<SystemOneResult<Q>> {
    const corpo = JSON.stringify(ordenado({ m: this.modelo, s: state, q: questions }));
    const arquivo = join(this.pasta, `${createHash("sha256").update(corpo).digest("hex").slice(0, 24)}.json`);
    if (this.modo !== "ao_vivo" && existsSync(arquivo)) {
      const registro = JSON.parse(readFileSync(arquivo, "utf8"));
      this.chamadas.push({ ...registro.medicao, cache: true });
      return registro.resposta as SystemOneResult<Q>;
    }
    if (this.modo === "gravado") throw new Error(`resposta não gravada no cache: ${arquivo}`);
    const cliente = this.cli(); // fora do cronômetro: a 1ª chamada montaria o cliente dentro da medição
    const inicio = performance.now();
    // Só state, questions e model: o SDK repassa campo extra no corpo, e a API responde 400 a campo extra.
    const r = await cliente.systemOne({ state, questions, model: this.modelo });
    const medicao = {
      ms: Math.round(performance.now() - inicio),
      input_tokens: r.usage?.input_tokens ?? 0,
      modelo: r.model,
      perguntas: Object.keys(questions).length,
    };
    const resposta = { model: r.model, answers: r.answers, usage: r.usage };
    writeFileSync(arquivo, JSON.stringify({ medicao, resposta }, null, 1), "utf8");
    this.chamadas.push({ ...medicao, cache: false });
    return resposta as SystemOneResult<Q>;
  }

  /** @description Resumo de custo e latência (latência medida na chamada real, mesmo quando veio do cache). */
  resumo() {
    const ms = this.chamadas.map((c) => c.ms).sort((a, b) => a - b);
    const tokens = this.chamadas.reduce((s, c) => s + c.input_tokens, 0);
    return {
      requisicoes: this.chamadas.length,
      do_cache: this.chamadas.filter((c) => c.cache).length,
      perguntas: this.chamadas.reduce((s, c) => s + c.perguntas, 0),
      p50_ms: ms.length ? ms[Math.floor((ms.length - 1) / 2)] : NaN,
      p95_ms: ms.length ? ms[Math.min(ms.length - 1, Math.floor(0.95 * ms.length))] : NaN,
      input_tokens: tokens,
      custo_us: (tokens / 1e6) * PRECO_US_POR_MILHAO_ENTRADA,
      modelos: [...new Set(this.chamadas.map((c) => c.modelo))].sort(),
      retentativas: this.retentativas,
    };
  }
}

/** @description Executa `fn` sobre os itens com no máximo `limite` promessas em voo; preserva a ordem. */
export async function emParalelo<T, R>(itens: T[], limite: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const saida = new Array<R>(itens.length);
  let proximo = 0;
  const trabalhador = async () => {
    while (proximo < itens.length) {
      const i = proximo++;
      saida[i] = await fn(itens[i]);
    }
  };
  await Promise.all(Array.from({ length: Math.min(limite, itens.length) }, trabalhador));
  return saida;
}
