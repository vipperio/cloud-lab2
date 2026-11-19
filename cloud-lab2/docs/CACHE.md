# Redis Caching

## Architecture

The application uses Amazon ElastiCache for Redis as a shared
cache between ECS Fargate tasks and Amazon RDS PostgreSQL.

Configuration:

- Redis version: 7.1
- Instance type: cache.t4g.micro
- Region: eu-north-1
- Port: 6379
- Cache strategy: Cache-Aside
- TTL: 60 seconds
- Encryption at rest: enabled
- Encryption in transit: enabled
- Access: private network, ECS security group only

## Cache implementation

The GET /notes endpoint supports two modes:

- GET /notes?use_cache=true
- GET /notes?use_cache=false

When caching is enabled, the application checks Redis first.
If the requested data exists, it is returned directly.
Otherwise, the application queries PostgreSQL and stores
the result in Redis for 60 seconds.

POST /notes invalidates the cached list after creating a note.

## Functional verification

| Operation | Hits | Misses | DB queries |
|---|---:|---:|---:|
| First GET | 0 | 1 | 1 |
| Second GET | 1 | 1 | 1 |
| GET after POST | 1 | 2 | 2 |

After POST /notes, Redis returned TTL = -2, confirming
that the cached key had been removed.

The next GET returned the updated list containing four notes.

## Cloud performance comparison

Both tests used the same k6 scenario, 30 maximum virtual
users and a duration of 10 minutes.

| Metric | Cache OFF | Cache ON |
|---|---:|---:|
| HTTP requests | 17990 | 18020 |
| Requests per second | 29.96 | 30.00 |
| Average latency (ms) | 656.99 | 655.78 |
| Median latency (ms) | 552.85 | 72.07 |
| p95 latency (ms) | 1690 | 3230 |
| p99 latency (ms) | 2060 | 4240 |
| Failed requests | 2 | 5 |
| Observed DB list queries | 12628 | 201 |
| Observed cache hits | 0 | 1058 |
| Observed cache misses | 0 | 201 |
| Observed cache hit rate | N/A | 84.03% |

## Limitations

Application statistics are stored separately in each ECS
process. Therefore, the reported DB query counts and cache
hit rate are not guaranteed to represent the entire cluster.

The second test started with a larger database because the
first test inserted additional notes.

The received data volume increased from 820 MB to 2.5 GB.
Consequently, the comparison does not isolate the effect
of caching from changes in database size and ECS capacity.

Cache invalidation reduces stale data after writes. However,
concurrent reads and writes may introduce race conditions.

## Conclusion

Redis caching was successfully integrated into the AWS
infrastructure. The observed cache hit rate reached 84.03%.

Median latency decreased by approximately 87%, while the
average latency remained almost unchanged.

The p95 and p99 latency increased during the second test.
A controlled experiment with identical initial datasets
and shared counters would be required to quantify the
isolated performance improvement.

## Evidence

- ../loadtest/cloud-off-stats.json
- ../loadtest/cloud-on-stats.json
- ../loadtest/cloud-off-summary.json
- ../loadtest/cloud-on-summary.json
- ../loadtest/redis-CacheHits.json
- ../loadtest/redis-CacheMisses.json
