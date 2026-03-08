from math import log
import sqlite3
import os
import ssl
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
import asyncio
from datetime import datetime
import password_generator
from typing import Any, Optional
import time
import json

