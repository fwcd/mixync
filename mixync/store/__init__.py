from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Optional, Iterable

from mixync.model.crate import Crate
from mixync.model.cue import Cue
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.options import Options
from mixync.utils.cli import info
from mixync.utils.progress import ProgressLine
from mixync.utils.str import truncate

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, opts: Options):
        """Copies the contents of this store to the given other store."""

        if opts.log:
            info(f'Copying from a {type(self).__name__} to a {type(other).__name__}')

        # TODO: Deltas?
        # TODO: Add methods for matching tracks to existing tracks in the DB
        #       at the store level? Perhaps just more fine grained query methods?

        # Copy directory metadata
        # NOTE: It is important that directory metadata is copied first since
        #       the store implementation may e.g. prompt the user in
        #       'absolutize_directory' about the mapping before writing anything.
        directories = list(self.directories())
        rel_directories = [self.relativize_directory(d, opts) for d in directories]
        dest_directories = [other.absolutize_directory(d, opts) if d else None for d in rel_directories]
        updated_directories = [d for d in dest_directories if d]
        updated_directory_count = 0 if opts.dry_run else other.update_directories(updated_directories)
        if opts.log:
            info(f'Copied {updated_directory_count} directory entries')

        # Copy track metadata
        tracks = list(self.tracks())
        rel_tracks = [self.relativize_track(t, opts) for t in tracks]
        dest_tracks = [other.absolutize_track(t, opts) if t else None for t in rel_tracks]
        updated_tracks = [t for t in dest_tracks if t]
        updated_track_count = 0 if opts.dry_run else other.update_tracks(updated_tracks)
        if opts.log:
            info(f'Copied {updated_track_count} track entries')

        # Copy actual track files
        zipped_tracks = [] if opts.dry_run else [(t, d) for t, d in zip(tracks, dest_tracks) if t and d]
        with ProgressLine(len(zipped_tracks), final_newline=opts.log) as progress:
            for track, dest_track in zipped_tracks:
                location = track.location
                dest_location = dest_track.location
                raw = self.download_track(location)
                other.upload_track(dest_location, raw)
                if opts.log:
                    progress.print(f"Copied '{truncate(Path(location).name, 40)}' ({len(raw) / 1_000_000} MB)")
        if opts.log:
            info(f'Copied {len(zipped_tracks)} track files')
        
        # Copy playlists
        playlists = list(self.playlists())
        updated_playlist_count = 0 if opts.dry_run else other.update_playlists(playlists)
        if opts.log:
            info(f'Copied {updated_playlist_count} playlists')
        
        # Copy crates
        crates = list(self.crates())
        updated_crate_count = 0 if opts.dry_run else other.update_crates(crates)
        if opts.log:
            info(f'Copied {updated_crate_count} crates')
        
    
    @classmethod
    def parse_ref(cls, ref: str):
        raise NotImplementedError(f'parse is not implemented for {cls.__name__}!')
    
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
    
    def update_tracks(self, tracks: list[Track]) -> int:
        """Merges the given tracks (metadata only) into the store."""
        raise NotImplementedError(f'update_tracks is not implemented for {type(self).__name__}!')

    def update_crates(self, crates: list[Crate]) -> int:
        """Merges the given crates into this store."""
        raise NotImplementedError(f'update_crates is not implemented for {type(self).__name__}!')

    def update_playlists(self, playlists: list[Playlist]) -> int:
        """Merges the given playlists into this store."""
        raise NotImplementedError(f'update_playlists is not implemented for {type(self).__name__}!')

    def update_directories(self, directories: list[Directory]) -> int:
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
