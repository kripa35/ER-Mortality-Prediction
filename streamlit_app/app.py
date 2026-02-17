import streamlit as st
from datetime import datetime
import pickle
import pandas as pd

# Page config
st.set_page_config(
    page_title="ER Mortality Identification",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MODEL LOADING 
@st.cache_resource
def load_model():
    try:
        with open("streamlit_app/rf_mortality_model.pickle", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("Model file not found. Please ensure 'rf_mortality_model.pickle' is in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Loading the model
package = load_model()

# CSS
st.markdown("""
<style>
/* Force sidebar to full height and proper layout */
[data-testid="stSidebar"] {
    background-color: #eef6fb !important;
}

/* Make sidebar container fill height and use flexbox */
[data-testid="stSidebar"] > div:first-child {
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    padding: 0 !important;
}

/* Remove any default padding/margins */
[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}

/* Logo section - top */
.logo-section {
    padding: 20px 20px 0 20px;
    text-align: center;
    flex-shrink: 0;
}

/* Pages section - middle */
.pages-section {
    padding: 20px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Footer section - bottom */
.footer-section {
    padding: 15px 20px;
    border-top: 1px solid rgba(0,0,0,0.1);
    flex-shrink: 0;
}

/* Button styling - FONT SIZE 14PX FOR ALL BUTTONS */
.stButton > button {
    width: 100%;
    border-radius: 8px;
    margin: 8px 0;
    border: 1px solid rgba(0,0,0,0.1) !important;
    padding: 12px;
    background-color: transparent;
    color: #333;
    font-size: 14px !important; /* Font size 14px for buttons */
    font-weight: 500 !important;
}

.stButton > button:hover {
    background-color: rgba(0, 71, 140, 0.1);
}

/* Primary button (active page) - KEEP BLUE COLOR */
.stButton > button[kind="primary"] {
    background-color: #00478c !important;
    color: white !important;
    border-color: #00478c !important;
}

/* Main content styling */
.main-header {
    color: #00478c;
    margin-bottom: 30px;
}

.content-section {
    line-height: 1.7;
    text-align: justify;
}

/* About page specific styling */
.subtopic-header {
    color: #00478c;
    font-size: 22px !important;
    font-weight: 600 !important;
    margin-top: 35px !important;
    margin-bottom: 15px !important;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 8px;
}

.bullet-list {
    margin-left: 20px;
    margin-bottom: 25px;
}

.bullet-list li {
    margin-bottom: 10px;
    line-height: 1.6;
}

.highlight-box {
    background-color: #f0f8ff;
    border-left: 4px solid #00478c;
    padding: 20px;
    margin: 25px 0;
    border-radius: 0 8px 8px 0;
}

.highlight-box h4 {
    color: #00478c;
    margin-top: 0;
    margin-bottom: 15px;
}

.icon-list {
    list-style-type: none;
    padding-left: 0;
}

.icon-list li {
    margin-bottom: 12px;
    padding-left: 25px;
    position: relative;
}

.icon-list li:before {
    content: "•";
    color: #00478c;
    font-size: 20px;
    position: absolute;
    left: 0;
}

/* Methodology image styling */
.methodology-image {
    display: block;
    margin: 25px auto;
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.methodology-section {
    margin-top: 15px;
}

.methodology-section h4 {
    color: #00478c;
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 18px;
}

/* Test page styling */
.input-container {
    background-color: #f8fafc;
    border-radius: 10px;
    padding: 25px;
    margin: 20px 0;
    border: 1px solid #e2e8f0;
}

.metric-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #00478c;
    margin-bottom: 5px;
}

.metric-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

.risk-high {
    color: #dc2626 !important;
}

.risk-low {
    color: #059669 !important;
}

/* Perfect centered predict button */
.centered-predict-button {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 30px 0;
}

.centered-predict-button .stButton > button {
    width: 200px !important;
    padding: 10px 20px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    background-color: #00478c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0, 71, 140, 0.2) !important;
}

.centered-predict-button .stButton > button:hover {
    background-color: #003366 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 8px rgba(0, 71, 140, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# Initializing session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = '**Home**'

# Sidebar content 
with st.sidebar:
    # 1. Logo Section
    st.markdown('<div class="logo-section">', unsafe_allow_html=True)
    try:
        st.image("assets/app_logo.png", use_container_width=True)
    except:
        st.markdown("""
        <div style="text-align: center;">
            <h3 style="color: #00478c; margin: 0;">ER Mortality</h3>
            <p style="color: #666; margin: 5px 0 0 0;">Identification System</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Pages Section - Navigation
    st.markdown('<div class="pages-section">', unsafe_allow_html=True)
    
    pages = ['**Home**', '**About the project**', '**Test the model**']
    
    for page in pages:
        is_active = st.session_state.current_page == page
        
        if st.button(
            page,
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_page = page
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. Footer Section
    st.markdown('<div class="footer-section">', unsafe_allow_html=True)
    
    st.markdown("**App By:** Kripa Maharjan")
    st.markdown(f"**Last Updated On:** {datetime.now().strftime('%Y-%m-%d')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

current_page_clean = st.session_state.current_page.replace('**', '')

# Displaying content based on selected page
if current_page_clean == 'Home':
    # Home Page Content
    st.markdown('<h1 class="main-header">Developing and validating predictive models for emergency department mortality in critically ill patients</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    st.write("""
    The Emergency Department (ED) is the frontline of healthcare, managing patients with diverse acute conditions, 
    including critically ill individuals who require immediate and complex interventions. These patients carry a 
    high risk of mortality, yet early and accurate risk stratification remains challenging due to heterogeneous 
    presentations, time-critical decisions, and limitations of existing prognostic tools.
    """)
    
    st.write("")
    
    st.write("""
    Traditional scoring systems and statistical models often rely on limited structured data and may fail to 
    capture complex, nonlinear relationships or the rich clinical information in unstructured records, resulting 
    in suboptimal predictive performance. Moreover, data scarcity, class imbalance, and difficulties in 
    integrating advanced analytics into real-time ED workflows further hinder the development of robust 
    predictive models.
    """)
    
    st.write("")
    
    st.write("""
    Accurate mortality prediction is crucial for optimizing care, prioritizing resources, and improving patient 
    outcomes. Recent studies demonstrate that even minimal clinical data, such as blood tests or ECG readings, 
    can achieve high predictive accuracy for mortality at various time intervals post-admission. Advanced 
    models, including convolutional neural networks, CatBoost, and Random Forest, have shown strong 
    performance, although many are focused on ICU settings and may not be directly applicable to ED 
    environments.
    """)
    
    st.write("")
    
    st.write("""
    This study aims to develop a reliable and actionable predictive tool tailored for the ED, enhancing timely, 
    evidence-based decision-making for critically ill patients. We focus on leveraging machine learning 
    techniques, identifying key mortality predictors through feature importance analysis, incorporating 
    insights from unstructured clinical records via natural language processing, and enhancing model 
    robustness through synthetic data augmentation. Furthermore, we assess the feasibility of real-time 
    implementation to support clinicians in one of the most high-stakes areas of modern medicine.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
elif current_page_clean == 'About the project':
    # About Page Content
    st.markdown('<h1 class="main-header">ABOUT THE PROJECT</h1>', unsafe_allow_html=True)
    
    # 1. Objectives Section
    st.markdown('<h2 class="subtopic-header">OBJECTIVES</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bullet-list">
    <ul>
        <li><strong>To develop and validate predictive models</strong> for estimating mortality in critically ill patients presenting to the ED</li>
        <li><strong>Compare the performance of machine learning models</strong> with traditional statistical models</li>
        <li><strong>Identify key predictors of mortality</strong> using feature importance analyses</li>
        <li><strong>Assess the feasibility of integrating predictive models</strong> into real-time ED workflows</li>
        <li><strong>Utilize Natural Language Processing (NLP)</strong> to extract insights from unstructured clinical data</li>
        <li><strong>Augment the dataset with synthetic data</strong> to address data scarcity and improve model robustness</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Highlighting Box with key information
    st.markdown("""
    <div class="highlight-box">
    <h4>Project Overview</h4>
    <p>This app provides a reliable, AI-powered tool to predict mortality risk for patients in the Emergency Department (ED), 
    using locally-relevant data from Patan Hospital. Analyzing data from 597 patients (71.5% mortality prevalence), 
    our Random Forest model achieved strong performance using a rigorous multi feature selection approach selecting the top 15 features using various algorithms to select and narrow it down to the top five features:</p>
    <ul class="icon-list">
        <li><strong>Lactate (ABG)</strong></li>
        <li><strong>Creatinine</strong></li>
        <li><strong>Platelets</strong></li>
        <li><strong>Urea</strong></li>
        <li><strong>Resuscitation Received</strong></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Why this tool matters section
    st.markdown('<h2 class="subtopic-header">WHY THIS TOOL MATTERS</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="line-height: 1.7;">
    <ul class="icon-list">
        <li><strong>⚡ Accurate Predictions:</strong> Random Forest outperforms traditional scoring systems like NEWS2, helping clinicians make faster, more informed decisions.</li>
        <li><strong>🔬 Key Insights:</strong> Lactate emerged as the strongest predictor, even with high missing data, showing the power of advanced analytics.</li>
        <li><strong>⏱️ Real-Time Ready:</strong> Our production-stable model is designed for seamless integration into ED workflows, supporting rapid risk assessment.</li>
        <li><strong>🧠 Smart Data Handling:</strong> NLP and synthetic data evaluation ensure robustness, while tree-based models handle sparse clinical data effectively.</li>
    </ul>
    <p style="margin-top: 20px; font-style: italic;">
    This tool empowers ED clinicians with validated, actionable insights to improve patient outcomes and optimize care in high-stakes environments.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Methodology Section
    st.markdown('<h2 class="subtopic-header">METHODOLOGY</h2>', unsafe_allow_html=True)
    try:
        st.image("assets/er_mortality_workflow.png", use_container_width=True, caption="ER Mortality Analysis Workflow")
    except:
        st.markdown("""
        <div style="text-align: center; padding: 20px; border: 2px dashed #ccc; border-radius: 8px; margin: 20px 0;">
            <p><em>ER Mortality Analysis Workflow Image</em></p>
            <p style="font-size: 12px; color: #666;">Placeholder for methodology workflow diagram</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="methodology-section">
    <h4>Data Acquisition & Preparation</h4>
    <ul class="icon-list">
        <li>Loaded ER dataset with demographic, clinical, lab, and outcome variables.</li>
        <li>Handled missing values, standardized formats, and corrected inconsistencies while preserving maximum patient records.</li>
    </ul>
    
    <h4>Exploratory Data Analysis (EDA)</h4>
    <ul class="icon-list">
        <li>Used Distribution, Trend, and Correlation (DTC) framework.</li>
        <li>Identified class imbalance, clinically meaningful variables, and potential multicollinearity.</li>
    </ul>
    
    <h4>Statistical Analysis</h4>
    <ul class="icon-list">
        <li>Applied chi-square tests for categorical predictors and logistic regression for odds ratios.</li>
        <li>Established baseline clinical relationships as a benchmark for machine learning models.</li>
    </ul>
    
    <h4>Feature Selection</h4>
    <ul class="icon-list">
        <li>Multi-stage ensemble approach: Random Forest, XGBoost, and HistGradientBoosting importance.</li>
        <li>Top 5 features selected for interpretability, robustness, and clinical feasibility: <strong>Lactate (ABG), Creatinine, Platelets, Urea, Resuscitation Received</strong>.</li>
    </ul>
    
    <h4>Modeling & Preprocessing Comparison</h4>
    <ul class="icon-list">
        <li>Evaluated multiple pipelines: logistic regression, HistGradientBoosting, Random Forest.</li>
        <li>Dropping missing values excluded >95% of records, so Random Forest was chosen for robustness and ability to handle mixed data.</li>
    </ul>
    
    <h4>Model Evaluation & Selection</h4>
    <ul class="icon-list">
        <li>Compared models using cross-validated ROC-AUC.</li>
        <li>Random Forest showed superior performance, interpretability, and resilience to missing data.</li>
    </ul>
    
    <h4>Final Model Training & Threshold Optimization</h4>
    <ul class="icon-list">
        <li>Trained on top 5 features for clinical usability.</li>
        <li>Optimized decision threshold to balance sensitivity and specificity (threshold = 0.612).</li>
        <li>Reported metrics: ROC-AUC, F1-score, precision, recall, and confusion matrix.</li>
    </ul>
    
    <h4>Deployment Readiness</h4>
    <ul class="icon-list">
        <li>Model and preprocessing steps serialized for reproducibility.</li>
        <li>Ready for integration into real-time ED decision-support workflows.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # 3. Results and Findings Section
    st.markdown('<h2 class="subtopic-header">RESULTS AND FINDINGS</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="results-subsection">
    
    <p><strong>Top Predictors of ED Mortality</strong></p>
    <p>Using machine learning, we identified five clinically meaningful features that effectively stratify mortality risk:</p>
    
    <div style="margin: 15px 0; padding: 15px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #00478c;">
        <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
            <div style="text-align: center;">
                <div style="font-size: 20px;">🩸</div>
                <div style="font-weight: 600; color: #00478c;">Lactate (ABG)</div>
                <div style="font-size: 14px; color: #666;">Tissue perfusion</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px;">🧪</div>
                <div style="font-weight: 600; color: #00478c;">Creatinine</div>
                <div style="font-size: 14px; color: #666;">Renal function</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px;">🩹</div>
                <div style="font-weight: 600; color: #00478c;">Platelets</div>
                <div style="font-size: 14px; color: #666;">Hematologic status</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px;">💉</div>
                <div style="font-weight: 600; color: #00478c;">Urea</div>
                <div style="font-size: 14px; color: #666;">Metabolic function</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px;">🚑</div>
                <div style="font-weight: 600; color: #00478c;">Resuscitation Received</div>
                <div style="font-size: 14px; color: #666;">Treatment intensity</div>
            </div>
        </div>
    </div>
    
    <p><strong>Model Performance</strong></p>
    <p>Random Forest classifier demonstrated superior performance:</p>
    
    <div style="margin: 15px 0; padding: 15px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #00478c;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 10px 0;">
            <div style="text-align: center; padding: 10px; background-color: white; border-radius: 6px;">
                <div style="font-size: 22px; font-weight: 700; color: #00478c;">0.784</div>
                <div style="font-size: 14px; color: #666;">F1-score</div>
            </div>
            <div style="text-align: center; padding: 10px; background-color: white; border-radius: 6px;">
                <div style="font-size: 22px; font-weight: 700; color: #00478c;">0.767</div>
                <div style="font-size: 14px; color: #666;">Precision</div>
            </div>
            <div style="text-align: center; padding: 10px; background-color: white; border-radius: 6px;">
                <div style="font-size: 22px; font-weight: 700; color: #00478c;">0.802</div>
                <div style="font-size: 14px; color: #666;">Recall</div>
            </div>
            <div style="text-align: center; padding: 10px; background-color: white; border-radius: 6px;">
                <div style="font-size: 22px; font-weight: 700; color: #00478c;">0.707</div>
                <div style="font-size: 14px; color: #666;">ROC-AUC</div>
            </div>
        </div>
        <p style="margin-top: 10px; font-size: 14px; color: #666;">
        Threshold optimization ensured ~80% of high-risk patients were correctly identified while keeping false alarms low.
        </p>
    </div>
    
    <p><strong>Comparison with Traditional Scoring (NEWS2)</strong></p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li>Outperformed NEWS2 in discriminative ability and precision using only 5 key features.</li>
        <li>Provides early, actionable insights without the complexity or limitations of conventional scores.</li>
    </ul>
    
    <p><strong>Clinical Relevance</strong></p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li>A parsimonious, interpretable model supports rapid, real-time decision-making in the ED.</li>
        <li>Helps clinicians prioritize interventions, optimize resource allocation, and improve patient outcomes.</li>
    </ul>
    
    <p><strong>Robustness & Practicality</strong></p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li>Handles missing data natively, making it reliable for real-world ED workflows.</li>
        <li>Focuses on physiologically relevant features, ensuring interpretability and trust.</li>
    </ul>
    
    </div>
    """, unsafe_allow_html=True)
    
elif current_page_clean == 'Test the model':

    # Test Model Page Content
    st.markdown('<h1 class="main-header">TEST THE MODEL</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom: 30px; line-height: 1.7;">
    Use this interactive tool to predict mortality risk for ER patients based on the top 5 clinical features 
    identified by our Random Forest model. Enter the patient's values below and click "Predict Mortality Risk" 
    to see the prediction.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        lactate = st.number_input(
            "Lactate (ABG)", 
            min_value=0.2, 
            max_value=15.0, 
            value=2.0, 
            step=0.1,
            help="Normal range: 0.5-2.2 mmol/L"
        )
        urea = st.number_input(
            "Urea (mg/dl)", 
            min_value=2.0, 
            max_value=450.0, 
            value=20.0, 
            step=1.0,
            help="Normal range: 7-20 mg/dL"
        )
    
    with col2:
        creatinine = st.number_input(
            "Creatinine (mg/dl)", 
            min_value=0.3, 
            max_value=16.0, 
            value=1.0, 
            step=0.1,
            help="Normal range: 0.6-1.2 mg/dL"
        )
        platelets = st.number_input(
            "Platelets (10⁶/µL)", 
            min_value=5.0, 
            max_value=800.0, 
            value=250.0, 
            step=1.0,
            help="Normal range: 150-450 ×10³/µL"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Resuscitation section
    resus = st.multiselect(
        "Select all resuscitation interventions received:",
        [
            "Fluid",
            "Use of Vasopressors",
            "Use of Invasive Ventilation",
            "Use of Non-Invasive Ventilation",
            "CPR"
        ],
        help="Select all that apply"
    )
    
    resus_value = ", ".join(resus) if resus else "None"
    
    # Prediction button 
    st.markdown('<div class="centered-predict-button">', unsafe_allow_html=True)
    predict_button = st.button(
        "Predict Mortality Risk", 
        type="primary"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Running model inference based on user inputs
    if predict_button and package:
        try:
            # Creating input dataframe
            input_df = pd.DataFrame({
                "Lactate (in ABG)": [lactate],
                "Urea (mg/dl)": [urea],
                "Creatinine (mg/dl)": [creatinine],
                "Platelets (10 ^ 6)": [platelets],
                "Resuscitation Received": [resus_value]
            })
            
            model = package["model"]
            threshold = package["threshold"]
            
            # Getting prediction
            proba = model.predict_proba(input_df)[:, 1][0]
            prediction = int(proba >= threshold)
            
            # Displaying results
            st.markdown("---")
            st.markdown('<h3 style="text-align: center;">Prediction Results</h3>', unsafe_allow_html=True)
            
            # Results in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                risk_class = "HIGH RISK 🚨" if prediction else "LOW RISK ✅"
                risk_color = "risk-high" if prediction else "risk-low"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {risk_color}">{risk_class}</div>
                    <div class="metric-label">Risk Level</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{proba:.3f}</div>
                    <div class="metric-label">Probability Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{threshold:.3f}</div>
                    <div class="metric-label">Decision Threshold</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Interpretation
            st.markdown("---")
            if prediction:
                st.error("""
                **🚨 HIGH RISK ALERT**
                
                This patient has a mortality probability above the optimized threshold of 0.612. 
                Consider immediate intervention and close monitoring. The model has identified 
                this patient as high-risk based on the entered clinical parameters.
                """)
            else:
                st.success("""
                **✅ LOW RISK**
                
                This patient has a mortality probability below the optimized threshold of 0.612. 
                Continue with standard care protocols while maintaining appropriate monitoring.
                """)
            
            # Model metrics expander
            with st.expander("View Model Performance Metrics"):
                if "metrics" in package:
                    metrics = package["metrics"]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("F1-Score", f"{metrics.get('F1', 0):.3f}")
                        st.metric("Precision", f"{metrics.get('Precision', 0):.3f}")

                    with col2:
                        st.metric("Recall", f"{metrics.get('Recall', 0):.3f}")
                    
                    if "classification_report" in metrics:
                        st.subheader("Classification Report")
                        st.text(metrics["classification_report"])
                else:
                    st.info("Detailed metrics not available in the model package.")
            
            # Creating expander for metrics explanations
            with st.expander("📊 Click to understand what these metrics mean"):
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #00478c; margin-bottom: 15px;">
                <h5 style="color: #00478c; margin-top: 0;">Probability Score</h5>
                <p>The probability score represents the model's estimated likelihood that a specific outcome will occur. 
                In a medical context, it indicates how strongly the model believes that a patient belongs to a high-risk group, 
                such as the probability of mortality. The score ranges from 0 to 1, where values closer to 1 indicate higher risk.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #00478c; margin-bottom: 15px;">
                <h5 style="color: #00478c; margin-top: 0;">Decision Threshold</h5>
                <p>The decision threshold is a predefined cut-off value used to convert the probability score into a final classification, 
                such as low risk or high risk. If the predicted probability exceeds this threshold, the model classifies the case as positive. 
                Threshold optimization involves selecting the most appropriate cut-off value to balance correct detections and false alarms.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #00478c; margin-bottom: 15px;">
                <h5 style="color: #00478c; margin-top: 0;">Precision</h5>
                <p>Precision measures the reliability of positive predictions made by the model. 
                It indicates the proportion of cases predicted as high risk that are truly high risk. 
                High precision means the model produces fewer false alarms.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #00478c; margin-bottom: 15px;">
                <h5 style="color: #00478c; margin-top: 0;">Recall</h5>
                <p>Recall measures the model's ability to correctly identify actual positive cases. 
                It reflects how many true high-risk cases are successfully detected by the model. 
                High recall indicates that fewer critical cases are missed.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #00478c; margin-bottom: 15px;">
                <h5 style="color: #00478c; margin-top: 0;">F1-Score</h5>
                <p>The F1-score combines precision and recall into a single measure, providing a balanced assessment of the model's performance. 
                It is particularly useful when the number of positive and negative cases is unequal, as it ensures that both false alarms and missed cases are considered.</p>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
    
    elif predict_button and not package:
        st.error("Model not loaded. Please check if 'rf_mortality_model.pickle' exists in the directory.")


        




