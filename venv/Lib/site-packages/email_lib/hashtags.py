"""
Work on hashtags
"""

import re

HASHTAG_PATTERN=re.compile(r'(^|\s)#([^\d\s]\w+\b)')


def extract_hashtags(content):
    """
    Extract twitter-like hashtags from a given content
    """
    return [
        matches[1]
        for matches in HASHTAG_PATTERN.findall(content)
    ]
