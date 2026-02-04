import streamlit as st
import plotly.graph_objects as go
from skills_extractor import (
    extract_text_from_pdf, 
    extract_skills, 
    categorize_skills,
    calculate_match_score
)

# Page configuration
st.set_page_config(
    page_title="AI Resume Skill Matcher",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 AI Resume Skill Matcher")
st.markdown("### Upload your resume and paste a job description to see your match score!")
st.markdown("---")

# Initialize session state
if 'resume_skills' not in st.session_state:
    st.session_state.resume_skills = []
if 'job_skills' not in st.session_state:
    st.session_state.job_skills = []

# Two columns layout
col1, col2 = st.columns(2)

# LEFT COLUMN - Resume Upload
with col1:
    st.header("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF only)",
        type=['pdf'],
        help="Upload your resume in PDF format"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text.startswith("Error"):
                st.error(resume_text)
            else:
                st.session_state.resume_skills = extract_skills(resume_text)
                
                st.success(f"✅ Found {len(st.session_state.resume_skills)} skills in your resume")
                
                # Show categorized skills
                categorized = categorize_skills(st.session_state.resume_skills)
                
                with st.expander("View Detected Skills", expanded=False):
                    for category, skills in categorized.items():
                        st.markdown(f"**{category.upper()}:**")
                        st.write(", ".join(skills))

# RIGHT COLUMN - Job Description
with col2:
    st.header("💼 Job Description")
    job_desc = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the full job description including requirements..."
    )
    
    if job_desc:
        with st.spinner("Analyzing job description..."):
            st.session_state.job_skills = extract_skills(job_desc)
            
            st.success(f"✅ Found {len(st.session_state.job_skills)} required skills")
            
            # Show categorized skills
            categorized = categorize_skills(st.session_state.job_skills)
            
            with st.expander("View Required Skills", expanded=False):
                for category, skills in categorized.items():
                    st.markdown(f"**{category.upper()}:**")
                    st.write(", ".join(skills))

# ANALYSIS SECTION
if st.session_state.resume_skills and st.session_state.job_skills:
    st.markdown("---")
    st.header("📊 Match Analysis")
    
    match_result = calculate_match_score(
        st.session_state.resume_skills,
        st.session_state.job_skills
    )
    
    # Three columns for metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("Match Score", f"{match_result['score']}%")
    
    with metric_col2:
        st.metric("Matched Skills", len(match_result['matched_skills']))
    
    with metric_col3:
        st.metric("Missing Skills", len(match_result['missing_skills']))
    
    # Gauge Chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=match_result['score'],
        title={'text': "Compatibility Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "#0066cc"},
            'steps': [
                {'range': [0, 40], 'color': "#ffcccc"},
                {'range': [40, 70], 'color': "#fff4cc"},
                {'range': [70, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills breakdown
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("✅ Matched Skills")
        if match_result['matched_skills']:
            for skill in match_result['matched_skills']:
                st.markdown(f"✅ **{skill}**")
        else:
            st.info("No matching skills found")
    
    with col4:
        st.subheader("❌ Skills to Add")
        if match_result['missing_skills']:
            for skill in match_result['missing_skills']:
                st.markdown(f"❌ **{skill}**")
        else:
            st.success("You have all required skills!")
    
    # Extra skills
    if match_result['extra_skills']:
        with st.expander("💡 Additional Skills You Have", expanded=False):
            st.write(", ".join(match_result['extra_skills']))
    
    # Recommendations
    st.markdown("---")
    st.header("🎓 Learning Recommendations")
    
    if match_result['missing_skills']:
        st.info(f"Focus on learning these {len(match_result['missing_skills'])} skills to improve your match:")
        
        for i, skill in enumerate(match_result['missing_skills'][:5], 1):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{i}. {skill.title()}**")
            with col_b:
                search_url = f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}"
                st.markdown(f"[Find Course]({search_url})")
    else:
        st.success("🎉 Great! You match all required skills for this role!")
    
    # Action recommendation
    st.markdown("---")
    if match_result['score'] >= 70:
        st.success("✨ **Strong Match!** Your profile aligns well with this role. Consider applying!")
    elif match_result['score'] >= 40:
        st.warning("⚠️ **Moderate Match.** Consider upskilling in the missing areas before applying.")
    else:
        st.error("❌ **Low Match.** Significant skill gap. Focus on learning the missing skills first.")