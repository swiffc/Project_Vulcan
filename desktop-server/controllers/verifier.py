"""
Visual Verifier
Compares current screen state against reference images for CAD validation.
Uses OpenCV for image difference calculation.
"""

import cv2
import numpy as np
import mss
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class VisualVerifier:
    def __init__(self, storage_dir="storage/verification"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def capture_and_compare(
        self, reference_path: str, threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Capture current screen and compare with reference image.

        Args:
            reference_path: Path to the 'gold master' image.
            threshold: Similarity score threshold (0.0 to 1.0) to pass.

        Returns:
            Dict containing 'passed' (bool), 'score' (float), and 'diff_path' (str).
        """
        ref_path = Path(reference_path)
        if not ref_path.exists():
            return {
                "passed": False,
                "error": f"Reference image not found: {reference_path}",
            }

        # 1. Capture Screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            current_img = np.array(sct_img)
            # Remove alpha channel if present
            if current_img.shape[2] == 4:
                current_img = cv2.cvtColor(current_img, cv2.COLOR_BGRA2BGR)

        # 2. Load Reference
        reference_img = cv2.imread(str(ref_path))
        if reference_img is None:
            return {"passed": False, "error": "Failed to load reference image"}

        # 3. Resize current to match reference (simple approach)
        # In a real CAD scenario, we might want to template match specific regions
        # but for full screen verification:
        if current_img.shape != reference_img.shape:
            current_img = cv2.resize(
                current_img, (reference_img.shape[1], reference_img.shape[0])
            )

        # 4. Compute Difference (SSIM is better but requires skimage, use MSE/Norm for now)
        # Calculate absolute difference
        diff = cv2.absdiff(current_img, reference_img)

        # Convert diff to grayscale to count non-zero pixels or calculate score
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Calculate match percentage (Simple Pixel Match)
        # Count pixels that are "close enough" (tolerance)
        tolerance = 10
        match_mask = gray_diff < tolerance
        match_count = np.count_nonzero(match_mask)
        total_pixels = gray_diff.size
        similarity = match_count / total_pixels

        passed = similarity >= threshold

        # 5. Save Diff if failed
        diff_path = None
        if not passed:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            diff_filename = f"diff_fail_{timestamp}.png"
            diff_path = str(self.storage_dir / diff_filename)
            # Save a side-by-side or just the diff? Let's save the diff heatmap
            # Normalize diff for visualization
            diff_norm = cv2.normalize(gray_diff, None, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite(diff_path, diff_norm)

        return {
            "passed": passed,
            "score": round(similarity, 4),
            "threshold": threshold,
            "diff_path": diff_path,
        }


verifier = VisualVerifier()
