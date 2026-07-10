from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

from protocol.encoder import from_b64
from constant import STORAGE_DIR

def store_signed_object(signed_object: dict):
    if signed_object:
        object_path = None
        try:
            last_object_id = get_last_object_id()
            object_path = Path(STORAGE_DIR) / f"object_{last_object_id}"
            object_path.mkdir(exist_ok=False)

            #store the public key
            with open(object_path / "public_key.pem", "wb") as f:
                f.write(from_b64(signed_object['public_key_b64']))

            #store the content
            with open(object_path / "content.bin", "wb") as f:
                f.write(from_b64(signed_object['message_b64']))

            #store the signature
            with open(object_path / "signature.bin", "wb") as f:
                f.write(from_b64(signed_object['signature_b64']))   

            #store the metadata
            metadata = built_metadata(signed_object, last_object_id)
            with open(object_path / "metadata.json", "w") as f:
                json.dump(metadata, f)
        except Exception:
            if object_path and object_path.exists():
                shutil.rmtree(object_path)  # delete the folder
            raise
    
def get_last_object_id(): # get the last ID
    storage = Path(STORAGE_DIR)
    object_ids = [
        int(folder.name.split("_")[1])
        for folder in storage.iterdir()
        if folder.is_dir() and folder.name.startswith("object_")
    ]
    last_id = max(object_ids, default=0)
    return last_id + 1    

def built_metadata(signed_object: dict, object_id): # build the metadata for JSON file
    metadata = {
        "object_id": object_id,
        "object_name": signed_object["object_name"],
        "sender": signed_object["sender"],
        "message_b64": signed_object["message_b64"],
        "signature_b64": signed_object["signature_b64"],
        "public_key_b64": signed_object["public_key_b64"],
        "hash_algorithm": signed_object["hash_algorithm"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tampered": False,
    }
    return metadata

def get_list_object():
    storage = Path(STORAGE_DIR)
    data = {
        "objects": []
    }

    for object_path in storage.iterdir():
        print(object_path)
        if object_path.is_dir()  and object_path.name.startswith("object_"):
            print("HERE ", object_path)
            metadata_path = object_path / "metadata.json"
            if metadata_path.exists():
                print("Cela existe")
                # Read from metadata file and parse JSON
                with open(metadata_path, "r") as f:
                    data["objects"].append(json.load(f))
    return data
    