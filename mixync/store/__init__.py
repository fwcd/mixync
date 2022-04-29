from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path
from shutil import get_terminal_size
from typing import Callable, Optional, Iterable, TypeVar

from mixync.model.crate import Crate, CrateHeader
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist, PlaylistHeader
from mixync.model.track import Track, TrackHeader
from mixync.options import Options
from mixync.utils.cli import info
from mixync.utils.progress import ProgressLine
from mixync.utils.str import truncate
from mixync.utils.list import with_compact, zip_or
from mixync.utils.typing import HasId

T = TypeVar('T', bound='HasId')

@dataclass
class IdMapping:
    """Maps ids between stores for a specific resource (tracks/directories/...)."""

    mapping: dict[int, int] = field(default_factory=dict)

    def filter_unmapped(self, values: list[T]) -> list[Optional[T]]:
        """Turns the values without a mapped id into None."""
        return [None if v.id in self.mapping else v for v in values]
    
    def apply_or_match(self, values: list[T], matcher: Callable[[list[T]], Iterable[Optional[int]]]) -> list[T]:
        """Maps the values with a mapped id directly and uses the matcher function for all others."""
        known_ids = [self.get(d.id) if d.id else None for d in values]
        unmapped_values = self.filter_unmapped(values)
        mapped_ids = zip_or(known_ids, with_compact(matcher, unmapped_values))
        mapped_values = [replace(d, id=id) for d, id in zip(values, mapped_ids)]
        return mapped_values
    
    def get(self, id: int) -> Optional[int]:
        """Fetches the mapped value or none."""
        return self.mapping.get(id, None)

    def update(self, values: list[T], new_ids: list[int]):
        for v, id in zip(values, new_ids):
            if v.id:
                self.mapping[v.id] = id

@dataclass
class IdMappings:
    """Id mappings for the different resource types that stores deal with."""

    tracks: IdMapping = field(default_factory=IdMapping)
    directories: IdMapping = field(default_factory=IdMapping)
    playlists: IdMapping = field(default_factory=IdMapping)
    crates: IdMapping = field(default_factory=IdMapping)

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, opts: Options):
        """Copies the contents of this store to the given other store."""

        if opts.log:
            info(f'Copying from a {type(self).__name__} to a {type(other).__name__}')
        
        # TODO: Deltas?
        # TODO: Add methods for matching tracks to existing tracks in the DB
        #       at the store level? Perhaps just more fine grained query methods?

        # Create empty id mappings
        id_mappings = IdMappings()

        # Copy metadata and tracks
        # NOTE: It is important that directory metadata is copied first since
        #       the store implementation may e.g. prompt the user in
        #       'absolutize_directory' about the mapping before writing anything.
        #       Also we want to make sure that tracks are copied before playlists
        #       and crates, since otherwise the ids wouldn't be mapped.
        self.copy_directories_to(other, id_mappings, opts)
        tracks, dest_tracks = self.copy_tracks_to(other, id_mappings, opts)
        self.copy_track_files_to(other, tracks, dest_tracks, id_mappings, opts)
        self.copy_playlists_to(other, id_mappings, opts)
        self.copy_crates_to(other, id_mappings, opts)

    def copy_directories_to(self, other: Store, id_mappings: IdMappings, opts: Options):
        """Copies directory metadata to the given store."""
        directories = list(self.directories())
        # Relativize paths here, absolute them in the other store
        rel_directories = [self.relativize_directory(d, opts) for d in directories]
        dest_directories = [other.absolutize_directory(d, opts) if d else None for d in rel_directories]
        updated_directories = [d for d in dest_directories if d]
        # Map the ids (by first looking up already known mappings, then matching)
        mapped_directories = id_mappings.directories.apply_or_match(updated_directories, other.match_directories)
        # Update the directories
        if not opts.dry_run:
            new_ids = other.update_directories(mapped_directories)
            id_mappings.directories.update(directories, new_ids)
        if opts.log:
            info(f'Copied {len(mapped_directories)} directory entries')

    def copy_tracks_to(self, other: Store, id_mappings: IdMappings, opts: Options) -> tuple[list[Track], list[Optional[Track]]]:
        """Copies track metadata ot the given store."""
        tracks = list(self.tracks())
        # Relativize paths here, absolute them in the other store
        rel_tracks = [self.relativize_track(t, opts) for t in tracks]
        dest_tracks = [other.absolutize_track(t, opts) if t else None for t in rel_tracks]
        updated_tracks = [t for t in dest_tracks if t]
        # Map the ids (by first looking up already known mappings, then matching)
        mapped_tracks = id_mappings.tracks.apply_or_match(updated_tracks, lambda ts: other.match_tracks([t.header() for t in ts]))
        # Update the tracks
        if not opts.dry_run:
            new_ids = other.update_tracks(mapped_tracks)
            id_mappings.tracks.update(tracks, new_ids)
        if opts.log:
            info(f'Copied {len(mapped_tracks)} track entries')
        return tracks, dest_tracks

    def copy_track_files_to(self, other: Store, tracks: list[Track], dest_tracks: list[Optional[Track]], id_mappings: IdMappings, opts: Options):
        """Copies actual track files to the given store."""
        zipped_tracks = [] if opts.dry_run else [(t, d) for t, d in zip(tracks, dest_tracks) if d]
        with ProgressLine(len(zipped_tracks), final_newline=opts.log) as progress:
            for track, dest_track in zipped_tracks:
                location = track.location
                dest_location = dest_track.location
                raw = self.download_track(location)
                other.upload_track(dest_location, raw)
                if opts.log:
                    prefix = "Copied '"
                    suffix = f"' ({len(raw) / 1_000_000} MB)"
                    terminal_width = get_terminal_size((80, 20)).columns
                    available_width = max(5, terminal_width - len(progress.prefix()) - len(prefix) - len(suffix) - 3)
                    progress.print(prefix + truncate(Path(location).name, available_width) + suffix)
        if opts.log:
            info(f'Copied {len(zipped_tracks)} track files')

    def copy_playlists_to(self, other: Store, id_mappings: IdMappings, opts: Options):
        """Copies playlists to the given store."""
        playlists = list(self.playlists())
        # Map playlist ids and their track ids
        mapped_playlists = []
        for playlist in id_mappings.playlists.apply_or_match(playlists, lambda ps: other.match_playlists([p.header() for p in ps])):
            mapped_ids = set()
            for track_id in playlist.track_ids:
                mapped_id = id_mappings.tracks.get(track_id)
                if mapped_id:
                    mapped_ids.add(mapped_id)
                else:
                    print(f"Warning: Track id {track_id} from playlist '{playlist.name}' could not be mapped.")
            mapped_playlists.append(replace(playlist, track_ids=mapped_ids))
        # Update the playlists
        if not opts.dry_run:
            new_ids = other.update_playlists(mapped_playlists)
            id_mappings.playlists.update(playlists, new_ids)
        if opts.log:
            info(f'Copied {len(mapped_playlists)} playlists')
    
    def copy_crates_to(self, other: Store, id_mappings: IdMappings, opts: Options):
        """Copies crates to the given store."""
        crates = list(self.crates())
        # Map crate ids and their track ids
        mapped_crates = []
        for crate in id_mappings.crates.apply_or_match(crates, lambda cs: other.match_crates([c.header() for c in cs])):
            mapped_ids = set()
            for track_id in crate.track_ids:
                mapped_id = id_mappings.tracks.get(track_id)
                if mapped_id:
                    mapped_ids.add(mapped_id)
                else:
                    print(f"Warning: Track id {track_id} from crate '{crate.name}' could not be mapped.")
            mapped_crates.append(replace(crate, track_ids=mapped_ids))
        # Update the crates
        if not opts.dry_run:
            new_ids = other.update_crates(mapped_crates)
            id_mappings.crates.update(crates, new_ids)
        if opts.log:
            info(f'Copied {len(mapped_crates)} crates')

    @classmethod
    def parse_ref(cls, ref: str):
        raise NotImplementedError(f'parse is not implemented for {cls.__name__}!')
    
    # Match methods

    def match_tracks(self, tracks: list[TrackHeader]) -> Iterable[Optional[int]]:
        """Fetches track ids that match the name/artist or similar."""
        return [None for _ in tracks]

    def match_crates(self, crates: list[CrateHeader]) -> Iterable[Optional[int]]:
        """Fetches crate ids that match the name or similar."""
        return [None for _ in crates]
    
    def match_playlists(self, playlists: list[PlaylistHeader]) -> Iterable[Optional[int]]:
        """Fetches playlist ids that match the name or similar."""
        return [None for _ in playlists]

    def match_directories(self, directories: list[Directory]) -> Iterable[Optional[int]]:
        """Fetches directory ids that match the location or similar."""
        return [None for _ in directories]

    # Query methods

    def tracks(self, name: Optional[str]=None, artist: Optional[str]=None) -> Iterable[Track]:
        """Fetches the tracks (and cues) from this store."""
        return []
    
    def crates(self, name: Optional[str]=None) -> Iterable[Crate]:
        """Fetches the crates from this store."""
        return []
    
    def playlists(self, name: Optional[str]=None) -> Iterable[Playlist]:
        """Fetches the playlists from this store."""
        return []

    def directories(self) -> Iterable[Directory]:
        """Fetches the directories from this store."""
        return []
    
    # Update methods
    
    def update_tracks(self, tracks: list[Track]) -> list[int]:
        """Merges the given tracks (metadata only) into the store."""
        raise NotImplementedError(f'update_tracks is not implemented for {type(self).__name__}!')

    def update_crates(self, crates: list[Crate]) -> list[int]:
        """Merges the given crates into this store."""
        raise NotImplementedError(f'update_crates is not implemented for {type(self).__name__}!')

    def update_playlists(self, playlists: list[Playlist]) -> list[int]:
        """Merges the given playlists into this store."""
        raise NotImplementedError(f'update_playlists is not implemented for {type(self).__name__}!')

    def update_directories(self, directories: list[Directory]) -> list[int]:
        """Merges the given directories into this store."""
        raise NotImplementedError(f'update_directories is not implemented for {type(self).__name__}!')

    # Relativization/absolutization methods
    
    def relativize_track(self, track: Track, opts: Options) -> Optional[Track]:
        """
        Outputs a 'relative' variant of the track location for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return deepcopy(track)
    
    def absolutize_track(self, track: Track, opts: Options) -> Optional[Track]:
        """
        Outputs an 'absolute' variant of the track location for 'import',
        passed to the this store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return deepcopy(track)

    def relativize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        """
        Outputs a 'relative' variant of the directory location for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return deepcopy(directory)
    
    def absolutize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        """
        Outputs an 'absolute' variant of the directory location for 'import',
        passed to the this store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return deepcopy(directory)

    # Upload/download methods

    def upload_track(self, location: str, raw: bytes):
        """
        Uploads a track from a track location from an in-memory buffer.
        """
        raise NotImplementedError(f'upload_track is not implemented for {type(self).__name__}!')

    def download_track(self, location: str) -> bytes:
        """
        Downloads a track from a track location to an in-memory buffer.
        """
        raise NotImplementedError(f'download_track is not implemented for {type(self).__name__}!')
    
    # TODO: Add upload/download methods for analysis data
