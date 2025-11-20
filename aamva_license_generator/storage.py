"""
File System Operations with Comprehensive Error Handling

This module provides robust file system operations with:
- Permission checking
- Disk space verification
- Atomic writes
- Safe cleanup
- Path sanitization
- Context managers for resource safety
"""

import os
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, Union, BinaryIO, TextIO, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum


class StorageError(Exception):
    """Base exception for storage operations"""
    pass


class PermissionError(StorageError):
    """Raised when file/directory permissions are insufficient"""
    pass


class DiskSpaceError(StorageError):
    """Raised when insufficient disk space is available"""
    pass


class PathError(StorageError):
    """Raised when path is invalid or inaccessible"""
    pass


class ChecksumError(StorageError):
    """Raised when file checksum verification fails"""
    pass


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiskSpaceInfo:
    """Information about disk space"""
    total: int  # Total bytes
    used: int   # Used bytes
    free: int   # Free bytes

    @property
    def percent_used(self) -> float:
        """Calculate percentage of disk space used"""
        return (self.used / self.total * 100) if self.total > 0 else 0.0

    @property
    def free_mb(self) -> float:
        """Free space in megabytes"""
        return self.free / (1024 * 1024)

    @property
    def free_gb(self) -> float:
        """Free space in gigabytes"""
        return self.free / (1024 * 1024 * 1024)


class FileSystemValidator:
    """Validates file system operations before execution"""

    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = False) -> Path:
        """
        Validate a file system path

        Args:
            path: Path to validate
            must_exist: If True, path must already exist

        Returns:
            Validated Path object

        Raises:
            PathError: If path is invalid
        """
        try:
            path_obj = Path(path).resolve()
        except (ValueError, OSError) as e:
            raise PathError(f"Invalid path '{path}': {e}")

        # Check for invalid characters (platform-specific)
        path_str = str(path_obj)
        if '\x00' in path_str:
            raise PathError(f"Path contains null character: {path}")

        # Check path length (Windows limitation)
        if len(path_str) > 260 and os.name == 'nt':
            raise PathError(f"Path too long (>{260} chars): {path}")

        if must_exist and not path_obj.exists():
            raise PathError(f"Path does not exist: {path}")

        return path_obj

    @staticmethod
    def check_writable(path: Union[str, Path]) -> bool:
        """
        Check if a path is writable

        Args:
            path: Path to check

        Returns:
            True if writable, False otherwise
        """
        path_obj = Path(path)

        # If path exists, check if we can write to it
        if path_obj.exists():
            return os.access(path_obj, os.W_OK)

        # If path doesn't exist, check if parent is writable
        parent = path_obj.parent
        return parent.exists() and os.access(parent, os.W_OK)

    @staticmethod
    def check_readable(path: Union[str, Path]) -> bool:
        """
        Check if a path is readable

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        path_obj = Path(path)
        return path_obj.exists() and os.access(path_obj, os.R_OK)

    @staticmethod
    def get_disk_space(path: Union[str, Path]) -> DiskSpaceInfo:
        """
        Get disk space information for a path

        Args:
            path: Path to check

        Returns:
            DiskSpaceInfo object with disk usage details
        """
        path_obj = Path(path)

        # Get parent if file doesn't exist
        check_path = path_obj if path_obj.exists() else path_obj.parent

        try:
            stat = shutil.disk_usage(check_path)
            return DiskSpaceInfo(
                total=stat.total,
                used=stat.used,
                free=stat.free
            )
        except OSError as e:
            raise StorageError(f"Could not get disk space for {path}: {e}")

    @staticmethod
    def ensure_space(path: Union[str, Path], required_bytes: int,
                     buffer_percent: float = 10.0) -> None:
        """
        Ensure sufficient disk space is available

        Args:
            path: Path where space is needed
            required_bytes: Minimum bytes required
            buffer_percent: Additional buffer percentage (default 10%)

        Raises:
            DiskSpaceError: If insufficient space
        """
        space = FileSystemValidator.get_disk_space(path)
        required_with_buffer = required_bytes * (1 + buffer_percent / 100)

        if space.free < required_with_buffer:
            raise DiskSpaceError(
                f"Insufficient disk space. Required: {required_with_buffer / (1024**2):.1f} MB, "
                f"Available: {space.free_mb:.1f} MB"
            )


class SafeFileOperations:
    """Safe file operations with automatic cleanup and error handling"""

    @staticmethod
    @contextmanager
    def atomic_write(filepath: Union[str, Path], mode: str = 'w',
                     encoding: Optional[str] = 'utf-8',
                     verify_checksum: bool = False):
        """
        Atomic file write using temporary file

        The file is written to a temporary location first, then moved to
        the final location. This ensures the target file is never corrupted
        if the write fails partway through.

        Args:
            filepath: Destination file path
            mode: File mode ('w' or 'wb')
            encoding: Text encoding (for text mode)
            verify_checksum: If True, verify file after write

        Yields:
            File handle for writing

        Example:
            with SafeFileOperations.atomic_write('output.txt') as f:
                f.write('Hello, World!')
        """
        filepath = FileSystemValidator.validate_path(filepath)

        # Check writable before starting
        if not FileSystemValidator.check_writable(filepath.parent):
            raise PermissionError(f"Cannot write to directory: {filepath.parent}")

        # Create temporary file in same directory
        # (ensures same filesystem for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent,
            prefix=f".tmp_{filepath.name}_"
        )

        temp_path_obj = Path(temp_path)

        try:
            # Close the file descriptor, we'll open properly
            os.close(temp_fd)

            # Open temp file with requested mode
            if 'b' in mode:
                with open(temp_path_obj, mode) as f:
                    yield f
            else:
                with open(temp_path_obj, mode, encoding=encoding) as f:
                    yield f

            # Verify checksum if requested
            if verify_checksum and filepath.exists():
                original_checksum = SafeFileOperations.calculate_checksum(filepath)
                new_checksum = SafeFileOperations.calculate_checksum(temp_path_obj)
                if original_checksum != new_checksum:
                    raise ChecksumError(
                        f"Checksum mismatch after write: {filepath}"
                    )

            # Atomic rename (overwrites destination)
            temp_path_obj.replace(filepath)

        except Exception as e:
            # Clean up temp file on error
            try:
                if temp_path_obj.exists():
                    temp_path_obj.unlink()
            except Exception:
                pass  # Best effort cleanup
            raise StorageError(f"Failed to write {filepath}: {e}") from e

    @staticmethod
    def safe_read(filepath: Union[str, Path], mode: str = 'r',
                  encoding: Optional[str] = 'utf-8',
                  chunk_size: Optional[int] = None):
        """
        Safely read a file with error handling

        Args:
            filepath: File to read
            mode: Read mode ('r' or 'rb')
            encoding: Text encoding (for text mode)
            chunk_size: If provided, read in chunks (for large files)

        Returns:
            File contents or generator of chunks

        Raises:
            PathError: If file doesn't exist
            PermissionError: If file not readable
            StorageError: On read error
        """
        filepath = FileSystemValidator.validate_path(filepath, must_exist=True)

        if not FileSystemValidator.check_readable(filepath):
            raise PermissionError(f"Cannot read file: {filepath}")

        try:
            if chunk_size:
                # Return generator for streaming reads
                return SafeFileOperations._read_chunks(filepath, mode, encoding, chunk_size)
            else:
                # Read entire file
                if 'b' in mode:
                    with open(filepath, mode) as f:
                        return f.read()
                else:
                    with open(filepath, mode, encoding=encoding) as f:
                        return f.read()
        except Exception as e:
            raise StorageError(f"Failed to read {filepath}: {e}") from e

    @staticmethod
    def _read_chunks(filepath: Path, mode: str, encoding: Optional[str],
                     chunk_size: int):
        """Generator for reading file in chunks"""
        if 'b' in mode:
            with open(filepath, mode) as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        else:
            with open(filepath, mode, encoding=encoding) as f:
                while chunk := f.read(chunk_size):
                    yield chunk

    @staticmethod
    def calculate_checksum(filepath: Union[str, Path],
                          algorithm: str = 'sha256') -> str:
        """
        Calculate file checksum

        Args:
            filepath: File to checksum
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256', etc.)

        Returns:
            Hexadecimal checksum string
        """
        filepath = FileSystemValidator.validate_path(filepath, must_exist=True)

        hasher = hashlib.new(algorithm)

        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def safe_copy(src: Union[str, Path], dst: Union[str, Path],
                  verify: bool = False, progress_callback: Optional[Callable] = None):
        """
        Safely copy a file with verification

        Args:
            src: Source file
            dst: Destination file
            verify: If True, verify checksums match
            progress_callback: Optional callback(bytes_copied, total_bytes)

        Raises:
            PathError: If source doesn't exist
            PermissionError: If cannot read source or write destination
            ChecksumError: If verification fails
            StorageError: On copy error
        """
        src_path = FileSystemValidator.validate_path(src, must_exist=True)
        dst_path = FileSystemValidator.validate_path(dst)

        if not FileSystemValidator.check_readable(src_path):
            raise PermissionError(f"Cannot read source: {src_path}")

        if not FileSystemValidator.check_writable(dst_path.parent):
            raise PermissionError(f"Cannot write to destination: {dst_path.parent}")

        # Get source size for progress tracking
        src_size = src_path.stat().st_size

        # Ensure sufficient space
        FileSystemValidator.ensure_space(dst_path, src_size)

        try:
            if progress_callback:
                # Copy with progress
                bytes_copied = 0
                with open(src_path, 'rb') as src_f, open(dst_path, 'wb') as dst_f:
                    while chunk := src_f.read(65536):
                        dst_f.write(chunk)
                        bytes_copied += len(chunk)
                        progress_callback(bytes_copied, src_size)
            else:
                # Simple copy
                shutil.copy2(src_path, dst_path)

            # Verify if requested
            if verify:
                src_checksum = SafeFileOperations.calculate_checksum(src_path)
                dst_checksum = SafeFileOperations.calculate_checksum(dst_path)
                if src_checksum != dst_checksum:
                    raise ChecksumError(
                        f"Checksum mismatch: {src_path} -> {dst_path}"
                    )

        except Exception as e:
            # Clean up partial copy
            try:
                if dst_path.exists():
                    dst_path.unlink()
            except Exception:
                pass
            raise StorageError(f"Failed to copy {src_path} -> {dst_path}: {e}") from e


class DirectoryManager:
    """Manages directory operations with error handling"""

    @staticmethod
    def ensure_directory(path: Union[str, Path], mode: int = 0o755) -> Path:
        """
        Ensure a directory exists, creating it if necessary

        Args:
            path: Directory path
            mode: Directory permissions (Unix)

        Returns:
            Path object for the directory

        Raises:
            PermissionError: If cannot create directory
            PathError: If path exists but is not a directory
        """
        path_obj = FileSystemValidator.validate_path(path)

        if path_obj.exists():
            if not path_obj.is_dir():
                raise PathError(f"Path exists but is not a directory: {path}")
            return path_obj

        # Check parent is writable
        parent = path_obj.parent
        if not parent.exists():
            raise PathError(f"Parent directory does not exist: {parent}")

        if not FileSystemValidator.check_writable(parent):
            raise PermissionError(f"Cannot create directory in: {parent}")

        try:
            path_obj.mkdir(mode=mode, parents=False)
            return path_obj
        except OSError as e:
            raise PermissionError(f"Failed to create directory {path}: {e}") from e

    @staticmethod
    def ensure_directory_tree(path: Union[str, Path], mode: int = 0o755) -> Path:
        """
        Ensure a directory tree exists, creating all parents if necessary

        Args:
            path: Directory path
            mode: Directory permissions (Unix)

        Returns:
            Path object for the directory

        Raises:
            PermissionError: If cannot create directory tree
        """
        path_obj = FileSystemValidator.validate_path(path)

        if path_obj.exists():
            if not path_obj.is_dir():
                raise PathError(f"Path exists but is not a directory: {path}")
            return path_obj

        try:
            path_obj.mkdir(mode=mode, parents=True, exist_ok=True)
            return path_obj
        except OSError as e:
            raise PermissionError(f"Failed to create directory tree {path}: {e}") from e

    @staticmethod
    def safe_cleanup(path: Union[str, Path], pattern: str = "*",
                    max_age_seconds: Optional[int] = None) -> int:
        """
        Safely clean up files in a directory

        Args:
            path: Directory to clean
            pattern: Glob pattern for files to remove (default: all)
            max_age_seconds: Only remove files older than this (optional)

        Returns:
            Number of files removed

        Raises:
            PathError: If directory doesn't exist
            PermissionError: If cannot delete files
        """
        import time

        path_obj = FileSystemValidator.validate_path(path, must_exist=True)

        if not path_obj.is_dir():
            raise PathError(f"Not a directory: {path}")

        removed_count = 0
        current_time = time.time()

        for file_path in path_obj.glob(pattern):
            if not file_path.is_file():
                continue

            # Check age if specified
            if max_age_seconds is not None:
                file_age = current_time - file_path.stat().st_mtime
                if file_age < max_age_seconds:
                    continue

            try:
                file_path.unlink()
                removed_count += 1
            except OSError as e:
                # Log but continue with other files
                print(f"Warning: Could not remove {file_path}: {e}")

        return removed_count

    @staticmethod
    def get_directory_size(path: Union[str, Path]) -> int:
        """
        Calculate total size of all files in a directory

        Args:
            path: Directory path

        Returns:
            Total size in bytes
        """
        path_obj = FileSystemValidator.validate_path(path, must_exist=True)

        total_size = 0
        for file_path in path_obj.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size


class TemporaryFileManager:
    """Manages temporary files with automatic cleanup"""

    @staticmethod
    @contextmanager
    def temporary_directory(prefix: str = "aamva_", cleanup: bool = True):
        """
        Create a temporary directory with automatic cleanup

        Args:
            prefix: Directory name prefix
            cleanup: If True, remove directory on exit

        Yields:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))

        try:
            yield temp_dir
        finally:
            if cleanup and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Could not clean up temp directory {temp_dir}: {e}")

    @staticmethod
    @contextmanager
    def temporary_file(suffix: str = "", prefix: str = "aamva_",
                      mode: str = 'w+b', cleanup: bool = True):
        """
        Create a temporary file with automatic cleanup

        Args:
            suffix: Filename suffix
            prefix: Filename prefix
            mode: File mode
            cleanup: If True, remove file on exit

        Yields:
            Tuple of (file handle, Path)
        """
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        temp_path_obj = Path(temp_path)

        try:
            # Close initial fd and reopen with requested mode
            os.close(temp_fd)

            if 'b' in mode:
                with open(temp_path_obj, mode) as f:
                    yield f, temp_path_obj
            else:
                with open(temp_path_obj, mode, encoding='utf-8') as f:
                    yield f, temp_path_obj
        finally:
            if cleanup and temp_path_obj.exists():
                try:
                    temp_path_obj.unlink()
                except Exception as e:
                    print(f"Warning: Could not clean up temp file {temp_path_obj}: {e}")
