# Makes the detector folder a package.
# Might add shared utils or model loading here later.

from .scoring import score_email

__all__ = ["score_email"]
