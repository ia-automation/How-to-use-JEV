"""UMA Choice de 7 destinos — a pergunta que a barra de comando faria a cada tecla.

Em inglês (idioma principal do Jev); o texto digitado, em português, vai no state sob `text`.
Sem afinação: este exemplo mede latência, não acerto (o rótulo é do próprio construtor).
"""

DESTINO = "destino"

PERGUNTAS = {
    DESTINO: {
        "type": "choice",
        "instructions": {
            "question": "The user typed `text` into the command bar of a real-estate CRM. Which action does it ask for?",
            "rules": ("Pick exactly one. A person's name or a phone number alone means finding that client; a property "
                      "code (like AP-48213 or a 4-digit number) alone means finding that property. Pick `nenhum` when "
                      "`text` is not a command at all: a pasted draft, a greeting, a question to support, or noise."),
        },
        "criteria": {
            "buscar_cliente": "Find or open a client, lead or contact record: by name, phone number or lead source.",
            "buscar_imovel": "Find or open properties or a listing: by code, neighbourhood, type, price, size or features.",
            "criar_tarefa": "Create a reminder, to-do or follow-up for the user, usually with a deadline.",
            "abrir_relatorio": "Open a report, chart, ranking or aggregate number about sales, leads, visits or commissions.",
            "agendar_visita": "Schedule, book or reschedule a property visit for a client at a date or time.",
            "enviar_mensagem": "Send a message, WhatsApp or e-mail to a client, or reply to one.",
            "nenhum": "Not a command: pasted text, a greeting, a note, a question about the CRM itself, or gibberish.",
        },
    }
}
