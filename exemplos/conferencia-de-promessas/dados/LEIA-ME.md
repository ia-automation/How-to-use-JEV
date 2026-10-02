# Conferência de promessas — decisões de rotulagem

Autor: fable (rotulador). Data: 2026-10-01. Escrito ANTES dos casos. Dados sintéticos: fichas no estilo
de portal, rascunhos no estilo de atendente de imobiliária (pt-BR). Bairros e cidades reais; nenhum
endereço com número, nenhum andar, nenhum número de unidade, nenhum nome ou contato.

Arquivos: `rascunho.json` (5 fichas fáceis, encanamento), `ajuste.json` (30 fichas), `teste.json`
(60 fichas, abrir uma vez no fim). Envelope `{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "ficha": {"titulo", "descricao", "campos"}, "afirmacoes": [{"id", "texto", "relacao",
"trecho_apoio"}], "nota"}`
- `campos` só com chaves públicas: `quartos`, `vagas`, `area_m2`, `orientacao_solar`, `aceita_pet`,
  `financiamento` (`aceita` | `proprietario_analisa` | `nao_aceita` | null), `distancia_metro_m`,
  `condominio_reais`, `mobiliado`. Campo ausente ou `null` = a ficha não declara. Campo e descrição
  nunca se contradizem na mesma ficha (garantido na autoria).
- `afirmacoes[].id`: `a1`, `a2`… `relacao` ∈ `supported` | `contradicted` | `not_stated`.
- `trecho_apoio`: substring literal de `ficha.descricao` **ou** o campo que sustenta/contradiz, na forma
  `"<campo>: <valor em JSON>"` (ex.: `"vagas: 2"`, `"aceita_pet: false"`,
  `"financiamento: \"nao_aceita\""`). `null` só em `not_stated`. Validado por script.
- `nota`: começa com `"difícil: <família>"` quando o caso é difícil; `"numérica: a2, a3"` lista as
  afirmações que o **código** deve comparar (área, vagas, preço, condomínio, distância). As duas partes
  se separam por `; `. `null` quando não há nada a dizer.

## As três relações
- **supported**: a ficha afirma o mesmo fato, literalmente ou por paráfrase que um corretor experiente
  aceita como equivalente estrito ("pronto para morar" ⇒ "não precisa de reforma"; "entregue com
  todos os móveis" ⇒ "mobiliado"; "3 suítes" com `quartos: 3` ⇒ "todos os quartos são suítes").
- **contradicted**: a ficha afirma o oposto ou um valor incompatível: negação explícita ("não aceita
  pet"), atributo mutuamente exclusivo (vaga rotativa × privativa; face oeste × sol da manhã; "na
  planta" × "pronto para morar"), número diferente (`vagas: 2` × "3 vagas"; `vagas: 2` × "tem 1 vaga" —
  contagem exata, não "pelo menos").
- **not_stated**: a ficha silencia **ou só sustenta uma versão mais fraca** da afirmação.

## Princípio único: exagero é `not_stated`, oposto é `contradicted`
Quando o rascunho afirma mais do que a ficha garante, a ficha não sustenta — mas também não nega.
Só vira `contradicted` quando a ficha nega explicitamente a versão forte ou afirma o que a condição
exclui. Aplicado às famílias difíceis do briefing:
1. **Possibilidade × garantia.** "Proprietário analisa/estuda/pode aceitar financiamento" →
   "aceita financiamento" / "financiamento aprovado" = `not_stated`; "não aceita financiamento" =
   `contradicted` (nega a possibilidade afirmada); "pode aceitar, a confirmar" = `supported`.
   "Aceita financiamento" na ficha → "já aprovado para você" = `not_stated` (aprovação é outro fato).
   Banco específico quando a ficha diz "financiamento bancário" = `supported` (instância do genérico).
2. **Vaga rotativa × privativa.** Rotativa → "privativa/fixa/demarcada/garantida" = `contradicted`;
   rotativa → "tem vaga" = `supported` (`vagas: 1`). "1 escriturada + 1 rotativa" → "2 vagas
   privativas" = `contradicted`. Ficha só com número → "coberta" = `not_stated`; "descoberta" na ficha
   → "coberta" = `contradicted`.
3. **Permissão condicionada.** "Pet de pequeno porte / até 10 kg / mediante aprovação / só gatos" →
   "aceita pet" (sem a condição) = `not_stated`; afirmação que respeita a condição = `supported`;
   afirmação do que a condição exclui ("aceita cão grande", "aceita golden retriever") =
   `contradicted`; "não aceita pet" diante de permissão condicionada = `contradicted`. Nessas fichas
   o campo `aceita_pet` fica ausente (a resposta não é um booleano). "Pets: consultar" → tanto
   "aceita" quanto "não aceita" = `not_stated`. "Semimobiliado" → "mobiliado" = `not_stated`.
4. **Distância estimada.** Número da ficha é a referência; o código compara (`numérica`). Conversão
   metros ↔ minutos a pé: ~80 m/min; tempo compatível dentro de ±50% = `supported`, fora =
   `contradicted` (1.200 m → "5 min a pé" é `contradicted`; 400 m → "5 min" é `supported`). Palavra
   vaga ("perto", "colado", "do lado") contra número: `not_stated`, salvo ≥ 2 km (`contradicted`);
   contra palavra da ficha ("próximo ao metrô") = `supported`. Bairro conhecido por ter metrô sem
   distância na ficha = `not_stated`.
5. **Orientação solar × cômodo iluminado.** Tabela fixa, decidida como corretor experiente no
   hemisfério sul: `leste`/"voltado para o leste" ⇒ "sol da manhã" `supported`, "sol da tarde"
   `contradicted`; `oeste` ⇒ "sol da manhã" `contradicted`; `norte` ⇒ "sol da manhã" `not_stated`,
   "sol a maior parte do dia" `supported`; `sul` ⇒ "ensolarado"/"pega bastante sol" `contradicted`.
   "Claro/bem iluminado/janelas amplas" ⇒ qualquer orientação ou "sol da manhã" = `not_stated`.
   "Sol da manhã" e "sol da tarde" são tratados como excludentes. "Sol da manhã nos quartos" →
   "sol o dia inteiro" = `not_stated`; "sol da manhã no quarto; sala sem incidência" → "sol da manhã
   na sala" = `contradicted`, "ensolarado" = `not_stated`.
6. **Paráfrase válida** é `supported`, nunca `contradicted`: dormitório = quarto; "garagem para dois
   carros" = `vagas: 2`; "não há restrição a animais" = aceita pet; "vista para a baía" = vista para o
   mar; "eletrodomésticos" inclui geladeira. Paráfrase negativa também vale ("precisa de reforma" ×
   "reformado" = `contradicted`).
7. **Negação na ficha.** "Não mobiliado" × "mobiliado" = `contradicted`; "não mobiliado" × "sem
   móveis" = `supported`; `aceita_pet: false` × "não aceita animais" = `supported`.

## Outras decisões
- **Afirmação composta** (dois fatos numa frase): `contradicted` se qualquer parte é contradita;
  senão `not_stated` se qualquer parte não é declarada; senão `supported`. Marcada "composta" na nota.
- **Opinião** sem fato ("ótima localização", "lugar seguro") = `not_stated`. Adjetivo colado a um
  fato sustentado ("condomínio barato, R$ 520") não derruba o fato: `supported`.
- **Aproximação numérica**: "cerca de/quase X" com desvio ≤ 5% = `supported`; "mais de 100 m²" com 98
  = `contradicted` (o código compara literalmente). Área construída ≠ área do terreno ≠ área total.
- **Fato ausente na ficha** (piscina, elevador, academia, taxa de pet) = `not_stated`, mesmo que
  plausível pelo bairro ou pelo padrão do prédio.
- `null` em `relacao` não é usado: toda afirmação é decidível com as regras acima; a indecisão real
  mora na família (nota) e é analisada por família nos resultados.

## Famílias cobertas (casos por família, impressos pelo validador do rotulador em 2026-10-01)
Rascunho: 5 fichas, 18 afirmações (11 supported, 4 contradicted, 3 not_stated), fáceis.
Ajuste: 30 fichas, 104 afirmações (56 supported, 29 contradicted, 19 not_stated), 36 numéricas, 26 difíceis.
Teste: 60 fichas, 200 afirmações (112 supported, 50 contradicted, 38 not_stated), 77 numéricas, 52 difíceis.

| Família (nota "difícil:") | ajuste | teste |
|---|---|---|
| possibilidade×garantia | 5 | 6 |
| vaga rotativa×privativa | 3 | 6 |
| condição | 3 | 8 |
| distância estimada | 4 | 6 |
| orientação×iluminação | 5 | 10 |
| paráfrase (válida e negativa) | 4 | 7 |
| negação | 2 | 7 |
| composta | 3 | 4 |
| opinião | 1 | 2 |
| aproximação numérica / dois números na ficha | 0 | 4 |

Um caso pode pertencer a mais de uma família. O validador conferiu: envelope, campos e tipos, enums,
IDs em ordem, `trecho_apoio` substring literal ou `campo: valor` igual ao campo, `null` só em
`not_stated`, ≥ 30% difíceis em ajuste e teste, ≥ 1 numérica a cada 4 afirmações, UTF-8 sem BOM, LF.
