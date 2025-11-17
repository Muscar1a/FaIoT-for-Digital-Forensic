import hashlib

def compute_hash(device_id, temperature, humidity, timestamp):
    raw = f"{device_id}{temperature}{humidity}{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()
