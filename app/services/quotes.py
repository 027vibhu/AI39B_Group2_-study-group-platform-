"""Motivation quote for the dashboard.

A curated list picked at random on each request. No DB, no network.
"""

import random

# Each entry: text + author.
QUOTES = [
    {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"text": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "Quality is not an act, it is a habit.", "author": "Aristotle"},

    # Custom quotes.
    {"text": "Surely the exam questions will just be about viral memes. No? Then let's open the actual study guide.", "author": "unknown"},
    {"text": "Staring at the ceiling hoping the syllabus absorbs via photosynthesis is a wild strategy. Let's actually read.", "author": "unknown"},
    {"text": "Waiting for the 'last-minute panic' to give you superpowers is a risky play. Let's just build the aura right now.", "author": "unknown"},
    {"text": "I'm sure the professor will grade your 'good intentions,' but just in case, let's get some actual definitions down.", "author": "unknown"},
    {"text": "An academic comeback requires you to actually come back, gang.", "author": "unknown"},
    {"text": "Surely the answer won't just spawn in your brain during the test, gang.", "author": "unknown"},
    {"text": "Please keep doomscrolling, gang—if you want your professor to absolutely humble you.", "author": "unknown"},
    {"text": "It's either an academic comeback or a certified skill issue, gang. Let's move.", "author": "unknown"},
    {"text": "Are we cooking, gang, or are we actively getting cooked?", "author": "unknown"},
    {"text": "Manifesting won't save the GPA anymore. Let's cook.", "author": "unknown"},
    {"text": "Aura +1000 if you finish this.", "author": "unknown"},
    {"text": "Study now so you can scroll later without that heavy, crushing existential dread.", "author": "unknown"},
    {"text": "Less panicking, more doing. You know more than you think.", "author": "unknown"},
    {"text": "The harder you work now, the better that post-exam nap feels.", "author": "unknown"},
    {"text": "Study now. Scroll mindlessly later, guilt-free.", "author": "unknown"},
]


def get_random_quote():
    """Return a randomly chosen quote, picked fresh on each call."""
    if not QUOTES:
        return {"text": "", "author": ""}
    return random.choice(QUOTES)
