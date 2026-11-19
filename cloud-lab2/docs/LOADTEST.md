# Load Testing

## Tool

Grafana k6 running in a Docker container.

## Test scenario

Each iteration performs:

1. One POST /notes request.
2. Eight GET /notes requests.
3. One GET /notes/{id} request.
4. A one-second pause.

The test uses a mixed workload containing one write
and nine read operations.

## Load profile

| Stage | Duration | Virtual users |
|---|---|---|
| Ramp-up | 3 minutes | Up to 30 |
| Constant load | 5 minutes | 30 |
| Ramp-down | 2 minutes | 30 to 0 |

Total duration: 10 minutes.

## Running the tests

PowerShell, from the project root:

    $url = terraform -chdir=terraform output -raw app_url

    Invoke-RestMethod -Method Post "$url/redis/reset"

    docker run --rm -v "${PWD}/loadtest:/scripts" grafana/k6 run -e BASE_URL=$url -e USE_CACHE=false -e VUS=30 --summary-export=/scripts/cloud-off-summary.json /scripts/cloud-test.js

    Invoke-RestMethod "$url/redis/stats" | ConvertTo-Json | Set-Content ./loadtest/cloud-off-stats.json

For the second test:

    Invoke-RestMethod -Method Post "$url/redis/reset"

    docker run --rm -v "${PWD}/loadtest:/scripts" grafana/k6 run -e BASE_URL=$url -e USE_CACHE=true -e VUS=30 --summary-export=/scripts/cloud-on-summary.json /scripts/cloud-test.js

    Invoke-RestMethod "$url/redis/stats" | ConvertTo-Json | Set-Content ./loadtest/cloud-on-stats.json

## Results

| Metric | Cache OFF | Cache ON |
|---|---:|---:|
| Duration (minutes) | 10 | 10 |
| Maximum VUs | 30 | 30 |
| Iterations | 1799 | 1802 |
| HTTP requests | 17990 | 18020 |
| RPS | 29.96 | 30.00 |
| Average latency (ms) | 656.99 | 655.78 |
| p50 (ms) | 552.85 | 72.07 |
| p90 (ms) | 1480 | 2610 |
| p95 (ms) | 1690 | 3230 |
| p99 (ms) | 2060 | 4240 |
| Maximum latency (ms) | 2810 | 6230 |
| Failed requests | 2 | 5 |
| Approximate error rate | 0.011% | 0.028% |
| Received data | 820 MB | 2.5 GB |

## Observations

Both tests completed successfully with a low error rate.

High CPU utilization triggered ECS Auto Scaling.
The desired capacity increased from one to four tasks
across the experiments.

Caching improved the observed median latency, but tail
latency increased.

The database grew during the experiments. The second
test therefore processed a larger dataset, limiting
the comparability of the measurements.

## Evidence

- ../loadtest/cloud-test.js
- ../loadtest/cloud-off-summary.json
- ../loadtest/cloud-on-summary.json
- ../loadtest/scaling-activities.json
