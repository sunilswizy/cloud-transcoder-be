import json
import sys, signal
from boto3 import exceptions, client
from services.transcoder import process_messages
from configs.settings import SQS_QUEUE_URL, REGION
from logger.logging import get_logger

sqs = client("sqs", region_name=REGION)
logger = get_logger(__name__)


def shutdown_handler(sig, frame):
    logger.info(msg="Shutting down listener...")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


def init_app():
    # listen for messages
    logger.info("Started Listening for messages...")
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
                    logger.warning(msg="TestEvent deleted (Ack)")
                    continue

                logger.info(msg=f"Message Received {body}")
                process_messages(body)
                logger.info(msg="Message has been processed")

                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"]
                )

                logger.info(msg="Message has been deleted (Ack) ")

        except exceptions.botocore.exceptions.ParamValidationError as e:
            logger.error(msg=f"Invalid Parameter to SQS: {e}")
            raise

        except exceptions.botocore.exceptions.ClientError as e:
            logger.error(msg=f"Invalid Credentials: {e}")
            raise

        except exceptions.botocore.exceptions.NoCredentialsError as e:
            logger.error(msg=f"No AWS Credentials found: {e}")
            raise

        except Exception as e:
            logger.exception(msg=f"Error processing the message (NACK): {e}")


if __name__ == "__main__":
    init_app()
