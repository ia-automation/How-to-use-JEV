/**
 * Perguntas, limiares e pesos da busca — ARQUIVO ÚNICO, revisável por humano.
 *
 * Duas leituras, dois states:
 *  1. CONSULTA (1 requisição por consulta, state `{buyer_request}`): o Jev lê O QUE a pessoa pede.
 *     Números viram Choice sobre faixas fechadas (limite #2: o Jev não compara número; ele só diz qual
 *     opção o texto escreveu). A comparação com preço/quartos/vagas do anúncio é do código.
 *     Critérios subjetivos: um Noul "pede X?" por critério do catálogo.
 *  2. ANÚNCIO (1 requisição por anúncio recuperado, state `{listing_description}`): para cada critério
 *     PEDIDO, uma Choice ternária afirma / nega / omite. Ternária e não Score porque o fato é ternário
 *     e a negação é veto na escala congelada ("não informa pet" ≠ aceita pet; negado ⇒ relevância 0).
 *
 * Perguntas em inglês, dados em português (medido: pt na mensagem ≈ en; perguntas em pt não ajudam).
 */
import { choice, noul } from "@typesafe-ai/sdk";

// ---------------------------------------------------------------- consulta: restrições duras

/** Valores do catálogo (fechados). `run.ts` confere que o catálogo não tem outros. */
export const TIPOS = { apartamento: "apartamento", casa: "casa", sobrado: "sobrado" } as const;
export const CIDADES = { aurora: "Cidade Aurora", horizonte: "Cidade Horizonte" } as const;
export const BAIRROS = { vila_verde: "Vila Verde", jardim_norte: "Jardim Norte", centro: "Centro" } as const;

/**
 * Grade de preço (R$): de 10 em 10 mil, de 200 mil a 1,5 milhão (131 opções; Choice aceita até 255).
 * Medido no rascunho: com grade de 50 mil, "até 620 mil" virou 600 mil (conf 0,91) — perda silenciosa de
 * recuperação; com 10 mil, 620 mil (1,00), "meio milhão" 500 mil, "1,1 milhão" 1.100 mil. Custa ~7 mil tokens
 * a mais por CONSULTA (não por anúncio). Valor fora da grade (ex.: 625 mil) continua limite declarado.
 */
export const PASSO_PRECO = 10_000;
export const GRADE_PRECO = Array.from({ length: (1_500_000 - 200_000) / PASSO_PRECO + 1 }, (_, i) => 200_000 + i * PASSO_PRECO);

/** "R$ 600 mil (R$ 600.000)" / "R$ 1,25 milhão (R$ 1.250.000)" — o texto que a consulta costuma escrever. */
function rotuloPreco(v: number): string {
  const extenso = v >= 1_000_000 ? `R$ ${(v / 1_000_000).toLocaleString("pt-BR")} milhão` : `R$ ${v / 1000} mil`;
  return `${extenso} (R$ ${v.toLocaleString("pt-BR")})`;
}
const opcoesPreco = Object.fromEntries(GRADE_PRECO.map((v) => [`p${v / 1000}`, rotuloPreco(v)]));

export const PERGUNTAS_CONSULTA = {
  tipo: choice("Which property type does the buyer ask for in `buyer_request`?", {
    apartamento: "An apartment (apartamento, apto).",
    casa: "A house (casa). A sobrado is a separate option.",
    sobrado: "A sobrado (two-story townhouse).",
    qualquer: "No specific type: the buyer says 'imóvel' or does not state a type.",
  }),
  cidade: choice("Which city does the buyer ask for in `buyer_request`?", {
    aurora: "Cidade Aurora.",
    horizonte: "Cidade Horizonte.",
    qualquer: "The buyer does not state a city.",
  }),
  bairro: choice("Which neighborhood (bairro) does the buyer ask for in `buyer_request`?", {
    vila_verde: "Vila Verde.",
    jardim_norte: "Jardim Norte.",
    centro: "Centro (the downtown neighborhood).",
    qualquer: "The buyer does not state a neighborhood (a city alone is not a neighborhood).",
  }),
  quartos_min: choice("What is the minimum number of bedrooms (quartos, dormitórios) the buyer asks for?", {
    sem_minimo: "The buyer does not state a number of bedrooms.",
    q1: "1 bedroom or more (um quarto).",
    q2: "2 bedrooms or more (dois quartos).",
    q3: "3 bedrooms or more (três quartos).",
    q4: "4 bedrooms or more (quatro quartos).",
    q5: "5 bedrooms or more (cinco quartos).",
  }),
  vagas_min: choice("What is the minimum number of parking spaces (vagas de garagem) the buyer asks for?", {
    sem_minimo: "The buyer does not state a number of parking spaces.",
    v1: "1 parking space or more (uma vaga).",
    v2: "2 parking spaces or more (duas vagas).",
    v3: "3 parking spaces or more (três vagas).",
    v4: "4 parking spaces or more (quatro vagas).",
  }),
  preco_max: choice("What maximum price does the buyer state (até, no máximo, teto, orçamento)?", {
    sem_limite: "The buyer states no maximum price.",
    ...opcoesPreco,
  }),
  preco_min: choice("What minimum price does the buyer state as a lower bound (a partir de, acima de, entre X e Y)?", {
    sem_minimo: "The buyer states no lower bound on price. A maximum price alone is not a lower bound.",
    ...opcoesPreco,
  }),
};

/**
 * Faixa de dúvida da leitura da consulta, orientada para NÃO PERDER recuperação: todo valor com probabilidade
 * ≥ P_ACEITA entra no filtro (tipo: aceita os dois; teto: o maior; mínimo: o menor; "qualquer" ≥ P_ACEITA
 * desliga a restrição). Errar para o lado largo custa ordenação; errar para o estreito some com o anúncio.
 */
export const P_ACEITA = 0.15;

// ---------------------------------------------------------------- critérios subjetivos (os 8 do catálogo)

interface Criterio {
  pedido: string; // como a PESSOA pede (lado da consulta), com as palavras dela entre parênteses
  alvo: string; // o fato no ANÚNCIO, em inglês
  afirma: string;
  nega: string;
}

export const CRITERIOS = {
  pet: {
    pedido: "a property that accepts pets (aceita pet, animais, cães, gatos)",
    alvo: "pets being allowed in the property",
    afirma: "The listing says pets or animals (dogs, cats) are allowed.",
    nega: "The listing says pets are not allowed or are restricted.",
  },
  rua_tranquila: {
    pedido: "a quiet street or calm surroundings (rua tranquila, silenciosa, sem barulho)",
    alvo: "a quiet street",
    afirma: "The listing says the street or surroundings are quiet, calm, with little traffic or noise.",
    nega: "The listing says the street or surroundings are noisy or have heavy traffic.",
  },
  home_office: {
    pedido: "a space to work from home (home office, escritório, trabalhar em casa)",
    alvo: "a space suitable for working from home (home office)",
    afirma: "The listing says there is a room or area suitable for an office or remote work.",
    nega: "The listing says there is no suitable space for an office or remote work.",
  },
  metro: {
    pedido: "being near a metro station (perto do metrô, metrô a pé)",
    alvo: "a metro station within walking distance",
    afirma: "The listing says a metro station is close enough to walk to.",
    nega: "The listing says there is no metro station within walking distance.",
  },
  sol_manha: {
    pedido: "morning sun (sol da manhã)",
    alvo: "morning sun",
    afirma: "The listing says the property gets morning sun.",
    nega: "The listing says the property gets no morning sun (for example, only afternoon sun).",
  },
  reformado: {
    pedido: "a renovated property, ready to move in (reformado, pronto para morar)",
    alvo: "the property being renovated and ready to move in",
    afirma: "The listing says the property was renovated and is ready to live in.",
    nega: "The listing says the property needs renovation or has pending works.",
  },
  vista: {
    pedido: "an open view (vista livre, vista aberta)",
    alvo: "an open, unobstructed view",
    afirma: "The listing says the property has an open or unobstructed view.",
    nega: "The listing says there is no open view or the view is blocked.",
  },
  jardim: {
    pedido: "a garden (jardim, área verde)",
    alvo: "a private garden",
    afirma: "The listing says the property has a private garden for its exclusive use.",
    nega: "The listing says the property has no private garden.",
  },
} satisfies Record<string, Criterio>;
export type NomeCriterio = keyof typeof CRITERIOS;
export const NOMES_CRITERIOS = Object.keys(CRITERIOS) as NomeCriterio[];

/**
 * Leitura da CONSULTA: a pessoa pede este critério? (um Noul por critério, todos na mesma requisição)
 * Frase do lado da PESSOA, não do anúncio: no rascunho, "perto do metrô" contra "metro within walking
 * distance" deu 0,53 e "precisa ter jardim" contra "a private garden" deu 0,30 — leitura literal (limite #1).
 */
export const perguntaPede = (c: NomeCriterio) =>
  noul(`Does the buyer in \`buyer_request\` ask for ${CRITERIOS[c].pedido}?`, {
    true: `The buyer asks for ${CRITERIOS[c].pedido}.`,
    false: `The buyer does not mention it, or says it does not matter.`,
  });
export const LIMIAR_PEDIDO = 0.5; // Noul ≥ isto ⇒ o critério entra na leitura dos anúncios

/** Leitura do ANÚNCIO: afirma / nega / omite (a omissão é resposta, não falta de resposta). */
export const perguntaAnuncio = (c: NomeCriterio) =>
  choice(`What does \`listing_description\` say about ${CRITERIOS[c].alvo}?`, {
    afirma: CRITERIOS[c].afirma,
    nega: CRITERIOS[c].nega,
    omite: `The listing says nothing about ${CRITERIOS[c].alvo}.`,
  });

// ---------------------------------------------------------------- ranking

/**
 * Ganho por nível de relevância = 2^rel − 1 (o mesmo do NDCG). Ordenar pelo ganho ESPERADO maximiza o DCG
 * esperado. A escala congelada vira probabilidade no código (`busca.ts`): P(3) = todos afirmados; P(0) = algum
 * negado; P(1) = todos omitidos; P(2) = o resto sem negação. Mudar peso aqui não custa chamada.
 */
export const GANHO = [0, 1, 3, 7] as const;

/** Requisições simultâneas ao Jev (por consulta, um anúncio por requisição). */
export const CONCORRENCIA = 8;
