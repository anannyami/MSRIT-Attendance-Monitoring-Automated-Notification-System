import asyncio
import logging
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth import get_current_teacher

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["Scraper"])

# Project root = msrit-scraper/ (3 levels up from backend/routers/scraper.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Simple lock to prevent concurrent scraper runs
_scraper_running = False


class ScrapeResponse(BaseModel):
    status:  str   # "success" | "failed" | "busy"
    message: str
    detail:  str = ""


@router.post("/run", response_model=ScrapeResponse, summary="Trigger scraper for all teachers")
async def run_scraper(current_teacher=Depends(get_current_teacher)):
    global _scraper_running

    if _scraper_running:
        return ScrapeResponse(
            status="busy",
            message="Scraper is already running — please wait",
        )

    _scraper_running = True
    logger.info(f"Scraper triggered by teacher: {current_teacher.email}")

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "app.main",
            cwd=str(_PROJECT_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
        except asyncio.TimeoutError:
            process.kill()
            return ScrapeResponse(
                status="failed",
                message="Scraper timed out after 10 minutes",
            )

        output = stdout.decode() + stderr.decode()
        logger.info(f"Scraper finished with return code {process.returncode}")

        if process.returncode == 0:
            # Extract summary line from output
            summary = next(
                (line for line in output.splitlines() if "Scrape complete" in line),
                "Scrape complete",
            )
            return ScrapeResponse(status="success", message=summary, detail=output)
        else:
            return ScrapeResponse(
                status="failed",
                message="Scraper encountered errors — check server logs",
                detail=output,
            )

    except Exception as e:
        logger.error(f"Failed to run scraper: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _scraper_running = False
