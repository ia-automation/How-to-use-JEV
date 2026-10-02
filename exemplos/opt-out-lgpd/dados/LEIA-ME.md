# Opt-out e LGPD — decisões de rotulagem

Autor: fable (rotulador). Data: 2026-10-01. Escrito ANTES dos casos. Mensagens sintéticas de clientes
de imobiliária (WhatsApp), pt-BR informal, curtas e longas. Nenhum nome completo, telefone, e-mail ou
CPF — quando o cliente "informa" um dado, o texto diz só que informou. Gabarito = o que o encarregado
de LGPD (ou um atendente experiente) decidiria lendo só a mensagem.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json` (30), `teste.json` (60, abrir uma vez no fim).
Envelope `{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "mensagem", "opt_out", "pedido_lgpd", "tipo_lgpd", "pausa_temporaria", "nota"}`
- `opt_out`, `pedido_lgpd`, `pausa_temporaria`: `true | false | null` (`null` = indecidível, sempre com nota).
- `tipo_lgpd` ∈ `exclusao | acesso | origem_dos_dados | correcao | null`; é `null` se e só se
  `pedido_lgpd` não é `true`.
- `nota`: começa com `"difícil: <família>"` nos casos difíceis.

## Opt-out definitivo × pausa temporária
- **`opt_out: true`** — o titular DESTE canal pede para parar de receber contato, sem prazo de retomada:
  "não me mande mais", "me tira da lista", "remove meu número", "me descadastra", "parem de me ligar".
  A porta aberta do lado do cliente ("se eu precisar eu procuro") não muda: é opt-out.
- **`pausa_temporaria: true`** — pede para não ser procurado **agora**, com prazo ou condição de
  retomada: "me chama mês que vem", "depois do carnaval", "quando o financiamento sair eu aviso",
  "por enquanto não", "não mandem nada até lá". Pausa NÃO é opt-out (`opt_out: false`).
- Os dois nunca são `true` juntos. "Não é pausa, é definitivo" → opt-out.
- **Não é opt-out nem pausa**: fim de interesse sem pedido de parar ("já comprei, obrigado"; "não tenho
  mais interesse") — o atendente encerra, mas não há pedido; preferência de canal ou horário com o
  outro canal mantido ("sem ligação, só mensagem"; "não me liga de manhã"); pedido de filtro ("para de
  mandar apê sem vaga"); recusa de UM imóvel ("não quero mais esse apê"); agendamento ("só consigo
  visitar depois do dia 15"); viagem sem pedido de parar ("tô viajando, mas pode mandar").
- **Opt-out parcial de campanha** ("não quero mais mensagem de lançamento") = `opt_out: true` (parar o
  disparo é a ação segura; a conversa iniciada pelo cliente continua por regra do código).
- **"Para"**: só conta com objeto de contato ("para de me mandar mensagem"). "para" sozinho ou "não
  quero mais" sem objeto → `opt_out: null`. "pode parar" depois de queixa de volume → `true`.

## O que conta como exercício de direito LGPD (`pedido_lgpd`) e os 4 tipos
- **`exclusao`**: pede para apagar/excluir dados, cadastro, CPF, histórico ("apaguem meus dados",
  "cancelem/encerrem meu cadastro", "quero a exclusão conforme a LGPD"). "Tirar da lista / remover meu
  número" é opt-out, NÃO exclusão.
- **`acesso`**: quer saber o que a empresa tem sobre ele, por quanto tempo, com quem compartilha.
- **`origem_dos_dados`**: pergunta de onde veio o contato / quem passou / base legal da coleta.
  Vale mesmo sem pedir exclusão e mesmo em tom de curiosidade ("quem é vc? como tem meu número?").
- **`correcao`**: pede para corrigir/atualizar dado pessoal NO CADASTRO ou em documento ("meu nome tá
  errado", "atualiza no cadastro"). "Me liga nesse outro número hoje" é preferência pontual, não correção.
- Dois tipos na mesma mensagem → precedência `exclusao > origem_dos_dados > acesso > correcao`; o
  segundo vai na nota.
- **Exclusão implica opt-out** (`opt_out: true`): sem cadastro não há contato. Exceção: o cliente pede
  explicitamente para continuar recebendo (exclusão parcial, ex.: "apaguem meu histórico de buscas, mas
  continuem mandando os lançamentos"). Acesso, origem e correção NÃO implicam opt-out.
- Pergunta retórica de cliente interessado ("ainda têm meu cadastro? podem usar") não é exercício de direito.

## Terceiro, ironia, negação
- **Terceiro**: vale quem é o titular DESTE canal. "Esse número é da minha mãe/filha, tirem" → opt-out
  (o número pede para sair). "Minha esposa não quer mais, eu sigo interessado" → `false` (o pedido é
  sobre outro contato; registrar e confirmar com a titular). Chip herdado ("não sou a Carla, tirem
  daqui") → `opt_out: true`, `pedido_lgpd: false` (não é a titular dos dados).
- **Ironia**: só vira opt-out quando a mensagem traz o pedido ("adoro spam… pode parar", "me tira dessa
  lista"). Ironia com interesse mantido ("vcs são insistentes hein, manda o do Tatuapé") → `false`.
- **Negação**: "não precisa parar", "não quero que tirem meu número", "não precisa apagar meus dados" →
  `false` no campo negado.
- **Reclamação longa**: procura-se o pedido; reclamação sem pedido de parar não é opt-out.

## Famílias e distribuição (contagem do validador do rotulador, 2026-10-01)
| Conjunto | n | difíceis | sem opt-out nem LGPD | `opt_out` T/F/null | `pedido_lgpd` T/F | exclusão/acesso/origem/correção | pausa T |
|---|---|---|---|---|---|---|---|
| rascunho | 5 | 0 | 2 | 2/3/0 | 2/3 | 1/0/1/0 | 1 |
| ajuste | 30 | 15 (50%) | 14 (47%) | 8/20/2 | 9/21 | 3/2/2/2 | 4 |
| teste | 60 | 30 (50%) | 28 (47%) | 19/40/1 | 18/42 | 6/4/5/3 | 7 |

"Sem opt-out nem LGPD" = `opt_out: false` E `pedido_lgpd: false` (cliente interessado, reclamação
comum, pausa, preferência, filtro) — é o que mede falso positivo; os `null` não entram nessa conta.

| Família (prefixo da `nota`) | ajuste | teste |
|---|---|---|
| negação ("não precisa parar", "não quero mais ESSE apê", nega a exclusão) | 2 | 5 |
| ironia (com e sem pedido) | 2 | 3 |
| terceiro (outro contato × titular deste canal × chip herdado) | 3 | 5 |
| pausa × opt-out | 2 | 4 |
| "para" ambíguo / "não quero mais" sem objeto (inclui os `null`) | 3 | 3 |
| reclamação longa (com e sem opt-out dentro) | 1 | 2 |
| origem sem pedir exclusão | 1 | 2 |
| fim de interesse sem pedido de parar | 1 | 1 |
| tipo de direito duvidoso (compartilhamento → acesso; correção em documento) | 0 | 3 |
| dois pedidos / exclusão parcial | 0 | 2 |

O validador conferiu: envelope, campos e tipos, enum de `tipo_lgpd`, `tipo_lgpd` não nulo se e só se
`pedido_lgpd: true`, opt-out e pausa nunca juntos, ≥ 40% sem opt-out nem LGPD, ≥ 30% difíceis, nenhuma
mensagem repetida (nem entre ajuste e teste), nenhum padrão de CPF/telefone/e-mail, UTF-8 sem BOM, LF.
