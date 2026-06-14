# 案件 c5: go-concurrency — Go 並行ワーカープール

## R1 (Go / concurrency, 5a)
The worker pool shall be free of data race and deadlock under concurrent
interleaving across threads.

## R2 (Go / pure function, 1b)
The `hashKey` function shall be a pure function: deterministic and idempotent.

## R3 (Go / soak, 5c)
The pool shall not leak goroutines over a long run (no accumulation over time).
