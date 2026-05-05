"""
File Operations Utility Module
Common file system operations
"""
import os
import shutil
import json
from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime


def read_file(path: str, encoding: str = 'utf-8') -> str:
    """Read text file content"""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(path: str, content: str, encoding: str = 'utf-8'):
    """Write content to text file"""
    # Create parent directories if needed
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)


def append_file(path: str, content: str, encoding: str = 'utf-8'):
    """Append content to file"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'a', encoding=encoding) as f:
        f.write(content)


def read_json(path: str) -> Any:
    """Read and parse JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any, indent: int = 2):
    """Write data to JSON file"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_binary(path: str) -> bytes:
    """Read binary file"""
    with open(path, 'rb') as f:
        return f.read()


def write_binary(path: str, data: bytes):
    """Write binary file"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(data)


def file_exists(path: str) -> bool:
    """Check if file exists"""
    return os.path.isfile(path)


def dir_exists(path: str) -> bool:
    """Check if directory exists"""
    return os.path.isdir(path)


def ensure_dir(path: str):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)


def delete_file(path: str):
    """Delete a file"""
    if os.path.isfile(path):
        os.remove(path)


def delete_dir(path: str, recursive: bool = False):
    """Delete a directory"""
    if os.path.isdir(path):
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)


def copy_file(src: str, dst: str):
    """Copy a file"""
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def move_file(src: str, dst: str):
    """Move a file"""
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dst)


def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    List files in directory
    
    Args:
        directory: Directory path
        pattern: Glob pattern (e.g., "*.txt")
        recursive: Search subdirectories
        
    Returns:
        List of file paths
    """
    path = Path(directory)
    
    if recursive:
        files = path.rglob(pattern)
    else:
        files = path.glob(pattern)
    
    return [str(f) for f in files if f.is_file()]


def list_dirs(directory: str) -> List[str]:
    """List subdirectories"""
    path = Path(directory)
    return [str(d) for d in path.iterdir() if d.is_dir()]


def get_file_info(path: str) -> Dict[str, Any]:
    """Get file information"""
    p = Path(path)
    stat = p.stat()
    
    return {
        "name": p.name,
        "path": str(p.absolute()),
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "extension": p.suffix
    }


def get_file_size(path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(path)


def get_extension(path: str) -> str:
    """Get file extension"""
    return Path(path).suffix


def change_extension(path: str, new_ext: str) -> str:
    """Change file extension"""
    p = Path(path)
    return str(p.with_suffix(new_ext if new_ext.startswith('.') else f'.{new_ext}'))
