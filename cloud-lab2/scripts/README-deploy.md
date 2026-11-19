# Поетапне розгортання (без автоматичного запуску платних ресурсів)

**Перш ніж виконувати `apply`:** перевір поточні AWS-витрати й ціни Fargate, ALB, публічних IPv4, CloudWatch, ECR та трафіку в `eu-central-1`. Бюджетні сповіщення не обмежують витрати. Використовуйте лише власний AWS-акаунт.

1. У `C:\cloud-lab2\terraform` заповни `terraform.tfvars` (скопіюй приклад; додай **власний** `alert_email`). Не коміть `tfvars` до Git.
2. Перевір: `terraform init`, `terraform fmt`, `terraform validate`, `terraform plan`.
3. Спочатку створюй **тільки ECR**, щоб до старту ECS існував Docker-образ:
   ```powershell
   terraform apply '-target=aws_ecr_repository.app'
   ```
   Переконайся, що план містить лише ECR; підтверди вручну. Якщо PowerShell розбиває аргумент, скористайся `terraform --% apply -target=aws_ecr_repository.app`.
4. У `C:\cloud-lab2` збери образ і завантаж його в ECR (PowerShell):
   ```powershell
   $region = 'eu-central-1'
   $account = (aws sts get-caller-identity --query Account --output text)
   $registry = "$account.dkr.ecr.$region.amazonaws.com"
   aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $registry
   docker build --platform linux/amd64 -t cloud-lab2-api:initial .
   docker tag cloud-lab2-api:initial "${registry}/cloud-lab2-api:initial"
   docker push "${registry}/cloud-lab2-api:initial"
   ```
   Перевір код завершення команд, перед тим як продовжити.
5. Повернись у `terraform`, запусти **звичайний** `terraform plan` і перевір, що ресурси тільки створюються, немає destroy/replace і зайвих сервісів. Лише після оцінки витрат: `terraform apply`. Це створить платні ресурси.
6. Дочекайся `aws ecs describe-services` зі значенням `runningCount >= 1`, перевір `terraform output -raw app_url`, `/health` і `/docs`.
7. Підтверди SNS-підписку через лист AWS (інакше email-сповіщення не працюватимуть).
8. Перевір CloudWatch Dashboard, Alarm, Application Auto Scaling і k6. Зроби реальні скріншоти; не вигадуй результати.
9. **Після демонстрації:** `terraform destroy` у тій самій папці; перевір у консолі, що ALB, ECS та інші платні ресурси зникли. Зберігай `terraform.tfstate` локально до завершення очищення.

Якщо попередній `terraform plan` показує інші дії, не підтверджуй зміни — перевір state і регіон.
