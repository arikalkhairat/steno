# File: security_storage.py
# Description: Simple JSON-based storage system for document security keys and metadata

import json
import os
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import platform

# Try to import fcntl for Unix-like systems, fallback for Windows
try:
    import fcntl
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

# Global lock for thread safety
_storage_lock = threading.RLock()
STORAGE_FILE = "security_keys.json"
BACKUP_DIR = "security_backups"


class SecurityStorageError(Exception):
    """Custom exception for security storage operations"""
    pass


def _get_file_lock(file_handle):
    """
    Cross-platform file locking implementation.
    
    Args:
        file_handle: Open file handle
        
    Returns:
        Context manager for file locking
    """
    class FileLock:
        def __init__(self, fh):
            self.fh = fh
            
        def __enter__(self):
            if FCNTL_AVAILABLE and platform.system() != 'Windows':
                try:
                    fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX)
                except Exception:
                    # fcntl operation failed, continue without locking
                    pass
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if FCNTL_AVAILABLE and platform.system() != 'Windows':
                try:
                    fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
    
    return FileLock(file_handle)


def _load_storage_data() -> Dict[str, Any]:
    """
    Load security storage data from JSON file with proper locking.
    
    Returns:
        Dict: Storage data structure
    """
    if not os.path.exists(STORAGE_FILE):
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "documents": {},
            "metadata": {
                "total_documents": 0,
                "last_cleanup": None
            }
        }
    
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            with _get_file_lock(f):
                data = json.load(f)
                
        # Validate data structure
        if not isinstance(data, dict) or "documents" not in data:
            print("[!] Warning: Invalid storage file format, reinitializing")
            return _load_storage_data()  # Recursive call with empty file
            
        return data
        
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error loading storage file: {e}")
        # Backup corrupted file
        if os.path.exists(STORAGE_FILE):
            backup_name = f"{STORAGE_FILE}.corrupted.{int(time.time())}"
            os.rename(STORAGE_FILE, backup_name)
            print(f"[!] Corrupted file backed up as: {backup_name}")
        
        # Return fresh data structure
        return _load_storage_data()


def _save_storage_data(data: Dict[str, Any]) -> bool:
    """
    Save security storage data to JSON file with proper locking.
    
    Args:
        data (Dict): Storage data to save
        
    Returns:
        bool: Success status
    """
    try:
        # Update metadata
        data["last_modified"] = datetime.now().isoformat()
        data["metadata"]["total_documents"] = len(data.get("documents", {}))
        
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Create temporary file for atomic write
        temp_file = f"{STORAGE_FILE}.tmp.{os.getpid()}.{int(time.time())}"
        
        # Write to temporary file first
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            
        # Create backup of existing file if it exists
        if os.path.exists(STORAGE_FILE):
            try:
                backup_file = os.path.join(BACKUP_DIR, f"security_keys_backup_{int(time.time())}.json")
                # Use copy instead of move to avoid file locking issues
                import shutil
                shutil.copy2(STORAGE_FILE, backup_file)
                print(f"[*] Previous storage backed up to: {backup_file}")
            except Exception as backup_error:
                print(f"[!] Warning: Could not create backup: {backup_error}")
        
        # Atomic replace with retry mechanism for Windows
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(STORAGE_FILE):
                    os.remove(STORAGE_FILE)
                os.rename(temp_file, STORAGE_FILE)
                return True
            except OSError as e:
                if attempt < max_retries - 1:
                    print(f"[*] Retry {attempt + 1}/{max_retries} after error: {e}")
                    time.sleep(0.1)  # Small delay before retry
                    continue
                else:
                    print(f"[!] Failed to replace storage file after {max_retries} attempts: {e}")
                    break
        
        return False
        
    except Exception as e:
        print(f"[!] Error saving storage file: {e}")
        # Clean up temp file if it exists
        if 'temp_file' in locals() and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False


def init_security_storage() -> bool:
    """
    Initialize JSON-based storage for security data.
    
    Creates the storage file if it doesn't exist and validates the structure.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    with _storage_lock:
        print("[*] Initializing security storage system...")
        
        try:
            # Load or create storage data
            data = _load_storage_data()
            
            # Ensure all required fields exist
            if "version" not in data:
                data["version"] = "1.0"
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            if "documents" not in data:
                data["documents"] = {}
            if "metadata" not in data:
                data["metadata"] = {
                    "total_documents": 0,
                    "last_cleanup": None
                }
            
            # Save initialized data
            success = _save_storage_data(data)
            
            if success:
                print(f"[*] Security storage initialized successfully")
                print(f"    Storage file: {os.path.abspath(STORAGE_FILE)}")
                print(f"    Backup directory: {os.path.abspath(BACKUP_DIR)}")
                print(f"    Existing documents: {len(data['documents'])}")
                return True
            else:
                print("[!] Failed to save initial storage data")
                return False
                
        except Exception as e:
            print(f"[!] Error initializing security storage: {e}")
            raise SecurityStorageError(f"Storage initialization failed: {e}")


def store_document_key(document_hash: str, key_data: Dict[str, Any]) -> bool:
    """
    Store document security information in the storage system.
    
    Args:
        document_hash (str): SHA-256 hash of the document
        key_data (Dict): Security key data containing:
            - 'document_key': Security key for the document
            - 'document_path': Optional original document path
            - 'created_by': Optional user identifier
            - 'metadata': Optional additional metadata
    
    Returns:
        bool: True if storage successful, False otherwise
    """
    with _storage_lock:
        try:
            # Validate inputs
            if not document_hash or not isinstance(document_hash, str):
                raise ValueError("Document hash must be a non-empty string")
            
            if not key_data or not isinstance(key_data, dict):
                raise ValueError("Key data must be a non-empty dictionary")
            
            if "document_key" not in key_data:
                raise ValueError("Key data must contain 'document_key' field")
            
            print(f"[*] Storing security key for document: {document_hash[:16]}...")
            
            # Load current storage data
            data = _load_storage_data()
            
            # Prepare document entry
            document_entry = {
                "document_hash": document_hash,
                "document_key": key_data["document_key"],
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1,
                "document_path": key_data.get("document_path", ""),
                "created_by": key_data.get("created_by", "system"),
                "metadata": key_data.get("metadata", {}),
                "storage_id": str(uuid.uuid4())
            }
            
            # Check if document already exists
            if document_hash in data["documents"]:
                existing_entry = data["documents"][document_hash]
                document_entry["access_count"] = existing_entry.get("access_count", 0) + 1
                document_entry["created_at"] = existing_entry.get("created_at", document_entry["created_at"])
                print(f"[*] Updating existing entry (access count: {document_entry['access_count']})")
            else:
                print(f"[*] Creating new security entry")
            
            # Store document entry
            data["documents"][document_hash] = document_entry
            
            # Save updated data
            success = _save_storage_data(data)
            
            if success:
                print(f"[*] Document security key stored successfully")
                print(f"    Document hash: {document_hash}")
                print(f"    Storage ID: {document_entry['storage_id']}")
                print(f"    Total documents in storage: {len(data['documents'])}")
                return True
            else:
                print("[!] Failed to save document security key")
                return False
                
        except Exception as e:
            print(f"[!] Error storing document key: {e}")
            raise SecurityStorageError(f"Failed to store document key: {e}")


def retrieve_document_key(document_hash: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve stored security key for a document.
    
    Args:
        document_hash (str): SHA-256 hash of the document
        
    Returns:
        Optional[Dict]: Document security data if found, None otherwise
    """
    with _storage_lock:
        try:
            if not document_hash or not isinstance(document_hash, str):
                raise ValueError("Document hash must be a non-empty string")
            
            print(f"[*] Retrieving security key for document: {document_hash[:16]}...")
            
            # Load storage data
            data = _load_storage_data()
            
            # Check if document exists
            if document_hash not in data["documents"]:
                print(f"[!] No security key found for document: {document_hash[:16]}")
                return None
            
            # Get document entry
            document_entry = data["documents"][document_hash]
            
            # Update access information
            document_entry["last_accessed"] = datetime.now().isoformat()
            document_entry["access_count"] = document_entry.get("access_count", 0) + 1
            
            # Save updated access info
            _save_storage_data(data)
            
            print(f"[*] Security key retrieved successfully")
            print(f"    Created: {document_entry.get('created_at', 'Unknown')}")
            print(f"    Access count: {document_entry['access_count']}")
            
            return document_entry
            
        except Exception as e:
            print(f"[!] Error retrieving document key: {e}")
            raise SecurityStorageError(f"Failed to retrieve document key: {e}")


def list_secured_documents() -> List[Dict[str, Any]]:
    """
    List all documents with stored security keys.
    
    Returns:
        List[Dict]: List of document security information
    """
    with _storage_lock:
        try:
            print("[*] Listing all secured documents...")
            
            # Load storage data
            data = _load_storage_data()
            
            documents = []
            for doc_hash, doc_data in data["documents"].items():
                documents.append({
                    "document_hash": doc_hash,
                    "document_hash_short": doc_hash[:16],
                    "created_at": doc_data.get("created_at"),
                    "last_accessed": doc_data.get("last_accessed"),
                    "access_count": doc_data.get("access_count", 0),
                    "document_path": doc_data.get("document_path", ""),
                    "created_by": doc_data.get("created_by", "system"),
                    "storage_id": doc_data.get("storage_id"),
                    "has_metadata": bool(doc_data.get("metadata"))
                })
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            print(f"[*] Found {len(documents)} secured documents")
            
            return documents
            
        except Exception as e:
            print(f"[!] Error listing secured documents: {e}")
            raise SecurityStorageError(f"Failed to list secured documents: {e}")


def delete_document_key(document_hash: str) -> bool:
    """
    Remove document security data from storage.
    
    Args:
        document_hash (str): SHA-256 hash of the document
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    with _storage_lock:
        try:
            if not document_hash or not isinstance(document_hash, str):
                raise ValueError("Document hash must be a non-empty string")
            
            print(f"[*] Deleting security key for document: {document_hash[:16]}...")
            
            # Load storage data
            data = _load_storage_data()
            
            # Check if document exists
            if document_hash not in data["documents"]:
                print(f"[!] No security key found for document: {document_hash[:16]}")
                return False
            
            # Get document info before deletion
            doc_info = data["documents"][document_hash]
            storage_id = doc_info.get("storage_id", "unknown")
            
            # Delete document entry
            del data["documents"][document_hash]
            
            # Save updated data
            success = _save_storage_data(data)
            
            if success:
                print(f"[*] Document security key deleted successfully")
                print(f"    Document hash: {document_hash}")
                print(f"    Storage ID: {storage_id}")
                print(f"    Remaining documents: {len(data['documents'])}")
                return True
            else:
                print("[!] Failed to save after deletion")
                return False
                
        except Exception as e:
            print(f"[!] Error deleting document key: {e}")
            raise SecurityStorageError(f"Failed to delete document key: {e}")


def cleanup_expired_keys(days: int = 30) -> Dict[str, int]:
    """
    Clean up old security keys based on last access time.
    
    Args:
        days (int): Number of days after which keys are considered expired
        
    Returns:
        Dict[str, int]: Cleanup statistics
    """
    with _storage_lock:
        try:
            print(f"[*] Cleaning up security keys older than {days} days...")
            
            # Load storage data
            data = _load_storage_data()
            
            # Calculate expiry date
            expiry_date = datetime.now() - timedelta(days=days)
            
            expired_documents = []
            total_documents = len(data["documents"])
            
            # Find expired documents
            for doc_hash, doc_data in data["documents"].items():
                last_accessed_str = doc_data.get("last_accessed", doc_data.get("created_at"))
                if last_accessed_str:
                    try:
                        last_accessed = datetime.fromisoformat(last_accessed_str.replace('Z', '+00:00'))
                        if last_accessed < expiry_date:
                            expired_documents.append(doc_hash)
                    except ValueError:
                        # Invalid date format, consider it expired
                        expired_documents.append(doc_hash)
            
            # Remove expired documents
            removed_count = 0
            for doc_hash in expired_documents:
                if doc_hash in data["documents"]:
                    print(f"    Removing expired key: {doc_hash[:16]}")
                    del data["documents"][doc_hash]
                    removed_count += 1
            
            # Update cleanup metadata
            data["metadata"]["last_cleanup"] = datetime.now().isoformat()
            
            # Save updated data
            success = _save_storage_data(data)
            
            cleanup_stats = {
                "total_documents_before": total_documents,
                "expired_documents_found": len(expired_documents),
                "documents_removed": removed_count,
                "documents_remaining": len(data["documents"]),
                "cleanup_successful": success
            }
            
            print(f"[*] Cleanup completed:")
            print(f"    Documents before cleanup: {cleanup_stats['total_documents_before']}")
            print(f"    Expired documents found: {cleanup_stats['expired_documents_found']}")
            print(f"    Documents removed: {cleanup_stats['documents_removed']}")
            print(f"    Documents remaining: {cleanup_stats['documents_remaining']}")
            
            return cleanup_stats
            
        except Exception as e:
            print(f"[!] Error during cleanup: {e}")
            raise SecurityStorageError(f"Cleanup failed: {e}")


def export_security_backup() -> str:
    """
    Export security data for backup purposes.
    
    Returns:
        str: JSON string containing backup data
    """
    with _storage_lock:
        try:
            print("[*] Exporting security data for backup...")
            
            # Load storage data
            data = _load_storage_data()
            
            # Create backup structure
            backup_data = {
                "backup_version": "1.0",
                "backup_created": datetime.now().isoformat(),
                "original_storage": data,
                "backup_metadata": {
                    "document_count": len(data.get("documents", {})),
                    "backup_id": str(uuid.uuid4()),
                    "source_file": STORAGE_FILE
                }
            }
            
            # Convert to JSON string
            backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Save backup to file
            backup_filename = f"security_backup_{int(time.time())}.json"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            os.makedirs(BACKUP_DIR, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_json)
            
            print(f"[*] Security backup exported successfully")
            print(f"    Backup file: {backup_path}")
            print(f"    Documents backed up: {backup_data['backup_metadata']['document_count']}")
            print(f"    Backup ID: {backup_data['backup_metadata']['backup_id']}")
            
            return backup_json
            
        except Exception as e:
            print(f"[!] Error exporting security backup: {e}")
            raise SecurityStorageError(f"Backup export failed: {e}")


def import_security_backup(backup_data: str) -> bool:
    """
    Import security data from backup.
    
    Args:
        backup_data (str): JSON string containing backup data
        
    Returns:
        bool: True if import successful, False otherwise
    """
    with _storage_lock:
        try:
            print("[*] Importing security data from backup...")
            
            # Parse backup data
            backup_dict = json.loads(backup_data)
            
            # Validate backup structure
            if "original_storage" not in backup_dict:
                raise ValueError("Invalid backup format: missing 'original_storage'")
            
            restored_data = backup_dict["original_storage"]
            
            # Validate restored data structure
            if not isinstance(restored_data, dict) or "documents" not in restored_data:
                raise ValueError("Invalid backup format: invalid storage structure")
            
            # Load current data for merge consideration
            current_data = _load_storage_data()
            
            # Merge strategy: imported data takes precedence
            merged_documents = current_data.get("documents", {}).copy()
            imported_documents = restored_data.get("documents", {})
            
            conflicts = []
            new_imports = []
            
            for doc_hash, doc_data in imported_documents.items():
                if doc_hash in merged_documents:
                    conflicts.append(doc_hash[:16])
                else:
                    new_imports.append(doc_hash[:16])
                
                # Import takes precedence
                merged_documents[doc_hash] = doc_data
            
            # Create final merged data
            final_data = {
                "version": restored_data.get("version", "1.0"),
                "created_at": current_data.get("created_at", datetime.now().isoformat()),
                "last_modified": datetime.now().isoformat(),
                "documents": merged_documents,
                "metadata": {
                    "total_documents": len(merged_documents),
                    "last_cleanup": current_data.get("metadata", {}).get("last_cleanup"),
                    "last_import": datetime.now().isoformat(),
                    "import_info": {
                        "imported_documents": len(imported_documents),
                        "conflicts_resolved": len(conflicts),
                        "new_documents": len(new_imports)
                    }
                }
            }
            
            # Save merged data
            success = _save_storage_data(final_data)
            
            if success:
                print(f"[*] Security backup imported successfully")
                print(f"    Documents imported: {len(imported_documents)}")
                print(f"    Conflicts resolved: {len(conflicts)}")
                print(f"    New documents: {len(new_imports)}")
                print(f"    Total documents after import: {len(merged_documents)}")
                
                if conflicts:
                    print(f"    Conflicting documents (overwritten): {', '.join(conflicts[:5])}{'...' if len(conflicts) > 5 else ''}")
                
                return True
            else:
                print("[!] Failed to save imported data")
                return False
                
        except Exception as e:
            print(f"[!] Error importing security backup: {e}")
            raise SecurityStorageError(f"Backup import failed: {e}")


# Utility functions for storage management

def get_storage_stats() -> Dict[str, Any]:
    """
    Get comprehensive storage statistics.
    
    Returns:
        Dict: Storage statistics and metadata
    """
    with _storage_lock:
        try:
            data = _load_storage_data()
            
            # Calculate storage file size
            file_size = os.path.getsize(STORAGE_FILE) if os.path.exists(STORAGE_FILE) else 0
            
            # Calculate access statistics
            access_counts = [doc.get("access_count", 0) for doc in data["documents"].values()]
            avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
            
            # Calculate age statistics
            now = datetime.now()
            ages = []
            for doc in data["documents"].values():
                created_str = doc.get("created_at")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        age_days = (now - created).days
                        ages.append(age_days)
                    except ValueError:
                        pass
            
            avg_age = sum(ages) / len(ages) if ages else 0
            
            return {
                "total_documents": len(data["documents"]),
                "storage_file_size_bytes": file_size,
                "storage_file_size_mb": round(file_size / (1024 * 1024), 2),
                "average_access_count": round(avg_access, 2),
                "average_age_days": round(avg_age, 2),
                "oldest_document_days": max(ages) if ages else 0,
                "newest_document_days": min(ages) if ages else 0,
                "last_cleanup": data["metadata"].get("last_cleanup"),
                "storage_version": data.get("version"),
                "created_at": data.get("created_at"),
                "last_modified": data.get("last_modified")
            }
            
        except Exception as e:
            print(f"[!] Error getting storage stats: {e}")
            return {"error": str(e)}


def verify_storage_integrity() -> Dict[str, Any]:
    """
    Verify the integrity of the storage system.
    
    Returns:
        Dict: Integrity check results
    """
    with _storage_lock:
        try:
            print("[*] Verifying storage integrity...")
            
            # Check if storage file exists and is readable
            if not os.path.exists(STORAGE_FILE):
                return {"valid": False, "error": "Storage file does not exist"}
            
            # Load and validate data structure
            data = _load_storage_data()
            
            issues = []
            
            # Validate required fields
            required_fields = ["version", "documents", "metadata"]
            for field in required_fields:
                if field not in data:
                    issues.append(f"Missing required field: {field}")
            
            # Validate document entries
            for doc_hash, doc_data in data.get("documents", {}).items():
                if not isinstance(doc_data, dict):
                    issues.append(f"Invalid document data for {doc_hash[:16]}")
                    continue
                
                required_doc_fields = ["document_key", "created_at"]
                for field in required_doc_fields:
                    if field not in doc_data:
                        issues.append(f"Document {doc_hash[:16]} missing field: {field}")
            
            # Check file permissions
            file_readable = os.access(STORAGE_FILE, os.R_OK)
            file_writable = os.access(STORAGE_FILE, os.W_OK)
            
            if not file_readable:
                issues.append("Storage file is not readable")
            if not file_writable:
                issues.append("Storage file is not writable")
            
            result = {
                "valid": len(issues) == 0,
                "issues": issues,
                "file_exists": True,
                "file_readable": file_readable,
                "file_writable": file_writable,
                "document_count": len(data.get("documents", {})),
                "check_timestamp": datetime.now().isoformat()
            }
            
            if result["valid"]:
                print("[*] Storage integrity check passed")
            else:
                print(f"[!] Storage integrity issues found: {len(issues)}")
                for issue in issues:
                    print(f"    - {issue}")
            
            return result
            
        except Exception as e:
            print(f"[!] Error during integrity check: {e}")
            return {
                "valid": False,
                "error": str(e),
                "check_timestamp": datetime.now().isoformat()
            }


if __name__ == "__main__":
    # Simple test when run directly
    print("=== Security Storage System Test ===")
    
    try:
        # Initialize storage
        init_result = init_security_storage()
        print(f"Initialization: {'SUCCESS' if init_result else 'FAILED'}")
        
        # Test storage
        test_hash = hashlib.sha256(b"test_document").hexdigest()
        test_key_data = {
            "document_key": "test_key_12345",
            "document_path": "/path/to/test.docx",
            "created_by": "test_user"
        }
        
        # Store test key
        store_result = store_document_key(test_hash, test_key_data)
        print(f"Store test key: {'SUCCESS' if store_result else 'FAILED'}")
        
        # Retrieve test key
        retrieved = retrieve_document_key(test_hash)
        print(f"Retrieve test key: {'SUCCESS' if retrieved else 'FAILED'}")
        
        # List documents
        documents = list_secured_documents()
        print(f"List documents: {len(documents)} found")
        
        # Get stats
        stats = get_storage_stats()
        print(f"Storage stats: {stats['total_documents']} documents, {stats['storage_file_size_mb']} MB")
        
        # Verify integrity
        integrity = verify_storage_integrity()
        print(f"Integrity check: {'PASSED' if integrity['valid'] else 'FAILED'}")
        
        # Clean up test data
        delete_result = delete_document_key(test_hash)
        print(f"Delete test key: {'SUCCESS' if delete_result else 'FAILED'}")
        
        print("=== Test completed ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
