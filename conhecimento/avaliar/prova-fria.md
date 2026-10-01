---
name: prova-fria
description: Como avaliamos o PRÓPRIO acervo — a prova respondida por um agente "frio" que só lê a cópia exportada — com o que é configurado, verificado ou só declarado, as condições para comparar Claude e Codex e o resultado da rodada 1 (2026-09-30).
tipo: principio
fonte: decisão do coordenador com a proposta do Codex (canal de coordenação, P10 e P11, 2026-09-30) + ferramentas/copia_fria.py
estudado_em: 2026-09-30
---

# Prova fria — avaliar o acervo, não o Jev

**Pergunta que responde:** um Claude ou um Codex que só tenha este repositório sabe o que importa sobre o
Jev? O critério de aceite está em [decisoes](../evidencias/decisoes.md). As perguntas e o gabarito **nunca
entram na distribuição** (ficam em `prova/`, fora da cópia), e quem consolida o acervo não lê o gabarito.

## Protocolo usado (2026-09-30)
1. **Exportar** com `ferramentas/copia_fria.py` ([README](../../README.md#ferramentas)): lista permitida de
   entradas da raiz e extensões, arquivo a arquivo; entrada não classificada, nome de credencial ou link
   interrompe; o manifesto lista cada arquivo com hash e a árvore inteira.
2. **Revisão adversarial** da cópia congelada por outro agente antes da prova (hash conferido de forma
   independente), com correção e nova exportação.
3. **Durante a rodada**, os arquivos de avaliação (gabarito, crítica e rascunho da prova) são **realocados**
   para fora da árvore do repositório e devolvidos depois, com hash conferido.
4. As **perguntas vão no prompt**; o agente recebe instrução de ler só a cópia.
5. **Auditoria** do registro de ferramentas da sessão: leitura bem-sucedida fora da cópia invalida a
   rodada; tentativa negada conta como evidência da barreira.
6. **Correção** pelo autor do gabarito (o examinador), não por quem consolidou; cada participante é
   corrigido e a nota fechada **antes** de abrir a resposta do outro.

## Comparar Claude e Codex: condições definidas ANTES
Duas sessões só são comparáveis se as condições forem fixadas antes da rodada e o consumo for registrado
depois. Fixar e registrar, para cada participante:
| Condição | O que fixar antes | O que registrar depois |
|---|---|---|
| Pacote | mesma cópia (hash da árvore do manifesto) | hash conferido na hora da rodada |
| Caderno e instruções | mesmo texto injetado no prompt | — |
| Ferramentas | equivalentes: só leitura dentro da cópia; sem web, rede, outro diretório ou memória | cada chamada/comando (registro bruto) |
| Modelo e esforço | nome exato e nível de raciocínio | o efetivo, se o cliente informar |
| Orçamento | teto de tempo, de chamadas/comandos e de tokens; tamanho da resposta | tempo, chamadas e tokens gastos |
| Saída | pasta própria, vazia, uma por participante | hash das respostas |
| Ambiente | onde roda (máquina do autor, contêiner, VM) e o que fica visível | montagens/canário, quando houver |

- **Adaptações entre clientes** (ferramenta de leitura diferente, resposta em arquivo × mensagem final,
  ambiente diferente) são registradas como tal. Com elas, a rodada mede se **o acervo basta** para cada
  um; **não** é comparação controlada de modelos — diferença de nota, tempo ou tokens não se atribui ao modelo.
- **Sem transferir respostas:** pastas de saída separadas; nenhum participante vê a resposta do outro; o
  examinador fecha uma nota antes de ler a outra.
- **Repetir os mesmos itens depois do retorno da correção é revisão assistida**, não prova fria. Nova
  rodada fria exige itens inéditos e condições definidas antes.

## Rodada 1 (2026-09-30) — o que aconteceu
- Pacote: cópia de 1.332 arquivos; caderno v1 (60 itens, 10 críticos; aceite 108/120, ≥ 75% por bloco,
  2 em todo crítico). **Nenhum orçamento foi fixado antes** — a lacuna que esta seção fecha.
- **Codex** (`gpt-6-astra`, esforço high), em **contêiner** (só a cópia montada para leitura + saída vazia;
  canário fora invisível; login próprio; contêiner removido ao fim): 10 comandos de leitura, 489 s,
  ~665 mil tokens de entrada e 15 mil de saída → **120/120**.
- **Claude** (subagente Opus), na máquina do autor pelo método acima: 80 leituras/buscas, todas na cópia,
  + 8 gravações no próprio arquivo de respostas (permitidas); 818 s; ~432 mil tokens → **117/120**.
- **Aceite conjunto não atingido** na rodada 1 (um item crítico abaixo do máximo). Lição geral levada ao
  acervo: as condições comparáveis da seção acima. O diagnóstico por item fica nos relatórios de correção,
  fora da distribuição.
- Auditorias feitas pelo executor (Claude) sobre os registros brutos: tudo dentro do permitido — leitura só
  no pacote, escrita só na saída de cada participante; o examinador não conferiu os registros brutos.

## O que isso garante e o que não
- **Nome honesto do método:** "cópia por lista permitida + instrução + realocação dos arquivos de
  avaliação + auditoria". **Não é isolamento.** Na mesma máquina, o agente ainda alcança o resto do disco;
  realocar tira o arquivo do caminho óbvio, não do disco visível.
- A auditoria **complementa**, não substitui o isolamento: busca por caminho no registro não cobre acesso
  indireto (caminho relativo, variável, link, outro conector) nem contexto carregado antes da primeira
  ferramenta. Cópias em históricos, backups ou memórias continuam fontes possíveis. Ausência de acesso
  detectado **não prova** que a leitura era impossível.
- Um resultado assim mostra que o acervo **basta** para responder; não demonstra independência total.

## A opção forte: VM ou contêiner descartável
**Desenho:** usuário novo, versão fixada da CLI, autenticação própria (nunca copiar a credencial do host),
sem perfis, memórias, plugins, MCP ou ganchos do host; só a exportação montada para leitura, as perguntas
injetadas pelo controlador e uma pasta de saída vazia. O original e o gabarito não existem no disco visível.
Rede só para inferência e autenticação. Antes da sessão: conferir manifestos, ausência de links que escapem,
e testar que a leitura de um arquivo-canário fora da exportação falha.
**Como foi feito na rodada 1 (Codex):** contêiner Docker (Docker Desktop sobre WSL2, Windows Home sem
Hyper-V), imagem Node com a mesma versão da CLI, `ca-certificates` instalado (sem ele o login falha);
login por código de dispositivo feito pelo dono; montagens conferidas (só `/pacote` read-only e `/saida`).
O sandbox interno da CLI não sobe em contêiner (sem *user namespaces*), então **a barreira é o contêiner**;
a rede fica aberta para a inferência, e o registro de eventos é auditado para comando de rede ou escrita.
Contêiner não é VM completa: isola o disco, não o kernel. Uma flag de sandbox da CLI que **acrescenta**
raiz legível não retira as permissões amplas — não serve como isolamento.

Lições de método do resto do repositório: [metodo](metodo.md).
