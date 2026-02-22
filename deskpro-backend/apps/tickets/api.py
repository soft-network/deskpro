"""
Tickets API — all endpoints require a valid JWT (JWTBearer).

GET  /api/tickets/      → list of all tickets for the tenant
GET  /api/tickets/{id}  → single ticket with messages
"""
from ninja import Router
from ninja.errors import HttpError

from apps.tickets.auth import CookieAuth
from apps.tickets.models import Ticket
from apps.tickets.schemas import TicketOut

router = Router(tags=["Tickets"])
jwt_auth = CookieAuth()


@router.get("/", response=list[TicketOut], auth=jwt_auth)
def list_tickets(request):
    """Return all tickets for the current tenant (DB routed via thread-local)."""
    tickets = Ticket.objects.prefetch_related("messages").all()
    return [_serialize_ticket(t) for t in tickets]


@router.get("/{ticket_id}", response=TicketOut, auth=jwt_auth)
def get_ticket(request, ticket_id: int):
    """Return a single ticket by ID, or 404 if not found."""
    try:
        ticket = Ticket.objects.prefetch_related("messages").get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise HttpError(404, f"Ticket {ticket_id} not found.")
    return _serialize_ticket(ticket)


def _serialize_ticket(ticket: Ticket) -> dict:
    return {
        "id": ticket.pk,
        "subject": ticket.subject,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "status": ticket.status,
        "priority": ticket.priority,
        "channel": ticket.channel,
        "assignee": ticket.assignee,
        "tags": ticket.tags or [],
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "messages": [
            {
                "id": str(msg.id),
                "sender": msg.sender,
                "body": msg.body,
                "timestamp": msg.timestamp,
            }
            for msg in ticket.messages.all()
        ],
    }
