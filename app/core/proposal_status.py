from enum import Enum


class ProposalStatus(str, Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    UNDER_REVIEW = "Under Review"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    EXPIRED = "Expired"