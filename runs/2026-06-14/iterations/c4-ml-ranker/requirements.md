# 案件 c4: ml-ranker — 関連度ランキングモデル

## R1 (ML / statistical, 4a)
The ranker shall produce a statistical ranking whose distribution of relevance
scores matches the frozen dataset within tolerance.

## R2 (ML / metric, 4d)
The evaluation metric shall report precision and recall (f1 score) on a frozen
dataset; accuracy must not regress.

## R3 (ML / stochastic, 4b)
The training shall be reproducible given a fixed seed within floating point
tolerance.

## R4 (latency, 4c)
The inference shall complete within the documented latency SLA (p99) without a
blocking call.
