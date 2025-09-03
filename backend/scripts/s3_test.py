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


def read_local_csv_gz(path: str, limit: int = 20) -> None:
    with gzip.open(path, 'rt', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            print(line.rstrip())
            if i + 1 >= limit:
                break


def read_local_parquet(path: str, limit: int = 20) -> None:
    table = pq.read_table(path)
    print(f"columns={table.schema.names}, rows={table.num_rows}")
    head = table.slice(0, min(limit, table.num_rows))
    names = head.schema.names
    cols = [head.column(i).to_pylist() for i in range(head.num_columns)]
    num_rows = len(cols[0]) if cols else 0
    for i in range(num_rows):
        row = {names[j]: cols[j][i] for j in range(len(names))}
        print(row)


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
    key = os.getenv('S3_KEY', '')
    region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
    out_csv = os.getenv('S3_EXPORT_CSV')
    local_path = os.getenv('LOCAL_PATH') or key

    # 로컬 경로가 존재하면 로컬 모드로 처리
    if local_path and os.path.exists(local_path):
        if out_csv:
            if local_path.lower().endswith(('.parquet', '.snappy.parquet')):
                table = pq.read_table(local_path)
                pacsv.write_csv(table, out_csv)
                print(f"wrote CSV: {out_csv} (rows={table.num_rows})")
            elif local_path.lower().endswith('.csv.gz'):
                with gzip.open(local_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                with open(out_csv, 'w', encoding='utf-8', newline='') as o:
                    o.write(text)
                print(f"wrote CSV: {out_csv}")
            elif local_path.lower().endswith('.csv'):
                with open(local_path, 'rb') as src, open(out_csv, 'wb') as dst:
                    dst.write(src.read())
                print(f"wrote CSV: {out_csv}")
            else:
                raise ValueError('Unsupported LOCAL_PATH type')
        else:
            if local_path.lower().endswith('.csv.gz'):
                read_local_csv_gz(local_path, limit=20)
            elif local_path.lower().endswith(('.parquet', '.snappy.parquet')):
                read_local_parquet(local_path, limit=20)
            elif local_path.lower().endswith('.csv'):
                with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        print(line.rstrip())
                        if i + 1 >= 20:
                            break
            else:
                raise ValueError('Unsupported LOCAL_PATH type')
    else:
        if out_csv:
            export_s3_to_csv(bucket, key, out_csv, region)
        else:
            if key.lower().endswith('.csv.gz'):
                read_csv_gz_from_s3(bucket, key, region, limit=20)
            else:
                read_parquet_from_s3(bucket, key, region, limit=20)