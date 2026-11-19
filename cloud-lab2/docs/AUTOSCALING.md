# ECS Auto Scaling

## Configuration

| Parameter | Value |
|---|---|
| Service | cloud-lab2-service |
| Cluster | cloud-lab2-cluster |
| Launch type | Fargate |
| Minimum capacity | 1 task |
| Maximum capacity | 4 tasks |
| Scaling policy | Target Tracking |
| CPU target | 60% |
| Scale-out cooldown | 120 seconds |
| Scale-in cooldown | 300 seconds |
| CPU per task | 256 CPU units |
| Memory per task | 512 MiB |

## Parameter justification

A CPU target of 60% provides a resource buffer before
the service reaches CPU saturation.

The minimum capacity of one task reduces idle costs.

The maximum capacity of four tasks limits resource usage
while allowing horizontal scaling.

The shorter scale-out cooldown allows the service to
respond to increasing demand.

The longer scale-in cooldown helps prevent frequent
capacity changes during temporary load fluctuations.

## Experimental results

Successful scaling activities were recorded during
the experiments on November 19-20, 2026.

All timestamps below use the local timezone UTC+02:00.

| Start time | End time | Capacity | Status |
|---|---|---|---|
| Nov 19 23:48:38 | Nov 19 23:49:45 | 1 to 2 | Successful |
| Nov 19 23:54:38 | Nov 19 23:55:14 | 2 to 3 | Successful |
| Nov 20 00:02:38 | Nov 20 00:03:13 | 3 to 4 | Successful |

The scaling policy successfully increased the service
capacity to its configured maximum.

Scale-in is enabled, but a completed automatic return
to one task was not captured in the supplied results.

## Conclusion

The experiment confirmed that ECS can automatically
increase the number of running application tasks
in response to CPU utilization.

## Evidence

- ../terraform/autoscaling.tf
- ../loadtest/scaling-activities.json
- CloudWatch Dashboard screenshots
