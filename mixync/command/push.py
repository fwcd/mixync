from sqlalchemy.orm import make_transient
from pathlib import Path

from mixync.context import Context
from mixync.model.track import Track
from mixync.model.track_locations import TrackLocation

def perform_push(ctx: Context):
    # Copy database
    copy_db_library(ctx)
    copy_db_track_locations(ctx)

    # TODO: Copy (rsync?) file trees
    # TODO: Copy (rsync?) analysis meta

def copy_db_library(ctx: Context):
    entries = []
    with ctx.local_store.session() as local_session:
        with ctx.portable_store.session() as portable_session:
            for row in local_session.query(Track):
                make_transient(row)
                row.id = None
                # TODO: Find a more performant solution, perhaps involving a
                #       unique constraint across (title, artist) on the portable
                #       db and ignoring when a constraint would be violated?
                #       (this seems to be non-trivial with the high-level ORM API though)
                if not portable_session.query(Track).where(Track.title == row.title, Track.artist == row.artist).first():
                    entries.append(row)

            portable_session.add_all(entries)
            portable_session.commit()

    print(f'==> Copied {len(entries)} library entries')

def copy_db_track_locations(ctx: Context):
    entries = []
    visited_locations = set()
    with ctx.local_store.session() as local_session:
        with ctx.portable_store.session() as portable_session:
            for row in local_session.query(TrackLocation):
                make_transient(row)
                row.id = None

                # Use relative paths in portable db
                directory = Path(row.directory)
                rel_location = Path(row.location).relative_to(directory.parent).as_posix()
                row.directory = directory.name
                row.location = rel_location

                if not row.fs_deleted and rel_location not in visited_locations and not portable_session.query(TrackLocation).where(TrackLocation.location == rel_location).first():
                    visited_locations.add(rel_location)
                    entries.append(row)

            portable_session.add_all(entries)
            portable_session.commit()

    print(f'==> Copied {len(entries)} track locations')
