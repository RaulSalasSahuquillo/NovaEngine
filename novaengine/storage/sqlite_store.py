"""Relational SQLite storage provider for ACID-compliant ledger tracking."""

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Optional

from novaengine.core.orders import OrderReceipt, OrderStatus
from novaengine.core.portfolio import PortfolioPosition, PortfolioState
from novaengine.storage.base import StorageProvider


class SqliteStorageProvider(StorageProvider):
    """Stores portfolio positions and transaction logs in an embedded SQLite database."""

    def __init__(self, db_path: str = "novaengine.sqlite3"):
        self.db_path = Path(db_path)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    def _init_schema(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_meta (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    cash_balance REAL NOT NULL,
                    initial_capital REAL NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    asset_id TEXT PRIMARY KEY,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    avg_buy_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    image_url TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price_per_unit REAL NOT NULL,
                    total_gross_amount REAL NOT NULL,
                    broker_fee REAL NOT NULL,
                    transaction_tax REAL NOT NULL,
                    capital_gains_tax REAL NOT NULL,
                    net_amount REAL NOT NULL,
                    country_code TEXT NOT NULL,
                    status TEXT NOT NULL,
                    rejection_reason TEXT
                )
            """)
            conn.commit()

    def save(self, state: PortfolioState) -> bool:
        """Stores account balances and all positions within a single transaction."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO portfolio_meta (id, cash_balance, initial_capital, updated_at)
                    VALUES (1, ?, ?, ?)
                """, (state.cash_balance, state.initial_capital, datetime.now().isoformat()))

                cursor.execute("DELETE FROM positions")
                for pos in state.positions.values():
                    cursor.execute("""
                        INSERT INTO positions (asset_id, asset_name, asset_type, quantity, avg_buy_price, current_price, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (pos.asset_id, pos.asset_name, pos.asset_type, pos.quantity, pos.avg_buy_price, pos.current_price, pos.image_url))

                for tx in state.transactions:
                    cursor.execute("""
                        INSERT OR IGNORE INTO transactions (
                            id, timestamp, asset_id, asset_name, asset_type, side, quantity,
                            price_per_unit, total_gross_amount, broker_fee, transaction_tax,
                            capital_gains_tax, net_amount, country_code, status, rejection_reason
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tx.id, tx.timestamp.isoformat(), tx.asset_id, tx.asset_name, tx.asset_type,
                        tx.side, tx.quantity, tx.price_per_unit, tx.total_gross_amount,
                        tx.broker_fee, tx.transaction_tax, tx.capital_gains_tax, tx.net_amount,
                        tx.country_code,
                        tx.status.value if isinstance(tx.status, OrderStatus) else str(tx.status),
                        tx.rejection_reason,
                    ))
                conn.commit()
            return True
        except Exception:
            return False

    def load(self) -> Optional[PortfolioState]:
        """Reconstructs state and historical transaction receipts from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cash_balance, initial_capital FROM portfolio_meta WHERE id = 1")
                row = cursor.fetchone()
                if not row:
                    return None

                state = PortfolioState(cash_balance=row[0], initial_capital=row[1])

                cursor.execute("SELECT asset_id, asset_name, asset_type, quantity, avg_buy_price, current_price, image_url FROM positions")
                for pos_row in cursor.fetchall():
                    pos = PortfolioPosition(
                        asset_id=pos_row[0],
                        asset_name=pos_row[1],
                        asset_type=pos_row[2],
                        quantity=pos_row[3],
                        avg_buy_price=pos_row[4],
                        current_price=pos_row[5],
                        image_url=pos_row[6],
                    )
                    state.positions[pos.asset_id] = pos

                cursor.execute("SELECT id, timestamp, asset_id, asset_name, asset_type, side, quantity, price_per_unit, total_gross_amount, broker_fee, transaction_tax, capital_gains_tax, net_amount, country_code, status, rejection_reason FROM transactions ORDER BY timestamp DESC")
                for tx_row in cursor.fetchall():
                    tx = OrderReceipt(
                        id=tx_row[0],
                        timestamp=datetime.fromisoformat(tx_row[1]),
                        asset_id=tx_row[2],
                        asset_name=tx_row[3],
                        asset_type=tx_row[4],
                        side=tx_row[5],
                        quantity=tx_row[6],
                        price_per_unit=tx_row[7],
                        total_gross_amount=tx_row[8],
                        broker_fee=tx_row[9],
                        transaction_tax=tx_row[10],
                        capital_gains_tax=tx_row[11],
                        net_amount=tx_row[12],
                        country_code=tx_row[13],
                        status=OrderStatus(tx_row[14]),
                        rejection_reason=tx_row[15],
                    )
                    state.transactions.append(tx)

                return state
        except Exception:
            return None
