# 案件: claim-feedback — フィードバック収集マイクロ機能

> 統合製品 (Builder → Security → Auditor) の薄い軸 (Go / TypeScript / React) を
> 意図的に踏む合成案件。各 fragment は分類器の規則表 (§8) に当たる語彙で記述。

## R1 (Go / pure function, sub-domain 1b)
The `NormalizeRating` function shall be a pure function: for identical inputs it
returns identical counts, is deterministic and idempotent, and the round-trip of
encode then decode reproduces the input.

## R2 (TypeScript / structural type, sub-domain 1a)
The `Feedback` type shall be non-null and its `severity` field shall be an enum of
{low, high}; the data type must be well-formed and non-empty.

## R3 (React / component UX, sub-domain 6b)
The Submit button shall be selectable via click and the feedback form shall be
navigable by an operator in the documented interaction scenario.

## R4 (Python / parser, sub-domain 1e)
The collector shall parse the raw payload and serialize each feedback record to
JSON format following the documented schema.
