# 案件 c3: rust-checksum — Rust チェックサムライブラリ

## R1 (Rust / pure function, 1b)
The `crc32` function shall be a pure function: deterministic, idempotent, and the
round-trip of encode then decode reproduces identical counts.

## R2 (Rust / type, 1a)
The `Digest` type shall be non-null and its `kind` field shall be an enum of
{crc32, sha256}; the data type must be well-formed.

## R3 (Rust / fuzz, 2c)
The parser shall never crash on arbitrary input and always terminates.
