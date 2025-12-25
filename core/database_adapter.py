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
        Boolean,
        ForeignKey,
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship

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
        validation_meta = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
        created_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyModel(Base):
    """Digital Twin Strategy - Phase 20 Task 17"""
    __tablename__ = "strategies"
    if HAS_SQLALCHEMY:
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False, index=True)
        product_type = Column(String, nullable=False)  # weldment, sheet_metal, machining, etc.
        description = Column(Text)
        schema_json = Column(JSON)  # Serialized product model
        version = Column(Integer, default=1)
        is_experimental = Column(Boolean, default=False)  # Sandbox flag
        performance_score = Column(Float, default=0.0)  # 0-100 based on validation pass rate
        usage_count = Column(Integer, default=0)
        tags = Column(JSON)  # List of tags
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        created_by = Column(String, default="system")


class StrategyPerformance(Base):
    """Track strategy execution results - Phase 20 Task 21"""
    __tablename__ = "strategy_performance"
    if HAS_SQLALCHEMY:
        id = Column(Integer, primary_key=True, autoincrement=True)
        strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
        execution_date = Column(DateTime, default=datetime.utcnow)
        part_name = Column(String)
        validation_passed = Column(Boolean, default=False)
        error_count = Column(Integer, default=0)
        errors_json = Column(JSON)  # Which checks failed
        execution_time = Column(Float)  # Seconds
        user_rating = Column(Integer)  # 1-5 stars (optional)
        notes = Column(Text)


class StrategyVersion(Base):
    """Version history for evolved strategies - Rollback support"""
    __tablename__ = "strategy_versions"
    if HAS_SQLALCHEMY:
        id = Column(Integer, primary_key=True, autoincrement=True)
        strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
        version = Column(Integer, nullable=False)
        schema_json = Column(JSON)  # Snapshot of strategy at this version
        change_reason = Column(Text)  # Why was it evolved?
        performance_before = Column(Float)
        performance_after = Column(Float)
        created_at = Column(DateTime, default=datetime.utcnow)
        created_by = Column(String, default="system")


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

    # ===== STRATEGY CRUD OPERATIONS (Phase 20) =====

    def save_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Save a new strategy or update existing one."""
        session = self.get_session()
        try:
            strategy_id = strategy_data.get("id")
            if strategy_id:
                # Update existing
                strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
                if strategy:
                    for key, value in strategy_data.items():
                        if hasattr(strategy, key) and key != "id":
                            setattr(strategy, key, value)
                    strategy.updated_at = datetime.utcnow()
                    session.commit()
                    return strategy.id

            # Create new
            strategy = StrategyModel(
                name=strategy_data.get("name"),
                product_type=strategy_data.get("product_type"),
                description=strategy_data.get("description"),
                schema_json=strategy_data.get("schema_json"),
                version=strategy_data.get("version", 1),
                is_experimental=strategy_data.get("is_experimental", False),
                tags=strategy_data.get("tags", []),
                created_by=strategy_data.get("created_by", "system"),
            )
            session.add(strategy)
            session.commit()
            return strategy.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save strategy: {e}")
            raise
        finally:
            session.close()

    def load_strategy(self, strategy_id: int) -> Optional[Dict]:
        """Load a strategy by ID."""
        session = self.get_session()
        try:
            strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
            if strategy:
                return self._to_dict(strategy)
            return None
        finally:
            session.close()

    def load_strategy_by_name(self, name: str) -> Optional[Dict]:
        """Load a strategy by name."""
        session = self.get_session()
        try:
            strategy = session.query(StrategyModel).filter_by(name=name).first()
            if strategy:
                return self._to_dict(strategy)
            return None
        finally:
            session.close()

    def list_strategies(
        self,
        product_type: Optional[str] = None,
        is_experimental: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List strategies with optional filters."""
        session = self.get_session()
        try:
            query = session.query(StrategyModel)
            if product_type:
                query = query.filter_by(product_type=product_type)
            if is_experimental is not None:
                query = query.filter_by(is_experimental=is_experimental)
            strategies = query.order_by(StrategyModel.updated_at.desc()).limit(limit).all()
            return [self._to_dict(s) for s in strategies]
        finally:
            session.close()

    def delete_strategy(self, strategy_id: int) -> bool:
        """Delete a strategy by ID."""
        session = self.get_session()
        try:
            strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
            if strategy:
                session.delete(strategy)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete strategy: {e}")
            raise
        finally:
            session.close()

    def update_strategy_score(self, strategy_id: int, score: float) -> bool:
        """Update a strategy's performance score."""
        session = self.get_session()
        try:
            strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
            if strategy:
                strategy.performance_score = score
                strategy.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def increment_strategy_usage(self, strategy_id: int) -> bool:
        """Increment usage count for a strategy."""
        session = self.get_session()
        try:
            strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
            if strategy:
                strategy.usage_count += 1
                strategy.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()

    # ===== STRATEGY PERFORMANCE TRACKING (Phase 20 Task 21) =====

    def record_performance(self, perf_data: Dict[str, Any]) -> int:
        """Record a strategy execution performance."""
        session = self.get_session()
        try:
            perf = StrategyPerformance(
                strategy_id=perf_data.get("strategy_id"),
                part_name=perf_data.get("part_name"),
                validation_passed=perf_data.get("validation_passed", False),
                error_count=perf_data.get("error_count", 0),
                errors_json=perf_data.get("errors_json"),
                execution_time=perf_data.get("execution_time"),
                user_rating=perf_data.get("user_rating"),
                notes=perf_data.get("notes"),
            )
            session.add(perf)
            session.commit()

            # Update strategy score
            self._recalculate_strategy_score(session, perf_data.get("strategy_id"))

            return perf.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to record performance: {e}")
            raise
        finally:
            session.close()

    def get_strategy_performance(
        self,
        strategy_id: int,
        days: int = 30
    ) -> List[Dict]:
        """Get performance records for a strategy."""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            records = (
                session.query(StrategyPerformance)
                .filter(StrategyPerformance.strategy_id == strategy_id)
                .filter(StrategyPerformance.execution_date >= cutoff)
                .order_by(StrategyPerformance.execution_date.desc())
                .all()
            )
            return [self._to_dict(r) for r in records]
        finally:
            session.close()

    def _recalculate_strategy_score(self, session, strategy_id: int):
        """Recalculate strategy score based on recent performance."""
        if not strategy_id:
            return
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        records = (
            session.query(StrategyPerformance)
            .filter(StrategyPerformance.strategy_id == strategy_id)
            .filter(StrategyPerformance.execution_date >= cutoff)
            .all()
        )
        if records:
            passed = sum(1 for r in records if r.validation_passed)
            score = (passed / len(records)) * 100
            strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
            if strategy:
                strategy.performance_score = score
                session.commit()

    # ===== STRATEGY VERSIONING (Rollback Support) =====

    def save_strategy_version(
        self,
        strategy_id: int,
        version: int,
        schema_json: Dict,
        change_reason: str = None,
        perf_before: float = None,
        perf_after: float = None
    ) -> int:
        """Save a version snapshot for rollback."""
        session = self.get_session()
        try:
            version_record = StrategyVersion(
                strategy_id=strategy_id,
                version=version,
                schema_json=schema_json,
                change_reason=change_reason,
                performance_before=perf_before,
                performance_after=perf_after,
            )
            session.add(version_record)
            session.commit()
            return version_record.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save strategy version: {e}")
            raise
        finally:
            session.close()

    def get_strategy_versions(self, strategy_id: int) -> List[Dict]:
        """Get all versions of a strategy."""
        session = self.get_session()
        try:
            versions = (
                session.query(StrategyVersion)
                .filter_by(strategy_id=strategy_id)
                .order_by(StrategyVersion.version.desc())
                .all()
            )
            return [self._to_dict(v) for v in versions]
        finally:
            session.close()

    def rollback_strategy(self, strategy_id: int, to_version: int) -> bool:
        """Rollback a strategy to a previous version."""
        session = self.get_session()
        try:
            version = (
                session.query(StrategyVersion)
                .filter_by(strategy_id=strategy_id, version=to_version)
                .first()
            )
            if version and version.schema_json:
                strategy = session.query(StrategyModel).filter_by(id=strategy_id).first()
                if strategy:
                    strategy.schema_json = version.schema_json
                    strategy.version = to_version
                    strategy.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"Rolled back strategy {strategy_id} to version {to_version}")
                    return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to rollback strategy: {e}")
            raise
        finally:
            session.close()

    def get_top_strategies(self, limit: int = 5, product_type: str = None) -> List[Dict]:
        """Get top performing strategies."""
        session = self.get_session()
        try:
            query = session.query(StrategyModel).filter(StrategyModel.is_experimental == False)
            if product_type:
                query = query.filter_by(product_type=product_type)
            strategies = (
                query.order_by(StrategyModel.performance_score.desc())
                .limit(limit)
                .all()
            )
            return [self._to_dict(s) for s in strategies]
        finally:
            session.close()

    def get_low_performing_strategies(self, threshold: float = 50.0, min_usage: int = 3) -> List[Dict]:
        """Get strategies with low performance scores (candidates for evolution)."""
        session = self.get_session()
        try:
            strategies = (
                session.query(StrategyModel)
                .filter(StrategyModel.performance_score < threshold)
                .filter(StrategyModel.usage_count >= min_usage)
                .filter(StrategyModel.is_experimental == False)
                .order_by(StrategyModel.performance_score.asc())
                .all()
            )
            return [self._to_dict(s) for s in strategies]
        finally:
            session.close()


# Singleton
_db_adapter: Optional[DatabaseAdapter] = None


def get_db_adapter() -> DatabaseAdapter:
    """Get or create database adapter singleton."""
    global _db_adapter
    if _db_adapter is None:
        _db_adapter = DatabaseAdapter()
    return _db_adapter
