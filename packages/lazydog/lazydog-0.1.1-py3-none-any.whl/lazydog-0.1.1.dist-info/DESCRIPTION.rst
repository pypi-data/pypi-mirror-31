Python module monitoring high-level file system events like Creation, Modification, Move, Copy, and Deletion of files and folders. Lazydog tries to aggregate low-level events between them in order to emit a minimum number of high-level events (actualy one event per user action). Lazydog uses python Watchdog module to detect low-level events.


