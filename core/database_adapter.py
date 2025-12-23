"""
Database Adapter - PostgreSQL Persistence

Provides a unified interface for database operations across the project.
Uses SQLAlchemy for ORM-like capabilities while maintaining raw SQL performance.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from sqlalchemy import (
        create_engine,
        Column,
        String,
        Float,
        DateTime,
        JSON,
        Integer,
        Text,
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

logger = logging.getLogger("core.database")

Base = declarative_base() if HAS_SQLALCHEMY else object


class TradeModel(Base):
    __tablename__ = "trades"
    if HAS_SQLALCHEMY:
        id = Column(String, primary_key=True)
        symbol = Column(String, nullable=False)
        direction = Column(String)  # "long", "short"
        entry_price = Column(Float)
        exit_price = Column(Float)
        quantity = Column(Integer, default=1)
        notes = Column(Text)
        setup = Column(String)
        bias = Column(String)
        target = Column(Float)
        stop = Column(Float)
        rr = Column(Float)
        result = Column(String)  # "win", "loss", "breakeven"
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ValidationModel(Base):
    __tablename__ = "validations"
    if HAS_SQLALCHEMY:
        id = Column(String, primary_key=True)
        job_id = Column(String, unique=True, index=True)
        status = Column(String)  # "pending", "running", "complete", "failed"
        file_path = Column(String)
        report_path = Column(String)
        errors = Column(JSON)
        metadata = Column(JSON)
        created_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseAdapter:
    """Adapter for PostgreSQL database."""

    def __init__(self, database_url: str = None):
        if not HAS_SQLALCHEMY:
            logger.error("SQLAlchemy not installed. Database functionalitly limited.")
            self.engine = None
            self.Session = None
            return

        self.url = database_url or os.getenv("DATABASE_URL")
        if not self.url:
            logger.warning(
                "DATABASE_URL not set. Falling back to SQLite for local development."
            )
            self.url = "sqlite:///./vulcan.db"

        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables verified/created.")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")

    def get_session(self):
        """Get a new database session."""
        if not self.Session:
            raise RuntimeError(
                "Database not initialized. Check SQLAlchemy installation."
            )
        return self.Session()

    def add_trade(self, trade_data: Dict[str, Any]) -> str:
        """Add a trade record."""
        session = self.get_session()
        try:
            import uuid

            trade_id = trade_data.get("id") or str(uuid.uuid4())
            trade = TradeModel(
                id=trade_id,
                symbol=trade_data.get("symbol") or trade_data.get("pair"),
                direction=trade_data.get("direction"),
                entry_price=trade_data.get("entry_price") or trade_data.get("entry"),
                exit_price=trade_data.get("exit_price"),
                quantity=trade_data.get("quantity", 1),
                notes=trade_data.get("notes"),
                setup=trade_data.get("setup"),
                bias=trade_data.get("bias"),
                target=trade_data.get("target"),
                stop=trade_data.get("stop"),
                rr=trade_data.get("rr"),
                result=trade_data.get("result"),
            )
            session.add(trade)
            session.commit()
            return trade_id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add trade: {e}")
            raise
        finally:
            session.close()

    def get_recent_trades(self, limit: int = 50) -> List[Dict]:
        """Get recent trades."""
        session = self.get_session()
        try:
            trades = (
                session.query(TradeModel)
                .order_by(TradeModel.created_at.desc())
                .limit(limit)
                .all()
            )
            return [self._to_dict(t) for t in trades]
        finally:
            session.close()

    def _to_dict(self, model_obj) -> Dict:
        """Convert SQLAlchemy model to dictionary."""
        return {c.name: getattr(model_obj, c.name) for c in model_obj.__table__.columns}


# Singleton
_db_adapter: Optional[DatabaseAdapter] = None


def get_db_adapter() -> DatabaseAdapter:
    """Get or create database adapter singleton."""
    global _db_adapter
    if _db_adapter is None:
        _db_adapter = DatabaseAdapter()
    return _db_adapter
