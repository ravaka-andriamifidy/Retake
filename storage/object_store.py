from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

from protocol.encoder import from_b64
from constant import REQUIRED_METADATA_FIELDS, STORAGE_DIR

class StorageError(Exception):
    pass

class MetadataError(Exception):
    pass

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
        if object_path.is_dir()  and object_path.name.startswith("object_"):
            metadata_path = object_path / "metadata.json"
            if metadata_path.exists():
                # Read from metadata file and parse JSON
                with open(metadata_path, "r") as f:
                    data["objects"].append(json.load(f))
    return data

def get_object_by_id(object_id: str):
    storage = Path(STORAGE_DIR)
    data = {
        "objects": []
    }

    for object_path in storage.iterdir():
        if object_path.is_dir()  and object_path.name == f"object_{object_id}":
            metadata_path = object_path / "metadata.json"
            if metadata_path.exists():
                # Read from metadata file and parse JSON
                with open(metadata_path, "r") as f:
                    data["objects"].append(json.load(f))
    return data

def tamper(object_id: str) -> dict:
    object_path = Path(STORAGE_DIR) / f"object_{object_id}"
    metadata = {}
 
    if not object_path.exists():
        raise StorageError(f"Folder 'object_{object_id}' not found")
    
    if object_path.exists():
        metadata = load_metadata(object_path)
    
        with open(object_path / "content.bin", "rb") as f:
            original_bytes = f.read() # read the content
        with open(object_path / "content.bin", "wb") as f:
            f.write(original_bytes + b" [TAMPERED]") # modify the content
    
        metadata["tampered"] = True
        with open(object_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
 
    return metadata

# LOAD METADATA
def load_metadata(object_path: Path) -> dict:
    metadata_path = object_path / "metadata.json"
 
    if not metadata_path.exists():
        raise StorageError(f" Metadata.json file not found")
 
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        raise MetadataError(f" JSONDecodeError: {e}")
 
    validate_metadata(metadata)
    return metadata

# VALIDATE METADATA FIELD
def validate_metadata(metadata: dict) -> None:
    if not isinstance(metadata, dict):
        raise MetadataError(f"Invalid JSON object in metadata")
 
    missing = [f for f in REQUIRED_METADATA_FIELDS if f not in metadata]
    if missing:
        raise MetadataError( f"Missing mandatory fields -> {missing}")
 
    for field, expected_type in REQUIRED_METADATA_FIELDS.items():
        value = metadata[field]
        if not isinstance(value, expected_type):
            raise MetadataError(f" Field '{field}' must be " f"'{expected_type.__name__}' type (current type: {type(value).__name__})")
 
    