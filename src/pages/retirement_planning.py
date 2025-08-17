import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

from database.db_utils import (
    get_db_session, get_retirement_profile, save_retirement_profile,
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
    
    if sensitivity_data:
        # Create sensitivity chart
        sensitivity_fig = create_sensitivity_chart(sensitivity_data, results['savings_projections']['total_projected_savings'])
        st.plotly_chart(sensitivity_fig, use_container_width=True)
        
        st.write("**Key Insights:**")
        st.write("• Investment returns have the highest impact on your retirement savings")
        st.write("• Small changes in retirement age can significantly affect outcomes")
        st.write("• Inflation erodes purchasing power over time")

def show_scenarios_tab(session, user_id, profile, base_results):
    """Show scenario analysis"""
    
    st.subheader("Retirement Scenarios")
    
    # Get existing scenarios
    scenarios = get_user_scenarios(session, profile.id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if scenarios:
            st.write("**Saved Scenarios:**")
            
            for scenario in scenarios:
                with st.expander(f"{scenario.scenario_name} - {scenario.description}"):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if scenario.corpus_needed:
                            st.metric("Corpus Needed", format_currency(scenario.corpus_needed))
                    
                    with col_b:
                        if scenario.projected_savings:
                            st.metric("Projected Savings", format_currency(scenario.projected_savings))
                    
                    with col_c:
                        if scenario.success_probability:
                            st.metric("Success Rate", f"{scenario.success_probability:.1f}%")
                    
                    if st.button(f"Delete {scenario.scenario_name}", key=f"del_{scenario.id}"):
                        # Delete scenario logic would go here
                        st.rerun()
        else:
            st.info("No saved scenarios yet. Create one below!")
    
    with col2:
        st.write("**Quick Scenarios:**")
        
        if st.button("🏠 Conservative Scenario"):
            create_conservative_scenario(session, profile)
            st.rerun()
        
        if st.button("🚀 Aggressive Scenario"):
            create_aggressive_scenario(session, profile)
            st.rerun()
        
        if st.button("⏰ Late Start Scenario"):
            create_late_start_scenario(session, profile)
            st.rerun()
    
    # Custom scenario creator
    st.subheader("Create Custom Scenario")
    
    with st.form("custom_scenario"):
        scenario_name = st.text_input("Scenario Name", value="My Custom Scenario")
        description = st.text_area("Description", value="Custom retirement scenario")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            custom_retirement_age = st.number_input("Retirement Age", 
                                                  min_value=50, max_value=80, 
                                                  value=profile.retirement_age)
        
        with col2:
            custom_monthly = st.number_input("Monthly Contribution", 
                                           min_value=0, 
                                           value=int(profile.monthly_contribution))
        
        with col3:
            custom_return = st.slider("Pre-Retirement Return (%)", 
                                    3, 12, 
                                    int(profile.pre_retirement_return_rate * 100)) / 100
        
        if st.form_submit_button("Create Scenario"):
            create_custom_scenario(session, profile, {
                'scenario_name': scenario_name,
                'description': description,
                'retirement_age': custom_retirement_age,
                'monthly_contribution': custom_monthly,
                'pre_retirement_return_rate': custom_return
            })
            st.success("Scenario created!")
            st.rerun()

def show_recommendations_tab(session, user_id):
    """Show AI-powered recommendations"""
    
    st.subheader("💡 Personalized Recommendations")
    
    with st.spinner("Generating personalized recommendations..."):
        recommendations = generate_retirement_recommendations(session, user_id)
    
    if not recommendations:
        st.info("No specific recommendations at this time. Your retirement plan looks solid!")
        return
    
    for i, rec in enumerate(recommendations):
        # Color code by priority
        if rec['type'] == 'critical':
            st.error(f"**🔴 {rec['title']}**")
        elif rec['type'] == 'high':
            st.warning(f"**🟡 {rec['title']}**")
        else:
            st.info(f"**🔵 {rec['title']}**")
        
        st.write(rec['description'])
        
        if rec.get('action_items'):
            st.write("**Action Items:**")
            for action in rec['action_items']:
                st.write(f"• {action}")
        
        if i < len(recommendations) - 1:
            st.divider()
    
    # Goal tracking section
    st.subheader("🎯 Retirement Goals")
    
    profile = get_retirement_profile(session, user_id)
    if profile:
        goal_tracker = RetirementGoalTracker(session, user_id)
        milestones = goal_tracker.create_milestone_goals(profile)
        
        if milestones:
            st.write("**Suggested Milestones:**")
            
            for milestone in milestones[:3]:  # Show top 3
                feasibility = goal_tracker.calculate_goal_feasibility(
                    milestone['target_amount'],
                    milestone['years_to_goal'],
                    profile.current_savings,
                    profile.monthly_contribution
                )
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{milestone['goal_name']}**")
                    st.write(milestone['description'])
                
                with col2:
                    st.metric("Target", format_currency(milestone['target_amount']))
                    st.write(f"Age {milestone['target_age']}")
                
                with col3:
                    if feasibility['feasible']:
                        st.success("✅ On Track")
                    else:
                        st.error("❌ Behind")
                        st.write(f"Need: +{format_currency(feasibility['additional_monthly_needed'])}/mo")

def show_settings_tab(session, user_id, profile):
    """Show settings and profile management"""
    
    st.subheader("⚙️ Retirement Profile Settings")
    
    with st.form("update_profile"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            current_age = st.number_input("Current Age", min_value=18, max_value=80, value=profile.current_age)
            retirement_age = st.number_input("Retirement Age", min_value=50, max_value=80, value=profile.retirement_age)
            life_expectancy = st.number_input("Life Expectancy", min_value=retirement_age+1, max_value=100, value=profile.life_expectancy)
            
            st.subheader("Financial Information")
            current_income = st.number_input("Annual Income", min_value=0, value=int(profile.current_annual_income))
            income_ratio = st.slider("Retirement Income %", 40, 100, int(profile.desired_retirement_income_ratio * 100)) / 100
        
        with col2:
            st.subheader("Savings")
            current_savings = st.number_input("Current Savings", min_value=0, value=int(profile.current_savings))
            monthly_contribution = st.number_input("Monthly Contribution", min_value=0, value=int(profile.monthly_contribution))
            
            st.subheader("Employer Benefits")
            employer_match_rate = st.slider("Employer Match %", 0, 100, int(profile.employer_match_rate * 100)) / 100
            employer_match_limit = st.slider("Match Limit %", 0, 15, int(profile.employer_match_limit * 100)) / 100
        
        with st.expander("Investment Assumptions"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                pre_return = st.slider("Pre-Retirement Return %", 3, 12, int(profile.pre_retirement_return_rate * 100)) / 100
            with col_b:
                post_return = st.slider("Post-Retirement Return %", 2, 8, int(profile.post_retirement_return_rate * 100)) / 100
            with col_c:
                inflation = st.slider("Inflation %", 1, 6, int(profile.inflation_rate * 100)) / 100
        
        with st.expander("Additional Income"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                social_security = st.number_input("Social Security", min_value=0, value=int(profile.estimated_social_security or 0))
            with col_b:
                healthcare = st.number_input("Healthcare Costs", min_value=0, value=int(profile.estimated_healthcare_costs or 0))
            with col_c:
                pension = st.number_input("Pension", min_value=0, value=int(profile.estimated_pension or 0))
        
        if st.form_submit_button("Update Profile", type="primary"):
            updated_data = {
                'current_age': current_age,
                'retirement_age': retirement_age,
                'life_expectancy': life_expectancy,
                'current_annual_income': current_income,
                'desired_retirement_income_ratio': income_ratio,
                'current_savings': current_savings,
                'monthly_contribution': monthly_contribution,
                'employer_match_rate': employer_match_rate,
                'employer_match_limit': employer_match_limit,
                'pre_retirement_return_rate': pre_return,
                'post_retirement_return_rate': post_return,
                'inflation_rate': inflation,
                'estimated_social_security': social_security,
                'estimated_healthcare_costs': healthcare,
                'estimated_pension': pension
            }
            
            try:
                save_retirement_profile(session, user_id, updated_data)
                st.success("✅ Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {e}")
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Data"):
            export_retirement_data(session, user_id)
    
    with col2:
        if st.button("🔄 Reset Calculations"):
            reset_calculation_history(session, profile.id)
    
    with col3:
        if st.button("🗑️ Delete Profile", type="secondary"):
            if st.button("Confirm Delete", type="primary"):
                delete_retirement_profile_data(session, user_id)

def show_reports_tab(results, profile):
    """Show comprehensive reports"""
    
    st.subheader("📄 Retirement Planning Report")
    
    # Summary report
    with st.expander("Executive Summary", expanded=True):
        generate_executive_summary(results, profile)
    
    # Detailed analysis
    with st.expander("Detailed Analysis"):
        generate_detailed_analysis(results, profile)
    
    # Action plan
    with st.expander("Action Plan"):
        generate_action_plan(results, profile)
    
    # Download options
    st.subheader("Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download PDF Report"):
            generate_pdf_report(results, profile)
    
    with col2:
        if st.button("📊 Download Excel Analysis"):
            generate_excel_report(results, profile)
    
    with col3:
        if st.button("📋 Email Summary"):
            email_report_summary(results, profile)

# Helper functions for scenarios
def create_conservative_scenario(session, profile):
    """Create conservative scenario"""
    scenario_data = {
        'profile_id': profile.id,
        'scenario_name': 'Conservative Scenario',
        'description': 'Lower returns, higher inflation assumptions',
        'scenario_type': 'conservative',
        'parameter_overrides': {
            'pre_retirement_return_rate': profile.pre_retirement_return_rate - 0.02,
            'post_retirement_return_rate': profile.post_retirement_return_rate - 0.01,
            'inflation_rate': profile.inflation_rate + 0.01
        }
    }
    save_retirement_scenario(session, scenario_data)

def create_aggressive_scenario(session, profile):
    """Create aggressive scenario"""
    scenario_data = {
        'profile_id': profile.id,
        'scenario_name': 'Aggressive Scenario',
        'description': 'Higher returns, increased savings',
        'scenario_type': 'aggressive',
        'parameter_overrides': {
            'pre_retirement_return_rate': profile.pre_retirement_return_rate + 0.02,
            'monthly_contribution': profile.monthly_contribution * 1.5
        }
    }
    save_retirement_scenario(session, scenario_data)

def create_late_start_scenario(session, profile):
    """Create late start scenario"""
    scenario_data = {
        'profile_id': profile.id,
        'scenario_name': 'Catch-Up Scenario',
        'description': 'Work longer, save more aggressively',
        'scenario_type': 'catch_up',
        'parameter_overrides': {
            'retirement_age': profile.retirement_age + 3,
            'monthly_contribution': profile.monthly_contribution * 2
        }
    }
    save_retirement_scenario(session, scenario_data)

def create_custom_scenario(session, profile, custom_params):
    """Create custom scenario"""
    scenario_data = {
        'profile_id': profile.id,
        'scenario_name': custom_params['scenario_name'],
        'description': custom_params['description'],
        'scenario_type': 'custom',
        'parameter_overrides': {
            k: v for k, v in custom_params.items() 
            if k not in ['scenario_name', 'description']
        }
    }
    save_retirement_scenario(session, scenario_data)

# Report generation functions
def generate_executive_summary(results, profile):
    """Generate executive summary"""
    needs = results['retirement_needs']
    projections = results['savings_projections']
    monte_carlo = results['monte_carlo_results']
    
    st.markdown(f"""
    **Retirement Planning Summary for {profile.user_id}**
    
    **Current Situation:**
    - Age: {profile.current_age}, Retirement Goal: Age {profile.retirement_age}
    - Current Savings: {format_currency(profile.current_savings)}
    - Monthly Contribution: {format_currency(profile.monthly_contribution)}
    
    **Retirement Goals:**
    - Target Corpus: {format_currency(needs['retirement_corpus_needed'])}
    - Projected Savings: {format_currency(projections['total_projected_savings'])}
    - Success Probability: {monte_carlo['success_rate']:.1f}%
    
    **Key Findings:**
    """)
    
    if projections['shortfall'] > 0:
        st.error(f"⚠️ Retirement shortfall of {format_currency(projections['shortfall'])}")
        st.write(f"Recommend increasing monthly savings by {format_currency(projections['additional_monthly_needed'])}")
    else:
        st.success(f"✅ On track with surplus of {format_currency(projections['surplus'])}")

def generate_detailed_analysis(results, profile):
    """Generate detailed analysis"""
    # This would include comprehensive charts and analysis
    st.write("Detailed analysis would include:")
    st.write("• Cash flow projections")
    st.write("• Tax impact analysis")
    st.write("• Risk assessment")
    st.write("• Asset allocation recommendations")
    st.write("• Estate planning considerations")

def generate_action_plan(results, profile):
    """Generate action plan"""
    projections = results['savings_projections']
    
    st.write("**Immediate Actions (Next 30 days):**")
    if projections['shortfall'] > 0:
        st.write("• Review monthly budget for additional savings opportunities")
        st.write("• Meet with HR to maximize employer 401(k) match")
        st.write("• Consider automatic contribution increases")
    
    st.write("**Medium-term Actions (Next 6 months):**")
    st.write("• Review and rebalance investment portfolio")
    st.write("• Research additional retirement account options")
    st.write("• Consider meeting with a financial advisor")
    
    st.write("**Long-term Actions (Next 12+ months):**")
    st.write("• Annual retirement plan review and updates")
    st.write("• Tax strategy optimization")
    st.write("• Estate planning review")

def generate_pdf_report(results, profile):
    """Generate PDF report"""
    st.info("PDF report generation would be implemented here using libraries like ReportLab")

def generate_excel_report(results, profile):
    """Generate Excel report"""
    st.info("Excel report generation would be implemented here using pandas and openpyxl")

def email_report_summary(results, profile):
    """Email report summary"""
    st.info("Email functionality would be implemented here using email services")

# Data management functions
def export_retirement_data(session, user_id):
    """Export retirement data"""
    st.info("Data export functionality would be implemented here")

def reset_calculation_history(session, profile_id):
    """Reset calculation history"""
    st.info("Reset functionality would be implemented here")

def delete_retirement_profile_data(session, user_id):
    """Delete retirement profile"""
    st.info("Delete functionality would be implemented here")