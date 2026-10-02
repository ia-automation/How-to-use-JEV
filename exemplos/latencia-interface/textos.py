"""Textos curtos de barra de comando de um CRM imobiliário, escritos à mão pelo construtor (2026-10-02).

Rótulo `destino` é do PRÓPRIO construtor, não de rotulador independente: o acerto aqui é secundário e serve só
para dizer que as respostas não são aleatórias. A alegação deste exemplo é LATÊNCIA. Nomes e telefones fictícios.
Inclui os casos difíceis da spec: nome de pessoa que é bairro, "visita" como busca × agendamento, número que é
código de imóvel × telefone, dois destinos, texto colado, abreviação de corretor.
"""

DESTINOS = ["buscar_cliente", "buscar_imovel", "criar_tarefa", "abrir_relatorio", "agendar_visita",
            "enviar_mensagem", "nenhum"]

TEXTOS = [
    # buscar_cliente
    ("ficha da Mariana Costa", "buscar_cliente"),
    ("cliente 11 98877-1234", "buscar_cliente"),
    ("quem é o Rogério da Vila Mariana?", "buscar_cliente"),
    ("procurar lead Juliano Pereira", "buscar_cliente"),
    ("abrir cadastro do Sr. Antônio Ramos", "buscar_cliente"),
    ("cli joana silva", "buscar_cliente"),
    ("telefone 21 99654-0088 é de quem", "buscar_cliente"),
    ("histórico do cliente Marcelo Pinheiros", "buscar_cliente"),
    ("leads que entraram hoje pelo site", "buscar_cliente"),
    ("Pinheiros, Carla — contato", "buscar_cliente"),
    # buscar_imovel
    ("apto 2 dorms Pinheiros até 600 mil", "buscar_imovel"),
    ("imóvel AP-48213", "buscar_imovel"),
    ("casas em Alphaville com piscina", "buscar_imovel"),
    ("código 7731", "buscar_imovel"),
    ("imóveis que já receberam visita esta semana", "buscar_imovel"),
    ("cobertura na Vila Mariana 3 vagas", "buscar_imovel"),
    ("ap 3q mooca 400k", "buscar_imovel"),
    ("terrenos acima de 500 m² zona sul", "buscar_imovel"),
    ("o que temos de sala comercial na Paulista", "buscar_imovel"),
    ("AP-10992 ainda está disponível?", "buscar_imovel"),
    # criar_tarefa
    ("lembrar de ligar pro Juliano amanhã 9h", "criar_tarefa"),
    ("tarefa: enviar contrato da Mariana até sexta", "criar_tarefa"),
    ("anotar follow-up com Carla Pinheiros", "criar_tarefa"),
    ("cobrar documentação do AP-48213 na segunda", "criar_tarefa"),
    ("me lembra de pedir as chaves do 7731", "criar_tarefa"),
    ("criar pendência: avaliar imóvel da Rua Augusta 120", "criar_tarefa"),
    ("fup antonio qui 14h", "criar_tarefa"),
    ("to-do renovar anúncio da cobertura", "criar_tarefa"),
    ("depois da visita, lembrar de ligar pra Joana", "criar_tarefa"),
    # abrir_relatorio
    ("relatório de vendas de setembro", "abrir_relatorio"),
    ("quantos leads vieram do Instagram este mês", "abrir_relatorio"),
    ("funil por corretor", "abrir_relatorio"),
    ("comissões pagas no trimestre", "abrir_relatorio"),
    ("visitas realizadas por semana", "abrir_relatorio"),
    ("rel conversão out/26", "abrir_relatorio"),
    ("gráfico de propostas por bairro", "abrir_relatorio"),
    ("ranking de imóveis mais visitados", "abrir_relatorio"),
    ("fechamentos acima de 1 milhão no ano", "abrir_relatorio"),
    # agendar_visita
    ("visita do Juliano no AP-48213 sábado 10h", "agendar_visita"),
    ("marcar visita Mariana cobertura Vila Mariana", "agendar_visita"),
    ("agendar Carla no 7731 quinta de manhã", "agendar_visita"),
    ("levar o Sr. Antônio na casa de Alphaville amanhã", "agendar_visita"),
    ("vis joana ap mooca sex 16h", "agendar_visita"),
    ("remarcar a visita do Rogério para terça", "agendar_visita"),
    ("Marcelo quer ver a sala da Paulista hoje às 18h", "agendar_visita"),
    ("reservar horário de visita no terreno da zona sul", "agendar_visita"),
    ("visita 21 99654-0088 AP-10992 dom 11h", "agendar_visita"),
    # enviar_mensagem
    ("mandar whats pra Mariana confirmando sábado", "enviar_mensagem"),
    ("avisar o Juliano que o AP-48213 baixou de preço", "enviar_mensagem"),
    ("responder a Carla sobre as fotos", "enviar_mensagem"),
    ("msg antonio: chaves liberadas", "enviar_mensagem"),
    ("enviar e-mail com a proposta para o Rogério", "enviar_mensagem"),
    ("escrever para 11 98877-1234: bom dia, podemos falar?", "enviar_mensagem"),
    ("mandar os documentos do 7731 pra Joana", "enviar_mensagem"),
    ("avisar o Marcelo que a visita foi cancelada", "enviar_mensagem"),
    ("agradecer a Carla pela visita de ontem", "enviar_mensagem"),
    # nenhum (não é comando: rascunho colado, pergunta ao suporte, texto solto)
    ("como faço para mudar minha senha?", "nenhum"),
    ("Prezado cliente, conforme conversado, segue em anexo o", "nenhum"),
    ("o sistema está lento hoje", "nenhum"),
    ("qwerty asdf", "nenhum"),
    ("bom dia pessoal, reunião às 9", "nenhum"),
    ("Imóvel com 3 dormitórios, 2 vagas, lazer completo, aceita financiamento", "nenhum"),
    ("obrigado, pessoal!", "nenhum"),
    ("por que o relatório não abre no celular?", "nenhum"),
    ("rascunho: lembrar que o Juliano prefere manhã", "nenhum"),
    ("preciso de ajuda com o login", "nenhum"),
]

assert len(TEXTOS) >= 60, len(TEXTOS)
assert all(10 <= len(t) <= 80 for t, _ in TEXTOS), [t for t, _ in TEXTOS if not 10 <= len(t) <= 80]
assert all(d in DESTINOS for _, d in TEXTOS)
