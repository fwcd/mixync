from __future__ import annotations
from typing import Optional, Iterable

from mixync.model.crate import Crate
from mixync.model.cue import Cue
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.options import Options
from mixync.utils.progress import ProgressLine
from mixync.utils.str import truncate

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, opts: Options):
        """Copies the contents of this store to the given other store."""

        # TODO: Deltas?

        # Copy track metadata
        tracks = list(self.tracks())
        updated_track_count = other.update_tracks(tracks)
        if opts.log:
            print(f'==> Copied {updated_track_count} tracks')
        
        # Copy directory metadata
        directories = list(self.directories())
        rel_directories = [self.relativize_directory(d, opts) for d in directories]
        dest_directories = [other.absolutize_directory(d, opts) if d else None for d in rel_directories]
        updated_directories = [d for d in dest_directories if d]
        updated_directory_count = other.update_directories(updated_directories)
        if opts.log:
            print(f'==> Copied {updated_directory_count} directories')

        # Copy track location metadata
        locations = list(self.track_locations())
        rel_locations = [self.relativize_track_location(l, opts) for l in locations]
        dest_locations = [other.absolutize_track_location(l, opts) if l else None for l in rel_locations]
        updated_locations = [l for l in dest_locations if l]
        updated_location_count = other.update_track_locations(updated_locations)
        if opts.log:
            print(f'==> Copied {updated_location_count} track locations')

        # Copy actual track files
        zipped_locations = [(l, d) for l, d in zip(locations, dest_locations) if l and d]
        with ProgressLine(len(zipped_locations), final_newline=opts.log) as progress:
            for location, dest_location in zipped_locations:
                raw = self.download_track(location.location)
                other.upload_track(dest_location.location, raw)
                if opts.log:
                    progress.print(f"Copied '{truncate(location.filename, 40)}' ({len(raw) / 1_000_000} MB)")
        if opts.log:
            print(f'==> Copied {len(zipped_locations)} track files')
        
        # Copy cue metadata
        cues = list(self.cues())
        other.update_cues(cues)
        if opts.log:
            print(f'==> Copied {len(cues)} cues')
        
        # Copy playlists
        playlists = list(self.playlists())
        updated_playlist_count = other.update_playlists(playlists)
        if opts.log:
            print(f'==> Copied {updated_playlist_count} playlists')
        
        # Copy crates
        crates = list(self.crates())
        updated_crate_count = other.update_crates(crates)
        if opts.log:
            print(f'==> Copied {updated_crate_count} crates')
        
    
    @classmethod
    def parse_ref(cls, ref: str):
        raise NotImplementedError(f'parse is not implemented for {cls.__name__}!')
    
    # Query methods

    def tracks(self) -> Iterable[Track]:
        """Fetches the tracks (and cues) from this store."""
        return []
    
    def crates(self) -> Iterable[Crate]:
        """Fetches the crates from this store."""
        return []
    
    def playlists(self) -> Iterable[Playlist]:
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
    
    def relativize_track_location(self, location: str, opts: Options) -> Optional[str]:
        """
        Outputs a 'relative' variant of the track location for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return location
    
    def absolutize_track_location(self, location: str, opts: Options) -> Optional[str]:
        """
        Outputs an 'absolute' variant of the track location for 'import',
        passed to the this store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return location

    def relativize_directory_location(self, location: str, opts: Options) -> Optional[str]:
        """
        Outputs a 'relative' variant of the directory location for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return location
    
    def absolutize_directory_location(self, location: str, opts: Options) -> Optional[str]:
        """
        Outputs an 'absolute' variant of the directory location for 'import',
        passed to the this store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return location

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
