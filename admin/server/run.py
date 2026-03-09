#!/usr/bin/env python3
"""
Скрипт для запуска сервера админ панели
"""

import uvicorn
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

if __name__ == '__main__':
    uvicorn.run(
        'api:app',
        reload=True,
        port=3001,
        host="0.0.0.0"
    )
