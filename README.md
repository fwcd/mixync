# Mixync

> **NOTE: The project is still in very early stages, so please make sure to back up your mixxxdb and your music before trying it.**

```
+-------------------+  
|    Your local     |     mixync
|  mixxxdb.sqlite   |   <--------+    +--------------------------+
+-------------------+            |    | A portable mixxxlib with |
                                 +--> |  all your tracks, cues,  |
+-------------------+            |    | grids and other metadata |
|    Your local     |   <--------+    +--------------------------+
|   music folders   |
+-------------------+

                         Push: -->
                         Pull: <--
```

A small CLI tool for copying a Mixxx database along with tracks to and from a portable folder (`*.mixxxlib`) for archival, storage on a flash drive, a web server, etc.

A portable `mixxxlib` as generated by `mixync` has the following format:

```
my-library.mixxxlib
- mixxxdb.portable.sqlite   <- Mixxx database, but with relative paths, etc.
- folder1                   <- Exported music folder
  - track1.mp3
  - track2.mp3
    ...
- folder2                   <- Exported music folder
  - track1.mp3
  - track2.mp3
    ...
```
