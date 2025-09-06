from flask import Flask, render_template, request
from analyzer import analyze_posts
import math

app = Flask(__name__)

def compute_wellness(avg_polarity, usage_data, sleep_hours, study_hours):
    # polarity in [-1,1] -> 0..100
    polarity_score = (avg_polarity + 1) / 2 * 100

    total_usage = sum(usage_data.values())  # hours per day total
    # more usage reduces score; tuned factor
    usage_score = max(0, 100 - total_usage * 7)

    # sleep_score: best between 7-9 hours
    if 7 <= sleep_hours <= 9:
        sleep_score = 100
    elif sleep_hours < 7:
        sleep_score = max(0, 50 + sleep_hours * 6)  # gentle penalty for low sleep
    else:
        sleep_score = max(0, 100 - (sleep_hours - 9) * 10)

    # study_score: more studying up to a point helps
    study_score = min(100, 40 + study_hours * 10)  # e.g. 3h -> 70

    # weighted combination (tuneable)
    wellness = 0.4 * polarity_score + 0.3 * usage_score + 0.2 * sleep_score + 0.1 * study_score
    return round(wellness, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    # default zero usage for GET
    default_usage = {"Instagram": 0, "YouTube": 0, "WhatsApp": 0, "Others": 0}
    if request.method == "POST":
        posts_text = request.form.get("posts", "").strip()
        posts = [p.strip() for p in posts_text.splitlines() if p.strip()]

        results = []
        polarities = []
        for p in posts:
            mood, polarity = analyze_posts(p)
            results.append({"post": p, "mood": mood, "polarity": round(polarity, 3)})
            polarities.append(polarity)

        avg_polarity = sum(polarities) / len(polarities) if polarities else 0.0

        # read numeric inputs (hours)
        def get_float(name, default=0.0):
            try:
                return float(request.form.get(name, default))
            except:
                return default

        usage_data = {
            "Instagram": get_float("instagram", 0.0),
            "YouTube": get_float("youtube", 0.0),
            "WhatsApp": get_float("whatsapp", 0.0),
            "Others": get_float("others", 0.0)
        }
        sleep_hours = get_float("sleep_hours", 7.0)
        study_hours = get_float("study_hours", 2.0)

        wellness = compute_wellness(avg_polarity, usage_data, sleep_hours, study_hours)

        # badge and tips
        if wellness >= 75:
            badge = "Healthy"
            badge_class = "low-risk"
            tips = ["Great balance — keep routine sleep & focused study sessions.", "Continue mindful breaks."]
        elif wellness >= 50:
            badge = "Balanced"
            badge_class = "medium-risk"
            tips = ["Set screen-time limits in the evening.", "Try the Pomodoro technique (25/5) to improve focus."]
        else:
            badge = "At-risk"
            badge_class = "high-risk"
            tips = ["Limit late-night scrolling; establish phone-free hours.", "Consider speaking with a counselor or peer support."]

        return render_template(
            "report.html",
            results=results,
            usage_data=usage_data,
            wellness=wellness,
            badge=badge,
            badge_class=badge_class,
            tips=tips,
            sleep_hours=sleep_hours,
            study_hours=study_hours
        )

    return render_template("report.html", results=None, usage_data=default_usage, wellness=None)

if __name__ == "__main__":
    app.run(debug=True)
