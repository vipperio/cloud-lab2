# CloudWatch Alerts

## Configuration

| Parameter | Value |
|---|---|
| Alarm name | cloud-lab2-cpu-overload |
| Metric | AWS/ECS CPUUtilization |
| Statistic | Average |
| Threshold | Greater than 80% |
| Evaluation periods | 2 |
| Period | 60 seconds |
| Notification service | Amazon SNS |
| SNS topic | cloud-lab2-alerts |
| Notification type | Email |

The alarm sends notifications through SNS when the
service enters ALARM or returns to OK.

## Experimental results

All timestamps use UTC+02:00 on November 19, 2026.

| Time | Transition | Reason |
|---|---|---|
| 23:32:41 | INSUFFICIENT_DATA to OK | CPU 0% |
| 23:47:41 | OK to ALARM | CPU 99.97% and 99.86% |
| 23:51:41 | ALARM to OK | CPU decreased to 49.91% |

## Observations

The CPU alarm successfully detected overload during
the load test.

After the service recovered, the alarm returned to OK.

Both transitions were confirmed by the CloudWatch
alarm history exported through AWS CLI.

The SNS notification actions were configured for
both ALARM and OK states. Actual email delivery
must be verified separately using the received emails.

## Evidence

- ../terraform/monitoring.tf
- ../loadtest/alarm-history.json
