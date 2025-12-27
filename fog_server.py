import socket
import json 
import hashlib
import requests
import time 
import os

HOST  = "0.0.0.0"
PORT = 5000
SECRET_KEY = "MY_FORENSIC_KEY_2025"
CLOUD_API_URL = "http://127.0.0.1:8000/upload"

def verify_log_integrity(log_data):
    try:
        raw_str = (
            SECRET_KEY + 
            log_data['device_id'] + 
            str(log_data['timestamp']) + 
            str(log_data['seq_num']) +
            log_data['action'] + 
            log_data['prev_hash']
        )
        
        expected_hash = hashlib.sha256(raw_str.encode()).hexdigest()
        
        return expected_hash == log_data['signature']
    except Exception as e:
        print(f"Error verifying: {e}")
        return False
    

def fog_layer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Fog server listening on {HOST}:{PORT}. Waiting for IoT data...")
    
    while True:
        conn, addr = server.accept()
        try :
            data = conn.recv(4096).decode()
            if not data: continue
            
            log_entry = json.loads(data)
            
            if verify_log_integrity(log_entry):
                status = "VERIFIED"
                print(f"[FOG] {status}: {log_entry['action]']} (Seq: {log_entry['seq_num']})")
                
                try:
                    log_entry['fog_received_time'] = time.time()
                    log_entry['fog_ip'] = "192.168.1.10"
                     
                    requests.post(CLOUD_API_URL, json=log_entry)
                except:
                    print(f"[FOG] TAMPERED LOG DETECTED FROM {addr}")
            
        except json.JSONDecodeError:
            print("[FOG] Invalid JSON format")
        except Exception as e:
            print(f"[FOG] Error: {e}")
        finally:
            conn.close()