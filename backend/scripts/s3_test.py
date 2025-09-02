from dotenv import load_dotenv
load_dotenv()

import os, io, boto3, gzip
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pacsv


def read_parquet_from_s3(bucket: str, key: str, region: str | None = None, limit: int = 20) -> None:
    s3 = boto3.client('s3', region_name=region or os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'))
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()

    table = pq.read_table(io.BytesIO(body))
    print(f"columns={table.schema.names}, rows={table.num_rows}")

    head = table.slice(0, min(limit, table.num_rows))
    names = head.schema.names
    cols = [head.column(i).to_pylist() for i in range(head.num_columns)]
    num_rows = len(cols[0]) if cols else 0
    for i in range(num_rows):
        row = {names[j]: cols[j][i] for j in range(len(names))}
        print(row)


def read_csv_gz_from_s3(bucket: str, key: str, region: str | None = None, limit: int = 20) -> None:
    s3 = boto3.client('s3', region_name=region or os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'))
    obj = s3.get_object(Bucket=bucket, Key=key)
    byts = obj['Body'].read()
    with gzip.GzipFile(fileobj=io.BytesIO(byts)) as gz:
        text = gz.read().decode('utf-8', errors='ignore')
        for i, line in enumerate(text.splitlines()):
            print(line)
            if i + 1 >= limit:
                break


def export_s3_to_csv(bucket: str, key: str, out_csv: str, region: str | None = None) -> None:
    s3 = boto3.client('s3', region_name=region or os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'))
    obj = s3.get_object(Bucket=bucket, Key=key)
    byts = obj['Body'].read()

    # Parquet → CSV
    if key.lower().endswith(('.parquet', '.snappy.parquet')):
        table = pq.read_table(io.BytesIO(byts))
        pacsv.write_csv(table, out_csv)
        print(f"wrote CSV: {out_csv} (rows={table.num_rows})")
        return

    # CSV.GZ → CSV
    if key.lower().endswith('.csv.gz'):
        with gzip.GzipFile(fileobj=io.BytesIO(byts)) as gz:
            text = gz.read().decode('utf-8', errors='ignore')
        with open(out_csv, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        print(f"wrote CSV: {out_csv}")
        return

    # 원시 CSV (압축 없음)
    if key.lower().endswith('.csv'):
        with open(out_csv, 'wb') as f:
            f.write(byts)
        print(f"wrote CSV: {out_csv}")
        return

    raise ValueError("Unsupported S3 key type. Use .parquet/.snappy.parquet/.csv.gz/.csv")


if __name__ == "__main__":
    bucket = os.getenv('S3_BUCKET', 'ecps-event-log')
    # 기본값은 Parquet이지만, .csv.gz 키를 주면 CSV GZip으로 읽습니다.
    key = os.getenv('S3_KEY', 'features/dt=2025-09-03/part-00000-d0264f76-2948-454b-99f1-b2866aed32a8-c000.snappy.parquet')
    region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
    out_csv = os.getenv('S3_EXPORT_CSV')
    if out_csv:
        export_s3_to_csv(bucket, key, out_csv, region)
    else:
        if key.lower().endswith('.csv.gz'):
            read_csv_gz_from_s3(bucket, key, region, limit=20)
        else:
            read_parquet_from_s3(bucket, key, region, limit=20)