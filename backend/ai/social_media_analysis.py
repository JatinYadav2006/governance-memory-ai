from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from backend.services.sentiment_service import analyze_sentiment


SOCIAL_TOPIC_KEYWORDS = {
    "Water": ["water", "pipeline", "supply", "tap", "leak", "pressure"],
    "Garbage": ["garbage", "trash", "waste", "sanitation", "bin", "overflow"],
    "Road": ["road", "pothole", "traffic", "surface", "street"],
    "Drainage": ["drain", "drainage", "waterlogged", "sewage", "flood"],
    "Electricity": ["power", "electric", "electricity", "outage", "grid", "streetlight"],
}

MISINFORMATION_PATTERNS = [
    {
        "keywords": ["poison", "water"],
        "label": "Potential Water Contamination Narrative",
        "message": "Posts are amplifying an unverified water contamination claim that could trigger public panic.",
    },
    {
        "keywords": ["bridge", "collapsed"],
        "label": "Potential Infrastructure Collapse Narrative",
        "message": "A potentially false infrastructure collapse claim is circulating and needs fast clarification.",
    },
    {
        "keywords": ["riot", "protest"],
        "label": "Potential Escalation Narrative",
        "message": "Posts suggest civic unrest escalation; this should be verified before it spreads further.",
    },
]


def _detect_topic(text: str) -> str:
    lowered = text.lower()
    for topic, keywords in SOCIAL_TOPIC_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return topic
    return "General Civic Concern"


def _location_from_posts(posts: list[dict[str, Any]]) -> str:
    locations = [str(post.get("location", "")).strip() for post in posts if str(post.get("location", "")).strip()]
    if not locations:
        return "Unknown"
    return Counter(locations).most_common(1)[0][0]


def summarize_social_sentiment(posts: list[dict[str, Any]]) -> dict[str, Any]:
    if not posts:
        return {
            "total_posts": 0,
            "negative_posts": 0,
            "positive_posts": 0,
            "neutral_posts": 0,
            "negative_share": 0.0,
            "top_topic": "No social activity",
        }

    sentiment_counter: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()

    for post in posts:
        sentiment = analyze_sentiment(str(post.get("text", "")))
        post["sentiment"] = sentiment
        topic = _detect_topic(str(post.get("text", "")))
        post["topic"] = topic
        sentiment_counter[sentiment] += 1
        topic_counter[topic] += 1

    total_posts = len(posts)
    negative_posts = sentiment_counter.get("negative", 0)
    return {
        "total_posts": total_posts,
        "negative_posts": negative_posts,
        "positive_posts": sentiment_counter.get("positive", 0),
        "neutral_posts": sentiment_counter.get("neutral", 0),
        "negative_share": round((negative_posts / total_posts) * 100, 1) if total_posts else 0.0,
        "top_topic": topic_counter.most_common(1)[0][0] if topic_counter else "No social activity",
    }


def detect_emerging_social_issues(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        topic = post.get("topic") or _detect_topic(str(post.get("text", "")))
        location = str(post.get("location", "Unknown")).strip() or "Unknown"
        grouped[(str(topic), location)].append(post)

    emerging: list[dict[str, Any]] = []
    for (topic, location), grouped_posts in grouped.items():
        negative_posts = sum(1 for post in grouped_posts if str(post.get("sentiment", "")).lower() == "negative")
        average_engagement = round(
            sum(int(post.get("engagement", 0)) for post in grouped_posts) / len(grouped_posts),
            1,
        ) if grouped_posts else 0.0
        if len(grouped_posts) < 2:
            continue

        signal = "High" if len(grouped_posts) >= 4 or negative_posts >= 3 else "Watch"
        emerging.append(
            {
                "topic": topic,
                "location": location,
                "post_count": len(grouped_posts),
                "negative_posts": negative_posts,
                "signal": signal,
                "average_engagement": average_engagement,
                "summary": (
                    f"Residents are increasingly discussing {topic.lower()} problems in {location}. "
                    f"{negative_posts} of the tracked posts carry negative sentiment."
                ),
            }
        )

    emerging.sort(key=lambda item: (-int(item["post_count"]), -int(item["negative_posts"]), str(item["location"])))
    return emerging


def detect_misinformation_alerts(
    posts: list[dict[str, Any]],
    complaint_clusters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    cluster_titles = " ".join(str(cluster.get("cluster_title", "")).lower() for cluster in complaint_clusters)

    for pattern in MISINFORMATION_PATTERNS:
        matching_posts = [
            post
            for post in posts
            if all(keyword in str(post.get("text", "")).lower() for keyword in pattern["keywords"])
        ]
        if not matching_posts:
            continue

        corroborated = any(keyword in cluster_titles for keyword in pattern["keywords"])
        severity = "High" if len(matching_posts) >= 2 and not corroborated else "Medium"
        alerts.append(
            {
                "alert_title": pattern["label"],
                "location": _location_from_posts(matching_posts),
                "severity": severity,
                "message": pattern["message"],
                "post_count": len(matching_posts),
                "evidence_terms": list(pattern["keywords"]),
                "status": "Needs verification before official rebuttal",
                "recommended_response": (
                    "Issue an official clarification and compare the claim against verified complaint evidence."
                    if not corroborated
                    else "Monitor the claim closely and publish a verification-backed update."
                ),
            }
        )

    alerts.sort(key=lambda item: (-int(item["post_count"]), str(item["location"])))
    return alerts


def compare_social_and_complaint_pressure(
    emerging_issues: list[dict[str, Any]],
    complaint_clusters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cluster_index: dict[tuple[str, str], dict[str, Any]] = {}
    for cluster in complaint_clusters:
        cluster_index[(str(cluster.get("location", "")).strip().lower(), str(cluster.get("cluster_title", "")).lower())] = cluster

    mismatches: list[dict[str, Any]] = []
    for issue in emerging_issues:
        topic = str(issue.get("topic", "")).lower()
        location = str(issue.get("location", "")).strip().lower()
        matching_cluster = next(
            (
                cluster
                for cluster in complaint_clusters
                if location == str(cluster.get("location", "")).strip().lower()
                and topic.split()[0] in str(cluster.get("cluster_title", "")).lower()
            ),
            None,
        )
        cluster_count = int(matching_cluster.get("issue_count", 0)) if matching_cluster else 0
        buzz_gap = int(issue.get("post_count", 0)) - cluster_count
        if buzz_gap <= 1:
            continue
        mismatches.append(
            {
                "topic": issue.get("topic", "Civic Issue"),
                "location": issue.get("location", "Unknown"),
                "social_posts": issue.get("post_count", 0),
                "complaint_count": cluster_count,
                "signal": "Social buzz is running ahead of formal complaints",
            }
        )

    return mismatches[:5]
