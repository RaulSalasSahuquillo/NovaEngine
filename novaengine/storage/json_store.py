"""Atomic JSON file persistence for local portfolio simulation states."""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Optional

from novaengine.core.orders import OrderReceipt, OrderStatus
from novaengine.core.portfolio import PortfolioPosition, PortfolioState
from novaengine.storage.base import StorageProvider


class JsonStorageProvider(StorageProvider):
    """Saves and loads portfolio ledger states using atomic filesystem writes."""

    def __init__(self, file_path: str = "portfolio_state.json"):
        self.file_path = Path(file_path)

    def save(self, state: PortfolioState) -> bool:
        """Writes state atomically via a sibling temporary file."""
        data = {
            "cash_balance": state.cash_balance,
            "initial_capital": state.initial_capital,
            "positions": {
                k: {
                    "asset_id": pos.asset_id,
                    "asset_name": pos.asset_name,
                    "asset_type": pos.asset_type,
                    "quantity": pos.quantity,
                    "avg_buy_price": pos.avg_buy_price,
                    "current_price": pos.current_price,
                    "image_url": pos.image_url,
                }
                for k, pos in state.positions.items()
            },
            "transactions": [
                {
                    "id": tx.id,
                    "timestamp": tx.timestamp.isoformat(),
                    "asset_id": tx.asset_id,
                    "asset_name": tx.asset_name,
                    "asset_type": tx.asset_type,
                    "side": tx.side,
                    "quantity": tx.quantity,
                    "price_per_unit": tx.price_per_unit,
                    "total_gross_amount": tx.total_gross_amount,
                    "broker_fee": tx.broker_fee,
                    "transaction_tax": tx.transaction_tax,
                    "capital_gains_tax": tx.capital_gains_tax,
                    "net_amount": tx.net_amount,
                    "country_code": tx.country_code,
                    "status": tx.status.value if isinstance(tx.status, OrderStatus) else str(tx.status),
                    "rejection_reason": tx.rejection_reason,
                }
                for tx in state.transactions
            ],
        }

        # Write to temporary file and atomically rename to avoid partial write corruptions
        temp_path = self.file_path.with_suffix(".tmp")
        try:
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.file_path)
            return True
        except Exception:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            return False

    def load(self) -> Optional[PortfolioState]:
        """Loads and parses the persisted ledger file if present."""
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)

            state = PortfolioState(
                cash_balance=float(raw.get("cash_balance", 100000.0)),
                initial_capital=float(raw.get("initial_capital", 100000.0)),
            )

            for key, pos_dict in raw.get("positions", {}).items():
                state.positions[key] = PortfolioPosition(
                    asset_id=pos_dict["asset_id"],
                    asset_name=pos_dict["asset_name"],
                    asset_type=pos_dict["asset_type"],
                    quantity=float(pos_dict["quantity"]),
                    avg_buy_price=float(pos_dict["avg_buy_price"]),
                    current_price=float(pos_dict["current_price"]),
                    image_url=pos_dict.get("image_url"),
                )

            for tx_dict in raw.get("transactions", []):
                state.transactions.append(
                    OrderReceipt(
                        id=tx_dict["id"],
                        timestamp=datetime.fromisoformat(tx_dict["timestamp"]),
                        asset_id=tx_dict["asset_id"],
                        asset_name=tx_dict["asset_name"],
                        asset_type=tx_dict["asset_type"],
                        side=tx_dict["side"],
                        quantity=float(tx_dict["quantity"]),
                        price_per_unit=float(tx_dict["price_per_unit"]),
                        total_gross_amount=float(tx_dict["total_gross_amount"]),
                        broker_fee=float(tx_dict["broker_fee"]),
                        transaction_tax=float(tx_dict["transaction_tax"]),
                        capital_gains_tax=float(tx_dict["capital_gains_tax"]),
                        net_amount=float(tx_dict["net_amount"]),
                        country_code=tx_dict["country_code"],
                        status=OrderStatus(tx_dict.get("status", "filled")),
                        rejection_reason=tx_dict.get("rejection_reason"),
                    )
                )

            return state
        except Exception:
            return None
