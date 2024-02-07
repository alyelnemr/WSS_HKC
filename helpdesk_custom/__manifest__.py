
{
    "name": "Helpdesk Custom",
    "summary": "create helpdesk ticket from approval request",
    "version": "17.0.0.0.0",
    "category": "Helpdesk",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["helpdesk", "approvals"],
    "data": [
        "views/approval_request.xml",
        "views/helpdesk_ticket.xml",
    ],
}
