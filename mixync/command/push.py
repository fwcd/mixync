from sqlalchemy.orm import make_transient

from mixync.context import Context
from mixync.model.library import LibraryEntry

def perform_push(ctx: Context):
    local = ctx.local_store
    portable = ctx.portable_store

    # TODO: Handle duplicates

    # Copy library
    entries = []
    for row in local.query(LibraryEntry):
        make_transient(row)
        row.id = None
        entries.append(row)
    portable.add_all(entries)

