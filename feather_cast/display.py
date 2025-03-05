import streamlit as st
from flask import Flask, render_template
from database import get_recent_detections

# Flask Web UI setup
app = Flask(__name__)

@app.route("/")
def index():
    detections = get_recent_detections(5)
    return render_template("index.html", detections=detections)

# Streamlit Web UI setup
def streamlit_ui():
    st.title("Bird Detections")

    # Fetch the recent detections (up to 5)
    detections = get_recent_detections(5)

    # Display each bird detection
    for common_name, scientific_name, confidence, label, timestamp in detections:
        st.write(f"🐦 {common_name} - {confidence:.2f} ({timestamp})")


# Main entry point
if __name__ == "__main__":
    import sys

    # Check if we are running Streamlit or Flask
    if "streamlit" in sys.argv:
        print("Running Streamlit UI")
        streamlit_ui()
    else:
        app.run(host="0.0.0.0", port=5000)
