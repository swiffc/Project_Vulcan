"""
Sentry Adapter - Error Tracking Integration
Capture and report errors to Sentry for monitoring and alerting.

Path B - Infrastructure Adapter
Enables:
- Automatic error capture and reporting
- Performance monitoring
- Release tracking
- User context and breadcrumbs
"""

import logging
import os
from typing import Optional, Dict, Any, List, Callable
from functools import wraps

logger = logging.getLogger("core.sentry_adapter")


class SentryAdapter:
    """
    Sentry error tracking and performance monitoring adapter.
    Provides integration with Sentry for error capture, performance tracing,
    and release tracking.
    """
    
    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: str = "production",
        release: Optional[str] = None,
        traces_sample_rate: float = 0.1,
        profiles_sample_rate: float = 0.1,
        enable_tracing: bool = True
    ):
        """
        Initialize Sentry adapter.
        
        Args:
            dsn: Sentry DSN (or from env SENTRY_DSN)
            environment: Environment name (production, staging, development)
            release: Release version string
            traces_sample_rate: Percentage of transactions to trace (0.0-1.0)
            profiles_sample_rate: Percentage of transactions to profile (0.0-1.0)
            enable_tracing: Enable performance monitoring
        """
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            self.sentry_sdk = sentry_sdk
            
            # Get DSN from params or environment
            sentry_dsn = dsn or os.getenv("SENTRY_DSN")
            
            if not sentry_dsn:
                logger.warning(
                    "Sentry DSN not provided. Set SENTRY_DSN environment variable "
                    "or pass to constructor. Sentry will not capture events."
                )
                self.enabled = False
                return
            
            # Configure logging integration
            logging_integration = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            # Initialize Sentry
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                release=release,
                traces_sample_rate=traces_sample_rate if enable_tracing else 0.0,
                profiles_sample_rate=profiles_sample_rate if enable_tracing else 0.0,
                integrations=[logging_integration],
                # Set in_app_include to mark our code vs dependencies
                in_app_include=["core", "agents", "desktop_server"],
            )
            
            self.enabled = True
            logger.info(f"Sentry initialized (env: {environment}, release: {release})")
            
        except ImportError:
            logger.warning(
                "sentry-sdk not installed. Install with: pip install sentry-sdk"
            )
            self.enabled = False
    
    def capture_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ) -> Optional[str]:
        """
        Capture and report exception to Sentry.
        
        Args:
            error: Exception instance
            context: Additional context dictionary
            level: Severity level (fatal, error, warning, info, debug)
        
        Returns:
            Event ID string or None if not captured
        """
        if not self.enabled:
            return None
        
        try:
            # Set context if provided
            if context:
                with self.sentry_sdk.configure_scope() as scope:
                    for key, value in context.items():
                        scope.set_context(key, value)
                    
                    # Set level
                    scope.level = level
            
            # Capture exception
            event_id = self.sentry_sdk.capture_exception(error)
            
            logger.debug(f"Captured exception to Sentry: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to capture exception to Sentry: {e}")
            return None
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Capture and report message to Sentry.
        
        Args:
            message: Message string
            level: Severity level
            context: Additional context
        
        Returns:
            Event ID or None
        """
        if not self.enabled:
            return None
        
        try:
            # Set context if provided
            if context:
                with self.sentry_sdk.configure_scope() as scope:
                    for key, value in context.items():
                        scope.set_context(key, value)
            
            # Capture message
            event_id = self.sentry_sdk.capture_message(message, level=level)
            
            logger.debug(f"Captured message to Sentry: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to capture message to Sentry: {e}")
            return None
    
    def set_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """
        Set user context for error tracking.
        
        Args:
            user_id: User identifier
            email: User email
            username: Username
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
            logger.debug(f"Set Sentry user context: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to set Sentry user: {e}")
    
    def clear_user(self):
        """Clear user context."""
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_user(None)
            logger.debug("Cleared Sentry user context")
            
        except Exception as e:
            logger.error(f"Failed to clear Sentry user: {e}")
    
    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict] = None
    ):
        """
        Add breadcrumb for debugging context.
        
        Args:
            message: Breadcrumb message
            category: Category (navigation, http, user, etc.)
            level: Severity level
            data: Additional data dictionary
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.add_breadcrumb({
                "message": message,
                "category": category,
                "level": level,
                "data": data or {}
            })
            
        except Exception as e:
            logger.error(f"Failed to add Sentry breadcrumb: {e}")
    
    def start_transaction(self, name: str, op: str = "function") -> Any:
        """
        Start performance transaction.
        
        Args:
            name: Transaction name
            op: Operation type (http, function, db.query, etc.)
        
        Returns:
            Transaction object (use as context manager)
        """
        if not self.enabled:
            # Return dummy context manager
            class DummyTransaction:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
                def set_tag(self, *args):
                    pass
                def set_data(self, *args):
                    pass
            
            return DummyTransaction()
        
        try:
            return self.sentry_sdk.start_transaction(name=name, op=op)
            
        except Exception as e:
            logger.error(f"Failed to start Sentry transaction: {e}")
            return None
    
    def set_tag(self, key: str, value: str):
        """
        Set tag for error categorization.
        
        Args:
            key: Tag key
            value: Tag value
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_tag(key, value)
            
        except Exception as e:
            logger.error(f"Failed to set Sentry tag: {e}")
    
    def set_context(self, name: str, context: Dict[str, Any]):
        """
        Set named context for additional data.
        
        Args:
            name: Context name
            context: Context data dictionary
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_context(name, context)
            
        except Exception as e:
            logger.error(f"Failed to set Sentry context: {e}")
    
    def monitor_function(self, func: Callable) -> Callable:
        """
        Decorator to monitor function performance and errors.
        
        Args:
            func: Function to monitor
        
        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            func_name = f"{func.__module__}.{func.__name__}"
            
            with self.start_transaction(name=func_name, op="function"):
                try:
                    # Add breadcrumb
                    self.add_breadcrumb(
                        message=f"Calling {func_name}",
                        category="function",
                        level="info"
                    )
                    
                    # Call function
                    result = func(*args, **kwargs)
                    
                    return result
                    
                except Exception as e:
                    # Capture exception
                    self.capture_exception(
                        e,
                        context={
                            "function": func_name,
                            "args": str(args)[:200],  # Limit size
                            "kwargs": str(kwargs)[:200]
                        }
                    )
                    raise
        
        return wrapper
    
    def flush(self, timeout: int = 2):
        """
        Force flush pending events to Sentry.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.flush(timeout=timeout)
            logger.debug("Flushed pending Sentry events")
            
        except Exception as e:
            logger.error(f"Failed to flush Sentry events: {e}")


# Singleton instance
_sentry_adapter: Optional[SentryAdapter] = None


def get_sentry_adapter(
    dsn: Optional[str] = None,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_tracing: bool = True
) -> SentryAdapter:
    """
    Get or create Sentry adapter singleton.
    
    Args:
        dsn: Sentry DSN
        environment: Environment name
        release: Release version
        traces_sample_rate: Transaction sampling rate
        profiles_sample_rate: Profile sampling rate
        enable_tracing: Enable performance monitoring
    
    Returns:
        SentryAdapter instance
    """
    global _sentry_adapter
    
    if _sentry_adapter is None:
        _sentry_adapter = SentryAdapter(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            enable_tracing=enable_tracing
        )
    
    return _sentry_adapter


def capture_exception(error: Exception, context: Optional[Dict] = None):
    """Convenience function to capture exception."""
    adapter = get_sentry_adapter()
    return adapter.capture_exception(error, context)


def capture_message(message: str, level: str = "info", context: Optional[Dict] = None):
    """Convenience function to capture message."""
    adapter = get_sentry_adapter()
    return adapter.capture_message(message, level, context)


def monitor(func: Callable) -> Callable:
    """Convenience decorator for function monitoring."""
    adapter = get_sentry_adapter()
    return adapter.monitor_function(func)
