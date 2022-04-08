from __future__ import annotations
from typing import Optional

from mixync.model.directory import Directory
from mixync.model.track import Track
from mixync.model.track_location import TrackLocation
from mixync.options import Options
from mixync.utils.progress import ProgressLine
from mixync.utils.str import truncate

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, opts: Options):
        """Copies the contents of this store to the given other store."""

        # TODO: Deltas?

        # Copy track metadata
        tracks = self.tracks()
        other.update_tracks(tracks)
        if opts.log:
            print(f'==> Copied {len(tracks)} tracks')
        
        # Copy directory metadata
        directories = self.directories()
        rel_directories = [self.relativize_directory(d, opts) for d in directories]
        dest_directories = [other.absolutize_directory(d, opts) for d in rel_directories]
        updated_directories = [d for d in dest_directories if d]
        other.update_directories(updated_directories)
        if opts.log:
            print(f'==> Copied {len(updated_directories)} directories')

        # Copy track location metadata
        locations = self.track_locations()
        rel_locations = [self.relativize_track_location(l, opts) for l in locations]
        dest_locations = [other.absolutize_track_location(l, opts) for l in rel_locations]
        updated_locations = [l for l in dest_locations if l]
        other.update_track_locations(updated_locations)
        if opts.log:
            print(f'==> Copied {len(updated_locations)} track locations')

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
    
    @classmethod
    def parse_ref(cls, ref: str):
        raise NotImplementedError(f'parse is not implemented for {cls.__name__}!')

    def tracks(self) -> list[Track]:
        """Fetches the tracks (metadata only) from this store."""
        return []
    
    def track_locations(self) -> list[TrackLocation]:
        """Fetches the track locations from this store."""
        return []
    
    def directories(self) -> list[Directory]:
        """Fetches the music directories from this store."""
        return []

    def update_tracks(self, tracks: list[Track]):
        """Merges the given tracks (metadata only) into the store."""
        raise NotImplementedError(f'update_tracks is not implemented for {type(self).__name__}!')

    def update_track_locations(self, track_locations: list[TrackLocation]):
        """Merges the given track locations into the store."""
        raise NotImplementedError(f'update_track_locations is not implemented for {type(self).__name__}!')

    def update_directories(self, directories: list[Directory]):
        """Merges the given music directories into the store."""
        raise NotImplementedError(f'update_directories is not implemented for {type(self).__name__}!')
    
    def relativize_track_location(self, track_location: TrackLocation, opts: Options) -> Optional[TrackLocation]:
        """
        Outputs a 'relative' variant of the track location for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return track_location.clone()
    
    def absolutize_track_location(self, track_location: TrackLocation, opts: Options) -> Optional[TrackLocation]:
        """
        Outputs an 'absolute' variant of the track location for 'import',
        passed to the this store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return track_location.clone()

    def relativize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        """
        Outputs a 'relative' variant of the directory for 'export',
        passed to the other store in methods like 'copy_to'. Returning
        None will filter out this track. This is the identity function by default.
        """
        return directory.clone()
    
    def absolutize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        """
        Outputs an 'absolute' variant of the directory for 'import',
        passed to the this store in methods like 'copy_to'. This is the
        None will filter out this track. This is the identity function by default.
        """
        return directory.clone()

    def upload_track(self, location: str, raw: bytes):
        """
        Uploads a track from a TrackLocation.location as returned by
        track_locations from an in-memory buffer.
        """
        raise NotImplementedError(f'upload_track is not implemented for {type(self).__name__}!')

    def download_track(self, location: str) -> bytes:
        """
        Downloads a track from a TrackLocation.location as returned by
        track_locations to an in-memory buffer.
        """
        raise NotImplementedError(f'download_track is not implemented for {type(self).__name__}!')
    
    # TODO: Add support for crates and playlists
    # TODO: Add upload/download methods for analysis data
