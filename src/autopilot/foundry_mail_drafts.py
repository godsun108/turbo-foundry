"""Foundry Mail phase-zero: RFC-style drafts without sending or network access.

This is NOT a private hosted mailbox or an encrypted mail store.
No SMTP, IMAP, credentials, network calls or marketing automation exist here.
"""
from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import parseaddr
from pathlib import Path


@dataclass(frozen=True)
class MailDraft:
    to_address: str
    from_address: str
    subject: str
    body: str
    reviewed: bool = False


def _address(raw: str) -> str:
    if (not isinstance(raw, str) or len(raw) > 254 or "\r" in raw
            or "\n" in raw or raw.strip() != raw):
        raise ValueError("invalid email address")
    name, addr = parseaddr(raw)
    if name or addr != raw or addr.count("@") != 1:
        raise ValueError("simple mailbox address required")
    local, domain = addr.rsplit("@", 1)
    if not local or "." not in domain or " " in addr:
        raise ValueError("valid mailbox address required")
    return addr


def compose_draft(draft: MailDraft) -> EmailMessage:
    """Create a locally inspectable draft, never send it."""
    if not isinstance(draft, MailDraft):
        raise ValueError("draft required")
    if not isinstance(draft.reviewed, bool):
        raise ValueError("reviewed must be boolean")
    if (not isinstance(draft.subject, str) or not draft.subject.strip()
            or "\r" in draft.subject or "\n" in draft.subject
            or len(draft.subject) > 180):
        raise ValueError("invalid subject")
    if not isinstance(draft.body, str) or not draft.body.strip():
        raise ValueError("nonempty body required")
    msg = EmailMessage()
    msg["From"] = _address(draft.from_address)
    msg["To"] = _address(draft.to_address)
    msg["Subject"] = draft.subject
    msg["X-Foundry-Draft-Status"] = "reviewed" if draft.reviewed else "unreviewed"
    msg.set_content(draft.body)
    return msg


def save_draft(draft: MailDraft, destination: str | Path):
    """Write an EML file locally; fail on overwrite; no address book or transport."""
    msg = compose_draft(draft)
    destination = Path(destination)
    # Never accidentally check these into the repository; callers must choose
    # a secured, non-repository location for real addresses and content.
    import os
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(msg.as_bytes(policy=SMTP))
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
