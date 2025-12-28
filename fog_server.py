import socket
import json 
import hashlib
import time 
import boto3
import datetime
import os

CLOUD_ENDPOINT_URL = "https://eu-east-1.storage.impossibleapi.net"
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET_NAME = "faiot"

HOST = '0.0.0.0'
PORT  = 5000
SECRET_KEY_HASH = "MY_FORENSIC_KEY_123"

s3_client = boto3.client(
    's3',
    endpoint_url=CLOUD_ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def verify_log_integrity(log_data):
    try:
        raw_str = (SECRET_KEY_HASH + log_data['device_id'] + str(log_data['timestamp']) +
                    str(log_data['seq_num']) + log_data['action'] + log_data['prev_hash'])
        expected_hash = hashlib.sha256(raw_str.encode()).hexdigest()
        
        return expected_hash == log_data['signature']
    except: return False

def upload_immutable_log(log_data):
    try:
        file_name = f"logs/{log_data['device_id']}_{log_data['seq_num']}_{int(time.time())}.json"
        json_body = json.dumps(log_data)

        print(f"    [Cloud] Uploading {file_name}...")
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json_body,
            ContentType="application/json"
        )
        
        retention_date = datetime.datetime.utcnow() + datetime.timedelta(days=31)

        s3_client.put_object_retention(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Retention={
                'Mode': 'COMPLIANCE',
                'RetainUntilDate': retention_date
            }
        )
        print("   [Cloud] LOCKED successfully! (Mode: COMPLIANCE)")
        return True

    except Exception as e:
        print(f"   [Cloud Error] {e}")
        return False
        
            
def fog_layer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[FOG] Connected to Impossible Cloud. Waiting for logs...")

    while True:
        conn, addr = server.accept()
        try :
            data = conn.recv(4096).decode()
            if not data: continue
            log_entry = json.loads(data)
            
            if verify_log_integrity(log_entry):
                print(f"[VERIFIED] Log received via Fog.")
                upload_immutable_log(log_entry)
            else:
                print(f"[ALERT] Tampered Log!")
        except Exception as e:
            print(f"[FOG] Error: {e}")
        finally:
            conn.close()
            
if __name__ == "__main__":
    fog_layer()