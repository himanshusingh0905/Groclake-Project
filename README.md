
# SETUP:
1. Install required dependencies to run this project
   * *Creating virtual environment is optional*
      * create virtual environment: `python -m venv venv`
      * activate it : `source venv/bin/activate`

2. INSTALL DEPEDENCIES : `pip install -r requirements.txt`

3. After setting up : you can run it using `python app.py`

4. you may need to wait for a while for output.


---
# Future scope:
1. Initially I was mean't to connnect a healthband's data to the **AGENT**. But connecting a healthband api would limit our requests but more importantly, it won't give us edge-case data. so I'm using dummy dataset of healthband data.

2. With further enhancements we can also implement:
   1. **Predictive Healthcare Alerts for Chronic Patients:**
      * Tracks trends in blood pressure, heart rate, and respiration for early risk detection.
      * Alerts users or healthcare providers if vitals show worrying patterns.
      * Assists in managing conditions like hypertension, sleep apnea, and diabetes.

   2. **Early Detection of Heart Diseases:**
      * Uses ECG and AFib detection to identify irregular heart rhythms.
      * Monitors blood pressure fluctuations and correlates with stress levels.
      * Predicts potential cardiovascular risks using AI-based predictive models.