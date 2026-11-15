# TRICORDER / SENTINEL local data foundation

Dependency-free Python standard-library modules shared by both projects.

## Requirements
- Python 3.10+
- No third-party packages or network access

## Simulate and validate observations
```sh
python tricorder.py simulate --count 100 --seed 7 --output sample.jsonl
python tricorder.py validate sample.jsonl
```

## Append to the durable local store
```sh
python -c "from tricorder import simulated_records; from tricorder_store import ObservationStore; s=ObservationStore('data/observations.jsonl'); [s.append(x) for x in simulated_records(20)]; print(s.last_sequence)"
```

Each stored line is a JSON envelope containing a monotonically increasing
sequence number, the unchanged observation, and a SHA-256 checksum over the
canonical envelope payload. Appends call fsync before acknowledging success.

## Recovery and integrity
- A non-newline-terminated final fragment is treated as an interrupted write
  and truncated to the last complete record on startup.
- A malformed complete line, invalid observation, sequence gap, or checksum
  mismatch fails closed with StoreCorruptionError.
- This is a single-writer local store. It does not claim safe concurrent
  multi-process writers, power-loss guarantees beyond the filesystem's
  documented behavior, or protection against a privileged attacker rewriting
  both data and checksums.
- Back up the data file; checksum chains and signed provenance are future work.

## Sensor health
`sensor_health.summarize_sensor_health` derives an advisory status from the
latest observation per sensor. It distinguishes online, stale, out_of_range,
sensor_fault, and uncalibrated. It is not a certified alarm or safety system.

## Tests
```sh
python -m unittest -v
```

All Genesis ingestion remains read-only. No device actuation is implemented.
