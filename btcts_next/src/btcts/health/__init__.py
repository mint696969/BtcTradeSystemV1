# path: ./btcts_next/src/btcts/health/__init__.py
# desc: Health（収集健全性）の公開I/F。

from .svc import read_health

__all__ = ["read_health"]
