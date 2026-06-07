"""
UUON Fractal Signature Module

Creates stable mathematical fingerprints from
fractal measurements.

No renderer access.
No GLSL access.
Only analyzer metrics.
"""

import hashlib
import json


SIGNATURE_VERSION = "UFS1"


def normalize(value, digits=3):
    """
    Keep signatures stable despite tiny floating errors.
    """

    try:
        return round(float(value), digits)

    except Exception:
        return None



def create_signature(metrics: dict) -> dict:

    payload = {
        "dimension": normalize(
            metrics.get("dimension")
        ),

        "lacunarity": normalize(
            metrics.get("lacunarity")
        ),

        "entropy": normalize(
            metrics.get("entropy")
        ),

        "symmetry": normalize(
            metrics.get("symmetry")
        ),
    }


    encoded = json.dumps(
        payload,
        sort_keys=True
    )


    digest = hashlib.sha256(
        encoded.encode()
    ).hexdigest()


    signature = (
        f"{SIGNATURE_VERSION}-"
        f"{digest[:4].upper()}-"
        f"{digest[4:8].upper()}-"
        f"{digest[8:12].upper()}"
    )


    return {

        "signature": signature,

        "version": SIGNATURE_VERSION,

        "metrics": payload
    }
