    # Withdrawal strategies comparison
    st.subheader("Withdrawal Strategies Analysis")
    
    strategies = results['withdrawal_strategies']
    
    strategy_cols = st.columns(len(strategies))
    
    for i, (key, strategy) in enumerate(strategies.items()):
        with strategy_cols[i]:
            with st.container():
                st.markdown(f"**{strategy['name']}**")
                
                if 'initial_withdrawal' in strategy:
                    st.metric("Initial Withdrawal", format_currency(strategy['initial_withdrawal']))
                elif 'required_corpus' in strategy:
                    st.metric("Required Corpus", format_currency(strategy['required_corpus']))
                
                if 'success_rate' in strategy:
                    success_rate = strategy['success_rate']
                    color = 'green' if success_rate >= 90 else 'orange' if success_rate >= 75 else 'red'
                    st.markdown(f"Success Rate: :{color}[{success_rate}%]")
                
                with st.expander("Details"):
                    st.write(strategy.get('description', ''))
                    
                    if 'pros' in strategy:
                        st.write("**Pros:**")
                        for pro in strategy['pros']:
                            st.write(f"• {pro}")
                    
                    if 'cons' in strategy:
                        st.write("**Cons:**")
                        for con in strategy['cons']:
                            st.write(f"• {con}")
    
    # Detailed yearly breakdown
    st.subheader("Year-by-Year Breakdown")
    
    df = pd.DataFrame(yearly_data)
    
    # Show every 5 years for readability
    if len(df) > 0:
        display_years = df[df['age'] % 5 == 0].copy()
        
        # Format for display
        display_df = display_years[['age', 'phase', 'balance', 'contribution', 'investment_return', 'withdrawal']].copy()
        display_df.columns = ['Age', 'Phase', 'Balance', 'Contribution', 'Investment Return', 'Withdrawal']
        
        # Format currency columns
        for col in ['Balance', 'Contribution', 'Investment Return', 'Withdrawal']:
            display_df[col] = display_df[col].apply(lambda x: format_currency(x) if x > 0 else '-')
        
        display_df['Phase'] = display_df['Phase'].str.title()
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Sensitivity analysis
    st.subheader("Sensitivity Analysis")
    
    sensitivity_data = results.get('sensitivity_analysis', {})
    
    if sensitimport streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

from database.db_utils import (
    get_database_session, get_retirement_profile, save_retirement_profile,
    get_user_scenarios, save_retirement_scenario, get_calculation_history
)
from services.retirement_service import (
    calculate_retirement_plan, calculate_retirement_score, 
    generate_retirement_recommendations, RetirementGoalTracker
)
from components.charts import create_retirement_projection_chart, create_sensitivity_chart
from components.widgets import retirement_metrics_widget, goal_progress_widget
from utils.retirement_helpers import format_currency, calculate_inflation_impact

def show_retirement_planning():
    """Main retirement planning interface"""
    
    st.title("🏖️ Retirement Planning")
    st.markdown("Plan your financial future with comprehensive retirement analysis")
    
    # Check if user has a retirement profile
    session = get_database_session()
    user_id = st.session_state.get('user_id', 'default_user')
    profile = get_retirement_profile(session, user_id)
    
    if not profile:
        show_profile_setup(session, user_id)
    else:
        show_retirement_dashboard(session, user_id, profile)
    
    session.close()

def show_profile_setup(session, user_id):
    """Show retirement profile setup form"""
    
    st.info("👋 Welcome! Let's set up your retirement planning profile.")
    
    with st.form("retirement_profile_setup"):
        st.subheader("Personal Information")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            current_age = st.number_input("Current Age", min_value=18, max_value=80, value=35)
        with col2:
            retirement_age = st.number_input("Planned Retirement Age", min_value=50, max_value=80, value=65)
        with col3:
            life_expectancy = st.number_input("Life Expectancy", min_value=retirement_age+1, max_value=100, value=85)
        
        st.subheader("Income & Goals")
        col1, col2 = st.columns(2)
        with col1:
            current_income = st.number_input("Current Annual Income ($)", min_value=0, value=75000, step=1000)
        with col2:
            income_replacement = st.slider("Desired Retirement Income (% of current)", 40, 100, 80) / 100
        
        st.subheader("Current Savings")
        col1, col2 = st.columns(2)
        with col1:
            current_savings = st.number_input("Current Retirement Savings ($)", min_value=0, value=50000, step=1000)
        with col2:
            monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0, value=800, step=50)
        
        st.subheader("Employer Benefits")
        col1, col2 = st.columns(2)
        with col1:
            employer_match_rate = st.slider("Employer Match Rate (%)", 0, 100, 50) / 100
        with col2:
            employer_match_limit = st.slider("Employer Match Limit (% of salary)", 0, 15, 6) / 100
        
        with st.expander("Advanced Settings"):
            col1, col2, col3 = st.columns(3)
            with col1:
                pre_retirement_return = st.slider("Pre-Retirement Return (%)", 3, 12, 7) / 100
            with col2:
                post_retirement_return = st.slider("Post-Retirement Return (%)", 2, 8, 5) / 100
            with col3:
                inflation_rate = st.slider("Inflation Rate (%)", 1, 6, 3) / 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                social_security = st.number_input("Expected Social Security ($)", min_value=0, value=18000, step=1000)
            with col2:
                healthcare_costs = st.number_input("Expected Healthcare Costs ($)", min_value=0, value=8000, step=500)
            with col3:
                pension = st.number_input("Expected Pension ($)", min_value=0, value=0, step=1000)
        
        submitted = st.form_submit_button("Create Retirement Plan", type="primary")
        
        if submitted:
            profile_data = {
                'current_age': current_age,
                'retirement_age': retirement_age,
                'life_expectancy': life_expectancy,
                'current_annual_income': current_income,
                'desired_retirement_income_ratio': income_replacement,
                'current_savings': current_savings,
                'monthly_contribution': monthly_contribution,
                'employer_match_rate': employer_match_rate,
                'employer_match_limit': employer_match_limit,
                'pre_retirement_return_rate': pre_retirement_return,
                'post_retirement_return_rate': post_retirement_return,
                'inflation_rate': inflation_rate,
                'estimated_social_security': social_security,
                'estimated_healthcare_costs': healthcare_costs,
                'estimated_pension': pension
            }
            
            try:
                profile = save_retirement_profile(session, user_id, profile_data)
                st.success("✅ Retirement profile created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating profile: {e}")

def show_retirement_dashboard(session, user_id, profile):
    """Show main retirement dashboard"""
    
    # Calculate retirement plan
    with st.spinner("Calculating your retirement plan..."):
        results = calculate_retirement_plan(session, user_id)
    
    if 'error' in results:
        st.error(results['error'])
        return
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", "📈 Projections", "🎯 Scenarios", "💡 Recommendations", "⚙️ Settings", "📄 Reports"
    ])
    
    with tab1:
        show_dashboard_tab(results, profile)
    
    with tab2:
        show_projections_tab(results, profile)
    
    with tab3:
        show_scenarios_tab(session, user_id, profile, results)
    
    with tab4:
        show_recommendations_tab(session, user_id)
    
    with tab5:
        show_settings_tab(session, user_id, profile)
    
    with tab6:
        show_reports_tab(results, profile)

def show_dashboard_tab(results, profile):
    """Show dashboard overview"""
    
    needs = results['retirement_needs']
    projections = results['savings_projections']
    monte_carlo = results['monte_carlo_results']
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        years_to_retirement = needs['years_to_retirement']
        st.metric("Years to Retirement", f"{years_to_retirement}")
    
    with col2:
        corpus_needed = needs['retirement_corpus_needed']
        st.metric("Corpus Needed", format_currency(corpus_needed))
    
    with col3:
        projected_savings = projections['total_projected_savings']
        st.metric("Projected Savings", format_currency(projected_savings))
    
    with col4:
        success_rate = monte_carlo['success_rate']
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Progress visualization
    st.subheader("Retirement Readiness")
    
    progress = min(projected_savings / corpus_needed, 1.0) if corpus_needed > 0 else 0
    st.progress(progress)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if projections['shortfall'] > 0:
            st.error(f"**Shortfall:** {format_currency(projections['shortfall'])}")
            st.write(f"Additional monthly savings needed: {format_currency(projections['additional_monthly_needed'])}")
        else:
            st.success(f"**Surplus:** {format_currency(projections['surplus'])}")
            st.write("You're on track to meet your retirement goals! 🎉")
    
    with col2:
        # Risk assessment
        risk_level = monte_carlo['risk_assessment']
        risk_colors = {'low': 'green', 'medium': 'orange', 'high': 'red', 'very_high': 'darkred'}
        
        st.markdown(f"**Risk Level:** :{risk_colors.get(risk_level, 'gray')}[{risk_level.replace('_', ' ').title()}]")
        
        if risk_level in ['high', 'very_high']:
            st.warning("Consider adjusting your retirement strategy to reduce risk.")
        elif risk_level == 'low':
            st.info("Your retirement plan appears to be on solid ground.")
    
    # Quick stats
    st.subheader("Key Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Current Situation:**")
        st.write(f"• Current Age: {profile.current_age}")
        st.write(f"• Annual Income: {format_currency(profile.current_annual_income)}")
        st.write(f"• Current Savings: {format_currency(profile.current_savings)}")
        st.write(f"• Monthly Contribution: {format_currency(profile.monthly_contribution)}")
    
    with col2:
        st.write("**Retirement Goals:**")
        st.write(f"• Retirement Age: {profile.retirement_age}")
        st.write(f"• Income Replacement: {profile.desired_retirement_income_ratio*100:.0f}%")
        st.write(f"• Required Income: {format_currency(needs['desired_annual_income_today'])}")
        st.write(f"• Future Income Need: {format_currency(needs['future_annual_need'])}")
    
    with col3:
        st.write("**Investment Assumptions:**")
        st.write(f"• Pre-Retirement Return: {profile.pre_retirement_return_rate*100:.1f}%")
        st.write(f"• Post-Retirement Return: {profile.post_retirement_return_rate*100:.1f}%")
        st.write(f"• Inflation Rate: {profile.inflation_rate*100:.1f}%")
        st.write(f"• Effective Monthly: {format_currency(projections['effective_monthly_contribution'])}")

def show_projections_tab(results, profile):
    """Show detailed projections and charts"""
    
    st.subheader("Retirement Savings Projections")
    
    yearly_data = results['yearly_projections']
    
    if not yearly_data:
        st.warning("No projection data available.")
        return
    
    # Create projection chart
    fig = create_retirement_projection_chart(yearly_data, profile)
    st.plotly_chart(fig, use_container_width=True)
    
    # Withdrawal strategies comparison
    st.subheader