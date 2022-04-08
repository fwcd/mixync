from __future__ import annotations

from mixync.model.track import Track
from mixync.model.track_location import TrackLocation
from mixync.utils.progress import ProgressLine

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, log: bool=False):
        """Copies the contents of this store to the given other store."""

        # TODO: Deltas?

        # Copy track metadata
        tracks = self.tracks()
        other.update_tracks(tracks)
        if log:
            print(f'==> Copied {len(tracks)} tracks')

        # Copy track location metadata
        locations = self.track_locations()
        rel_locations = [self.relativize_track_location(l) for l in locations]
        dest_locations = [other.absolutize_track_location(l) for l in rel_locations]
        other.update_track_locations(dest_locations)
        if log:
            print(f'==> Copied {len(locations)} track locations')

        # Copy actual track files
        with ProgressLine(len(locations), final_newline=log) as progress:
            for i, (location, dest_location) in enumerate(zip(locations, dest_locations)):
                raw = self.download_track(location.location)
                other.upload_track(dest_location.location, raw)
                if log:
                    progress.print(f"Copied '{location.filename}' ({len(raw) / 1_000_000} MB)")
        if log:
            print(f'==> Copied {len(locations)} track files')
    
    @classmethod
    def parse_ref(cls, ref: str):
        raise NotImplementedError(f'parse is not implemented for {cls.__name__}!')

    def tracks(self) -> list[Track]:
        """Fetches the tracks (metadata only) from this store."""
        return []
    
    def track_locations(self) -> list[TrackLocation]:
        """Fetches the track locations from this store."""
        return []
    
    def update_tracks(self, tracks: list[Track]):
        """Merges the given tracks (metadata only) into the store."""
        raise NotImplementedError(f'update_tracks is not implemented for {type(self).__name__}!')

    def update_track_locations(self, track_locations: list[TrackLocation]):
        """Merges the given track locations into the store."""
        raise NotImplementedError(f'update_track_locations is not implemented for {type(self).__name__}!')
    
    def relativize_track_location(self, track_location: TrackLocation) -> TrackLocation:
        """
        Outputs a 'relative' variant of the track location for 'export',
        passed to the other store in methods like 'copy_to'. This is the
        identity function by default.
        """
        return track_location.clone()
    
    def absolutize_track_location(self, track_location: TrackLocation) -> TrackLocation:
        """
        Outputs an 'absolute' variant of the track location for 'import',
        passed to the this store in methods like 'copy_to'. This is the
        identity function by default.
        """
        return track_location.clone()

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
