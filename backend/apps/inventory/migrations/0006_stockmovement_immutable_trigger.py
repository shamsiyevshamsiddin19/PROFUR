"""Append-only DB trigger for StockMovement.

Prevents UPDATE and DELETE at the PostgreSQL level. On non-PostgreSQL
backends (e.g. SQLite in dev) the migration is a no-op — ORM-level
protection still applies.
"""

from django.db import connection, migrations


def forwards(apps, schema_editor):
    if connection.vendor != "postgresql":
        return
    schema_editor.execute("""
        CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Ledger entries are immutable: %% not allowed',
                TG_OP;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS ledger_append_only
            ON inventory_stockmovement;

        CREATE TRIGGER ledger_append_only
            BEFORE UPDATE OR DELETE ON inventory_stockmovement
            FOR EACH ROW
            EXECUTE FUNCTION prevent_ledger_mutation();
    """)


def backwards(apps, schema_editor):
    if connection.vendor != "postgresql":
        return
    schema_editor.execute("""
        DROP TRIGGER IF EXISTS ledger_append_only
            ON inventory_stockmovement;
        DROP FUNCTION IF EXISTS prevent_ledger_mutation();
    """)


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0005_stockbalance_low_stock_notified_stocknotification"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
