from dotenv import load_dotenv
load_dotenv()

import os, boto3, gzip

s3 = boto3.client('s3', region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'))
obj = s3.get_object(Bucket='ecps-event-log', Key='features/user_master_csv/part-00000-829abc09-fb71-49e8-b9cb-2cf9dd420ca4-c000.csv.gz')
with gzip.GzipFile(fileobj=obj['Body']) as gz:
    for i, line in enumerate(gz.read().decode('utf-8').splitlines()):
        print(line)
        if i >= 19: break