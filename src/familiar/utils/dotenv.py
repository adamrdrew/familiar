"""Dotenv file loading utilities."""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def load_dotenv_file(
    dotenv_path: Optional[Path] = None,
    verbose: bool = False,
) -> bool:
    """Load environment variables from .env file.
    
    Loads variables from .env file in current directory (or specified path).
    Does NOT override existing environment variables (secure by default).
    
    Args:
        dotenv_path: Path to .env file. If None, looks for .env in CWD.
        verbose: If True, log info about loaded variables.
    
    Returns:
        True if .env file was found and loaded, False otherwise.
    
    Raises:
        No exceptions raised - fails gracefully with logging.
    
    Example:
        >>> load_dotenv_file()
        True  # Loaded from ./.env
        
        >>> load_dotenv_file(Path("/path/to/.env"))
        True  # Loaded from specified path
        
        >>> load_dotenv_file()
        False  # No .env file found (not an error)
    """
    try:
        from dotenv import load_dotenv
        
        # Determine .env path
        if dotenv_path is None:
            dotenv_path = Path.cwd() / ".env"
        
        # Check if file exists
        if not dotenv_path.exists():
            if verbose:
                logger.debug(f"No .env file found at {dotenv_path}")
            return False
        
        # Load .env file (override=False means existing env vars win)
        load_dotenv(dotenv_path=dotenv_path, override=False, verbose=verbose)
        
        if verbose:
            logger.info(f"Loaded environment variables from {dotenv_path}")
        
        return True
        
    except Exception as e:
        logger.warning(f"Failed to load .env file: {e}")
        return False

