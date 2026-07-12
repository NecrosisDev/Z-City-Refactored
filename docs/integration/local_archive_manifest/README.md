# Local Archive Generated File Manifest

This directory records reproducible evidence for the uploaded `Trauma.zip` archive.

## Pinned identities

- Archive SHA-256: `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`
- Canonical CSV SHA-256: `28f6eca648b80d6eca1419ce3e30fc60d2971ab743457d23aeee9d5a261cd4b0`
- Expected file rows: `1040`

## Reproduction

Run the standard-library-only generator from the repository root:

```text
python docs/integration/tools/generate_local_archive_manifest.py /path/to/Trauma.zip /tmp/LOCAL_ARCHIVE_FILE_MANIFEST.csv
```

The generator verifies the archive hash, strips the outer `TMod/` deployment wrapper, records every normalized path, candidate clean-repository path, byte size, SHA-256 and Git blob SHA-1, and rejects output that does not reproduce the pinned CSV digest.

The generated 1,040-row CSV is evidence derived from an externally held source archive and is intentionally not committed as runtime or source content. `gamemodes/trauma/**` receives a candidate mapping to `gamemodes/zcity/**`; this is only a comparison aid and does not establish semantic equivalence.
