import sqlalchemy

from pathlib import Path

class PortableStore:
    """A wrapper around the portable mixxxlib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

        db_path = path / 'mixxxdb.portable.sqlite3'
        self.connection = sqlalchemy.create_engine(f'sqlite:///{db_path}')

        self.create_tables()
    
    def create_tables(self):
        # Create 'track_locations' table
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS track_locations ('
            '  id integer PRIMARY KEY AUTOINCREMENT,'
            '  location varchar(512) UNIQUE,'
            '  filename varchar(512),'
            '  directory varchar(512),'
            '  filesize integer,'
            '  fs_deleted integer,'
            '  needs_verification integer'
            ')'
        )
        
        # Create 'library' table
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS library ('
            '  id integer PRIMARY KEY AUTOINCREMENT,'
            '  artist varchar(64),'
            '  title varchar(64),'
            '  album varchar(64),'
            '  year varchar(16),'
            '  genre varchar(64),'
            '  tracknumber varchar(3),'
            '  location integer REFERENCES track_locations(location),'
            '  comment varchar(256),'
            '  url varchar(256),'
            '  duration float,'
            '  samplerate integer,'
            '  cuepoint integer,'
            '  bpm float,'
            '  wavesummaryhex blob,'
            '  channels integer,'
            '  datetime_added DEFAULT CURRENT_TIMESTAMP,'
            '  mixxx_deleted integer,'
            '  played integer,'
            '  header_parsed integer DEFAULT 0,'
            '  filetype varchar(8) DEFAULT "?",'
            '  replaygain float DEFAULT 0,'
            '  timesplayed integer DEFAULT 0,'
            '  rating integer DEFAULT 0,'
            '  key varchar(8) DEFAULT "",'
            '  beats blob,'
            '  beats_version text,'
            '  composer varchar(64) DEFAULT "",'
            '  bpm_lock integer DEFAULT 0,'
            '  beats_sub_version text DEFAULT "",'
            '  keys blob,'
            '  keys_version text,'
            '  keys_sub_version text,'
            '  key_id integer DEFAULT 0,'
            '  grouping text DEFAULT "",'
            '  album_artist text DEFAULT "",'
            '  coverart_source integer DEFAULT 0,'
            '  coverart_type integer DEFAULT 0,'
            '  coverart_location text DEFAULT "",'
            '  coverart_color integer,'
            '  coverart_digest blob,'
            '  replaygain_peak real DEFAULT -1.0,'
            '  tracktotal text DEFAULT "//",'
            '  color integer,'
            '  last_played_at datetime DEFAULT null,'
            '  source_synchronized_ms integer DEFAULT null'
            ')'
        )
