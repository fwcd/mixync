# Mixync

Like `rsync` but for Mixxx databases and music.

> **NOTE: The project is still in very early stages, so please make sure to back up your mixxxdb and your music before trying it.**

```
+-------------------+
|    Your local     |
|  mixxxdb.sqlite   |   <--+                +--------------------------+
+-------------------+      |                | A portable musiclib with |
                           +--> mixync <--> |  all your tracks, cues,  |
+-------------------+      |                | grids and other metadata |
|    Your local     |   <--+                +--------------------------+
|   music folders   |
+-------------------+
```

A small CLI tool for copying a Mixxx database along with tracks to and from a portable folder (`*.mixxxlib`) for archival, storage on a flash drive, a web server, etc.

## Usage

All invocations of `mixync` follow the same pattern, roughly analogous to `rsync` or `cp`:

```sh
mixync [source] [dest]
```

where `source` and `dest` are so-called _refs_, which describe a store for metadata and music. Each ref can be one of the following:

- A local mixxxdb, e.g. `@local`, `path/to/mixxxdb.sqlite`
- A portable musiclib, e.g. `path/to/library.musiclib`

For example:

```sh
# Copy your local mixxxdb and music to a portable musiclib
mixync @local ~/my-library.musiclib
```

```sh
# Copy a portable musiclib to your local mixxxdb and music folders
mixync ~/my-library.musiclib @local
```

## Portable Musiclib Structure

A portable `musiclib` (a new format introduced by this tool) as generated by `mixync` has the following directory structure:

```
my-library.musiclib
- library.sqlite3           <- Tracks (with portable paths), playlists, crates and cues
- folder1                   <- Exported music folder
  - track1.mp3
  - track2.mp3
    ...
- folder2                   <- Exported music folder
  - track1.mp3
  - track2.mp3
    ...
```
