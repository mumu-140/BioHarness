import hashlib

import rfc8785


def canonical_json_bytes(value: object) -> bytes:
    return rfc8785.dumps(value)


def sha256_canonical(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
