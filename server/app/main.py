import json
from boto3 import exceptions, client
from services.decoder import process_messages
from configs.settings import SQS_QUEUE_URL, REGION

sqs = client('sqs', region_name=REGION)

#listen for messages
print("Started Listening for messages...")
while True:

    try:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        messages = response.get('Messages', [])

        for msg in messages:
            body = json.loads(msg['Body'])

            if body.get("Event") == "s3:TestEvent":
                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=msg['ReceiptHandle']
                )
                print("TestEvent deleted (Ack)")
                continue

            print("Message Received", body)
            process_messages(body)
            print("Message has been processed")

            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )

            print("Message has been deleted (Ack) ")

    except exceptions.botocore.exceptions.ParamValidationError as e:
        print("Invalid Parameter to SQS:", e)
        raise(e)
    except Exception as e:
        print("Error processing the message (NACK):", e)