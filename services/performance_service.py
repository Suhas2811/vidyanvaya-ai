"""
Performance analysis service for VidyānVaya AI.

Week 6:
- Stores practice-test performance
- Calculates performance statistics
- Identifies weak and strong areas
- Generates personalized recommendations
"""

from collections import defaultdict


def create_performance_record(
    topic,
    difficulty,
    score,
    total_marks,
    questions_attempted,
    evaluations=None,
):
    """
    Create a structured performance record for one
    completed practice test.

    Parameters:
        topic: Topic selected for the practice test.
        difficulty: Difficulty level.
        score: Marks obtained.
        total_marks: Maximum possible marks.
        questions_attempted: Number of questions.
        evaluations: Individual question evaluations.

    Returns:
        Dictionary containing the test performance.
    """

    if evaluations is None:
        evaluations = []

    percentage = 0.0

    if total_marks > 0:
        percentage = (score / total_marks) * 100

    return {
        "topic": str(topic),
        "difficulty": str(difficulty),
        "score": float(score),
        "total_marks": float(total_marks),
        "percentage": round(percentage, 2),
        "questions_attempted": int(questions_attempted),
        "evaluations": evaluations,
    }


def calculate_overall_performance(history):
    """
    Calculate overall performance from completed tests.

    Parameters:
        history: List of performance records.

    Returns:
        Dictionary containing overall statistics.
    """

    if not history:
        return {
            "tests_attempted": 0,
            "total_score": 0.0,
            "total_marks": 0.0,
            "percentage": 0.0,
        }

    total_score = sum(
        float(record.get("score", 0))
        for record in history
    )

    total_marks = sum(
        float(record.get("total_marks", 0))
        for record in history
    )

    percentage = 0.0

    if total_marks > 0:
        percentage = (
            total_score / total_marks
        ) * 100

    return {
        "tests_attempted": len(history),
        "total_score": round(total_score, 2),
        "total_marks": round(total_marks, 2),
        "percentage": round(percentage, 2),
    }


def analyze_topic_performance(history):
    """
    Analyze performance topic-wise.

    Returns:
        Dictionary where each topic contains:
        - tests
        - score
        - total_marks
        - percentage
    """

    topic_data = defaultdict(
        lambda: {
            "tests": 0,
            "score": 0.0,
            "total_marks": 0.0,
        }
    )

    for record in history:

        topic = record.get(
            "topic",
            "Unknown"
        )

        topic_data[topic]["tests"] += 1

        topic_data[topic]["score"] += float(
            record.get("score", 0)
        )

        topic_data[topic]["total_marks"] += float(
            record.get("total_marks", 0)
        )

    result = {}

    for topic, data in topic_data.items():

        percentage = 0.0

        if data["total_marks"] > 0:
            percentage = (
                data["score"]
                / data["total_marks"]
            ) * 100

        result[topic] = {
            "tests": data["tests"],
            "score": round(
                data["score"],
                2
            ),
            "total_marks": round(
                data["total_marks"],
                2
            ),
            "percentage": round(
                percentage,
                2
            ),
        }

    return result


def identify_weak_areas(
    history,
    threshold=50.0,
):
    """
    Identify topics where performance is below
    the specified percentage threshold.

    Default threshold:
        50%
    """

    topic_performance = analyze_topic_performance(
        history
    )

    weak_areas = []

    for topic, data in topic_performance.items():

        if data["percentage"] < threshold:

            weak_areas.append(
                {
                    "topic": topic,
                    "percentage": data[
                        "percentage"
                    ],
                    "tests": data["tests"],
                }
            )

    weak_areas.sort(
        key=lambda item: item["percentage"]
    )

    return weak_areas


def identify_strong_areas(
    history,
    threshold=75.0,
):
    """
    Identify topics where performance is at or
    above the specified percentage threshold.

    Default threshold:
        75%
    """

    topic_performance = analyze_topic_performance(
        history
    )

    strong_areas = []

    for topic, data in topic_performance.items():

        if data["percentage"] >= threshold:

            strong_areas.append(
                {
                    "topic": topic,
                    "percentage": data[
                        "percentage"
                    ],
                    "tests": data["tests"],
                }
            )

    strong_areas.sort(
        key=lambda item: item["percentage"],
        reverse=True,
    )

    return strong_areas


def generate_recommendations(
    history,
    weak_threshold=50.0,
):
    """
    Generate personalized study recommendations
    based on weak areas.

    Returns:
        List of recommendation dictionaries.
    """

    weak_areas = identify_weak_areas(
        history,
        threshold=weak_threshold,
    )

    recommendations = []

    for area in weak_areas:

        topic = area["topic"]
        percentage = area["percentage"]

        if percentage < 30:
            priority = "High"
            action = (
                "Revise the fundamentals and "
                "practice basic questions."
            )

        elif percentage < 50:
            priority = "High"
            action = (
                "Review the core concepts and "
                "practice more questions."
            )

        else:
            priority = "Medium"
            action = (
                "Revise the topic and attempt "
                "additional practice questions."
            )

        recommendations.append(
            {
                "topic": topic,
                "percentage": percentage,
                "priority": priority,
                "recommendation": action,
            }
        )

    return recommendations


def get_performance_summary(history):
    """
    Generate a complete performance summary.

    This function combines overall performance,
    topic analysis, weak areas, strong areas,
    and recommendations.
    """

    overall = calculate_overall_performance(
        history
    )

    topic_performance = analyze_topic_performance(
        history
    )

    weak_areas = identify_weak_areas(
        history
    )

    strong_areas = identify_strong_areas(
        history
    )

    recommendations = generate_recommendations(
        history
    )

    return {
        "overall": overall,
        "topic_performance": topic_performance,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "recommendations": recommendations,
    }