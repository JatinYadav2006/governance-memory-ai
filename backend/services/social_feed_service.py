from __future__ import annotations

from typing import Any

from backend.ai.social_media_analysis import (
    compare_social_and_complaint_pressure,
    detect_emerging_social_issues,
    detect_misinformation_alerts,
    summarize_social_sentiment,
)


SOCIAL_POSTS: list[dict[str, Any]] = [
    {
        "platform": "X",
        "author": "@ward7resident",
        "location": "Prayagraj",
        "text": "No water again in Ward 7 since morning. Taps are dry and nobody from the department has shown up.",
        "engagement": 54,
    },
    {
        "platform": "Instagram",
        "author": "@civiclens",
        "location": "Prayagraj",
        "text": "People near Civil Lines are posting videos of weak water pressure and pipeline leakage.",
        "engagement": 39,
    },
    {
        "platform": "X",
        "author": "@studentvoice",
        "location": "Lucknow",
        "text": "Garbage overflow near the university gate is getting worse and the smell is unbearable.",
        "engagement": 31,
    },
    {
        "platform": "Facebook",
        "author": "City Watch Lucknow",
        "location": "Lucknow",
        "text": "Trash and waste bags are piling up near the market lane. Sanitation response still missing.",
        "engagement": 26,
    },
    {
        "platform": "X",
        "author": "@kanpurcommuter",
        "location": "Kanpur",
        "text": "Massive potholes on ring road are dangerous for bikes. This can cause an accident anytime.",
        "engagement": 42,
    },
    {
        "platform": "WhatsApp Monitor",
        "author": "Forwarded Message",
        "location": "Prayagraj",
        "text": "Warning: water in Ward 7 is poisoned. Do not drink anything from municipal taps.",
        "engagement": 63,
    },
    {
        "platform": "Facebook",
        "author": "Local Forum",
        "location": "Varanasi",
        "text": "Drainage overflow after rain has left the whole lane dirty and unsafe for children.",
        "engagement": 21,
    },
    {
        "platform": "X",
        "author": "@civicobserver",
        "location": "Varanasi",
        "text": "People are upset because blocked drains are still causing waterlogging near residential pockets.",
        "engagement": 19,
    },
    {
        "platform": "Instagram",
        "author": "@urbanpulse",
        "location": "Prayagraj",
        "text": "Water crisis posts are spreading much faster than complaint acknowledgements right now.",
        "engagement": 44,
    },
    {
        "platform": "X",
        "author": "@nightcommuter",
        "location": "Kanpur",
        "text": "Broken road surface near the bus stand is still unresolved and traffic is suffering daily.",
        "engagement": 17,
    },
]


def get_social_posts() -> list[dict[str, Any]]:
    return [dict(post) for post in SOCIAL_POSTS]


def build_social_pulse(complaint_clusters: list[dict[str, Any]]) -> dict[str, Any]:
    posts = get_social_posts()
    sentiment_summary = summarize_social_sentiment(posts)
    emerging_issues = detect_emerging_social_issues(posts)
    misinformation_alerts = detect_misinformation_alerts(posts, complaint_clusters)
    mismatch_alerts = compare_social_and_complaint_pressure(emerging_issues, complaint_clusters)

    return {
        "sentiment_summary": sentiment_summary,
        "emerging_issues": emerging_issues,
        "misinformation_alerts": misinformation_alerts,
        "mismatch_alerts": mismatch_alerts,
        "recent_posts": posts[:8],
    }
