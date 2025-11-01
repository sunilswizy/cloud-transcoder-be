from configs.settings import DECODE_FILE_PATH, UPLOAD_FILE_PATH
from configs.config import resolutions
import subprocess
import boto3
import urllib.parse
import os

client = boto3.client('s3')

def download_file(key, bucket, input_path):
    try:
        response = client.get_object(
            Bucket=bucket,
            Key=key
        )

        with open(input_path, "wb") as f:
            f.write(response['Body'].read())

    except Exception as e:
        print("Get file error ", e)
        raise e


def upload_file(bucket, path):
    try:
        client.upload_file(path, bucket, path)
    except Exception as e:
        print("Error at uploading file ", e)
        raise e

def delete_file(path):
    if os.path.exists(path):
        return os.remove(path)
    print("File path does not exists", path)

def transcode_videos(bucket, file_name, input_path, output_base):
    output_files = []

    for label, size in resolutions.items():
        output_path = f'{output_base}/{file_name}-{label}.mp4'
        command = [
            "ffmpeg", "-i", input_path,
            "-vf", f"scale={size}",
            "-c:a", "copy",
            output_path
        ]
        subprocess.run(command, check=True)
        upload_file(bucket, output_path)
        output_files.append(output_path)

    return output_files

def clean_up_files(output_files):
    for path in output_files:
        delete_file(path)
    
    print("files has been cleaned up")

def process_messages(payload):
    # Initializing and parsing the payload
    record = payload["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    encoded_key = record["s3"]["object"]["key"]
    key = urllib.parse.unquote_plus(encoded_key)
    file_name = key.split("/")[-1]

    if not bucket or not key or not file_name: 
        print(f"Invalid payload - bucket = {bucket}, key = {key}, file_name = {file_name}")
        return False
    
    print(f"Started processing - bucket = {bucket}, key = {key}, file_name = {file_name}")
    input_path = f'{UPLOAD_FILE_PATH}/{file_name}'
    output_base = DECODE_FILE_PATH

    download_file(key, bucket, input_path)
    output_files = transcode_videos(bucket, file_name, input_path, output_base)

    print("Processed and uploaded resolutions = ", output_files)

    delete_file(input_path)
    clean_up_files(output_files)

    return True

