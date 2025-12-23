"""
Nextdoor scraper - requires login/verification.
"""

import logging
from typing import List

from models.opportunity import SocialOpportunity

logger = logging.getLogger(__name__)


class NextdoorScraper:
    """
    Nextdoor scraper.

    WARNING: Nextdoor requires:
    - Address verification
    - Login credentials
    - May detect and block automated access

    For best results, monitor Nextdoor manually or use their official app.
    """

    def __init__(self):
        """Initialize the scraper."""
        logger.warning(
            "Nextdoor monitoring is not fully implemented. "
            "Nextdoor requires address verification and login. "
            "Recommend manual monitoring via their app/website."
        )
        self.authenticated = False

    def get_manual_instructions(self):
        """Get instructions for manual Nextdoor monitoring."""
        return """
NEXTDOOR MANUAL MONITORING GUIDE
=================================

Nextdoor is the BEST platform for finding local construction leads,
but it requires manual monitoring due to their security measures.

HOW TO SET UP:

1. GO TO NEXTDOOR:
   - Website: https://nextdoor.com
   - Or download the Nextdoor app (iOS/Android)

2. VERIFY YOUR ADDRESS:
   - Enter your Omaha address
   - Verify via postcard, phone, or nearby member

3. JOIN YOUR NEIGHBORHOOD:
   - You'll be auto-added to your neighborhood
   - Can also join nearby neighborhoods (up to 2)

4. ENABLE NOTIFICATIONS:
   - Settings → Notifications
   - Enable "Recommendations" category
   - Enable "Services" category
   - Get instant alerts when people ask for contractors!

5. SEARCH FOR KEYWORDS:
   Use Nextdoor's search feature for:
   - "contractor"
   - "tile"
   - "remodel"
   - "bathroom"
   - "kitchen"
   - "flooring"
   - "handyman"

6. RESPOND QUICKLY:
   - People often hire the first responder
   - Be helpful and professional
   - Mention you're local (same neighborhood = trust)

7. BUILD REPUTATION:
   - Get reviews on Nextdoor
   - Join as a "Business" for credibility
   - Post helpful tips occasionally

WHY NEXTDOOR IS GREAT:
- ✓ Hyper-local (your exact neighborhoods)
- ✓ People actively looking for contractors
- ✓ High trust (verified neighbors)
- ✓ Less competition than Google/Yelp
- ✓ Can message directly

EXAMPLE POSTS YOU'LL SEE:
- "Does anyone know a good tile installer?"
- "Need bathroom remodel recommendations"
- "Looking for contractor for kitchen renovation"
- "Anyone have a handyman they recommend?"

RESPONSE TEMPLATE:
"Hi [Name]! I'm a local contractor here in [neighborhood] and
specialize in [tile work/remodeling/etc]. I'd be happy to give you
a free quote. You can call/text me at [phone] or check out my work
at [website]. I've done several projects right here in the neighborhood!"

SET ASIDE 10 MINUTES DAILY:
- Check Nextdoor 2-3 times per day
- Search keywords weekly
- Respond within 1-2 hours of posts

This is your BEST source for local leads!
"""

    def monitor_all(self):
        """
        Nextdoor monitoring not implemented.

        Returns empty list. Use manual monitoring instead.
        """
        logger.info(self.get_manual_instructions())
        return []
