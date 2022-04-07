from model.track import Track
from model.track_location import TrackLocation

class Store:
    """A store interface for music and metadata, e.g. a local mixxxdb or a remote server."""

    def tracks(self) -> list[Track]:
        """Fetches the tracks from this store."""
        return []
    
    def track_locations(self) -> list[TrackLocation]:
        """Fetches the track locations from this store."""
        return []
    
    def update_tracks(self, tracks: list[Track]):
        raise NotImplementedError('update_tracks is not implemented!')

    def update_track_locations(self, track_locations: list[TrackLocation]):
        raise NotImplementedError('update_track_locations is not implemented!')
