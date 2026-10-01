---
name: decisoes
description: Decisões do acervo e do dono em 2026-09-30 — ordem de estudo, material de terceiros fora do Git, skills por papel, API direta como referência, estrutura única (conhecimento/ + AGENTS.md), Claude coordena e Codex critica, dados reais só anonimizados e enviados após auditoria.
tipo: referencia
fonte: memory/decisions.md (Codex) + decisões do dono na conversa de 2026-09-30 + briefing da consolidação
estudado_em: 2026-09-30
---

# Decisões

Decisões do acervo, não exigências impostas pelo Jev. Autorizações futuras do dono podem mudar destino,
instalação ou alcance dos experimentos. Não apagar uma decisão superada: marcar e datar a nova.

| Data | Decisão | Origem / razão |
|---|---|---|
| 2026-09-30 | Estudar vídeos 01 → 02 → 03 → documentação. | Ordem expressa pelo usuário; cumprida pelos dois estudos. |
| 2026-09-30 | Manter a entrega local em `Documents/JEV`. | Usuário pediu uma pasta para levar ao GitHub depois. |
| 2026-09-30 | Separar fontes integrais e memória versionável: vídeos, legendas e snapshots de terceiros ficam fora do Git (`.local/`, `fontes/docs/`, `fontes/videos/`). | Conferência local × continuidade; direitos autorais resolvidos pela estrutura. |
| 2026-09-30 | Criar skills próprias por papel, com o conhecimento em notas linkadas. | Leitura sob demanda. *Revista na consolidação:* 4 skills (desenhar, integrar, avaliar, manter), só procedimento. |
| 2026-09-30 | Registrar a skill oficial sem instalá-la. | Pode complementar a integração; instalar globalmente é etapa separada. |
| 2026-09-30 | Exemplos sintéticos e respostas rotuladas como mock no estudo inicial. | Sem autorização nem configuração para experimentos pagos naquele momento. *Superada no mesmo dia:* houve chamadas reais medidas ([medicoes](medicoes-2026-09-30.md)); o mock segue como mock. |
| 2026-09-30 | Usar o contrato direto da TypeSafe como referência da API. | Vídeos mostram intermediários; não presumir envelopes idênticos. |
| 2026-09-30 | Não escolher arquitetura de negócio do CRM nesta etapa. | A tarefa é aprender o Jev e organizar o conhecimento; pilotos ficam como propostas. |
| 2026-09-30 | **Coordenação:** Claude coordena o trabalho; Codex atua como crítico. | Decisão do dono. Neste dia o Codex escreveu os dados rotulados dos exemplos, as propostas e a prova. |
| 2026-09-30 | **Dados reais:** só dados nossos, anonimizados, numa base local fora do Git. | Decisão do dono. |
| 2026-09-30 | **Envio à API:** texto real anonimizado só vai à TypeSafe depois de (1) varredura automática sem dado pessoal remanescente e (2) auditoria de uma amostra pelo dono; até lá, zero chamadas com dado real. | Decisão do dono. |
| 2026-09-30 | Conversas reais anonimizadas enviadas à API depois da auditoria, com aval do dono. | Registrado na pasta de estudo (privada); nem o texto nem os números entram na versão pública. |
| 2026-09-30 | **Consolidação:** um repositório único — `AGENTS.md` (instruções + núcleo) como fonte única, `CLAUDE.md` só aponta para ele, conhecimento em `conhecimento/` (um fato, um lugar), superados em `.local/antigos/2026-09-30/`. | Briefing da consolidação; os dois acervos (`memoria/` e `memory/`) duplicavam fatos e divergiam. |
| 2026-09-30 | **Prova de aceite:** o repositório vale se agentes frios (Claude e Codex), sem gabarito, chat nem `.local/`, acertam ≥ 90% da prova do Codex, zero erro nos itens críticos. | Briefing da consolidação; cópia fria por `ferramentas/copia_fria.py`. |
| 2026-09-30 | **Isolamento da prova fria (rodada 1):** fallback declarado — cópia por lista permitida + instrução + realocação dos arquivos de avaliação + auditoria; não é VM e não prova independência total. | Proposta do Codex; a VM descartável fica como opção forte para o dono decidir. Detalhe: [prova-fria](../avaliar/prova-fria.md). |
| 2026-09-30 | **Rodada 1 da prova fria:** Codex em contêiner Docker isolado (o dono autorizou VM local e fez o login); Claude pelo método acima. Codex 120/120, Claude 117/120 com um item crítico abaixo do máximo → aceite conjunto não atingido. | Lacuna do pacote (condições comparáveis) corrigida depois em [prova-fria](../avaliar/prova-fria.md); repetir os mesmos itens seria revisão assistida, não nova prova fria. |
| 2026-10-01 | **Publicação:** esta pasta continua como pasta de estudo (privada); a versão pública é `ia-automation/How-to-use-JEV` (organização da Inovai), com código MIT e textos CC BY 4.0 (*licença superada no mesmo dia: MIT único, linha abaixo*). Ficam fora: `privado/` (material interno), `prova/` (para provas frias futuras valerem), `.local/` e material integral de terceiros. | Decisão do dono. Números de dados internos não vão a público; as notas levam só a lição qualitativa. |
| 2026-10-01 | **Licença única MIT** para todo o acervo próprio; repositório **aberto a contribuições** (fork + PR), com merge e publicação **só pelos mantenedores**. Contribuição aceita entra primeiro na pasta de estudo e é republicada (a versão pública é gerada). | Decisão do dono. Regras em `CONTRIBUTING.md`. |
