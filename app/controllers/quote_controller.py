import random

from app.controllers.base_controller import BaseController

# Motivational lines shown on the dashboard. Edit this list freely —
# each entry is a single plain string with no author attribution.
QUOTES = [
    "Aura +1000 if we finish this chapter, absolute zero if we open TikTok.",
    "It's either an academic comeback or a certified skill issue, gang. Let's move.",
    "Either we cook or we get cooked, gang. Open the notes.",
    "Timer's running, gang. Time to cook or get fried.",
    "Aura check, gang: are we cooking, or are we actively getting cooked?",
    "We actually have to read, gang. Delusion has carried us as far as it can.",
    "We are not letting a PDF hit us with the 'skill issue.' Open the notes.",
    "The scrolling isn't even hitting right now, gang. Put it down.",
    "Aura drops to zero if we close this tab, gang.",
    "Manifesting won't save the GPA anymore, gang. Let's cook.",
    "No cooked behavior allowed on this dashboard, gang.",
    "Is the phone screen really that interesting, gang? Be serious.",
    "The math is not mathing yet. Keep going.",
    "Your brain can remember 4K edits of fictional characters but not one formula? Be serious.",
    "The math is mathing, you just need to look at it.",
    "Study now. Scroll mindlessly later, guilt-free.",
    "If your brain can store viral memes, it can store this syllabus.",
    "The harder you work now, the better that post-exam nap feels.",
    "Surely the answer won't just spawn in your brain during the test. Let's actually learn it.",
    "We can't rely on pure vibes and the power of friendship to pass this. Open the notes and let's move.",
    "Please keep doomscrolling, gang—if you want your professor to absolutely humble you. Let's prove them wrong instead.",
    "Staring at the ceiling hoping the syllabus absorbs via photosynthesis is a wild strategy, gang. Let's actually read.",
]


class QuoteController(BaseController):
    """Serves a random motivational line from a built-in local list."""

    def get_random_quote(self):
        return random.choice(QUOTES)
