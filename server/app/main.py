import json
import sys, signal
from boto3 import exceptions, client
from services.transcoder import process_messages
from configs.settings import SQS_QUEUE_URL, REGION
from logger.logging import get_logger

sqs = client("sqs", region_name=REGION)
logger = get_logger(__name__)


def shutdown_handler(sig, frame):
    logger.info("Shutting down listener...")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# listen for messages
logger.log("Started Listening for messages...")
while True:

    try:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10
        )

        messages = response.get("Messages", [])

        for msg in messages:
            body = json.loads(msg["Body"])

            if body.get("Event") == "s3:TestEvent":
                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"]
                )
                logger.warning("TestEvent deleted (Ack)")
                continue

            logger.info("Message Received", body)
            process_messages(body)
            logger.info("Message has been processed")

            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"]
            )

            logger.info("Message has been deleted (Ack) ")

    except exceptions.botocore.exceptions.ParamValidationError as e:
        logger.error("Invalid Parameter to SQS:", e)
        raise

    except exceptions.botocore.exceptions.ClientError as e:
        logger.error("Invalid Credentials:", e)
        raise

    except exceptions.botocore.exceptions.NoCredentialsError as e:
        logger.error("No AWS Credentials found:", e)
        raise

    except Exception as e:
        logger.exception("Error processing the message (NACK):", e)
