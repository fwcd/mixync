from sqlalchemy.orm import make_transient

from mixync.context import Context
from mixync.model.library import LibraryEntry

def perform_push(ctx: Context):
    copy_library(ctx)

def copy_library(ctx: Context):
    entries = []
    with ctx.local_store.session() as local_session:
        with ctx.portable_store.session() as portable_session:
            for row in local_session.query(LibraryEntry):
                make_transient(row)
                row.id = None
                # TODO: Find a more performant solution, perhaps involving a
                #       unique constraint across (title, artist) on the portable
                #       db and ignoring when a constraint would be violated?
                #       (this seems to be non-trivial with the high-level ORM API though)
                if not portable_session.query(LibraryEntry).where(LibraryEntry.title == row.title, LibraryEntry.artist == row.artist).first():
                    entries.append(row)
            portable_session.add_all(entries)
            portable_session.commit()
    print(f'==> Copied {len(entries)} library entries')
