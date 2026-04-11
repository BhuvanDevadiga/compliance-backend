from app.db.database import build_engine_kwargs, resolve_database_url


def test_resolve_database_url_falls_back_to_local_sqlite():
    assert resolve_database_url(None).endswith("/compliance.db")
    assert resolve_database_url(None).startswith("sqlite:///")


def test_resolve_database_url_prefers_explicit_value():
    assert (
        resolve_database_url("postgresql+psycopg2://user:pass@localhost:5432/app")
        == "postgresql+psycopg2://user:pass@localhost:5432/app"
    )


def test_build_engine_kwargs_for_sqlite_uses_thread_safe_connect_args():
    kwargs = build_engine_kwargs("sqlite:///./compliance.db")

    assert kwargs["pool_pre_ping"] is True
    assert kwargs["connect_args"] == {"check_same_thread": False}
    assert "pool_size" not in kwargs
