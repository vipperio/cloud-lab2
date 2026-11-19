# Monitoring

## CloudWatch Dashboard

Dashboard name: cloud-lab2-dashboard

Region: eu-north-1

The dashboard is managed by Terraform and contains
five primary monitoring widgets.

| Widget | Metric | Statistic |
|---|---|---|
| ECS Desired and Running Tasks | DesiredTaskCount, RunningTaskCount | Average |
| ECS CPU Utilization | CPUUtilization | Average |
| ALB Requests per Minute | RequestCount | Sum |
| Response Time p95 | TargetResponseTime | p95 |
| HTTP 5xx Errors | Target and ELB 5XX counts | Sum |

The monitoring period is 60 seconds.

The CPU widget includes annotations for:

- Auto Scaling target: 60%
- CPU overload alarm: 80%

ECS Container Insights is enabled.

## Observations

During load testing, CPU utilization approached 100%.
The service scaled from one to four ECS tasks.

The dashboard recorded increasing request rates,
response latency and occasional server errors.

## Redis monitoring

Additional Amazon ElastiCache metrics were exported
through the AWS CLI:

- CacheHits
- CacheMisses
- CPUUtilization
- CurrConnections
- DatabaseMemoryUsagePercentage

These metrics describe the shared Redis instance,
independently of the application process counters.

## Evidence

- ../terraform/monitoring.tf
- ../loadtest/redis-CacheHits.json
- ../loadtest/redis-CacheMisses.json
- ../loadtest/redis-CPUUtilization.json
- ../loadtest/redis-CurrConnections.json
- ../loadtest/redis-DatabaseMemoryUsagePercentage.json
- CloudWatch and ElastiCache screenshots
