"""
Viral format database and matching logic.
Contains templates for viral video formats (Cluely, YC demos, etc.)
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


# Viral format templates
VIRAL_FORMATS = [
    {
        "format_id": "yc_demo_classic",
        "name": "YC Demo Day Classic",
        "description": "The classic Y Combinator demo video format - problem, solution, demo, traction",
        "platform_fit": ["YouTube", "LinkedIn", "Twitter"],
        "duration_range": [60, 180],
        "structure": [
            {
                "segment": "hook",
                "duration": 5,
                "script_template": "We're [Company Name] and we're [solving X problem] for [Y audience]",
                "visual_guide": "Founder speaking directly to camera, simple background",
                "required": True
            },
            {
                "segment": "problem",
                "duration": 15,
                "script_template": "Today, [target audience] struggle with [specific problem]. This costs them [quantifiable impact]",
                "visual_guide": "Show the problem - screen recordings, statistics, user testimonials",
                "required": True
            },
            {
                "segment": "solution",
                "duration": 10,
                "script_template": "We built [product name] to solve this. Here's how it works...",
                "visual_guide": "Product logo, quick overview shot",
                "required": True
            },
            {
                "segment": "demo",
                "duration": 30,
                "script_template": "Let me show you... [walk through 2-3 key features]",
                "visual_guide": "Screen recording of product in action, narrated walkthrough",
                "required": True
            },
            {
                "segment": "traction",
                "duration": 10,
                "script_template": "We've helped [X users/companies] achieve [Y result]",
                "visual_guide": "Show metrics, testimonials, growth charts",
                "required": True
            },
            {
                "segment": "call_to_action",
                "duration": 5,
                "script_template": "Try [product] at [website] and [specific CTA]",
                "visual_guide": "Simple card with website and CTA",
                "required": True
            }
        ],
        "tags": ["b2b", "saas", "startup", "demo", "professional"],
        "example_videos": ["https://www.youtube.com/watch?v=example_yc"],
        "success_metrics": {
            "avg_retention": 0.75,
            "avg_conversion": 0.05,
            "viral_score": 85
        }
    },
    {
        "format_id": "cluely_launch",
        "name": "Cluely Launch Style",
        "description": "Fast-paced, personality-driven product launch video with quick cuts and energy",
        "platform_fit": ["TikTok", "Instagram", "Twitter"],
        "duration_range": [30, 60],
        "structure": [
            {
                "segment": "hook",
                "duration": 3,
                "script_template": "POV: You just launched [product] and...",
                "visual_guide": "Energetic opener, founder with personality, quick zoom",
                "required": True
            },
            {
                "segment": "problem_callout",
                "duration": 5,
                "script_template": "Everyone knows [common pain point] is broken",
                "visual_guide": "Fast cuts showing frustration, relatable moments",
                "required": True
            },
            {
                "segment": "solution_reveal",
                "duration": 7,
                "script_template": "So we built [product] - it's [one-liner description]",
                "visual_guide": "Product reveal with visual flair, logo animation",
                "required": True
            },
            {
                "segment": "key_features",
                "duration": 20,
                "script_template": "You can [feature 1], [feature 2], and [feature 3]",
                "visual_guide": "Rapid screen recordings, text overlays highlighting features",
                "required": True
            },
            {
                "segment": "social_proof",
                "duration": 5,
                "script_template": "[X] people are already using it",
                "visual_guide": "Show user count, testimonials, or usage clips",
                "required": False
            },
            {
                "segment": "cta",
                "duration": 5,
                "script_template": "Link in bio / Go to [website]",
                "visual_guide": "End card with clear CTA and website",
                "required": True
            }
        ],
        "tags": ["consumer", "fast-paced", "personality", "viral", "short-form"],
        "example_videos": ["https://twitter.com/cluely/status/example"],
        "success_metrics": {
            "avg_retention": 0.85,
            "avg_shares": 500,
            "viral_score": 92
        }
    },
    {
        "format_id": "educational_tutorial",
        "name": "Educational Tutorial Format",
        "description": "Step-by-step tutorial format for teaching skills or product usage",
        "platform_fit": ["YouTube", "Instagram", "TikTok"],
        "duration_range": [45, 120],
        "structure": [
            {
                "segment": "hook",
                "duration": 5,
                "script_template": "Want to [achieve X]? Here's how in [Y] steps",
                "visual_guide": "Show end result, create curiosity",
                "required": True
            },
            {
                "segment": "intro",
                "duration": 5,
                "script_template": "I'm [name] and I'll show you exactly how to [do X]",
                "visual_guide": "Quick self-intro, establish credibility",
                "required": True
            },
            {
                "segment": "step_1",
                "duration": 15,
                "script_template": "Step 1: [First step] - Here's why this matters...",
                "visual_guide": "Screen recording or demo of step 1",
                "required": True
            },
            {
                "segment": "step_2",
                "duration": 15,
                "script_template": "Step 2: [Second step] - Pro tip: [insider advice]",
                "visual_guide": "Screen recording or demo of step 2",
                "required": True
            },
            {
                "segment": "step_3",
                "duration": 15,
                "script_template": "Step 3: [Final step] - This is where most people mess up",
                "visual_guide": "Screen recording or demo of step 3",
                "required": True
            },
            {
                "segment": "recap",
                "duration": 10,
                "script_template": "Quick recap: [1, 2, 3]. Now you can [achieve result]",
                "visual_guide": "Quick cuts of all steps",
                "required": True
            },
            {
                "segment": "cta",
                "duration": 5,
                "script_template": "Save this for later, follow for more [niche] content",
                "visual_guide": "Subscribe/follow prompt",
                "required": True
            }
        ],
        "tags": ["educational", "tutorial", "how-to", "step-by-step"],
        "example_videos": [],
        "success_metrics": {
            "avg_retention": 0.70,
            "avg_saves": 200,
            "viral_score": 78
        }
    },
    {
        "format_id": "before_after_transformation",
        "name": "Before/After Transformation",
        "description": "Show dramatic transformation or improvement using your product/method",
        "platform_fit": ["TikTok", "Instagram", "YouTube"],
        "duration_range": [15, 60],
        "structure": [
            {
                "segment": "hook",
                "duration": 2,
                "script_template": "This is [before state]",
                "visual_guide": "Show problematic before state",
                "required": True
            },
            {
                "segment": "before_context",
                "duration": 8,
                "script_template": "I was struggling with [problem] and nothing worked until...",
                "visual_guide": "More before footage, build empathy",
                "required": True
            },
            {
                "segment": "transformation",
                "duration": 15,
                "script_template": "Then I tried [solution/product] and here's what happened",
                "visual_guide": "Show the process, product in action",
                "required": True
            },
            {
                "segment": "after_reveal",
                "duration": 5,
                "script_template": "Now look at this [after state]",
                "visual_guide": "Dramatic after reveal",
                "required": True
            },
            {
                "segment": "cta",
                "duration": 5,
                "script_template": "Get [product] at [link]",
                "visual_guide": "Product link and CTA",
                "required": True
            }
        ],
        "tags": ["transformation", "before-after", "results", "testimonial"],
        "example_videos": [],
        "success_metrics": {
            "avg_retention": 0.88,
            "avg_shares": 350,
            "viral_score": 89
        }
    }
]


async def seed_viral_formats(db: AsyncIOMotorDatabase):
    """Seed the database with viral format templates"""
    for format_data in VIRAL_FORMATS:
        format_data["created_at"] = datetime.now(timezone.utc).isoformat()
        format_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.viral_formats.update_one(
            {"format_id": format_data["format_id"]},
            {"$set": format_data},
            upsert=True
        )


async def query_viral_formats(
    db: AsyncIOMotorDatabase,
    platform: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Query viral formats based on filters.
    
    Args:
        db: MongoDB database instance
        platform: Filter by platform (TikTok, Instagram, YouTube, etc.)
        tags: Filter by tags
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
    
    Returns:
        List of matching viral formats
    """
    query = {}
    
    if platform:
        query["platform_fit"] = {"$in": [platform]}
    
    if tags:
        query["tags"] = {"$in": tags}
    
    if min_duration or max_duration:
        duration_query = {}
        if min_duration:
            duration_query["$gte"] = min_duration
        if max_duration:
            duration_query["$lte"] = max_duration
        query["duration_range.0"] = duration_query
    
    formats = await db.viral_formats.find(query, {"_id": 0}).to_list(100)
    return formats


async def calculate_format_match_score(
    user_goal: str,
    product_type: str,
    target_platform: str,
    format_data: Dict[str, Any]
) -> float:
    """
    Calculate how well a viral format matches the user's requirements.
    
    Args:
        user_goal: User's content goal description
        product_type: Type of product (b2b, consumer, educational, etc.)
        target_platform: Target platform
        format_data: Viral format data
    
    Returns:
        Match score between 0-100
    """
    score = 0.0
    
    # Platform match (40 points)
    if target_platform in format_data.get("platform_fit", []):
        score += 40
    
    # Tag match (30 points)
    user_tags = product_type.lower().split()
    format_tags = format_data.get("tags", [])
    matching_tags = len(set(user_tags) & set(format_tags))
    score += min(30, matching_tags * 10)
    
    # Viral score boost (30 points)
    viral_score = format_data.get("success_metrics", {}).get("viral_score", 0)
    score += (viral_score / 100) * 30
    
    return min(100, score)


async def get_format_by_id(db: AsyncIOMotorDatabase, format_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific viral format by ID"""
    format_data = await db.viral_formats.find_one({"format_id": format_id}, {"_id": 0})
    return format_data