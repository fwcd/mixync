from __future__ import annotations

from mixync.model.track import Track
from mixync.model.track_location import TrackLocation

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def copy_to(self, other: Store, log: bool=False):
        """Copies the contents of this store to the given other store."""

        # TODO: Deltas?

        tracks = self.tracks()
        other.update_tracks(tracks)
        if log:
            print(f'==> Copied {len(tracks)} tracks')

        locations = self.track_locations()
        other.update_track_locations(locations)
        if log:
            print(f'==> Copied {len(locations)} track locations')

        for location in locations:
            raw = self.download_track(location)
            other.upload_track(location, raw)
            if log:
                print(f'==> Copied {location.filename} ({len(raw)} bytes)')
    
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

    def upload_track(self, location: str, raw: bytes):
        """
        Uploads a track from a TrackLocation as returned by
        track_locations from an in-memory buffer.
        """
        raise NotImplementedError(f'upload_track is not implemented for {type(self).__name__}!')

    def download_track(self, location: TrackLocation) -> bytes:
        """
        Downloads a track from a TrackLocation as returned by
        track_locations to an in-memory buffer.
        """
        raise NotImplementedError(f'download_track is not implemented for {type(self).__name__}!')
    
    # TODO: Add support for crates and playlists
    # TODO: Add upload/download methods for analysis data
