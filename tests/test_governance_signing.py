import hashlib
import hmac
from unittest.mock import MagicMock, patch

from app.core.crypto_utils import encrypt_secret
from app.models.governance_event_log import GovernanceEventLog
from app.models.governance_key import GovernanceKey
from app.services.governance_service import (
    backfill_missing_signing_key_ids,
    log_governance_event,
)


class QueryStub:
    def __init__(self, *, first_result=None, all_result=None):
        self._first_result = first_result
        self._all_result = all_result or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._first_result

    def all(self):
        return self._all_result


def test_log_governance_event_sets_signing_key_id():
    db = MagicMock()
    db.query.return_value = QueryStub(first_result=None)

    with (
        patch("app.services.governance_service.compute_event_hash", return_value="hash-123"),
        patch("app.services.governance_service.sign_hash", return_value=("sig-123", "key-123")),
        patch("app.services.governance_service.check_event_spike") as check_event_spike,
    ):
        log_governance_event(
            db=db,
            event_type="FREEZE",
            tenant_id="tenant-1",
            previous_version="1.0.0",
            new_version=None,
            reason="test",
        )

    event = db.add.call_args.args[0]
    assert isinstance(event, GovernanceEventLog)
    assert event.signature == "sig-123"
    assert event.signing_key_id == "key-123"
    db.flush.assert_called_once()
    check_event_spike.assert_called_once()


def test_backfill_missing_signing_key_id():
    secret = "super-secret"
    key = GovernanceKey(
        key_id="key-1",
        encrypted_secret=encrypt_secret(secret),
        is_active=True,
    )
    event_hash = "hash-123"
    signature = hmac.new(
        secret.encode(),
        event_hash.encode(),
        hashlib.sha256,
    ).hexdigest()
    event = GovernanceEventLog(
        tenant_id="tenant-1",
        event_type="FREEZE",
        reason="legacy",
        event_hash=event_hash,
        signature=signature,
        signing_key_id=None,
    )

    db = MagicMock()

    def query_side_effect(model):
        if model is GovernanceEventLog:
            return QueryStub(all_result=[event])
        if model is GovernanceKey:
            return QueryStub(all_result=[key])
        raise AssertionError(f"Unexpected model queried: {model}")

    db.query.side_effect = query_side_effect

    updated = backfill_missing_signing_key_ids(db)

    assert updated == 1
    assert event.signing_key_id == "key-1"
    db.flush.assert_called_once()
