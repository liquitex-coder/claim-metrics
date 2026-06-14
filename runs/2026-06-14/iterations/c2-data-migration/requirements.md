# 案件 c2: data-migration — 顧客テーブル移行バッチ

## R1 (SQL / decidable, 1e parser)
The migrator shall parse the source schema and serialize each migrated row to
JSON format following the documented mapping.

## R2 (SQL / boundary, 2a)
The migration shall handle the empty table and the missing-column edge case
without overflow, at most once per row.

## R3 (shell / contract, 3a)
The deploy script shall exit with a non-zero exit code on precondition failure,
witnessed by a single automated test (pass/fail).

## R4 (SQL / invariant, 1d)
After migration the number of rows shall equal the source count; the ratio of
migrated to source rows is monotonic and bounded by 1.
