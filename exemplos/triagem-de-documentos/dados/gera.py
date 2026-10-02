"""Gerador dos dados do triagem-de-documentos (rotulador: fable, 2026-10-02). Só biblioteca padrão.

Monta `documentos.json`, `rascunho.json`, `condicoes_ajuste.json` e `condicoes_teste.json` a partir de um
banco de seções escritas à mão (abaixo) e de RECEITAS explícitas por documento (qual variante entra em cada
seção). A semente fixa só sorteia nomes, valores e datas; o que cada documento afirma, nega, revoga ou omite
é decidido pela receita, e o gabarito das condições é calculado desses fatos de autoria (ver LEIA-ME.md).

Uso: python -X utf8 exemplos/triagem-de-documentos/dados/gera.py
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SEED = 20261002
VERSAO = "2026-10-02"
VERSAO_CONDICOES = "2026-10-02b"  # v2: condições compostas escritas com " E " (TD-A03, TD-T03)
AUTOR = "fable"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
EXT = {2: "dois", 3: "três", 5: "cinco", 6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez", 11: "onze",
       12: "doze", 15: "quinze", 20: "vinte", 24: "vinte e quatro", 30: "trinta", 36: "trinta e seis"}


def ext(n: int) -> str:
    return EXT[n]


def reais(n: int) -> str:
    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def data_ext(d: date) -> str:
    dia = "1º" if d.day == 1 else str(d.day)
    return f"{dia} de {MESES[d.month - 1]} de {d.year}"


def soma_meses(d: date, meses: int) -> date:
    m = d.month - 1 + meses
    return date(d.year + m // 12, m % 12 + 1, d.day)


PESSOAS = ["Helena Prado Varela", "Otávio Ribeiro Nunes", "Marina Castelo Dias", "Rogério Albuquerque Sá",
           "Camila Fontes Barroso", "Teodoro Lins Pacheco", "Beatriz Sampaio Queiroz", "Fábio Monteiro Rezende",
           "Lúcia Andrade Peixoto", "Renato Vilas-Boas Figueira", "Isadora Cunha Teles", "Gustavo Paranhos Lemos",
           "Débora Furtado Maciel", "Anselmo Guedes Portela", "Patrícia Noronha Aguiar", "Caio Bittencourt Salles",
           "Vera Lúcia Taveira", "Mauro Esteves Carvalhal", "Joana Pimentel Arruda", "Sérgio Lacerda Quintão"]
EMPRESAS = ["Vértice Soluções Digitais Ltda.", "Alameda Comércio de Bebidas Ltda.", "Horizonte Contabilidade S/S",
            "Grupo Pinheiral Participações Ltda.", "Clínica Odontológica Sorriso Pleno Ltda.",
            "Oficina Mecânica Dois Irmãos ME", "Serra Azul Tecnologia Ltda.", "Padaria Estrela do Norte EIRELI",
            "Cooperativa Agrícola Vale do Ipê", "Studio Lumen Arquitetura Ltda.", "Escola de Idiomas Ponte Nova Ltda.",
            "Transportadora Rota Sul Ltda.", "Farmácia Bem Viver Ltda.", "Mercado Quatro Estações Ltda.",
            "Construtora Marquesa Engenharia Ltda.", "Agência Pulso Comunicação Ltda.", "Nutrivida Alimentos Ltda.",
            "Distribuidora Planalto de Autopeças Ltda.", "Hotel Pousada do Mirante Ltda.", "Lavanderia Sol Nascente ME"]
CONDOMINIOS = ["Condomínio Edifício Jardim das Acácias", "Condomínio Residencial Parque Mirante",
               "Condomínio Solar das Palmeiras", "Condomínio Edifício Monte Líbano", "Condomínio Vila Serena",
               "Condomínio Residencial Bosque Alto", "Condomínio Edifício Aurora", "Condomínio Portal do Lago",
               "Condomínio Residencial Ipê Amarelo", "Condomínio Edifício Dom Pedro", "Condomínio Reserva das Araucárias"]
ENDERECOS = ["Rua das Hortênsias, 412, apto. 73", "Avenida Brigadeiro Lima, 1.880, sala 1204", "Rua Coronel Bento, 97",
             "Alameda dos Jacarandás, 250, casa 4", "Rua Sete de Abril, 1.015, loja 2", "Travessa do Comércio, 38",
             "Rua Professor Anísio, 640, apto. 21", "Avenida das Nações, 3.300, conjunto 502", "Rua Pedra Azul, 155",
             "Rua Dona Francisca, 2.209, galpão B", "Rua Flor de Lis, 71, apto. 101"]
CIDADES = ["Campinas/SP", "Curitiba/PR", "Belo Horizonte/MG", "Porto Alegre/RS", "Florianópolis/SC", "Goiânia/GO",
           "Recife/PE", "Santos/SP", "Londrina/PR", "Juiz de Fora/MG", "Niterói/RJ"]
CAMARAS = ["Câmara de Mediação e Arbitragem Empresarial do Sul", "Centro de Arbitragem da Associação Comercial",
           "Câmara Brasileira de Mediação Imobiliária"]
OBRAS = ["a impermeabilização da laje do térreo e a troca da manta da cobertura",
         "a reforma completa da fachada, com recuperação das pastilhas e nova pintura",
         "a modernização dos dois elevadores sociais", "a reforma do salão de festas e da churrasqueira",
         "a troca da tubulação de gás das prumadas", "a instalação de gerador para as áreas comuns",
         "a reforma do playground e a troca do piso emborrachado", "a recuperação estrutural da rampa da garagem"]
EMPRESAS_OBRA = ["Impermax Engenharia Ltda.", "Fachadas Prime Serviços Ltda.", "ElevaTec Manutenção Ltda.",
                 "Reformar Construções ME", "GasSeg Instalações Ltda.", "Energiza Geradores Ltda.",
                 "Parque & Lazer Equipamentos Ltda.", "Estrutura Forte Engenharia Ltda."]
EMPRESAS_SEG = ["VigiaNet Monitoramento Ltda.", "Olhar Seguro Sistemas Ltda.", "Portão Inteligente Automação ME",
                "Sentinela Tecnologia Ltda."]

# ----------------------------------------------------------------------------------------------------------
# BANCO DE SEÇÕES — contrato de locação (placeholders entre chaves são preenchidos pelos parâmetros do doc)
# ----------------------------------------------------------------------------------------------------------
L_INTRO = {
    "res": ("Das partes e do objeto",
            "{locador}, doravante LOCADOR(A), e {locatario}, doravante LOCATÁRIO(A), celebram o presente contrato "
            "de locação residencial, que se rege pela Lei nº 8.245/1991 e pelas cláusulas seguintes. O objeto é o "
            "imóvel situado na {endereco}, {cidade}, composto de {descricao}, que o LOCATÁRIO declara ter "
            "vistoriado e recebido em bom estado de conservação, conforme laudo de vistoria assinado pelas partes "
            "e anexo a este instrumento. O imóvel destina-se exclusivamente a fins residenciais do LOCATÁRIO e de "
            "seus familiares, sendo vedada a mudança de destinação sem autorização escrita do LOCADOR."),
    "com": ("Das partes e do objeto",
            "{locador}, doravante denominado LOCADOR, e {locatario}, doravante denominado LOCATÁRIO, ajustam a "
            "locação não residencial do imóvel situado na {endereco}, {cidade}, {descricao}, destinado à "
            "atividade de {atividade}. O LOCATÁRIO declara conhecer o imóvel, suas instalações elétricas e "
            "hidráulicas e as condições de uso impostas pelo condomínio, responsabilizando-se pela obtenção dos "
            "alvarás e licenças necessários ao funcionamento. Qualquer alteração da atividade exercida depende de "
            "anuência prévia e expressa do LOCADOR. O laudo de vistoria inicial, com fotografias, integra este "
            "contrato para todos os fins."),
}
L_PRAZO_BASE = ("Do prazo",
                "A locação vigorará pelo prazo de {prazo_ext} ({prazo}) meses, com início em {inicio} e término em "
                "{fim}, data em que o LOCATÁRIO se obriga a restituir o imóvel desocupado, limpo e nas condições em "
                "que o recebeu, ressalvado o desgaste natural pelo uso regular. ")
RENOV = {
    "afirm": "Findo o prazo e não havendo manifestação escrita de qualquer das partes com antecedência mínima de "
             "trinta dias, o contrato ficará automaticamente prorrogado por igual período, nas mesmas condições, "
             "admitindo-se então a denúncia a qualquer tempo mediante aviso prévio de trinta dias.",
    "neg": "As partes convencionam que este contrato NÃO se renovará automaticamente: findo o prazo, a "
           "continuidade da locação dependerá de novo instrumento escrito, e a permanência do LOCATÁRIO sem "
           "contrato será tratada como ocupação precária, sujeita à retomada do imóvel.",
    "sil": "Eventual prorrogação será tratada pelas partes em instrumento próprio. O LOCATÁRIO comunicará por "
           "escrito, com trinta dias de antecedência, a data prevista para a entrega das chaves, de modo a "
           "permitir o agendamento da vistoria final e a apuração de eventuais reparos.",
}
L_REAJ = {
    "igpm": ("Do aluguel e do reajuste",
             "O aluguel mensal é de R$ {valor}, a ser pago até o dia {dia} de cada mês, mediante depósito na conta "
             "indicada pelo LOCADOR ou boleto bancário. O valor será reajustado anualmente, a cada doze meses "
             "contados do início da locação, pela variação acumulada do IGP-M/FGV no período; em caso de extinção "
             "do índice, aplicar-se-á o que vier a substituí-lo oficialmente. O atraso no pagamento sujeita o "
             "LOCATÁRIO a multa moratória de dez por cento e juros de um por cento ao mês, sem prejuízo da "
             "atualização pelo mesmo índice até o efetivo pagamento."),
    "ipca": ("Do aluguel e do reajuste",
             "O aluguel mensal é de R$ {valor}, a ser pago até o dia {dia} de cada mês, mediante depósito na conta "
             "indicada pelo LOCADOR ou boleto bancário. O valor será reajustado anualmente, a cada doze meses "
             "contados do início da locação, pela variação acumulada do IPCA/IBGE no período; em caso de extinção "
             "do índice, aplicar-se-á o que vier a substituí-lo oficialmente. O atraso no pagamento sujeita o "
             "LOCATÁRIO a multa moratória de dez por cento e juros de um por cento ao mês, sem prejuízo da "
             "atualização pelo mesmo índice até o efetivo pagamento."),
    "sem": ("Do aluguel",
            "O aluguel mensal é de R$ {valor}, a ser pago até o dia {dia} de cada mês, mediante depósito na conta "
            "indicada pelo LOCADOR ou boleto bancário. O valor permanecerá fixo durante toda a vigência deste "
            "contrato, sem aplicação de qualquer índice de reajuste, salvo se as partes, de comum acordo e por "
            "escrito, convencionarem novo valor em termo aditivo. O atraso no pagamento sujeita o LOCATÁRIO a multa "
            "moratória de dez por cento e juros de um por cento ao mês, contados do vencimento até o efetivo "
            "pagamento, independentemente de notificação."),
    "ind": ("Do aluguel e do reajuste",
            "O aluguel mensal é de R$ {valor}, a ser pago até o dia {dia} de cada mês, mediante depósito na conta "
            "indicada pelo LOCADOR ou boleto bancário. O reajuste anual observará índice a ser definido de comum "
            "acordo entre as partes por ocasião de cada aniversário contratual, tomando-se como referência os "
            "indicadores oficiais de inflação divulgados no período; não havendo acordo, prevalecerá o valor "
            "vigente até a assinatura de termo aditivo. O atraso no pagamento sujeita o LOCATÁRIO a multa "
            "moratória de dez por cento e juros de um por cento ao mês."),
}
L_GAR = {
    "fiador": ("Da garantia",
               "Para garantia das obrigações assumidas, {fiador}, qualificado(a) no anexo, assina este instrumento na "
               "condição de FIADOR(A) e principal pagador(a), solidariamente responsável com o LOCATÁRIO por "
               "aluguéis, encargos, multas e eventuais danos ao imóvel, renunciando expressamente ao benefício de "
               "ordem previsto no Código Civil. O FIADOR declara ser proprietário de imóvel livre e desembaraçado "
               "nesta comarca, apresentando certidão atualizada. Em caso de falecimento, insolvência ou alienação "
               "do bem do FIADOR, o LOCATÁRIO deverá apresentar nova garantia no prazo de trinta dias, sob pena de "
               "infração contratual."),
    "caucao": ("Da garantia",
               "A garantia da locação é prestada na modalidade de caução em dinheiro, no valor equivalente a três "
               "aluguéis, depositada pelo LOCATÁRIO em caderneta de poupança conjunta aberta especificamente para "
               "este fim. O valor, acrescido dos rendimentos, será restituído ao LOCATÁRIO em até trinta dias após a "
               "entrega das chaves e a aprovação da vistoria final, deduzidos eventuais débitos de aluguel, encargos "
               "ou reparos apurados. A caução não poderá ser utilizada pelo LOCATÁRIO para pagamento dos últimos "
               "aluguéis, salvo autorização escrita do LOCADOR. Não há fiador neste contrato."),
    "seguro": ("Da garantia",
               "O LOCATÁRIO contratará seguro-fiança locatícia junto a seguradora autorizada, com cobertura mínima "
               "de doze aluguéis e encargos, além de danos ao imóvel, mantendo a apólice vigente e paga durante "
               "toda a locação e suas eventuais prorrogações. A apólice deverá ser apresentada ao LOCADOR antes da "
               "entrega das chaves e renovada com antecedência de quinze dias do vencimento. A não renovação do "
               "seguro autoriza o LOCADOR a considerar rescindido o contrato por culpa do LOCATÁRIO. Esta é a única "
               "garantia da locação, não havendo fiador nem caução."),
}
L_RESC = {
    "multa": ("Da rescisão antecipada",
              "O LOCATÁRIO poderá devolver o imóvel antes do término do prazo, desde que pague ao LOCADOR multa "
              "equivalente a {n_ext} ({n}) aluguéis vigentes à época da devolução, calculada proporcionalmente ao "
              "período restante do contrato, na forma do artigo 4º da Lei do Inquilinato. Ficará dispensado da "
              "multa o LOCATÁRIO transferido pelo empregador para outra localidade, mediante comprovação e aviso "
              "prévio de trinta dias. O LOCADOR não poderá reaver o imóvel durante o prazo contratual, salvo nas "
              "hipóteses legais, respondendo, se o fizer, por igual multa em favor do LOCATÁRIO."),
    "neg": ("Da rescisão antecipada",
            "As partes convencionam expressamente que NÃO haverá multa em caso de devolução antecipada do imóvel "
            "pelo LOCATÁRIO, bastando comunicação escrita com antecedência mínima de trinta dias e a entrega das "
            "chaves após vistoria. A dispensa da multa é uma liberalidade do LOCADOR, em razão do curto prazo da "
            "locação, e não se estende a débitos de aluguel, encargos ou reparos devidos até a efetiva "
            "desocupação, que permanecem exigíveis. O LOCADOR, por sua vez, não poderá retomar o imóvel antes do "
            "término do prazo, salvo nas hipóteses previstas em lei."),
    "atraso": ("Da multa por atraso",
               "O não pagamento do aluguel e dos encargos até a data de vencimento sujeitará o LOCATÁRIO a multa de "
               "dez por cento sobre o valor devido, juros de mora de um por cento ao mês e atualização monetária "
               "até a data do efetivo pagamento, independentemente de notificação. O atraso superior a sessenta "
               "dias autoriza o LOCADOR a propor ação de despejo por falta de pagamento, cabendo ao LOCATÁRIO as "
               "custas e os honorários advocatícios de vinte por cento. Esta cláusula trata apenas da mora no "
               "pagamento; a devolução antecipada do imóvel não é regulada neste contrato e seguirá o que dispõe a "
               "lei."),
}
L_USO = {
    "proib": ("Da sublocação e da cessão",
              "É vedado ao LOCATÁRIO sublocar, ceder, emprestar ou transferir, no todo ou em parte, a qualquer "
              "título, os direitos decorrentes deste contrato, sem o consentimento prévio e escrito do LOCADOR. A "
              "infração a esta cláusula constitui falta grave e autoriza a rescisão do contrato, com a retomada do "
              "imóvel e a cobrança das penalidades previstas. A eventual tolerância do LOCADOR quanto à presença de "
              "terceiros no imóvel não configura anuência tácita nem novação. O LOCATÁRIO responde pessoalmente "
              "por todos os ocupantes do imóvel e por seus atos."),
    "perm": ("Da sublocação",
             "O LOCADOR autoriza desde já o LOCATÁRIO a sublocar parcialmente o imóvel, inclusive por temporada, "
             "desde que comunique por escrito o nome dos sublocatários e o período, mantendo-se integralmente "
             "responsável perante o LOCADOR pelo cumprimento de todas as obrigações contratuais e pela conservação "
             "do imóvel. A sublocação não poderá exceder o prazo deste contrato nem alterar a destinação pactuada. "
             "O sublocatário não terá relação direta com o LOCADOR, e a extinção da locação principal extingue "
             "automaticamente a sublocação, sem direito a indenização."),
    "titulo": ("Do uso e da sublocação",
               "O LOCATÁRIO obriga-se a usar o imóvel com zelo, respeitando a convenção e o regimento interno do "
               "condomínio, o sossego da vizinhança e as posturas municipais, bem como a comunicar imediatamente "
               "ao LOCADOR qualquer dano, infiltração ou defeito nas instalações. Correm por conta do LOCATÁRIO os "
               "reparos de pequena monta decorrentes do uso, como troca de lâmpadas, torneiras e vidros, e por "
               "conta do LOCADOR os reparos estruturais e os decorrentes de vício anterior à locação. Ao final, o "
               "imóvel será devolvido pintado nas cores originais e com as mesmas chaves entregues."),
}
L_ANIM = {
    "perm": ("Dos animais de estimação",
             "O LOCADOR autoriza o LOCATÁRIO a manter no imóvel animais de estimação domésticos, de qualquer porte, "
             "respeitadas as regras do condomínio e as normas sanitárias, respondendo o LOCATÁRIO por danos "
             "causados pelos animais ao imóvel ou a terceiros e pela limpeza das áreas por eles utilizadas. Ao "
             "final da locação, eventuais danos atribuíveis aos animais, como arranhões em portas e pisos, serão "
             "reparados às expensas do LOCATÁRIO antes da devolução das chaves. A autorização não se estende à "
             "criação ou ao comércio de animais no imóvel."),
    "proib": ("Dos animais",
              "Não é permitida a permanência de animais de qualquer espécie no imóvel, ainda que de pequeno porte "
              "ou em caráter temporário, em razão das regras do condomínio e da conservação do piso de madeira. A "
              "infração a esta cláusula, após notificação não atendida em dez dias, constitui infração contratual "
              "grave e autoriza a rescisão por culpa do LOCATÁRIO, com as penalidades previstas. O LOCATÁRIO "
              "declara ciência de que a vedação consta também do regimento interno do condomínio, a ele entregue "
              "nesta data, juntamente com a convenção."),
    "ind": ("Dos animais",
            "A permanência de animais de pequeno porte no imóvel dependerá de consulta prévia ao LOCADOR, que "
            "avaliará caso a caso, considerando a espécie, o porte e as regras do condomínio, e responderá por "
            "escrito em até quinze dias. Até que haja resposta, o LOCATÁRIO não deverá introduzir animais no "
            "imóvel. Caso autorizada, a permanência sujeita o LOCATÁRIO à reparação de quaisquer danos causados "
            "pelo animal e ao cumprimento das normas sanitárias e de convivência do condomínio."),
}
FORO = {
    "com": ("Do foro",
            "As partes elegem o foro da comarca de {cidade_foro} para dirimir quaisquer questões oriundas deste "
            "contrato, com renúncia expressa a qualquer outro, por mais privilegiado que seja. Antes de recorrer ao "
            "Judiciário, as partes se comprometem a tentar solução amigável por meio de reunião presencial ou por "
            "videoconferência, no prazo de quinze dias contados da notificação de uma pela outra. Este contrato é "
            "firmado em duas vias de igual teor, na presença de duas testemunhas, e obriga as partes, seus "
            "herdeiros e sucessores."),
    "arb": ("Da arbitragem",
            "Toda controvérsia decorrente deste contrato, inclusive quanto à sua validade, interpretação, execução "
            "ou rescisão, será resolvida definitivamente por arbitragem, administrada pela {camara}, por árbitro "
            "único escolhido conforme o regulamento da instituição, com sede em {cidade_foro} e em língua "
            "portuguesa. As partes reconhecem o caráter vinculante da sentença arbitral e renunciam ao foro "
            "judicial, ressalvadas as medidas de urgência e a execução de obrigações líquidas, que poderão ser "
            "levadas diretamente ao Judiciário."),
    "titulo": ("Do foro e da arbitragem",
               "Fica eleito o foro da comarca de {cidade_foro}, com exclusão de qualquer outro, para as ações "
               "decorrentes deste instrumento. As partes comprometem-se, antes de qualquer medida judicial, a "
               "buscar composição amigável em reunião convocada por notificação escrita, com prazo de resposta de "
               "dez dias. Os custos de eventual demanda, inclusive honorários advocatícios fixados em vinte por "
               "cento, correrão por conta da parte vencida. O contrato é assinado em duas vias na presença de "
               "testemunhas e poderá ser registrado, se as partes assim desejarem, no cartório de títulos e "
               "documentos."),
}
L_FIN = {
    "revmulta": ("Das disposições finais",
                 "Em razão da negociação havida entre as partes na assinatura deste instrumento, fica sem efeito a "
                 "multa por devolução antecipada prevista na cláusula de rescisão antecipada, que as partes "
                 "consideram não escrita; a devolução antecipada dependerá apenas de aviso prévio de trinta dias e "
                 "vistoria. As demais cláusulas permanecem íntegras. Este contrato obriga as partes e seus "
                 "sucessores, e só poderá ser alterado por termo aditivo assinado por ambas. As partes elegem o "
                 "endereço indicado no preâmbulo para o recebimento de notificações."),
    "revsub": ("Das disposições finais",
               "As partes, de comum acordo, revogam a vedação prevista na cláusula sobre sublocação e cessão, "
               "ficando o LOCATÁRIO autorizado a sublocar o imóvel, no todo ou em parte, sem necessidade de "
               "consentimento adicional, desde que comunique ao LOCADOR o nome dos ocupantes e permaneça "
               "responsável solidário por todas as obrigações deste contrato. As demais cláusulas permanecem "
               "íntegras. Este contrato obriga as partes e seus sucessores, só podendo ser alterado por termo "
               "aditivo assinado por ambas, e as notificações serão feitas por escrito aos endereços do preâmbulo."),
    "revrenov": ("Das disposições finais",
                 "As partes, de comum acordo, afastam a prorrogação automática prevista na cláusula de prazo: findo "
                 "o termo contratual, a locação só prosseguirá mediante novo contrato escrito, considerando-se a "
                 "permanência do LOCATÁRIO sem instrumento como ocupação precária. As demais cláusulas permanecem "
                 "íntegras. Este contrato obriga as partes e seus sucessores, só podendo ser alterado por termo "
                 "aditivo assinado por ambas, e as comunicações entre as partes serão feitas por escrito aos "
                 "endereços indicados no preâmbulo, inclusive por mensagem eletrônica com confirmação de "
                 "recebimento."),
    "fiadorchaves": ("Das disposições finais",
                     "A responsabilidade do FIADOR, prevista na cláusula de garantia, estende-se até a efetiva "
                     "devolução das chaves e a aprovação da vistoria final, ainda que a locação venha a ser "
                     "prorrogada por prazo indeterminado, o que o FIADOR declara aceitar expressamente, nos termos "
                     "do artigo 39 da Lei nº 8.245/1991. As demais cláusulas permanecem íntegras. O contrato obriga "
                     "as partes e seus sucessores, só pode ser alterado por termo aditivo assinado por todos, e as "
                     "comunicações serão feitas por escrito aos endereços do preâmbulo."),
    "chavessemfiador": ("Das disposições finais",
                        "A responsabilidade do LOCATÁRIO pelos aluguéis, encargos e conservação do imóvel estende-se "
                        "até a efetiva devolução das chaves e a aprovação da vistoria final, ainda que a locação "
                        "seja prorrogada por prazo indeterminado, não bastando a simples desocupação para "
                        "encerrá-la. As demais cláusulas permanecem íntegras. O contrato obriga as partes e seus "
                        "sucessores, só pode ser alterado por termo aditivo assinado por ambas, e as comunicações "
                        "serão feitas por escrito aos endereços indicados no preâmbulo, inclusive por mensagem "
                        "eletrônica."),
    "plain": ("Das disposições finais",
              "Este contrato obriga as partes e seus herdeiros e sucessores, e só poderá ser alterado por termo "
              "aditivo assinado por ambas. A tolerância de uma parte quanto ao descumprimento de qualquer cláusula "
              "pela outra não implica renúncia nem novação. As comunicações entre as partes serão feitas por "
              "escrito aos endereços indicados no preâmbulo, inclusive por mensagem eletrônica com confirmação de "
              "recebimento. Os tributos e taxas incidentes sobre o imóvel, como o IPTU, correm por conta do "
              "LOCATÁRIO, e o seguro contra incêndio, por conta do LOCADOR."),
}

# ----------------------------------------------------------------------------------------------------------
# BANCO DE SEÇÕES — prestação de serviço
# ----------------------------------------------------------------------------------------------------------
S_OBJ = {
    "ti": dict(servico="sustentação e evolução do sistema de gestão da CONTRATANTE",
               detalhe="correção de defeitos, pequenas melhorias, monitoramento do ambiente e atendimento de chamados",
               local="remotamente, com visitas mensais à sede da CONTRATANTE",
               excluido="o desenvolvimento de novos módulos e a aquisição de licenças"),
    "mkt": dict(servico="gestão de redes sociais e campanhas de anúncios digitais",
                detalhe="planejamento mensal, produção de peças, publicação, gestão de mídia paga e relatório de resultados",
                local="nas dependências da CONTRATADA, com reunião quinzenal presencial",
                excluido="a verba de mídia, que será paga diretamente às plataformas, e a produção de vídeo"),
    "limp": dict(servico="limpeza e conservação predial da sede da CONTRATANTE",
                 detalhe="limpeza diária das áreas internas, limpeza semanal de vidros e fachada térrea e reposição de insumos",
                 local="nas instalações da CONTRATANTE, de segunda a sexta, das 7h às 16h",
                 excluido="a limpeza de fachada em altura e a jardinagem"),
}
S_OBJ_T = ("Do objeto",
           "A CONTRATADA {contratada} prestará à CONTRATANTE {contratante} os serviços de {servico}, compreendendo "
           "{detalhe}, conforme a proposta técnica anexa, que integra este contrato. Os serviços serão executados "
           "{local} por profissionais da CONTRATADA, sem vínculo empregatício com a CONTRATANTE, cabendo à "
           "CONTRATADA todos os encargos trabalhistas, previdenciários e fiscais de sua equipe. Não estão incluídos "
           "no objeto {excluido}, que poderão ser contratados à parte mediante proposta específica.")
S_PRAZO_BASE = ("Da vigência",
                "O presente contrato vigorará por {prazo_ext} ({prazo}) meses a contar de {inicio}. Os serviços terão "
                "início na data de assinatura, com período de transição de quinze dias em que a CONTRATADA receberá "
                "da CONTRATANTE as informações, acessos e documentos necessários. ")
S_RENOV = {
    "afirm": "Ao término, não havendo denúncia escrita por qualquer das partes com antecedência de trinta dias, o "
             "contrato será renovado automaticamente por períodos sucessivos de doze meses, nas mesmas condições, "
             "inclusive de preço, ressalvado o reajuste previsto neste instrumento.",
    "neg": "O contrato não se renovará automaticamente; a continuidade dos serviços após o termo final dependerá "
           "de novo instrumento assinado pelas partes, e a prestação eventual sem contrato não gerará obrigação de "
           "renovação nem direito a indenização.",
    "sil": "A eventual prorrogação será objeto de termo aditivo a ser negociado pelas partes com antecedência "
           "mínima de sessenta dias do término, ocasião em que serão revistos escopo, equipe alocada e preço.",
}
S_REM_BASE = ("Da remuneração e do reajuste",
              "A CONTRATANTE pagará à CONTRATADA o valor mensal de R$ {valor}, mediante apresentação de nota fiscal "
              "até o dia 25 de cada mês, com vencimento em dez dias. ")
S_REAJ = {
    "igpm": "O valor será reajustado a cada doze meses pela variação acumulada do IGP-M/FGV, ou pelo índice que o "
            "substituir. O atraso sujeita a CONTRATANTE a multa de dois por cento e juros de um por cento ao mês. "
            "Despesas com deslocamento fora da região metropolitana serão reembolsadas mediante comprovação e "
            "aprovação prévia.",
    "ipca": "O valor será reajustado a cada doze meses pela variação acumulada do IPCA/IBGE, ou pelo índice que o "
            "substituir. O atraso sujeita a CONTRATANTE a multa de dois por cento e juros de um por cento ao mês. "
            "Despesas com deslocamento fora da região metropolitana serão reembolsadas mediante comprovação e "
            "aprovação prévia.",
    "sem": "O valor é fixo por toda a vigência e não sofrerá reajuste, salvo acordo escrito em termo aditivo. O "
           "atraso sujeita a CONTRATANTE a multa de dois por cento e juros de um por cento ao mês. Despesas com "
           "deslocamento fora da região metropolitana serão reembolsadas mediante comprovação e aprovação prévia.",
}
S_EXCL = {
    "afirm": ("Da exclusividade",
              "Durante a vigência deste contrato, a CONTRATADA prestará os serviços objeto deste instrumento com "
              "exclusividade à CONTRATANTE no segmento de {segmento}, abstendo-se de atender, direta ou "
              "indiretamente, empresas concorrentes da CONTRATANTE, assim entendidas as listadas no anexo ou que "
              "venham a atuar no mesmo mercado. A exclusividade abrange a equipe alocada e os sócios da CONTRATADA. "
              "O descumprimento autoriza a rescisão imediata e a cobrança de multa equivalente a três meses de "
              "remuneração, sem prejuízo de perdas e danos. A CONTRATANTE, por sua vez, não se obriga a contratar "
              "os serviços exclusivamente da CONTRATADA."),
    "parcial": ("Da exclusividade",
                "A CONTRATADA obriga-se a não prestar serviços da mesma natureza, enquanto vigorar este contrato, às "
                "empresas expressamente nominadas no Anexo II (concorrentes diretas da CONTRATANTE), ficando livre "
                "para atender quaisquer outros clientes, inclusive do mesmo setor, desde que não haja conflito de "
                "interesse concreto, a ser comunicado previamente à CONTRATANTE. A lista do Anexo II poderá ser "
                "atualizada uma vez por semestre, por acordo escrito. A violação desta cláusula sujeita a "
                "CONTRATADA à multa de dois meses de remuneração e autoriza a rescisão motivada."),
    "neg": ("Da não exclusividade",
            "As partes esclarecem que este contrato NÃO estabelece exclusividade de nenhuma das partes: a "
            "CONTRATADA poderá prestar serviços iguais ou semelhantes a terceiros, inclusive a concorrentes da "
            "CONTRATANTE, e a CONTRATANTE poderá contratar outros prestadores para os mesmos serviços, a seu "
            "critério. A CONTRATADA obriga-se apenas a não utilizar, em favor de terceiros, informações "
            "confidenciais da CONTRATANTE, e a comunicar conflito de interesse concreto. A ausência de "
            "exclusividade foi considerada na fixação do preço."),
    "titulo": ("Da exclusividade, da confidencialidade e da propriedade intelectual",
               "Todo material, código, layout, relatório e base de dados produzidos na execução deste contrato "
               "pertencem à CONTRATANTE desde a sua criação, cedendo a CONTRATADA, de forma irrevogável e sem ônus "
               "adicional, os direitos patrimoniais correspondentes. As informações técnicas, comerciais e "
               "financeiras a que a CONTRATADA tiver acesso são confidenciais e não poderão ser divulgadas, "
               "copiadas ou utilizadas para fins estranhos ao contrato, durante a vigência e por cinco anos após o "
               "término, sob pena de multa de vinte por cento do valor anual e perdas e danos. A CONTRATADA poderá "
               "citar a CONTRATANTE em seu portfólio, sem detalhar o escopo."),
}
S_CONF = ("Da confidencialidade",
          "A CONTRATADA obriga-se a manter sigilo sobre todas as informações, dados, documentos e processos da "
          "CONTRATANTE a que tiver acesso em razão deste contrato, utilizando-os exclusivamente para a execução dos "
          "serviços e limitando o acesso aos profissionais que deles necessitem, os quais assinarão termo de "
          "confidencialidade individual. A obrigação perdura por cinco anos após o término do contrato e não se "
          "aplica a informações públicas ou já conhecidas da CONTRATADA por meio legítimo. A violação sujeita a "
          "CONTRATADA à multa de vinte por cento do valor total do contrato, sem prejuízo da indenização por perdas "
          "e danos e da rescisão motivada.")
S_SLA = {
    "pen": ("Dos níveis de serviço",
            "A CONTRATADA atenderá chamados de severidade alta em até {sla} horas e os demais em até dois dias úteis, "
            "com disponibilidade mensal mínima de 99% para os serviços contratados. O descumprimento dos prazos ou "
            "da disponibilidade em um mês sujeita a CONTRATADA a desconto de {pen}% sobre a fatura do período para "
            "cada indicador não atingido, limitado a vinte por cento da remuneração mensal, aplicado "
            "automaticamente na nota fiscal seguinte. O descumprimento em três meses consecutivos autoriza a "
            "rescisão motivada pela CONTRATANTE. Os indicadores serão apurados em relatório mensal da CONTRATADA, "
            "sujeito a conferência."),
    "sem": ("Dos níveis de serviço",
            "A CONTRATADA envidará seus melhores esforços para atender chamados de severidade alta em até {sla} "
            "horas e os demais em até dois dias úteis, apresentando relatório mensal com os tempos de atendimento. "
            "Os prazos têm caráter de meta de desempenho, e as partes acordam que seu eventual descumprimento não "
            "gera, por si só, desconto, multa ou qualquer penalidade, devendo ser tratado em reunião de "
            "acompanhamento para ajuste de processos e de dimensionamento da equipe. Persistindo o problema por "
            "mais de três meses, qualquer das partes poderá propor a revisão do escopo ou do preço."),
    "ind": ("Dos níveis de serviço",
            "A CONTRATADA atenderá chamados críticos em até {sla} horas e os demais em até dois dias úteis, com "
            "apuração mensal dos tempos. O descumprimento reiterado dos prazos será registrado em ata de reunião de "
            "acompanhamento e poderá ensejar a revisão das condições deste contrato, inclusive de remuneração, a "
            "critério da CONTRATANTE e após notificação com prazo de trinta dias para regularização. As partes "
            "poderão, em termo aditivo, estabelecer tabela de descontos vinculada aos indicadores, o que não se "
            "presume."),
}
S_RESC = {
    "multa": ("Da rescisão",
              "Qualquer das partes poderá rescindir este contrato, sem motivo, mediante aviso prévio escrito de "
              "sessenta dias. A parte que rescindir sem observar o aviso, ou que der causa à rescisão por "
              "descumprimento, pagará à outra multa de {pct}% ({pct_ext} por cento) sobre o valor das parcelas "
              "vincendas até o término do prazo contratual. A rescisão por inadimplemento da CONTRATANTE por mais "
              "de sessenta dias dispensa aviso prévio. Na rescisão, a CONTRATADA entregará à CONTRATANTE todos os "
              "documentos, acessos e trabalhos em andamento, recebendo a remuneração proporcional aos serviços "
              "prestados até a data."),
    "neg": ("Da rescisão",
            "Qualquer das partes poderá rescindir o contrato a qualquer tempo, mediante aviso prévio de trinta dias, "
            "sem que seja devida multa, indenização ou compensação pela rescisão em si, remanescendo apenas a "
            "obrigação de pagar os serviços efetivamente prestados até a data do término e de devolver documentos "
            "e acessos. As partes reconhecem que a ausência de multa rescisória é condição essencial deste ajuste, "
            "refletida no preço mensal. O descumprimento de obrigações contratuais, contudo, continua sujeito à "
            "reparação de perdas e danos comprovados."),
}
S_NAOCONC = ("Da não concorrência",
             "A CONTRATADA e seus sócios obrigam-se, pelo prazo de doze meses contados do término deste contrato, a "
             "não contratar nem aliciar empregados da CONTRATANTE com quem tenham mantido contato em razão dos "
             "serviços, e a não desenvolver, para os concorrentes diretos da CONTRATANTE listados no anexo, solução "
             "equivalente à que foi objeto deste contrato, sob pena de multa de três meses de remuneração por "
             "infração. A obrigação não impede a CONTRATADA de exercer sua atividade regular com clientes de outros "
             "segmentos nem de contratar profissionais que a procurem espontaneamente.")
S_FIN = {
    "revmulta": ("Das disposições finais",
                 "Por acordo das partes nesta data, fica sem efeito a multa rescisória prevista na cláusula de "
                 "rescisão, que as partes consideram não escrita, bastando para a rescisão imotivada o aviso prévio "
                 "de sessenta dias ali previsto. As demais cláusulas permanecem íntegras. Este contrato só pode ser "
                 "alterado por termo aditivo assinado por ambas as partes, e nenhuma tolerância quanto ao "
                 "descumprimento de obrigação implica renúncia. As partes indicam no preâmbulo os endereços "
                 "eletrônicos válidos para notificações."),
    "revrenov": ("Das disposições finais",
                 "As partes, de comum acordo, afastam a renovação automática prevista na cláusula de vigência: ao "
                 "término do prazo, o contrato se extingue de pleno direito, e a continuidade dos serviços dependerá "
                 "de novo instrumento escrito. As demais cláusulas permanecem íntegras. Este contrato só pode ser "
                 "alterado por termo aditivo assinado por ambas as partes, e nenhuma tolerância quanto ao "
                 "descumprimento de obrigação implica renúncia. As notificações serão feitas por escrito aos "
                 "endereços do preâmbulo, inclusive eletrônicos."),
    "plain": ("Das disposições finais",
              "Este contrato não cria vínculo societário, trabalhista ou de representação entre as partes, e "
              "nenhuma delas poderá assumir obrigações em nome da outra. A CONTRATADA poderá subcontratar parte dos "
              "serviços com autorização escrita da CONTRATANTE, permanecendo responsável pela execução. As "
              "notificações serão feitas por escrito aos endereços do preâmbulo, inclusive eletrônicos. Eventual "
              "invalidade de uma cláusula não prejudica as demais. Este instrumento substitui todos os "
              "entendimentos anteriores entre as partes sobre o mesmo objeto e só pode ser alterado por termo "
              "aditivo assinado por ambas."),
}

# ----------------------------------------------------------------------------------------------------------
# BANCO DE SEÇÕES — ata de assembleia de condomínio
# ----------------------------------------------------------------------------------------------------------
A_ABERT = ("Abertura e verificação de quórum",
           "Aos {data_ext}, às {hora}, em {conv} convocação, reuniram-se no salão de festas do {condominio} os "
           "condôminos relacionados na lista de presença, representando {quorum}% das frações ideais, para a "
           "assembleia geral {tipo_ag} convocada por edital de {data_edital}. Assumiu a presidência dos trabalhos "
           "o condômino {presidente}, que convidou {secretario} para secretariar. O presidente declarou instalada a "
           "assembleia, {inst}, e passou à leitura da ordem do dia, que foi aprovada sem alterações pelos "
           "presentes.")
A_INST = {1: "verificado o quórum de maioria das frações ideais exigido em primeira convocação",
          2: "em segunda convocação, com qualquer número de presentes, conforme a convenção"}
A_CONTAS_BASE = ("Prestação de contas do exercício",
                 "O síndico apresentou o balanço do exercício de {ano}, com receitas de R$ {rec} e despesas de R$ "
                 "{desp}, acompanhado dos extratos bancários e dos comprovantes. ")
A_CONTAS = {
    "apr": "O conselho fiscal emitiu parecer favorável. Esclarecidas as dúvidas sobre o gasto com a manutenção dos "
           "elevadores e com a troca das bombas, as contas foram colocadas em votação e APROVADAS pela maioria dos "
           "presentes, com {abst} abstenções e nenhum voto contrário, dando-se quitação ao síndico pelo período. O "
           "saldo em caixa ao final do exercício, de R$ {saldo}, foi transferido ao fundo de reserva.",
    "ress": "O conselho fiscal apontou a ausência de três notas fiscais referentes ao serviço de jardinagem. Após "
            "debate, as contas foram APROVADAS COM RESSALVAS pela maioria dos presentes, comprometendo-se o síndico "
            "a apresentar os documentos faltantes em trinta dias, sob pena de reabertura do ponto na próxima "
            "assembleia. Com essa ressalva, foi dada quitação ao síndico pelo exercício, e o saldo de R$ {saldo} "
            "foi mantido em conta corrente.",
    "rej": "O conselho fiscal apresentou parecer contrário, apontando despesas sem comprovante no valor de R$ "
           "{semcomp} e pagamentos em duplicidade à empresa de limpeza. Após debate acalorado, as contas foram "
           "REJEITADAS por {votos} votos contra {votos2}, deliberando-se pela contratação de auditoria externa, "
           "cujo custo sairá do fundo de reserva, e pela convocação de nova assembleia para deliberar sobre as "
           "contas após o relatório da auditoria.",
    "adi": "O conselho fiscal informou que não concluiu a análise dos extratos bancários do segundo semestre. Por "
           "proposta do presidente, a deliberação sobre as contas foi ADIADA para assembleia extraordinária a ser "
           "convocada em até sessenta dias, sem que isso implique aprovação ou rejeição. Os condôminos presentes "
           "solicitaram que o balancete mensal passe a ser enviado por e-mail até o dia dez de cada mês.",
}
A_TAXA_BASE = ("Taxa condominial e previsão orçamentária",
               "A administradora apresentou a previsão orçamentária para o exercício de {ano2}, com aumento do custo "
               "da folha de funcionários e do contrato de manutenção dos elevadores. ")
A_TAXA = {
    "reaj": "Após discussão, foi APROVADO pela maioria dos presentes o reajuste da taxa condominial em {pct}% "
            "({pct_ext} por cento), passando a cota ordinária de R$ {taxa_antiga} para R$ {taxa_nova} por unidade "
            "de fração padrão, a partir da cobrança de {mes_ini}. Também foi mantido o rateio do fundo de reserva "
            "em cinco por cento da cota. Os condôminos inadimplentes não participaram da votação, conforme a "
            "convenção.",
    "mant": "Após discussão, decidiu-se MANTER a taxa condominial no valor atual de R$ {taxa_antiga}, sem reajuste "
            "neste exercício, compensando-se o aumento de custos com a redução das horas extras da portaria e com "
            "a renegociação do contrato de jardinagem, já em curso. A administradora alertou que a manutenção do "
            "valor poderá exigir revisão no meio do ano caso a inadimplência não seja reduzida. Foi mantido o "
            "rateio do fundo de reserva em cinco por cento da cota.",
    "rej": "A administradora propôs reajuste da taxa condominial em {pct_rej}% para recompor o fundo de reserva. "
           "Colocada em votação, a proposta foi REJEITADA pela maioria dos presentes, que entenderam que o fundo "
           "deve ser recomposto com o resultado das cobranças judiciais em andamento. A taxa permanece em R$ "
           "{taxa_antiga}. Ficou registrado o voto favorável ao reajuste de quatro condôminos, que pediram constar "
           "em ata a sua preocupação com o caixa.",
}
A_OBRA_BASE = ("Deliberação sobre obras nas áreas comuns",
               "Foram apresentados três orçamentos para {obra}, com valores entre R$ {o1} e R$ {o2}. ")
A_OBRA = {
    "apr": "Após esclarecimentos do síndico sobre o prazo de execução de {prazo_obra} dias e a garantia oferecida, "
           "a assembleia APROVOU, pela maioria dos presentes, a contratação da proposta de menor valor, da empresa "
           "{empresa_obra}, com rateio extraordinário em {parcelas} parcelas mensais a partir de {mes_ini}. O "
           "síndico ficou autorizado a assinar o contrato e a acompanhar a execução, prestando contas na próxima "
           "assembleia. Dois condôminos registraram voto contrário por entenderem que a obra poderia aguardar.",
    "rej": "Colocada em votação, a proposta foi REJEITADA pela maioria dos presentes, que consideraram o valor "
           "incompatível com a situação do caixa e pediram que o síndico obtenha novos orçamentos e apresente "
           "alternativa de execução por etapas em assembleia futura. Nenhuma obra foi autorizada neste ponto, e o "
           "rateio extraordinário proposto não será cobrado. Foi aprovada apenas a realização de reparos "
           "emergenciais, se necessários, dentro do orçamento ordinário.",
    "adi": "Diante do pedido de vários condôminos para análise mais detalhada dos orçamentos, e considerando que "
           "um deles foi recebido apenas na véspera, o presidente propôs e a assembleia ACEITOU adiar a "
           "deliberação para assembleia extraordinária a ser convocada em até quarenta e cinco dias, com envio "
           "prévio dos orçamentos por e-mail. Nenhuma contratação foi autorizada neste ponto, e o síndico ficou "
           "encarregado de obter um quarto orçamento.",
}
A_RETIF = ("Verificação de quórum qualificado e retificação",
           "Antes do encerramento, o conselho consultivo chamou a atenção para o artigo da convenção que exige "
           "aprovação de dois terços das frações ideais para obras de melhoramento voluptuário, como a deliberada no "
           "item sobre obras nas áreas comuns. Conferida a lista de presença, constatou-se que a proposta obteve "
           "apenas {pct_obra}% das frações ideais. O presidente declarou, então, SEM EFEITO a aprovação da obra "
           "registrada acima, que deverá ser submetida a nova assembleia especificamente convocada para esse fim, "
           "permanecendo válidas as demais deliberações desta ata.")
A_ANIM = {
    "lib": ("Regras sobre animais nas áreas comuns",
            "Após ampla discussão sobre a convivência com animais no condomínio, a assembleia APROVOU, por maioria, "
            "a alteração do regimento interno para permitir expressamente a permanência de animais de estimação "
            "nas unidades e sua circulação nas áreas comuns, desde que conduzidos com guia e, no caso de cães de "
            "grande porte, com focinheira, utilizando preferencialmente o elevador de serviço. Os tutores "
            "respondem pela limpeza e por danos causados. Fica revogado o artigo do regimento que vedava animais, "
            "considerado incompatível com o entendimento atual dos tribunais."),
    "proib": ("Regras sobre animais nas áreas comuns",
              "Após discussão, a assembleia decidiu MANTER a vedação à permanência de animais de estimação nas "
              "unidades e nas áreas comuns prevista no regimento interno, rejeitando a proposta de liberação "
              "apresentada por um grupo de moradores. A síndica ficou encarregada de notificar as unidades em "
              "desacordo, concedendo prazo de noventa dias para regularização, após o qual será aplicada a multa "
              "prevista na convenção. Registrou-se o voto vencido de nove unidades, que pediram que o tema volte à "
              "pauta no próximo ano."),
    "titulo": ("Animais e uso das áreas comuns",
               "A assembleia deliberou sobre o uso das áreas comuns: o salão de festas passará a ser reservado pelo "
               "aplicativo da administradora, com taxa de limpeza de R$ 150,00 e limite de uma reserva por unidade "
               "por mês; a churrasqueira ficará disponível até as 22h, e a piscina terá horário de funcionamento "
               "das 8h às 20h, com uso obrigatório de touca. A academia terá acesso por biometria a partir de "
               "{mes_ini}. Foi aprovada ainda a contratação de empresa para manutenção mensal da quadra. O ponto "
               "sobre animais, previsto no edital, não foi discutido por falta de tempo e ficará para a próxima "
               "assembleia."),
    "ind": ("Regras sobre animais nas áreas comuns",
            "A assembleia discutiu a proposta de permitir animais de estimação, mas não houve consenso sobre portes "
            "e regras de circulação. Decidiu-se constituir uma comissão de cinco moradores para elaborar, em "
            "sessenta dias, uma minuta de regulamento a ser votada em assembleia extraordinária. Enquanto isso, a "
            "administradora não aplicará as multas previstas no regimento às unidades que já possuem animais, sem "
            "que isso signifique autorização definitiva, e novos animais não deverão ser trazidos até a votação."),
}
A_SEG = {
    "cam": ("Segurança e controle de acesso",
            "O síndico apresentou duas propostas para a instalação de sistema de câmeras de monitoramento (CFTV) "
            "nas entradas, garagens e corredores, com gravação por trinta dias e acesso restrito à administração. "
            "A assembleia APROVOU, por maioria, a contratação da proposta da empresa {empresa_seg}, no valor de R$ "
            "{valor_seg}, com rateio em {parcelas} parcelas, e autorizou o síndico a assinar o contrato. Foi "
            "aprovada também a política de uso das imagens, que só serão fornecidas mediante solicitação formal ou "
            "ordem judicial. Os condôminos pediram que as câmeras não apontem para janelas das unidades."),
    "rej": ("Segurança e controle de acesso",
            "O síndico apresentou proposta para a instalação de sistema de câmeras de monitoramento nas entradas e "
            "garagens. A assembleia REJEITOU a instalação, pela maioria dos presentes, por considerar o custo "
            "elevado e por preocupação com a privacidade dos moradores, decidindo manter o atual esquema de "
            "portaria com dois funcionários e investir na iluminação do perímetro. O tema poderá ser retomado em "
            "outra assembleia com propostas mais baratas e política clara de uso das imagens. Não foi autorizada "
            "nenhuma contratação neste ponto."),
    "ind": ("Segurança e controle de acesso",
            "O síndico apresentou propostas para sistema de câmeras de monitoramento. Sem consenso sobre o custo, a "
            "assembleia aprovou apenas a instalação, em caráter experimental e por noventa dias, de duas câmeras "
            "na entrada da garagem, cedidas em comodato pela empresa {empresa_seg}, sem custo, para avaliação da "
            "qualidade das imagens. A decisão sobre o sistema completo ficará para assembleia específica, após "
            "relatório do síndico sobre o período de teste. A política de uso das imagens será discutida na mesma "
            "ocasião."),
    "parecida": ("Segurança e controle de acesso",
                 "A assembleia APROVOU a instalação de controle de acesso por biometria e tags veiculares nos "
                 "portões, com a empresa {empresa_seg}, no valor de R$ {valor_seg}, bem como a troca da fechadura "
                 "da porta de vidro da entrada social. A proposta de sistema de câmeras não foi apresentada nesta "
                 "assembleia e ficará para a próxima, após levantamento de custos pelo síndico. Os moradores "
                 "pediram o cadastro biométrico de prestadores de serviço recorrentes e a entrega de duas tags por "
                 "unidade sem custo."),
}
A_INAD = ("Inadimplência",
          "A administradora informou que a inadimplência atingiu {inad}% das unidades, com débito acumulado de R$ "
          "{debito}. A assembleia AUTORIZOU o síndico a promover a cobrança judicial das unidades com mais de três "
          "cotas em atraso, após notificação extrajudicial com prazo de quinze dias, e aprovou a contratação de "
          "escritório de advocacia por honorários de êxito. Foi aprovado também o parcelamento de débitos em até "
          "doze vezes, com juros de um por cento ao mês, para quem procurar a administradora em trinta dias. Os "
          "nomes das unidades inadimplentes não constarão desta ata, por decisão da assembleia.")
A_ENC = ("Assuntos gerais e encerramento",
         "Nos assuntos gerais, foram registradas reclamações sobre barulho após as 22h e sobre o estacionamento de "
         "visitantes em vagas de moradores, ficando a administradora encarregada de reforçar o regimento por "
         "circular. Um condômino pediu a revisão do contrato de jardinagem, e o síndico informou que a troca das "
         "lâmpadas das garagens por LED será concluída em trinta dias. Nada mais havendo a tratar, o presidente "
         "agradeceu a presença de todos e encerrou a assembleia às {hora_fim}, lavrando-se a presente ata, que, "
         "lida e aprovada, vai assinada pelo presidente e pela secretária. A lista de presença fica arquivada na "
         "administradora.")

# ----------------------------------------------------------------------------------------------------------
# BANCO DE SEÇÕES — proposta comercial
# ----------------------------------------------------------------------------------------------------------
P_APRES = ("Apresentação",
           "A {fornecedora} agradece a oportunidade de apresentar à {cliente} esta proposta comercial para "
           "{objeto}. Atuamos há {anos} anos no mercado de {mercado}, com equipe própria e as certificações "
           "exigidas pelo setor, e atendemos atualmente mais de {n_clientes} clientes na região. Esta proposta foi "
           "elaborada a partir da reunião de levantamento realizada em {data_reuniao} com a equipe da {cliente} e "
           "reflete nosso entendimento das necessidades apresentadas; eventuais ajustes de escopo serão tratados "
           "em revisão formal deste documento. Os valores e condições aqui descritos aplicam-se exclusivamente ao "
           "escopo detalhado a seguir.")
P_ESC = {
    "trein": ("Escopo dos serviços",
              "O escopo compreende {itens}. Está incluído o treinamento da equipe da {cliente}, em duas turmas de "
              "até dez pessoas, com carga horária de oito horas cada, ministrado nas instalações do cliente ou por "
              "videoconferência, com material didático e certificado de participação. Também estão incluídos a "
              "implantação, a migração dos dados do sistema atual e o acompanhamento presencial na primeira "
              "semana de operação. Não estão incluídos licenças de terceiros, equipamentos e customizações fora do "
              "levantamento, que serão orçados à parte."),
    "semtrein": ("Escopo dos serviços",
                 "O escopo compreende {itens}. Estão incluídos a implantação, a migração dos dados do sistema atual, "
                 "a configuração de perfis de acesso e o acompanhamento remoto na primeira semana de operação, com "
                 "atendimento prioritário pela central de suporte e manuais em português disponíveis no portal do "
                 "cliente. Não estão incluídos licenças de terceiros, equipamentos, integrações com sistemas não "
                 "listados e customizações fora do levantamento, que serão orçados à parte mediante solicitação "
                 "formal."),
}
P_PRECO = {
    "desc": ("Preço",
             "O investimento total para o escopo descrito é de R$ {valor}, já incluídos impostos, deslocamentos "
             "dentro da região metropolitana e o suporte do período de garantia. Sobre esse valor a {fornecedora} "
             "concede desconto comercial de {desc}% ({desc_ext} por cento), nas condições descritas na seção de "
             "pagamento, resultando no valor líquido de R$ {valor_liq}. O preço considera a execução no prazo "
             "proposto; mudanças de escopo serão orçadas à parte e formalizadas por aditivo. Os valores são "
             "expressos em reais e não sofrem reajuste durante a validade desta proposta."),
    "semdesc": ("Preço",
                "O investimento total para o escopo descrito é de R$ {valor}, já incluídos impostos, deslocamentos "
                "dentro da região metropolitana e o suporte do período de garantia. O preço é fechado para o escopo "
                "levantado e considera a execução no prazo proposto; mudanças de escopo solicitadas pela {cliente} "
                "serão orçadas à parte e formalizadas por aditivo, sem alteração do cronograma já em curso. Não há "
                "desconto adicional sobre o valor apresentado, que já reflete a melhor condição comercial da "
                "{fornecedora} para o porte do projeto. Os valores são expressos em reais e não sofrem reajuste "
                "durante a validade da proposta."),
}
P_PAG = {
    "avista": ("Condições de pagamento",
               "O pagamento poderá ser feito à vista ou parcelado. O desconto de {desc}% mencionado na seção de "
               "preço aplica-se EXCLUSIVAMENTE ao pagamento integral à vista, por transferência bancária, em até "
               "cinco dias úteis da assinatura do contrato. Na opção parcelada, o valor será o total sem desconto, "
               "dividido em {parc} parcelas mensais iguais, a primeira na assinatura e as demais a cada trinta "
               "dias, mediante boleto bancário. O atraso de qualquer parcela sujeita a {cliente} a multa de dois "
               "por cento e juros de um por cento ao mês, e suspende o cronograma de entrega até a regularização."),
    "qualquer": ("Condições de pagamento",
                 "O pagamento poderá ser feito à vista ou em {parc} parcelas mensais iguais, a primeira na "
                 "assinatura e as demais a cada trinta dias, por boleto bancário. O desconto de {desc}% informado "
                 "na seção de preço vale para qualquer das modalidades, à vista ou parcelada, por se tratar de "
                 "condição comercial de lançamento válida até o fim da validade desta proposta. O atraso de parcela "
                 "sujeita a {cliente} a multa de dois por cento e juros de um por cento ao mês, e suspende o "
                 "cronograma de entrega até a regularização. A nota fiscal será emitida a cada parcela."),
    "parcelado": ("Condições de pagamento",
                  "O pagamento será feito em {parc} parcelas mensais iguais, a primeira na assinatura e as demais a "
                  "cada trinta dias, por boleto bancário, com emissão de nota fiscal a cada parcela. "
                  "Alternativamente, a {cliente} poderá optar pelo pagamento integral à vista em até cinco dias "
                  "úteis da assinatura, pelo mesmo valor. O atraso de parcela sujeita a {cliente} a multa de dois "
                  "por cento e juros de um por cento ao mês, e suspende o cronograma de entrega até a "
                  "regularização. Despesas bancárias correm por conta de cada parte. Os dados bancários constam do "
                  "anexo."),
    "marcos": ("Condições de pagamento",
               "O pagamento seguirá marcos de entrega: trinta por cento na assinatura do contrato, quarenta por "
               "cento na homologação da implantação e trinta por cento na entrada em operação, mediante aceite "
               "formal de cada etapa pela {cliente} e emissão da nota fiscal correspondente. O aceite será "
               "considerado tácito se não houver manifestação em cinco dias úteis após a entrega. O atraso de "
               "qualquer parcela sujeita a {cliente} a multa de dois por cento e juros de um por cento ao mês, e "
               "suspende o cronograma até a regularização. Não há variação de valor conforme a forma de pagamento."),
}
P_ENTREGA = ("Prazo de entrega",
             "A implantação será concluída em {dias} dias corridos contados da assinatura do contrato e do "
             "recebimento das informações e acessos listados no anexo, conforme o cronograma: levantamento "
             "detalhado na primeira semana, configuração e migração nas semanas seguintes, homologação com a "
             "equipe da {cliente} e entrada em operação ao final. Atrasos na disponibilização de informações pelo "
             "cliente deslocam o cronograma na mesma proporção. A {fornecedora} comunicará semanalmente o "
             "andamento por relatório resumido e reunião de quinze minutos com o responsável indicado.")
P_GAR = ("Garantia e suporte",
         "A {fornecedora} garante os serviços entregues por {gar} meses contados do aceite final, corrigindo sem "
         "custo defeitos de configuração ou de funcionamento atribuíveis ao seu trabalho, mediante chamado na "
         "central de suporte, em dias úteis das 8h às 18h, com resposta em até um dia útil. Após o período de "
         "garantia, o suporte poderá ser contratado por plano mensal, com valores informados no anexo. A garantia "
         "não cobre mau uso, alterações feitas por terceiros, falhas de infraestrutura do cliente ou de "
         "fornecedores externos, nem perda de dados por ausência de backup sob responsabilidade da {cliente}.")
P_CONF = ("Confidencialidade",
          "As informações trocadas entre {fornecedora} e {cliente} durante a elaboração desta proposta e na "
          "eventual execução do projeto, incluindo dados de clientes, processos internos, preços e condições "
          "comerciais, são confidenciais e não serão divulgadas a terceiros nem usadas para fins diversos da "
          "avaliação e execução do projeto, pelo prazo de três anos a contar desta data, salvo exigência legal. "
          "Esta obrigação vincula as duas partes desde o recebimento desta proposta, independentemente da "
          "assinatura de contrato, e será reproduzida no instrumento definitivo, com as penalidades que as partes "
          "ajustarem.")
P_EQUIPE = ("Equipe e responsáveis",
            "A equipe alocada ao projeto será composta por um gerente de projeto, dois consultores de implantação e "
            "um analista de suporte, todos funcionários da {fornecedora}, com dedicação parcial e disponibilidade "
            "garantida nas etapas de homologação e entrada em operação. A {cliente} indicará um responsável com "
            "poder de decisão sobre o escopo e um usuário-chave por área, que participarão das reuniões semanais e "
            "validarão as entregas. A substituição de membros da equipe será comunicada com antecedência de cinco "
            "dias úteis e não altera prazos nem preço.")
P_VAL = ("Validade da proposta",
         "Esta proposta é válida por {val} dias corridos a contar da data de sua emissão, {data_emissao}. Após esse "
         "prazo, os valores, prazos e condições deverão ser reconfirmados pela {fornecedora}, podendo sofrer "
         "revisão em razão de alterações de custos, de disponibilidade de equipe ou de tabela de preços de "
         "fornecedores. A aceitação se dará pela assinatura do contrato de prestação de serviços ou pelo aceite "
         "formal desta proposta por e-mail, acompanhado da ordem de compra, a partir do que se inicia a contagem "
         "do prazo de entrega. Permanecemos à disposição para esclarecimentos.")
P_RESS = ("Exclusões e ressalvas",
          "Esclarecemos que o treinamento da equipe da {cliente} NÃO está incluído nesta proposta; a {fornecedora} "
          "disponibiliza vídeos e manuais no portal do cliente, e turmas de capacitação podem ser contratadas à "
          "parte, ao valor de R$ 2.400,00 por turma de até dez pessoas. Também não estão incluídos deslocamentos "
          "para fora da região metropolitana e horas de consultoria além das previstas no escopo. Qualquer serviço "
          "adicional será objeto de proposta complementar, com prazo e preço próprios, sem alteração das condições "
          "aqui apresentadas.")
P_OBJ = [
    dict(objeto="a implantação do sistema de gestão de locações", mercado="software para o mercado imobiliário",
         itens="a implantação do módulo de locações, do módulo financeiro e do portal do proprietário"),
    dict(objeto="a implantação do sistema de controle de estoque e vendas", mercado="automação comercial",
         itens="a implantação dos módulos de estoque, vendas, emissão fiscal e integração com o balcão"),
    dict(objeto="a implantação da plataforma de atendimento ao cliente", mercado="soluções de atendimento",
         itens="a implantação da central de atendimento, dos canais de chat e e-mail e dos relatórios gerenciais"),
    dict(objeto="a implantação do sistema de gestão de condomínios", mercado="software para administradoras",
         itens="a implantação dos módulos de cobrança, assembleias, portaria e aplicativo do morador"),
]

# ----------------------------------------------------------------------------------------------------------
# RECEITAS — o que cada documento afirma, nega, omite ou revoga (fatos de autoria)
# ----------------------------------------------------------------------------------------------------------
# Locação: intro, prazo, renov, reaj, gar, resc(multa n | neg | atraso | None), uso, anim, foro, fin
L_REC = {
    "L01": dict(intro="res", prazo=30, renov="afirm", reaj="igpm", gar="fiador", resc=3, uso="proib", anim=None, foro="com", fin="fiadorchaves"),
    "L02": dict(intro="com", prazo=36, renov="sil", reaj="ipca", gar="caucao", resc=2, uso="proib", anim=None, foro="arb", fin="revsub"),
    "L03": dict(intro="res", prazo=12, renov="neg", reaj="igpm", gar="fiador", resc="neg", uso=None, anim="perm", foro="com", fin="fiadorchaves"),
    "L04": dict(intro="res", prazo=6, renov="sil", reaj="sem", gar="seguro", resc="neg", uso="perm", anim="proib", foro="titulo", fin=None),
    "L05": dict(intro="com", prazo=24, renov="afirm", reaj="igpm", gar="fiador", resc=3, uso="proib", anim=None, foro="com", fin="revmulta"),
    "L06": dict(intro="res", prazo=30, renov="afirm", reaj="ipca", gar="fiador", resc=3, uso="proib", anim="perm", foro="com", fin=None),
    "L07": dict(intro="res", prazo=36, renov="sil", reaj="igpm", gar="caucao", resc="atraso", uso="perm", anim=None, foro="arb", fin="chavessemfiador"),
    "L08": dict(intro="com", prazo=8, renov="neg", reaj="ind", gar="seguro", resc=None, uso="titulo", anim="ind", foro="titulo", fin="plain"),
    "L09": dict(intro="res", prazo=30, renov="afirm", reaj="igpm", gar="fiador", resc=2, uso="proib", anim=None, foro="com", fin="revrenov"),
    "L10": dict(intro="res", prazo=12, renov="sil", reaj="sem", gar="fiador", resc=3, uso=None, anim="perm", foro="com", fin="fiadorchaves"),
    "L11": dict(intro="com", prazo=36, renov="sil", reaj="ipca", gar="fiador", resc=3, uso="proib", anim=None, foro="com", fin="fiadorchaves"),
}
# Serviço: obj, prazo, renov, reaj, excl, conf, sla, resc(pct | neg | None), naoconc, foro, fin
S_REC = {
    "S01": dict(obj="ti", prazo=12, renov="afirm", reaj="igpm", excl="afirm", conf=False, sla="pen", resc=20, naoconc=False, foro="com", fin=None),
    "S02": dict(obj="mkt", prazo=6, renov="neg", reaj="sem", excl="neg", conf=True, sla=None, resc="neg", naoconc=False, foro="com", fin=None),
    "S03": dict(obj="limp", prazo=24, renov="afirm", reaj="ipca", excl=None, conf=False, sla="pen", resc=30, naoconc=False, foro="arb", fin="revmulta"),
    "S04": dict(obj="ti", prazo=12, renov="sil", reaj="igpm", excl="titulo", conf=False, sla="sem", resc=None, naoconc=True, foro="com", fin=None),
    "S05": dict(obj="mkt", prazo=10, renov="afirm", reaj="sem", excl="afirm", conf=True, sla="ind", resc=None, naoconc=False, foro="titulo", fin="revrenov"),
    "S06": dict(obj="ti", prazo=24, renov="sil", reaj="ipca", excl="parcial", conf=True, sla="pen", resc=10, naoconc=False, foro="com", fin=None),
    "S07": dict(obj="limp", prazo=12, renov="neg", reaj="ipca", excl=None, conf=False, sla=None, resc=None, naoconc=False, foro="com", fin="plain"),
    "S08": dict(obj="ti", prazo=3, renov="sil", reaj="sem", excl="afirm", conf=False, sla="pen", resc="neg", naoconc=False, foro="arb", fin=None),
    "S09": dict(obj="mkt", prazo=12, renov="afirm", reaj="igpm", excl="titulo", conf=False, sla=None, resc=20, naoconc=True, foro="com", fin=None),
    "S10": dict(obj="limp", prazo=36, renov="sil", reaj="ipca", excl="neg", conf=True, sla="sem", resc=None, naoconc=False, foro="com", fin="plain"),
    "S11": dict(obj="ti", prazo=24, renov="sil", reaj="sem", excl="afirm", conf=False, sla="pen", resc=None, naoconc=False, foro="com", fin=None),
}
# Ata: quorum, conv, contas, taxa(reaj pct | mant | rej), obra(apr | rej | adi | aprrev | None), anim, seg, inad
A_REC = {
    "A01": dict(quorum=62, conv=1, contas="apr", taxa=12, obra="apr", anim=None, seg="cam", inad=False),
    "A02": dict(quorum=41, conv=2, contas="ress", taxa="mant", obra="rej", anim="lib", seg=None, inad=True),
    "A03": dict(quorum=71, conv=1, contas="apr", taxa=15, obra="apr", anim="proib", seg="cam", inad=False),
    "A04": dict(quorum=38, conv=2, contas="rej", taxa="rej", obra=None, anim=None, seg="rej", inad=True),
    "A05": dict(quorum=55, conv=1, contas="apr", taxa=10, obra="aprrev", anim=None, seg="cam", inad=False),
    "A06": dict(quorum=48, conv=2, contas="adi", taxa="mant", obra="adi", anim="titulo", seg=None, inad=False),
    "A07": dict(quorum=80, conv=1, contas="apr", taxa=8, obra="apr", anim="lib", seg="parecida", inad=False),
    "A08": dict(quorum=32, conv=2, contas="apr", taxa=6, obra=None, anim="ind", seg="cam", inad=True),
    "A09": dict(quorum=67, conv=1, contas="ress", taxa="rej", obra="apr", anim=None, seg="ind", inad=False),
    "A10": dict(quorum=45, conv=2, contas="rej", taxa="mant", obra="rej", anim="proib", seg="cam", inad=False),
    "A11": dict(quorum=58, conv=1, contas="adi", taxa=10, obra="apr", anim=None, seg="rej", inad=False),
}
# Proposta: esc, desc(pct | 0), pag, entrega(dias | None), gar, conf, equipe, val, ress
P_REC = {
    "P01": dict(esc="trein", desc=8, pag="avista", entrega=45, gar=12, conf=False, equipe=False, val=30, ress=False),
    "P02": dict(esc="semtrein", desc=5, pag="qualquer", entrega=None, gar=6, conf=True, equipe=False, val=10, ress=False),
    "P03": dict(esc="semtrein", desc=10, pag="avista", entrega=60, gar=12, conf=False, equipe=True, val=15, ress=False),
    "P04": dict(esc="trein", desc=0, pag="parcelado", entrega=None, gar=3, conf=True, equipe=False, val=7, ress=False),
    "P05": dict(esc="semtrein", desc=7, pag="parcelado", entrega=30, gar=24, conf=False, equipe=False, val=30, ress=True),
    "P06": dict(esc="trein", desc=12, pag="avista", entrega=None, gar=12, conf=True, equipe=False, val=20, ress=False),
    "P07": dict(esc="semtrein", desc=6, pag="marcos", entrega=90, gar=18, conf=False, equipe=False, val=30, ress=False),
    "P08": dict(esc="semtrein", desc=0, pag="marcos", entrega=None, gar=6, conf=False, equipe=False, val=10, ress=True),
    "P09": dict(esc="trein", desc=15, pag="avista", entrega=40, gar=12, conf=True, equipe=False, val=15, ress=False),
    "P10": dict(esc="semtrein", desc=9, pag="qualquer", entrega=None, gar=12, conf=False, equipe=True, val=5, ress=False),
    "P11": dict(esc="semtrein", desc=8, pag="avista", entrega=None, gar=36, conf=False, equipe=False, val=30, ress=False),
}


class Doc:
    def __init__(self, id_: str, tipo: str):
        self.id, self.tipo, self.secoes, self.fatos, self.campos = id_, tipo, [], {}, {}

    def add(self, titulo: str, texto: str, p: dict, **fatos):
        sid = f"{self.id}-s{len(self.secoes) + 1}"
        t = texto.format(**p)
        n = len(t.split())
        assert 60 <= n <= 200, f"{sid} ({titulo}): {n} palavras"
        self.secoes.append({"id": sid, "titulo": titulo, "texto": t})
        for k, v in fatos.items():
            self.fatos[k] = (v, sid)
        return sid

    def fato(self, k):
        return self.fatos.get(k, (None, None))

    def json(self):
        return {"id": self.id, "tipo": self.tipo, "secoes": self.secoes, "campos": self.campos}


def gera_locacao(id_, r, rnd) -> Doc:
    d = Doc(id_, "locacao")
    inicio = date(2026, rnd.randint(1, 9), rnd.choice([1, 5, 10, 15]))
    fim = soma_meses(inicio, r["prazo"]) - timedelta(days=1)
    com = r["intro"] == "com"
    p = dict(locador=rnd.choice(PESSOAS), locatario=rnd.choice(EMPRESAS) if com else rnd.choice(PESSOAS),
             endereco=rnd.choice(ENDERECOS), cidade=rnd.choice(CIDADES), fiador=rnd.choice(PESSOAS),
             camara=rnd.choice(CAMARAS), dia=rnd.choice([5, 10, 15]),
             descricao=("sala comercial com dois banheiros e uma vaga de garagem" if com else
                        rnd.choice(["dois dormitórios, sala, cozinha, área de serviço e uma vaga de garagem",
                                    "três dormitórios, sendo uma suíte, sala ampla, cozinha e duas vagas",
                                    "um dormitório, sala conjugada, cozinha americana e banheiro"])),
             atividade=rnd.choice(["escritório de contabilidade", "clínica odontológica", "loja de roupas",
                                   "consultório de fisioterapia", "estúdio de arquitetura"]),
             prazo=r["prazo"], prazo_ext=ext(r["prazo"]), inicio=data_ext(inicio), fim=data_ext(fim))
    p["cidade_foro"] = p["cidade"].split("/")[0]
    valor = rnd.choice([1800, 2300, 2750, 3200, 3900, 4500, 5200, 6800, 7500, 9800, 12000])
    p["valor"] = reais(valor)
    d.add(*L_INTRO[r["intro"]], p)
    d.add(L_PRAZO_BASE[0], L_PRAZO_BASE[1] + RENOV[r["renov"]], p, renov_auto=(r["renov"] == "afirm"))
    d.add(*L_REAJ[r["reaj"]], p, igpm=(r["reaj"] == "igpm"))
    d.add(*L_GAR[r["gar"]], p, garantia=r["gar"])
    multa_n = None
    if isinstance(r["resc"], int):
        p["n"], p["n_ext"] = r["resc"], ext(r["resc"])
        d.add(*L_RESC["multa"], p, multa=True)
        multa_n = r["resc"]
    elif r["resc"] == "neg":
        d.add(*L_RESC["neg"], p, multa=False)
    elif r["resc"] == "atraso":
        d.add(*L_RESC["atraso"], p, multa=False)
    if r["uso"]:
        d.add(*L_USO[r["uso"]], p, sublocacao_proibida=(r["uso"] == "proib"))
    if r["anim"]:
        d.add(*L_ANIM[r["anim"]], p, animais={"perm": True, "proib": False, "ind": "ind"}[r["anim"]])
    d.add(*FORO[r["foro"]], p, arbitragem=(r["foro"] == "arb"))
    if r["fin"]:
        f = r["fin"]
        if f == "revmulta":
            d.add(*L_FIN[f], p, multa=False); multa_n = None
        elif f == "revsub":
            d.add(*L_FIN[f], p, sublocacao_proibida=False)
        elif f == "revrenov":
            d.add(*L_FIN[f], p, renov_auto=False)
        elif f == "fiadorchaves":
            d.add(*L_FIN[f], p, fiador_chaves=(r["gar"] == "fiador"))
        elif f == "chavessemfiador":
            d.add(*L_FIN[f], p, fiador_chaves=False)
        else:
            d.add(*L_FIN[f], p)
    d.campos = {"valor_aluguel": valor, "prazo_meses": r["prazo"], "multa_alugueis": multa_n,
                "indice_reajuste": {"igpm": "IGP-M", "ipca": "IPCA"}.get(r["reaj"]),
                "garantia": {"fiador": "fiador", "caucao": "caucao", "seguro": "seguro_fianca"}[r["gar"]],
                "renovacao_automatica": d.fato("renov_auto")[0] is True}
    return d


def gera_servico(id_, r, rnd) -> Doc:
    d = Doc(id_, "prestacao_servico")
    inicio = date(2026, rnd.randint(1, 9), 1)
    p = dict(contratada=rnd.choice(EMPRESAS), contratante=rnd.choice(EMPRESAS), prazo=r["prazo"],
             prazo_ext=ext(r["prazo"]), inicio=data_ext(inicio), cidade_foro=rnd.choice(CIDADES).split("/")[0],
             camara=rnd.choice(CAMARAS), sla=rnd.choice([4, 8]), pen=rnd.choice([2, 3, 5]),
             segmento=rnd.choice(["varejo de materiais de construção", "clínicas e laboratórios",
                                  "administração de condomínios", "transporte rodoviário de cargas"]))
    p.update(S_OBJ[r["obj"]])
    valor = rnd.choice([4200, 6500, 8900, 11000, 14500, 18000, 23000, 31000])
    p["valor"] = reais(valor)
    d.add(*S_OBJ_T, p)
    d.add(S_PRAZO_BASE[0], S_PRAZO_BASE[1] + S_RENOV[r["renov"]], p, renov_auto=(r["renov"] == "afirm"))
    d.add(S_REM_BASE[0], S_REM_BASE[1] + S_REAJ[r["reaj"]], p, igpm=(r["reaj"] == "igpm"))
    if r["excl"]:
        e = r["excl"]
        if e == "titulo":
            d.add(*S_EXCL[e], p, exclusividade=False, confid=True)
        else:
            d.add(*S_EXCL[e], p, exclusividade=(e in ("afirm", "parcial")))
    if r["conf"]:
        d.add(*S_CONF, p, confid=True)
    if r["sla"]:
        d.add(*S_SLA[r["sla"]], p, sla_pen={"pen": True, "sem": False, "ind": "ind"}[r["sla"]])
    multa_pct = None
    if isinstance(r["resc"], int):
        p["pct"], p["pct_ext"] = r["resc"], ext(r["resc"])
        d.add(*S_RESC["multa"], p, multa=True); multa_pct = r["resc"]
    elif r["resc"] == "neg":
        d.add(*S_RESC["neg"], p, multa=False)
    if r["naoconc"]:
        d.add(*S_NAOCONC, p)
    d.add(*FORO[r["foro"]], p, arbitragem=(r["foro"] == "arb"))
    if r["fin"]:
        f = r["fin"]
        if f == "revmulta":
            d.add(*S_FIN[f], p, multa=False); multa_pct = None
        elif f == "revrenov":
            d.add(*S_FIN[f], p, renov_auto=False)
        else:
            d.add(*S_FIN[f], p)
    d.campos = {"valor_mensal": valor, "prazo_meses": r["prazo"], "multa_percentual": multa_pct,
                "indice_reajuste": {"igpm": "IGP-M", "ipca": "IPCA"}.get(r["reaj"]),
                "exclusividade": d.fato("exclusividade")[0] is True,
                "renovacao_automatica": d.fato("renov_auto")[0] is True}
    return d


def gera_ata(id_, r, rnd) -> Doc:
    d = Doc(id_, "ata_condominio")
    data = date(2026, rnd.randint(2, 9), rnd.randint(3, 27))
    taxa_antiga = rnd.choice([480, 620, 750, 890, 1050, 1300])
    pct = r["taxa"] if isinstance(r["taxa"], int) else 0
    taxa_nova = round(taxa_antiga * (100 + pct) / 100)
    i = rnd.randrange(len(OBRAS))
    p = dict(condominio=rnd.choice(CONDOMINIOS), data_ext=data_ext(data), hora=rnd.choice(["19h30", "20h", "19h"]),
             conv="primeira" if r["conv"] == 1 else "segunda", quorum=r["quorum"],
             tipo_ag=rnd.choice(["ordinária", "extraordinária"]), data_edital=data_ext(data - timedelta(days=10)),
             presidente=rnd.choice(PESSOAS), secretario=rnd.choice(PESSOAS), inst=A_INST[r["conv"]],
             ano=data.year - 1, ano2=data.year, rec=reais(rnd.randint(380, 920) * 1000),
             desp=reais(rnd.randint(360, 900) * 1000), abst=rnd.randint(1, 4), saldo=reais(rnd.randint(12, 80) * 1000),
             semcomp=reais(rnd.randint(8, 40) * 1000), votos=rnd.randint(18, 40), votos2=rnd.randint(5, 15),
             taxa_antiga=reais(taxa_antiga), taxa_nova=reais(taxa_nova), pct=pct, pct_ext=EXT.get(pct, ""),
             pct_rej=rnd.choice([9, 11, 14]), mes_ini=MESES[(data.month + 1) % 12],
             obra=OBRAS[i], empresa_obra=EMPRESAS_OBRA[i], o1=reais(rnd.randint(40, 120) * 1000),
             o2=reais(rnd.randint(130, 300) * 1000), prazo_obra=rnd.choice([45, 60, 90, 120]),
             parcelas=rnd.choice([6, 8, 10, 12]), pct_obra=rnd.choice([44, 51, 57]),
             empresa_seg=rnd.choice(EMPRESAS_SEG), valor_seg=reais(rnd.randint(18, 65) * 1000),
             inad=rnd.choice([9, 14, 18, 23]), debito=reais(rnd.randint(30, 160) * 1000),
             hora_fim=rnd.choice(["21h40", "22h05", "21h15"]))
    d.add(*A_ABERT, p)
    d.add(A_CONTAS_BASE[0], A_CONTAS_BASE[1] + A_CONTAS[r["contas"]], p,
          contas_aprovadas=(r["contas"] in ("apr", "ress")))
    d.add(A_TAXA_BASE[0], A_TAXA_BASE[1] + A_TAXA["reaj" if pct else r["taxa"]], p, taxa_reajuste=bool(pct))
    obra_ok = False
    if r["obra"]:
        o = "apr" if r["obra"] == "aprrev" else r["obra"]
        d.add(A_OBRA_BASE[0], A_OBRA_BASE[1] + A_OBRA[o], p, obra_aprovada=(o == "apr"))
        obra_ok = o == "apr"
    if r["anim"]:
        d.add(*A_ANIM[r["anim"]], p, animais={"lib": True, "proib": False, "titulo": False, "ind": "ind"}[r["anim"]])
    if r["seg"]:
        d.add(*A_SEG[r["seg"]], p, cameras={"cam": True, "rej": False, "ind": "ind", "parecida": False}[r["seg"]])
    if r["inad"]:
        d.add(*A_INAD, p)
    if r["obra"] == "aprrev":
        d.add(*A_RETIF, p, obra_aprovada=False); obra_ok = False
    d.add(*A_ENC, p)
    d.campos = {"data": data.isoformat(), "quorum_percentual": r["quorum"], "taxa_valor": taxa_nova,
                "reajuste_percentual": pct, "obra_aprovada": obra_ok}
    return d


def gera_proposta(id_, r, rnd) -> Doc:
    d = Doc(id_, "proposta_comercial")
    emissao = date(2026, rnd.randint(1, 9), rnd.randint(2, 26))
    valor = rnd.choice([38000, 54000, 72500, 89000, 118000, 146000, 210000, 265000])
    p = dict(fornecedora=rnd.choice(EMPRESAS), cliente=rnd.choice(EMPRESAS), anos=rnd.choice([9, 12, 15, 21]),
             n_clientes=rnd.choice([80, 150, 300]), data_reuniao=data_ext(emissao - timedelta(days=rnd.randint(4, 12))),
             valor=reais(valor), desc=r["desc"], desc_ext=EXT.get(r["desc"], ""),
             valor_liq=reais(round(valor * (100 - r["desc"]) / 100)), parc=rnd.choice([4, 6, 10]),
             dias=r["entrega"], gar=r["gar"], val=r["val"], data_emissao=data_ext(emissao))
    p.update(rnd.choice(P_OBJ))
    d.add(*P_APRES, p)
    d.add(*P_ESC[r["esc"]], p, treinamento=(r["esc"] == "trein"))
    d.add(*P_PRECO["desc" if r["desc"] else "semdesc"], p)
    d.add(*P_PAG[r["pag"]], p, desconto_condicional=(r["desc"] > 0 and r["pag"] == "avista"))
    if r["entrega"]:
        d.add(*P_ENTREGA, p)
    d.add(*P_GAR, p)
    if r["conf"]:
        d.add(*P_CONF, p, confid=True)
    if r["equipe"]:
        d.add(*P_EQUIPE, p)
    d.add(*P_VAL, p)
    if r["ress"]:
        d.add(*P_RESS, p, treinamento=False)
    d.campos = {"valor_total": valor, "validade_dias": r["val"], "prazo_entrega_dias": r["entrega"],
                "desconto_percentual": r["desc"], "garantia_meses": r["gar"]}
    return d


# ----------------------------------------------------------------------------------------------------------
# CONDIÇÕES — (id, texto, tipo, chave do fato | expressão numérica, tipos de documento, nota)
# ----------------------------------------------------------------------------------------------------------
def numerica(campo, op, val):
    def f(d):
        v = d.campos.get(campo)
        if v is None:
            return False, None
        ok = {"<": v < val, ">": v > val, "<=": v <= val, ">=": v >= val}[op]
        return ok, d.fatos_campo.get(campo)
    return f


def semantica(chave, tipos):
    def f(d):
        if d.tipo not in tipos:
            return False, None
        return d.fato(chave)
    return f


L, S, A, P = "locacao", "prestacao_servico", "ata_condominio", "proposta_comercial"
CONDICOES = {
    "rascunho": [
        ("TD-R01", "O documento prevê o reajuste do valor pelo IGP-M.", "semantica", semantica("igpm", {L, S}),
         "fácil: índice nomeado na seção de aluguel ou de remuneração; IPCA, valor fixo e 'índice a definir' são falsos"),
        ("TD-R02", "A ata registra a aprovação de obra ou reforma nas áreas comuns do condomínio.", "semantica",
         semantica("obra_aprovada", {A}), "fácil: mesma condição de uma deliberação explícita; rejeitada e adiada são falsas"),
        ("TD-R03", "Proposta comercial com garantia de doze meses ou mais (`garantia_meses` >= 12).", "numerica",
         numerica("garantia_meses", ">=", 12), "fácil: valor em `campos`, prova na seção de garantia"),
        ("TD-R04", "Contrato de locação em que a garantia da locação é prestada por fiador.", "semantica",
         semantica("garantia_fiador", {L}), "fácil: caução e seguro-fiança dizem explicitamente que não há fiador"),
        ("TD-R05", "O documento contém cláusula de confidencialidade (sigilo sobre informações da outra parte).",
         "semantica", semantica("confid", {S, P}), "fácil: seção própria ou dentro de seção composta"),
    ],
    "ajuste": [
        ("TD-A01", "Contrato de locação que prevê multa a cargo do locatário em caso de devolução antecipada do imóvel (rescisão antecipada).",
         "semantica", semantica("multa", {L}),
         "difícil: negada — 'NÃO haverá multa' (L03, L04) é falso; revogada em seção posterior (L05) é falso; seção parecida de outro assunto (multa por atraso, L07) é falso; L08 não tem a cláusula"),
        ("TD-A02", "Contrato de locação com multa por rescisão antecipada superior a dois aluguéis (`multa_alugueis` > 2).",
         "numerica", numerica("multa_alugueis", ">", 2),
         "fácil para o código: `multa_alugueis` é o valor EFETIVO (null quando negada, ausente ou revogada); dois aluguéis não é 'superior a dois'"),
        ("TD-A03", "Proposta comercial que concede desconto sobre o preço E condiciona esse desconto exclusivamente ao pagamento à vista.", "semantica",
         semantica("desconto_condicional", {P}),
         "difícil: duas seções — o desconto está na seção de preço e a condição 'exclusivamente à vista' na de pagamento; desconto 'para qualquer modalidade' (P02, P10) e desconto sem condição declarada (P05, P07) são falsos"),
        ("TD-A04", "Contrato de prestação de serviços com cláusula de exclusividade que restringe a contratada de atender concorrentes da contratante.",
         "semantica", semantica("exclusividade", {S}),
         "difícil: termo só no título — S04 e S09 têm 'exclusividade' no título de uma seção que só trata de confidencialidade e propriedade intelectual (falso); 'NÃO estabelece exclusividade' (S02, S10) é falso; exclusividade restrita a lista de concorrentes (S06) é verdadeira"),
        ("TD-A05", "Contrato (de locação ou de prestação de serviços) com prazo de vigência inferior a doze meses (`prazo_meses` < 12).",
         "numerica", numerica("prazo_meses", "<", 12), "fácil para o código: prazo em `campos`; atas e propostas não têm o campo e valem falso"),
        ("TD-A06", "Ata que registra a aprovação de reajuste da taxa condominial.", "semantica",
         semantica("taxa_reajuste", {A}),
         "difícil: negada — 'MANTER a taxa sem reajuste' (A02, A06, A10) e 'reajuste REJEITADO' (A04, A09) contêm o termo e são falsos"),
    ],
    "teste": [
        ("TD-T01", "Ata que registra a aprovação da instalação de câmeras de monitoramento.", "semantica",
         semantica("cameras", {A}),
         "difícil: negada — instalação REJEITADA (A04, A11) é falso; seção parecida (controle de acesso por biometria, A07) é falso; teste de duas câmeras em comodato por noventa dias (A09) é indecidível"),
        ("TD-T02", "Contrato que se renova automaticamente ao fim do prazo se nenhuma das partes se manifestar.",
         "semantica", semantica("renov_auto", {L, S}),
         "difícil: revogada — L09 e S05 preveem a renovação na cláusula de prazo e a afastam nas disposições finais (falso); 'NÃO se renovará' (L03, L08, S02, S07) é falso"),
        ("TD-T03", "Contrato de locação em que a garantia é prestada por fiador E a responsabilidade do fiador se estende até a efetiva devolução das chaves, inclusive na prorrogação.",
         "semantica", semantica("fiador_chaves", {L}),
         "difícil: duas seções — exige fiador na seção de garantia E a extensão nas disposições finais; L07 tem a frase 'até a devolução das chaves' mas a garantia é caução (falso); L05, L06, L09 têm fiador sem a extensão (falso)"),
        ("TD-T04", "O documento prevê a solução de controvérsias por arbitragem.", "semantica",
         semantica("arbitragem", {L, S}),
         "difícil: termo só no título — L04, L08 e S05 têm 'arbitragem' no título da seção de foro, cujo texto só elege comarca (falso)"),
        ("TD-T05", "Contrato de prestação de serviços que prevê desconto, multa ou outra penalidade pelo descumprimento dos níveis de serviço (SLA).",
         "semantica", semantica("sla_pen", {S}),
         "difícil: seção parecida de outro assunto — a multa por rescisão (S01, S06, S09) não é penalidade de SLA; níveis de serviço sem penalidade (S04, S10) é falso; 'poderá ensejar revisão do contrato' (S05) é indecidível"),
        ("TD-T06", "Ata com reajuste da taxa condominial igual ou superior a dez por cento (`reajuste_percentual` >= 10).",
         "numerica", numerica("reajuste_percentual", ">=", 10),
         "fácil para o código: `reajuste_percentual` é 0 quando a taxa foi mantida ou o reajuste rejeitado"),
        ("TD-T07", "Proposta comercial com validade inferior a quinze dias (`validade_dias` < 15).", "numerica",
         numerica("validade_dias", "<", 15), "fácil para o código: quinze dias não é 'inferior a quinze'"),
        ("TD-T08", "O documento autoriza a presença de animais de estimação (no imóvel locado ou no condomínio).",
         "semantica", semantica("animais", {L, A}),
         "difícil: negada — 'Não é permitida' (L04) e 'MANTER a vedação' (A03, A10) são falsos; 'depende de consulta prévia' (L08) e comissão com tolerância provisória (A08) são indecidíveis; A06 cita animais só no título e diz que o ponto não foi discutido (falso)"),
        ("TD-T09", "Proposta comercial que inclui o treinamento da equipe do cliente no escopo.", "semantica",
         semantica("treinamento", {P}),
         "difícil: documento sem a cláusula — o escopo com implantação, suporte e manuais (P02, P03, P07, P10, P11) parece treinamento e é falso; 'treinamento NÃO está incluído' nas ressalvas (P05, P08) é falso"),
        ("TD-T10", "Ata de assembleia instalada com menos da metade das frações ideais presentes (`quorum_percentual` < 50).",
         "numerica", numerica("quorum_percentual", "<", 50), "fácil para o código: percentual na seção de abertura"),
        ("TD-T11", "Contrato de locação que proíbe a sublocação do imóvel.", "semantica",
         semantica("sublocacao_proibida", {L}),
         "difícil: revogada — L02 veda a sublocação e revoga a vedação nas disposições finais (falso); L08 tem 'sublocação' no título de uma seção que só trata do uso do imóvel (falso); sublocação autorizada (L04, L07) é falso"),
        ("TD-T12", "Ata que registra a aprovação das contas da administração (ainda que com ressalvas).", "semantica",
         semantica("contas_aprovadas", {A}), "fácil: rejeitadas e adiadas são falsas; 'aprovadas com ressalvas' conta"),
    ],
}


def monta_condicao(cid, texto, tipo, f, nota, docs):
    verd, ind, prova = [], [], {}
    for d in docs:
        v, sid = f(d)
        if v is True:
            verd.append(d.id); prova[d.id] = sid
        elif v == "ind":
            ind.append(d.id)
    assert len(verd) >= 4, f"{cid}: só {len(verd)} verdadeiros"
    assert all(prova.values()), f"{cid}: verdadeiro sem seção que prova"
    return {"id": cid, "condicao": texto, "tipo": tipo, "documentos_verdadeiros": verd,
            "documentos_indecidiveis": ind, "secao_que_prova": prova, "nota": nota}


def escreve(nome, chave, itens, versao=VERSAO):
    obj = {"versao": versao, "autor": AUTOR, chave: itens}
    (AQUI / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    rnd = random.Random(SEED)
    docs = []
    for i, r in L_REC.items():
        docs.append(gera_locacao(i, r, rnd))
    for i, r in S_REC.items():
        docs.append(gera_servico(i, r, rnd))
    for i, r in A_REC.items():
        docs.append(gera_ata(i, r, rnd))
    for i, r in P_REC.items():
        docs.append(gera_proposta(i, r, rnd))
    # fatos derivados e seção que prova cada campo numérico
    for d in docs:
        if d.tipo == L:
            d.fatos["garantia_fiador"] = (d.fato("garantia")[0] == "fiador", d.fato("garantia")[1])
        d.fatos_campo = {}
        for s in d.secoes:
            t = s["titulo"]
            if t.startswith("Do prazo") or t.startswith("Da vigência"):
                d.fatos_campo["prazo_meses"] = s["id"]
            if t == "Da rescisão antecipada" and d.fato("multa")[0] is True:
                d.fatos_campo["multa_alugueis"] = s["id"]
            if t.startswith("Taxa condominial"):
                d.fatos_campo["reajuste_percentual"] = s["id"]
            if t.startswith("Abertura"):
                d.fatos_campo["quorum_percentual"] = s["id"]
            if t.startswith("Validade"):
                d.fatos_campo["validade_dias"] = s["id"]
            if t.startswith("Garantia e suporte"):
                d.fatos_campo["garantia_meses"] = s["id"]
        assert 4 <= len(d.secoes) <= 8, f"{d.id}: {len(d.secoes)} seções"
    escreve("documentos.json", "documentos", [d.json() for d in docs])
    for nome, chave in (("rascunho", "rascunho.json"), ("ajuste", "condicoes_ajuste.json"), ("teste", "condicoes_teste.json")):
        escreve(chave, "casos", [monta_condicao(*c, docs) for c in CONDICOES[nome]],
                VERSAO_CONDICOES if nome != "rascunho" else VERSAO)
    print(f"{len(docs)} documentos; condições: " + ", ".join(f"{k} {len(v)}" for k, v in CONDICOES.items()))


if __name__ == "__main__":
    main()
