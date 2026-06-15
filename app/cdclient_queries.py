"""Structured CDClient query helpers.

Lightweight query layer for cdclient.sqlite — not a full ORM, but centralizes
common lookups used across the dashboard.
"""
from app.luclient import query_cdclient


def get_zone_display_name(zone_id):
    row = query_cdclient(
        'select DisplayDescription from ZoneTable where zoneID = ?',
        [zone_id],
        one=True,
    )
    return row[0] if row else "Unknown Zone"


def get_render_component_id(lot):
    row = query_cdclient(
        'select component_id from ComponentsRegistry where component_type = 2 and id = ?',
        [lot],
        one=True,
    )
    return row[0] if row else None


def get_object_row(lot):
    return query_cdclient(
        'Select id, name, displayName from Objects where id = ?',
        [lot],
        one=True,
    )


def get_loot_objects():
    return query_cdclient('Select id, name, displayName from Objects where type = "Loot"')
