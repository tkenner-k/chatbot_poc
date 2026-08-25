import json
import os
import boto3
from botocore.exceptions import ClientError

def create_task_definition():

    commit_sha = os.environ.get("GITHUB_SHA", "unknown")[:8]
    aws_account_id = os.environ.get("AWS_ACCOUNT_ID", "")

    task_definition = {
        "family": "amazon-be",
        "containerDefinitions": [
            {
                "name": "api",
                "image": f"{aws_account_id}.dkr.ecr.us-east-2.amazonaws.com/amazon-be:{commit_sha}",
                "cpu": 0,
                "portMappings": [
                    {
                        "name": "api-8000-tcp",
                        "containerPort": 8000,
                        "hostPort": 8000,
                        "protocol": "tcp",
                        "appProtocol": "http"
                    }
                ],
                "essential": True,
                "environment": [
                    {
                        "name": "LANGSMITH_TRACING",
                        "value": "true"
                    },
                    {
                        "name": "LANGSMITH_ENDPOINT",
                        "value": "https://api.smith.langchain.com"
                    },
                    {
                        "name": "LANGSMITH_PROJECT",
                        "value": "rag-tracing"
                    }
                ],
                "mountPoints": [],
                "volumesFrom": [],
                "secrets": [
                    {
                        "name": "OPENAI_API_KEY",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/OPENAI_API_KEY-GhYIW4"
                    },
                    {
                        "name": "LANGSMITH_API_KEY",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/LANGSMITH_API_KEY-QEBjDk"
                    },
                    {
                        "name": "GROQ_API_KEY",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/GROQ_API_KEY-WCWnhD"
                    },
                    {
                        "name": "QDRANT_URL",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/QDRANT_URL-kclXaM"
                    },
                    {
                        "name": "QDRANT_API_KEY",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/QDRANT_API_KEY-xHOPyW"
                    },
                    {
                        "name": "SUPABASE_URL",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/SUPABASE_URL-gT3h8s"
                    },
                    {
                        "name": "SUPABASE_LANGGRAPH_USER",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/SUPABASE_LANGGRAPH_USER-TRqnyn"
                    },
                    {
                        "name": "SUPABASE_LANGGRAPH_PASSWORD",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/SUPABASE_LANGGRAPH_PASSWORD-MK7Wr7"
                    },
                    {
                        "name": "SUPABASE_TOOLS_USER",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/SUPABASE_TOOLS_USER-J8BzRj"
                    },
                    {
                        "name": "SUPABASE_TOOLS_PASSWORD",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/SUPABASE_TOOLS_PASSWORD-7OhLpa"
                    },
                    {
                        "name": "CO_API_KEY",
                        "valueFrom": f"arn:aws:secretsmanager:us-east-2:{aws_account_id}:secret:amazon-assistant/CO_API_KEY-azgm9n"
                    }
                ],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "/ecs/amazon-be",
                        "mode": "non-blocking",
                        "awslogs-create-group": "true",
                        "max-buffer-size": "25m",
                        "awslogs-region": "us-east-2",
                        "awslogs-stream-prefix": "ecs"
                    }
                },
                "systemControls": []
            }
        ],
        "taskRoleArn": f"arn:aws:iam::{aws_account_id}:role/amazon-be-task-role",
        "executionRoleArn": f"arn:aws:iam::{aws_account_id}:role/ecsTaskExecutionRole",
        "networkMode": "awsvpc",
        "volumes": [],
        "placementConstraints": [],
        "requiresCompatibilities": [
            "FARGATE"
        ],
        "cpu": "512",
        "memory": "2048",
        "runtimePlatform": {
            "cpuArchitecture": "X86_64",
            "operatingSystemFamily": "LINUX"
        },
        "enableFaultInjection": False,
        "tags": [
            {
                "key": "CommitSHA",
                "value": commit_sha
            },
            {
                "key": "ManagedBy",
                "value": "GitHub-Actions"
            }
        ]
    }

    try:
        ecs_client = boto3.client('ecs')
        
        response = ecs_client.register_task_definition(**task_definition)
        
        print(f"✅ Task definition registered successfully!")
        print(f"Task Definition ARN: {response['taskDefinition']['taskDefinitionArn']}")
        print(f"Revision: {response['taskDefinition']['revision']}")
        print(f"Commit SHA: {commit_sha}")
        
        return response
        
    except ClientError as e:
        print(f"❌ Error registering task definition: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":

    print("Creating ECS Task Definition...")
    create_task_definition()