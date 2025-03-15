Key Features
Text Analysis Tool :
Perform sentiment analysis on user-provided text using a pre-trained Hugging Face Transformer model (distilbert-base-uncased-finetuned-sst-2-english).
Real-time sentiment predictions with confidence scores.
Logs analysis results to a CSV file (sentiment_log.csv) for historical tracking.
Web Automation :
Generate a comprehensive report with visualizations:
Sentiment distribution bar chart.
Confidence trend scatter plot with connecting lines.
Downloadable text and graph reports.
Desktop Automation :
Automate desktop tasks using PyAutoGUI:
Opens a text editor (Notepad, TextEdit, or Gedit) and types the generated report.
Saves the report as a .txt file.
Opens an image viewer to display the generated graphs.
Cross-Platform Compatibility :
Supports Windows, macOS, and Linux for desktop automation.
Includes platform-specific commands for opening applications.
Error Handling :
Graceful handling of missing dependencies (e.g., PyAutoGUI).
User-friendly warnings and error messages for invalid inputs or failed operations.



├── app.py                  # Main application script
├── sentiment_log.csv       # Log file for sentiment analysis results
├── sentiment_report.txt    # Auto-generated text report
├── report_graphs.png       # Auto-generated graph visualization
├── automation_log.txt      # Log file for automation tasks
├── requirements.txt        # List of required Python libraries
└── README.md               # Documentation for the project
**for run app**
streamlit run app.py
streamlit run app.py