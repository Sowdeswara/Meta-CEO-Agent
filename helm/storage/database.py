"""
Database layer - SQLite-based data persistence
Stores all decisions and decision history
"""

import sqlite3
import logging
import json
import threading
from typing import Any, Dict, List, Optional

from ..schemas import StructuredDecision


logger = logging.getLogger(__name__)


class Database:
    """SQLite database abstraction layer for decision storage"""
    
    def __init__(self, db_path: str = ""):
        """Initialize Database
        
        Args:
            db_path: Path to SQLite database file
        """
        if not db_path:
            db_path = str(Path(__file__).parent / "helm_decisions.db")
        
        self.db_path = db_path
        self.connection = None
        self._lock = threading.Lock()  # Thread-safety lock
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        try:
            self.connect()
            self._create_tables()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            # check_same_thread=False allows multi-threaded access (required for async frameworks)
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
            self.connection.row_factory = sqlite3.Row
            logger.debug("Database connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
            self.connection = None
            logger.debug("Database connection closed")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary database tables"""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                agent_used TEXT NOT NULL,
                decision_text TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                roi_estimate REAL NOT NULL,
                validation_score REAL NOT NULL,
                product_score REAL DEFAULT 0.0,
                finance_score REAL DEFAULT 0.0,
                market_score REAL DEFAULT 0.0,
                competitive_score REAL DEFAULT 0.0,
                arbitration_score REAL DEFAULT 0.0,
                status TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                currency TEXT DEFAULT 'USD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Decision history table (for tracking changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                change_reason TEXT,
                FOREIGN KEY(decision_id) REFERENCES decisions(id)
            )
        ''')
        
        # Metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        logger.debug("Database tables created/verified")
    
    def insert_decision(self, decision: StructuredDecision) -> bool:
        """Insert a decision into the database
        
        Args:
            decision: StructuredDecision object
            
        Returns:
            bool: True if successful
        """
        if not self.connection:
            logger.error("Database not connected")
            return False
        
        try:
            with self._lock:  # Thread-safe database access
                cursor = self.connection.cursor()
                
                # Extract agent scores from reasoning
                agent_scores = decision.reasoning.get('arbitration', {}).get('agent_scores', {})
                product_score = agent_scores.get('product_strategy', 0.0)
                finance_score = agent_scores.get('finance_optimization', 0.0)
                market_score = agent_scores.get('market_intelligence', 0.0)
                competitive_score = agent_scores.get('competitive_strategy', 0.0)
                arbitration_score = decision.reasoning.get('arbitration', {}).get('composite_score', 0.0)
                
                cursor.execute('''
                    INSERT INTO decisions 
                    (id, timestamp, prompt, agent_used, decision_text, confidence, 
                     risk_level, roi_estimate, validation_score, product_score, finance_score,
                     market_score, competitive_score, arbitration_score, status, reasoning, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision.decision_id,
                    decision.timestamp.isoformat(),
                    '',  # prompt would come from input
                    decision.agent_used.value,
                    decision.decision_text,
                    decision.confidence,
                    decision.risk_level,
                    decision.roi_estimate,
                    decision.validation_score,
                    product_score,
                    finance_score,
                    market_score,
                    competitive_score,
                    arbitration_score,
                    decision.status.value,
                    json.dumps(decision.reasoning),
                    'USD'
                ))
                
                self.connection.commit()
                logger.debug(f"Decision {decision.decision_id} stored successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to insert decision: {e}")
            self.connection.rollback()
            return False
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        if not self.connection:
            logger.error("Database not connected")
            return []
        
        try:
            with self._lock:  # Thread-safe database access
                cursor = self.connection.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a decision by ID
        
        Args:
            decision_id: Decision ID
            
        Returns:
            Decision record or None
        """
        results = self.query(
            'SELECT * FROM decisions WHERE id = ?',
            (decision_id,)
        )
        return results[0] if results else None
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decisions
        
        Args:
            limit: Maximum number of decisions to return
            
        Returns:
            List of recent decisions
        """
        return self.query(
            'SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )
    
    def get_decisions_by_agent(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get all decisions made by specific agent
        
        Args:
            agent_type: Agent type filter
            
        Returns:
            List of decisions
        """
        return self.query(
            'SELECT * FROM decisions WHERE agent_used = ? ORDER BY created_at DESC',
            (agent_type,)
        )
    
    def get_decisions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all decisions with specific status
        
        Args:
            status: Status filter
            
        Returns:
            List of decisions
        """
        return self.query(
            'SELECT * FROM decisions WHERE status = ? ORDER BY created_at DESC',
            (status,)
        )
    
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert record (generic)
        
        Args:
            table: Table name
            data: Data dict
            
        Returns:
            bool: Success status
        """
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            
            sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            cursor.execute(sql, tuple(data.values()))
            self.connection.commit()
            
            logger.debug(f"Record inserted into {table}")
            return True
        
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False
    
    def update(self, table: str, data: Dict[str, Any], where: str) -> bool:
        """Update record
        
        Args:
            table: Table name
            data: Data to update
            where: WHERE clause (e.g., "id = 'xyz'")
            
        Returns:
            bool: Success status
        """
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
            
            sql = f'UPDATE {table} SET {set_clause} WHERE {where}'
            cursor.execute(sql, tuple(data.values()))
            self.connection.commit()
            
            logger.debug(f"Record updated in {table}")
            return True
        
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False
    
    def delete(self, table: str, where: str) -> bool:
        """Delete record
        
        Args:
            table: Table name
            where: WHERE clause
            
        Returns:
            bool: Success status
        """
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            sql = f'DELETE FROM {table} WHERE {where}'
            cursor.execute(sql)
            self.connection.commit()
            
            logger.debug(f"Record deleted from {table}")
            return True
        
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics
        
        Returns:
            Dict with statistics
        """
        try:
            total_decisions = self.query('SELECT COUNT(*) as count FROM decisions')
            accepted = self.query("SELECT COUNT(*) as count FROM decisions WHERE status = 'accepted'")
            rejected = self.query("SELECT COUNT(*) as count FROM decisions WHERE status = 'rejected'")
            avg_confidence = self.query('SELECT AVG(confidence) as avg FROM decisions')
            avg_roi = self.query('SELECT AVG(roi_estimate) as avg FROM decisions')
            
            return {
                'total_decisions': total_decisions[0]['count'] if total_decisions else 0,
                'accepted_decisions': accepted[0]['count'] if accepted else 0,
                'rejected_decisions': rejected[0]['count'] if rejected else 0,
                'average_confidence': avg_confidence[0]['avg'] if avg_confidence and avg_confidence[0]['avg'] else 0,
                'average_roi': avg_roi[0]['avg'] if avg_roi and avg_roi[0]['avg'] else 0
            }
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
