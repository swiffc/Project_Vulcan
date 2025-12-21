"""
J2 Tracker Controller - Browser automation for J2 job tracking system.

This module provides:
- SSO login to J2 Tracker
- Job list extraction
- Job status updates
- Workflow step tracking
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Import browser controller
try:
    from .browser import (
        get_page, save_session, get_browser,
        PLAYWRIGHT_AVAILABLE, SESSION_DIR
    )
    BROWSER_AVAILABLE = PLAYWRIGHT_AVAILABLE
except ImportError:
    BROWSER_AVAILABLE = False
    logger.warning("Browser controller not available")

router = APIRouter(prefix="/j2", tags=["j2-tracker"])

# J2 Tracker configuration
J2_BASE_URL = os.environ.get("J2_TRACKER_URL", "https://j2tracker.example.com")
J2_SESSION_ID = "j2_tracker"


# ============= Models =============

class J2Job(BaseModel):
    id: str
    title: str
    status: str  # Pending, In Progress, Review, Complete, On Hold
    assigned_to: str
    due_date: Optional[str] = None
    priority: str  # Low, Medium, High, Critical
    workflow_step: Optional[str] = None
    workflow_total: Optional[int] = None
    workflow_current: Optional[int] = None
    web_url: Optional[str] = None


class J2Summary(BaseModel):
    total: int
    active: int
    overdue: int
    due_this_week: int
    by_status: Dict[str, int]


class J2Response(BaseModel):
    jobs: List[J2Job]
    summary: J2Summary
    session_valid: bool
    last_refresh: str


class LoginRequest(BaseModel):
    timeout: int = 120  # seconds to wait for SSO completion


# ============= Session Management =============

async def check_session() -> bool:
    """Check if J2 session is valid."""
    if not BROWSER_AVAILABLE:
        return False

    session_file = SESSION_DIR / f"{J2_SESSION_ID}_cookies.json"
    return session_file.exists()


async def get_j2_page():
    """Get a page for J2 Tracker."""
    return await get_page(J2_SESSION_ID)


# ============= Endpoints =============

@router.get("/status")
async def j2_status():
    """Get J2 Tracker connection status."""
    session_valid = await check_session()

    return {
        "browser_available": BROWSER_AVAILABLE,
        "session_valid": session_valid,
        "j2_base_url": J2_BASE_URL,
        "session_id": J2_SESSION_ID,
    }


@router.post("/login")
async def j2_login(request: LoginRequest):
    """
    Start J2 SSO login - opens browser for user to complete authentication.
    Browser will be visible so user can enter credentials.
    """
    if not BROWSER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Browser automation not available. Install playwright.")

    page = await get_j2_page()

    try:
        # Navigate to J2 login
        login_url = f"{J2_BASE_URL}/login"
        await page.goto(login_url, wait_until="load", timeout=30000)

        logger.info(f"J2 SSO login started at {login_url}")

        # Wait for user to complete SSO and land on main page
        # Common J2 dashboard URLs after login
        success_patterns = [
            r"/dashboard",
            r"/home",
            r"/jobs",
            r"/my-work",
        ]

        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < request.timeout:
            current_url = page.url

            # Check if we've reached a logged-in page
            for pattern in success_patterns:
                if re.search(pattern, current_url):
                    # Save session cookies
                    await save_session(J2_SESSION_ID)

                    return {
                        "status": "authenticated",
                        "url": current_url,
                        "cookies_saved": True,
                        "message": "SSO login successful - session saved",
                    }

            # Small delay between checks
            import asyncio
            await asyncio.sleep(1)

        return {
            "status": "timeout",
            "message": f"Login not completed within {request.timeout} seconds",
            "current_url": page.url,
        }

    except Exception as e:
        logger.error(f"J2 login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def j2_logout():
    """Clear J2 session."""
    session_file = SESSION_DIR / f"{J2_SESSION_ID}_cookies.json"

    if session_file.exists():
        session_file.unlink()

    return {"status": "ok", "message": "J2 session cleared"}


@router.get("/jobs")
async def get_jobs(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 50
) -> J2Response:
    """
    Get jobs from J2 Tracker.
    Requires valid session from prior SSO login.
    """
    if not BROWSER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Browser automation not available")

    if not await check_session():
        raise HTTPException(status_code=401, detail="Not authenticated to J2. Call /j2/login first")

    page = await get_j2_page()

    try:
        # Navigate to jobs page
        jobs_url = f"{J2_BASE_URL}/jobs"
        if status:
            jobs_url += f"?status={status}"
        if assigned_to:
            jobs_url += f"&assigned_to={assigned_to}" if "?" in jobs_url else f"?assigned_to={assigned_to}"

        await page.goto(jobs_url, wait_until="networkidle", timeout=30000)

        # Wait for job table to load
        await page.wait_for_selector("table, .job-list, .jobs-container", timeout=10000)

        # Try to extract jobs from common J2 table structures
        jobs = await extract_jobs_from_page(page, limit)

        # Calculate summary
        summary = calculate_job_summary(jobs)

        return J2Response(
            jobs=jobs,
            summary=summary,
            session_valid=True,
            last_refresh=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to get J2 jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job_detail(job_id: str):
    """Get details for a specific job."""
    if not BROWSER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Browser automation not available")

    if not await check_session():
        raise HTTPException(status_code=401, detail="Not authenticated to J2")

    page = await get_j2_page()

    try:
        job_url = f"{J2_BASE_URL}/jobs/{job_id}"
        await page.goto(job_url, wait_until="networkidle", timeout=30000)

        # Extract job details
        title = await safe_extract(page, "h1, .job-title, .title")
        status = await safe_extract(page, ".status, .job-status, [data-status]")
        assigned = await safe_extract(page, ".assigned-to, .assignee, [data-assigned]")
        due_date = await safe_extract(page, ".due-date, [data-due]")
        priority = await safe_extract(page, ".priority, [data-priority]")

        # Extract workflow info
        workflow_step = await safe_extract(page, ".workflow-step, .current-step")
        workflow_info = await safe_extract(page, ".workflow-progress, .step-count")

        return {
            "id": job_id,
            "title": title,
            "status": status,
            "assigned_to": assigned,
            "due_date": due_date,
            "priority": priority,
            "workflow_step": workflow_step,
            "workflow_info": workflow_info,
            "url": job_url,
        }

    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-jobs")
async def get_my_jobs() -> J2Response:
    """Get jobs assigned to the current user."""
    if not BROWSER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Browser automation not available")

    if not await check_session():
        raise HTTPException(status_code=401, detail="Not authenticated to J2")

    page = await get_j2_page()

    try:
        # Navigate to my-work or assigned jobs page
        my_jobs_url = f"{J2_BASE_URL}/my-work"
        await page.goto(my_jobs_url, wait_until="networkidle", timeout=30000)

        # Wait for content
        await page.wait_for_selector("table, .job-list, .my-jobs", timeout=10000)

        jobs = await extract_jobs_from_page(page, limit=100)
        summary = calculate_job_summary(jobs)

        return J2Response(
            jobs=jobs,
            summary=summary,
            session_valid=True,
            last_refresh=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to get my jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Helper Functions =============

async def safe_extract(page, selector: str) -> Optional[str]:
    """Safely extract text from a selector."""
    try:
        element = await page.query_selector(selector)
        if element:
            return (await element.inner_text()).strip()
    except Exception:
        pass
    return None


async def extract_jobs_from_page(page, limit: int = 50) -> List[J2Job]:
    """
    Extract jobs from the current page.
    Handles various J2 table/list structures.
    """
    jobs = []

    # Try table structure first
    rows = await page.query_selector_all("table tbody tr, .job-row, .job-item")

    for i, row in enumerate(rows):
        if i >= limit:
            break

        try:
            # Try common column structures
            job_id = await safe_extract_from_element(row, ".job-id, [data-id], td:first-child a")
            title = await safe_extract_from_element(row, ".job-title, .title, td:nth-child(2)")
            status = await safe_extract_from_element(row, ".status, [data-status], td:nth-child(3)")
            assigned = await safe_extract_from_element(row, ".assigned, .assignee, td:nth-child(4)")
            due_date = await safe_extract_from_element(row, ".due-date, [data-due], td:nth-child(5)")
            priority = await safe_extract_from_element(row, ".priority, [data-priority], td:nth-child(6)")

            if job_id or title:  # Need at least one identifier
                jobs.append(J2Job(
                    id=job_id or f"job_{i}",
                    title=title or "Unknown",
                    status=normalize_status(status),
                    assigned_to=assigned or "Unassigned",
                    due_date=due_date,
                    priority=normalize_priority(priority),
                    web_url=f"{J2_BASE_URL}/jobs/{job_id}" if job_id else None,
                ))

        except Exception as e:
            logger.warning(f"Failed to extract job from row {i}: {e}")
            continue

    return jobs


async def safe_extract_from_element(element, selector: str) -> Optional[str]:
    """Safely extract text from an element using a selector."""
    try:
        child = await element.query_selector(selector)
        if child:
            return (await child.inner_text()).strip()
    except Exception:
        pass
    return None


def normalize_status(status: Optional[str]) -> str:
    """Normalize job status to standard values."""
    if not status:
        return "Unknown"

    status_lower = status.lower().strip()

    if "complete" in status_lower or "done" in status_lower:
        return "Complete"
    elif "progress" in status_lower or "active" in status_lower:
        return "In Progress"
    elif "review" in status_lower or "pending approval" in status_lower:
        return "Review"
    elif "hold" in status_lower or "pause" in status_lower:
        return "On Hold"
    elif "pending" in status_lower or "queue" in status_lower:
        return "Pending"

    return status.strip()


def normalize_priority(priority: Optional[str]) -> str:
    """Normalize priority to standard values."""
    if not priority:
        return "Medium"

    priority_lower = priority.lower().strip()

    if "critical" in priority_lower or "urgent" in priority_lower:
        return "Critical"
    elif "high" in priority_lower:
        return "High"
    elif "low" in priority_lower:
        return "Low"

    return "Medium"


def calculate_job_summary(jobs: List[J2Job]) -> J2Summary:
    """Calculate summary statistics from job list."""
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_end = today + timedelta(days=7)

    by_status: Dict[str, int] = {}
    active = 0
    overdue = 0
    due_this_week = 0

    for job in jobs:
        # Count by status
        status = job.status
        by_status[status] = by_status.get(status, 0) + 1

        # Count active (not complete or on hold)
        if status not in ["Complete", "On Hold"]:
            active += 1

        # Check due date
        if job.due_date:
            try:
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
                    try:
                        due = datetime.strptime(job.due_date.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    continue

                if due < today and status != "Complete":
                    overdue += 1
                elif today <= due <= week_end:
                    due_this_week += 1

            except Exception:
                pass

    return J2Summary(
        total=len(jobs),
        active=active,
        overdue=overdue,
        due_this_week=due_this_week,
        by_status=by_status,
    )
