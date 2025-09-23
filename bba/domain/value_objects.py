from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from typing import Optional
from datetime import date


class DebitCredit(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

    @staticmethod
    def from_symbol(symbol: str) -> "DebitCredit":
        normalized = str(symbol).strip().upper()
        if normalized in {"借", "DEBIT", "D"}:
            return DebitCredit.DEBIT
        if normalized in {"贷", "CREDIT", "C"}:
            return DebitCredit.CREDIT
        raise ValueError(f"无法识别的借贷标识: {symbol}")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "CNY"

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        object.__setattr__(self, "currency", str(self.currency).upper())

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float | Decimal) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("货币不一致，无法进行运算")


@dataclass(frozen=True)
class YearMonth:
    year: int
    month: int

    def __post_init__(self):
        if not (1 <= int(self.month) <= 12):
            raise ValueError("month 必须在 1..12 之间")
        object.__setattr__(self, "year", int(self.year))
        object.__setattr__(self, "month", int(self.month))

    @staticmethod
    def from_date(d: date) -> "YearMonth":
        return YearMonth(d.year, d.month)



