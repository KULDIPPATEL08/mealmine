# app.py
import streamlit as st
from transformers import pipeline
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import io
import base64
import time
import sys

# Initialize session state
if 'automation_triggered' not in st.session_state:
    st.session_state.automation_triggered = False
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'automation_progress' not in st.session_state:
    st.session_state.automation_progress = 0

# Check if we're in a desktop environment
desktop_capable = False
try:
    import pyautogui
    desktop_capable = True
except ImportError:
    st.sidebar.warning("PyAutoGUI not found. Desktop automation will be disabled. Install with: pip install pyautogui")
    desktop_capable = False

# Custom CSS styling
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header {
        color: #2c3e50;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="header">Sentiment Analyzer & Automator</div>', unsafe_allow_html=True)
st.markdown("### Your intelligent text analysis and automation companion")

# Task A: UI Components
with st.container():
    st.markdown("### 📝 Text Analysis Tool")
    with st.form("analysis_form"):
        user_input = st.text_area("Enter text for sentiment analysis:", 
                                placeholder="Type or paste your text here...",
                                height=150)
        analyze_btn = st.form_submit_button("Analyze Sentiment")

# Task B: AI/ML Integration
if analyze_btn and user_input:
    with st.spinner("Analyzing text..."):
        try:
            # Explicit model specification for production use
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                revision="714eb0f"
            )
            result = sentiment_pipeline(user_input)[0]
            
            # Log results to dataframe
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_text": user_input,
                "sentiment": result['label'],
                "confidence": round(result['score'], 4)
            }
            
            # Store the current result in session state
            st.session_state.last_result = log_entry
            
            # Add to session state log data for historical tracking
            st.session_state.log_data.append(log_entry)
            
            # Create dataframe for logging
            df = pd.DataFrame([log_entry])
            
            # Save to CSV with append mode
            file_exists = os.path.isfile("sentiment_log.csv")
            df.to_csv("sentiment_log.csv", mode='a', header=not file_exists)
            st.session_state.log_exists = True
            
            # Display results
            st.success(f"Sentiment: {result['label']} ({result['score']:.1%})")
            st.progress(result['score'])
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

# Create a function to generate visual report using matplotlib only
def generate_visual_report():
    # Create a figure with multiple plots
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))
    
    # Convert session data to DataFrame
    if len(st.session_state.log_data) > 0:
        df = pd.DataFrame(st.session_state.log_data)
        
        # Plot 1: Sentiment Distribution
        ax1 = axes[0]
        sentiment_counts = df['sentiment'].value_counts()
        colors = ['#ff9999' if x == 'NEGATIVE' else '#66b3ff' for x in sentiment_counts.index]
        ax1.bar(sentiment_counts.index, sentiment_counts.values, color=colors)
        ax1.set_title('Sentiment Distribution', fontsize=16)
        ax1.set_ylabel('Count')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Plot 2: Confidence Levels
        ax2 = axes[1]
        df_sorted = df.sort_values(by='timestamp')
        sentiments = df_sorted['sentiment'].tolist()
        confidences = df_sorted['confidence'].tolist()
        indices = range(len(df_sorted))
        colors = ['red' if s == 'NEGATIVE' else 'blue' for s in sentiments]
        
        for i, (idx, conf, color) in enumerate(zip(indices, confidences, colors)):
            ax2.scatter(idx, conf, color=color, s=100)
            if i > 0:
                # Connect points with a line
                ax2.plot([indices[i-1], idx], [confidences[i-1], conf], 
                         color='green', linestyle='-', alpha=0.5)
        
        ax2.set_title('Confidence Trend', fontsize=16)
        ax2.set_xlabel('Analysis Index')
        ax2.set_ylabel('Confidence Score')
        ax2.set_ylim(0, 1)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save image to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        
        # Save as a file for desktop automation
        plt.savefig("report_graphs.png")
        plt.close()
        
        # Create text report
        last_entry = st.session_state.log_data[-1]
        text_report = f"""
AUTO-GENERATED REPORT - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*40}
LATEST ANALYSIS RESULTS:
- Input Text: "{last_entry['input_text']}"
- Sentiment: {last_entry['sentiment'].upper()}
- Confidence: {last_entry['confidence']:.1%}

SUMMARY STATISTICS:
- Total Analyses: {len(df)}
- POSITIVE Sentiments: {len(df[df['sentiment'] == 'POSITIVE'])}
- NEGATIVE Sentiments: {len(df[df['sentiment'] == 'NEGATIVE'])}
- Average Confidence: {df['confidence'].mean():.1%}

RUN INFORMATION:
- Timestamp: {last_entry['timestamp']}
- Model Used: distilbert-base-uncased-finetuned-sst-2-english
"""
        # Save report to file for desktop automation
        with open("sentiment_report.txt", "w") as f:
            f.write(text_report)
            
        return text_report, buf
    return None, None

# Function for desktop automation
def run_desktop_automation():
    if not desktop_capable:
        return False, "PyAutoGUI not installed. Desktop automation cannot run."
    
    try:
        # Check if we have the required files
        if not os.path.exists("sentiment_report.txt") or not os.path.exists("report_graphs.png"):
            return False, "Report files not found. Please generate a report first."
        
        # Get screen size for safety checks
        screen_width, screen_height = pyautogui.size()
        
        # Fail-safe enabled by default (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        
        # Open Notepad
        if sys.platform == 'win32':
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write('notepad')
            pyautogui.press('enter')
        elif sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 'space')
            time.sleep(0.5)
            pyautogui.write('textedit')
            pyautogui.press('enter')
        else:  # Linux and others
            pyautogui.hotkey('ctrl', 'alt', 't')  # Open terminal
            time.sleep(0.5)
            pyautogui.write('gedit')  # Open gedit
            pyautogui.press('enter')
        
        time.sleep(1.5)  # Wait for app to open
        
        # Read the report
        with open("sentiment_report.txt", "r") as f:
            report_text = f.read()
        
        # Type the report content
        pyautogui.write(report_text, interval=0.01)
        
        # Save the file
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)
        pyautogui.write('auto_sentiment_report.txt')
        pyautogui.press('enter')
        time.sleep(0.5)
        
        # Try to open the image with default image viewer
        if sys.platform == 'win32':
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write('mspaint')
            pyautogui.press('enter')
            time.sleep(1.5)
            pyautogui.hotkey('ctrl', 'o')
            time.sleep(0.5)
            # Navigate to the current directory
            current_dir = os.path.abspath(os.getcwd())
            pyautogui.write(os.path.join(current_dir, "report_graphs.png"))
            pyautogui.press('enter')
        
        return True, "Desktop automation completed successfully!"
    except Exception as e:
        return False, f"Desktop automation failed: {str(e)}"

# Task C: Automated Report Generation with Visualizations
tabs = st.tabs(["Web Automation", "Desktop Automation", "Batch Processing"])

with tabs[0]:
    st.markdown("### 🤖 Web Report Generation")
    st.info("Click below to automatically generate a comprehensive report with graphs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Run Web Reporting"):
            if len(st.session_state.log_data) == 0:
                st.warning("Please perform at least one analysis first")
            else:
                st.session_state.automation_running = True
                st.session_state.automation_progress = 0
    
    with col2:
        if st.button("Stop Web Automation"):
            st.session_state.automation_running = False

    # Display automation progress
    if st.session_state.automation_running:
        progress_bar = st.progress(st.session_state.automation_progress)
        status_text = st.empty()
        
        # Simulate automation steps
        steps = ["Collecting data...", "Processing sentiments...", "Generating visualizations...", "Creating report..."]
        
        for i, step in enumerate(steps):
            # Update status
            status_text.text(f"Automation in progress: {step}")
            # Update progress (each step is 25% of the total)
            progress_value = (i + 1) * 0.25
            st.session_state.automation_progress = progress_value
            progress_bar.progress(progress_value)
            # Simulate processing time
            time.sleep(0.7)
        
        # Generate the report
        text_report, image_buffer = generate_visual_report()
        
        if text_report and image_buffer:
            st.session_state.automation_running = False
            st.success("Automated report generated successfully!")
            
            # Display the report preview
            st.subheader("Report Preview")
            st.text(text_report)
            
            # Display the graph
            st.image(image_buffer, caption="Sentiment Analysis Visualization")
            
            # Provide download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download Text Report",
                    data=text_report,
                    file_name="sentiment_report.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Convert image to downloadable format
                b64 = base64.b64encode(image_buffer.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="sentiment_graphs.png">Download Graph Report</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            # Log the generation
            with open("automation_log.txt", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WEB REPORT GENERATED\n")
        else:
            st.error("Not enough data to generate a report. Please perform at least one analysis.")
            st.session_state.automation_running = False

with tabs[1]:
    st.markdown("### 🖥️ Desktop Automation")
    
    if desktop_capable:
        st.info("This feature uses PyAutoGUI to automate desktop applications. Make sure you have generated a report first.")
        st.warning("⚠️ Desktop automation will take control of your mouse and keyboard. Keep your mouse at screen corner to abort.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Report Files"):
                if len(st.session_state.log_data) == 0:
                    st.warning("Please perform at least one analysis first")
                else:
                    with st.spinner("Generating report files..."):
                        text_report, _ = generate_visual_report()
                        if text_report:
                            st.success("Report files generated and saved to disk.")
        
        with col2:
            if st.button("Run Desktop Automation"):
                if len(st.session_state.log_data) == 0:
                    st.warning("Please perform at least one analysis first")
                else:
                    with st.spinner("Running desktop automation..."):
                        success, message = run_desktop_automation()
                        if success:
                            st.success(message)
                            # Log the automation
                            with open("automation_log.txt", "a") as f:
                                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DESKTOP AUTOMATION COMPLETED\n")
                        else:
                            st.error(message)
    else:
        st.error("PyAutoGUI is not installed. Desktop automation is disabled.")
        st.info("To enable desktop automation, run: pip install pyautogui")
        if st.button("Try to Install PyAutoGUI"):
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
                st.success("PyAutoGUI installed successfully! Please restart the application.")
            except Exception as e:
                st.error(f"Failed in {str(e)}")