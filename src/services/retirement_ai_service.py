# Enhanced AI service for retirement planning
# Add this to your existing services/ai_service.py or create a new retirement_ai_service.py

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
from retirement_planner import RetirementProfile, RetirementCalculator, RetirementReportGenerator

class RetirementAIAdvisor:
    """AI-powered retirement planning advisor"""
    
    def __init__(self, ai_client=None):
        """
        Initialize with your existing AI client
        This could be OpenAI, Claude, or any other AI service
        """
        self.ai_client = ai_client
        self.context_template = self._build_context_template()
    
    def get_retirement_advice(self, 
                            profile: RetirementProfile,
                            calculation_results: Dict,
                            specific_question: str = None) -> str:
        """Get AI-powered retirement advice"""
        
        # Build context for the AI
        context = self._build_retirement_context(profile, calculation_results)
        
        # Create the prompt
        if specific_question:
            prompt = self._create_specific_question_prompt(context, specific_question)
        else:
            prompt = self._create_general_advice_prompt(context)
        
        # Get response from AI
        try:
            response = self._call_ai_service(prompt)
            return self._format_ai_response(response)
        except Exception as e:
            return f"I apologize, but I'm having trouble generating advice right now. Error: {str(e)}"
    
    def analyze_retirement_gaps(self, profile: RetirementProfile, calculation_results: Dict) -> Dict[str, str]:
        """Analyze retirement planning gaps and provide specific advice"""
        
        gaps_analysis = {
            "savings_gap": "",
            "investment_strategy": "",
            "tax_optimization": "",
            "risk_management": "",
            "lifestyle_planning": ""
        }
        
        # Analyze savings gap
        if calculation_results.get('shortfall', 0) > 0:
            shortfall = calculation_results['shortfall']
            additional_monthly = calculation_results.get('additional_monthly_needed', 0)
            
            gaps_analysis["savings_gap"] = self._get_ai_advice_for_gap(
                "savings_shortfall",
                {
                    "shortfall_amount": shortfall,
                    "additional_monthly_needed": additional_monthly,
                    "current_savings_rate": profile.monthly_contribution,
                    "income": profile.current_annual_income
                }
            )
        else:
            gaps_analysis["savings_gap"] = "✅ Your current savings rate appears to be on track for your retirement goals."
        
        # Analyze investment strategy
        gaps_analysis["investment_strategy"] = self._get_ai_advice_for_gap(
            "investment_strategy",
            {
                "pre_retirement_return": profile.pre_retirement_return_rate,
                "post_retirement_return": profile.post_retirement_return_rate,
                "current_age": profile.current_age,
                "retirement_age": profile.retirement_age
            }
        )
        
        # Add other analyses...
        return gaps_analysis
    
    def generate_personalized_scenarios(self, profile: RetirementProfile) -> List[Dict]:
        """Generate AI-suggested retirement scenarios"""
        
        scenarios = []
        
        # Conservative scenario
        conservative_profile = self._modify_profile_for_scenario(profile, {
            "pre_retirement_return_rate": profile.pre_retirement_return_rate - 0.02,
            "post_retirement_return_rate": profile.post_retirement_return_rate - 0.01,
            "inflation_rate": profile.inflation_rate + 0.01
        })
        
        scenarios.append({
            "name": "Conservative Scenario",
            "description": "Lower returns, higher inflation",
            "profile": conservative_profile,
            "ai_advice": self._get_scenario_advice("conservative", conservative_profile)
        })
        
        # Aggressive scenario
        aggressive_profile = self._modify_profile_for_scenario(profile, {
            "pre_retirement_return_rate": profile.pre_retirement_return_rate + 0.02,
            "monthly_contribution": profile.monthly_contribution * 1.5
        })
        
        scenarios.append({
            "name": "Aggressive Scenario", 
            "description": "Higher returns, increased savings",
            "profile": aggressive_profile,
            "ai_advice": self._get_scenario_advice("aggressive", aggressive_profile)
        })
        
        # Late starter scenario (if applicable)
        if profile.current_age > 40:
            late_starter_profile = self._modify_profile_for_scenario(profile, {
                "retirement_age": profile.retirement_age + 3,
                "monthly_contribution": profile.monthly_contribution * 2
            })
            
            scenarios.append({
                "name": "Catch-Up Scenario",
                "description": "Work longer, save more",
                "profile": late_starter_profile,
                "ai_advice": self._get_scenario_advice("catch_up", late_starter_profile)
            })
        
        return scenarios
    
    def get_market_context_advice(self, profile: RetirementProfile, market_data: Dict = None) -> str:
        """Get advice considering current market conditions"""
        
        # This would integrate with market data if available
        market_context = market_data or self._get_default_market_context()
        
        prompt = f"""
        Given the current market conditions and the following retirement profile,
        provide advice on how to adjust the retirement strategy:
        
        Market Context:
        {json.dumps(market_context, indent=2)}
        
        Retirement Profile:
        - Age: {profile.current_age}
        - Years to retirement: {profile.retirement_age - profile.current_age}
        - Current savings: ${profile.current_savings:,.2f}
        - Monthly contribution: ${profile.monthly_contribution:,.2f}
        
        Please provide specific, actionable advice considering the current market environment.
        """
        
        try:
            response = self._call_ai_service(prompt)
            return self._format_ai_response(response)
        except Exception as e:
            return "Unable to provide market-specific advice at this time."
    
    def _build_retirement_context(self, profile: RetirementProfile, calculation_results: Dict) -> str:
        """Build context string for AI prompts"""
        
        calculator = RetirementCalculator(profile)
        needs = calculator.calculate_retirement_needs()
        projections = calculator.calculate_savings_projection()
        
        context = f"""
        RETIREMENT PLANNING CONTEXT:
        
        Personal Information:
        - Current Age: {profile.current_age}
        - Retirement Age: {profile.retirement_age}
        - Years to Retirement: {needs['years_to_retirement']}
        - Life Expectancy: {profile.life_expectancy}
        
        Financial Situation:
        - Current Income: ${profile.current_annual_income:,.2f}
        - Current Savings: ${profile.current_savings:,.2f}
        - Monthly Contribution: ${profile.monthly_contribution:,.2f}
        - Effective Monthly Contribution: ${projections['effective_monthly_contribution']:,.2f}
        
        Goals:
        - Desired Retirement Income: {profile.desired_retirement_income_ratio*100:.0f}% of current income
        - Required Annual Income (today's $): ${needs['desired_annual_income_today']:,.2f}
        - Required Corpus: ${needs['total_corpus_needed']:,.2f}
        
        Projections:
        - Projected Total at Retirement: ${projections['total_projected_savings']:,.2f}
        - Gap: ${projections.get('shortfall', 0) - projections.get('surplus', 0):+,.2f}
        
        Investment Assumptions:
        - Pre-retirement return: {profile.pre_retirement_return_rate*100:.1f}%
        - Post-retirement return: {profile.post_retirement_return_rate*100:.1f}%
        - Inflation rate: {profile.inflation_rate*100:.1f}%
        """
        
        return context
    
    def _create_general_advice_prompt(self, context: str) -> str:
        """Create prompt for general retirement advice"""
        
        return f"""
        You are a knowledgeable financial advisor specializing in retirement planning.
        Based on the following retirement planning context, provide comprehensive,
        personalized advice to help improve this person's retirement outlook.
        
        {context}
        
        Please provide advice on:
        1. Current retirement readiness assessment
        2. Specific action items to improve the situation
        3. Investment strategy recommendations
        4. Risk management considerations
        5. Tax optimization opportunities
        6. Timeline and milestone recommendations
        
        Make your advice practical, specific, and actionable.
        Focus on the most impactful changes they can make.
        """
    
    def _create_specific_question_prompt(self, context: str, question: str) -> str:
        """Create prompt for specific retirement questions"""
        
        return f"""
        You are a knowledgeable financial advisor specializing in retirement planning.
        Based on the following retirement planning context, answer the specific question.
        
        {context}
        
        Question: {question}
        
        Please provide a detailed, practical answer that considers their specific situation.
        Include specific numbers and actionable steps where appropriate.
        """
    
    def _get_ai_advice_for_gap(self, gap_type: str, gap_data: Dict) -> str:
        """Get AI advice for specific gaps"""
        
        prompts = {
            "savings_shortfall": f"""
            This person has a retirement savings shortfall of ${gap_data['shortfall_amount']:,.2f}.
            They need an additional ${gap_data['additional_monthly_needed']:,.2f} per month.
            Current monthly savings: ${gap_data['current_savings_rate']:,.2f}
            Annual income: ${gap_data['income']:,.2f}
            
            Provide specific strategies to close this gap, considering their income level.
            """,
            
            "investment_strategy": f"""
            Investment assumptions:
            - Pre-retirement expected return: {gap_data['pre_retirement_return']*100:.1f}%
            - Post-retirement expected return: {gap_data['post_retirement_return']*100:.1f}%
            - Current age: {gap_data['current_age']}
            - Retirement age: {gap_data['retirement_age']}
            
            Provide investment strategy recommendations considering their age and time horizon.
            """
        }
        
        prompt = prompts.get(gap_type, "Provide general retirement planning advice.")
        
        try:
            response = self._call_ai_service(prompt)
            return self._format_ai_response(response)
        except:
            return "Unable to generate specific advice for this area at this time."
    
    def _get_scenario_advice(self, scenario_type: str, profile: RetirementProfile) -> str:
        """Get AI advice for specific scenarios"""
        
        scenario_prompts = {
            "conservative": """
            This is a conservative retirement scenario with lower expected returns and higher inflation.
            Provide advice on how to prepare for this scenario and mitigate risks.
            """,
            
            "aggressive": """
            This is an aggressive retirement scenario with higher expected returns and increased savings.
            Provide advice on implementing this strategy and managing the associated risks.
            """,
            
            "catch_up": """
            This is a catch-up scenario for someone who may be behind on retirement savings.
            Provide advice on accelerated savings strategies and catch-up contributions.
            """
        }
        
        base_prompt = scenario_prompts.get(scenario_type, "Provide scenario-specific advice.")
        full_prompt = f"{base_prompt}\n\nProfile: Age {profile.current_age}, retiring at {profile.retirement_age}, ${profile.monthly_contribution:,.2f}/month savings."
        
        try:
            response = self._call_ai_service(full_prompt)
            return self._format_ai_response(response)
        except:
            return "Unable to generate scenario-specific advice."
    
    def _modify_profile_for_scenario(self, profile: RetirementProfile, modifications: Dict) -> RetirementProfile:
        """Create a modified profile for scenario analysis"""
        
        # Convert profile to dict, apply modifications, create new profile
        profile_dict = asdict(profile)
        profile_dict.update(modifications)
        return RetirementProfile(**profile_dict)
    
    def _get_default_market_context(self) -> Dict:
        """Get default market context when real data isn't available"""
        
        return {
            "market_environment": "moderate_volatility",
            "interest_rates": "rising",
            "inflation_trend": "elevated",
            "recommendation": "Stay diversified, consider I-bonds for inflation protection"
        }
    
    def _build_context_template(self) -> str:
        """Build template for AI context"""
        
        return """
        You are a certified financial planner with 20+ years of experience in retirement planning.
        Your advice should be:
        - Practical and actionable
        - Based on established financial planning principles
        - Tailored to the individual's specific situation
        - Include specific dollar amounts and percentages when relevant
        - Consider tax implications
        - Address risk management
        - Be encouraging but realistic
        
        Always remind users that this is general advice and they should consult with a qualified financial advisor for personalized guidance.
        """
    
    def _call_ai_service(self, prompt: str) -> str:
        """Call the AI service with the given prompt"""
        
        # This is where you'd integrate with your existing AI service
        # Example implementations for different services:
        
        if hasattr(self.ai_client, 'create_completion'):
            # OpenAI-style API
            response = self.ai_client.create_completion(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.context_template},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        elif hasattr(self.ai_client, 'complete'):
            # Claude-style API
            response = self.ai_client.complete(
                prompt=f"{self.context_template}\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens=1000
            )
            return response.completion
        
        else:
            # Fallback for testing or if no AI client is available
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Provide fallback responses when AI service is unavailable"""
        
        if "shortfall" in prompt.lower():
            return """
            Based on your retirement gap, consider these strategies:
            1. Increase your monthly contributions gradually
            2. Take advantage of employer matching if available
            3. Consider catch-up contributions if you're over 50
            4. Review your investment allocation for appropriate risk level
            5. Consider working 1-2 additional years if feasible
            
            Remember to consult with a qualified financial advisor for personalized advice.
            """
        
        return """
        Your retirement planning looks like it needs attention. Consider reviewing:
        1. Your current savings rate
        2. Investment allocation
        3. Expected retirement timeline
        4. Income replacement goals
        
        Please consult with a qualified financial advisor for personalized guidance.
        """
    
    def _format_ai_response(self, response: str) -> str:
        """Format the AI response for display"""
        
        # Clean up the response
        formatted_response = response.strip()
        
        # Add disclaimer if not already present
        if "financial advisor" not in formatted_response.lower():
            formatted_response += "\n\n⚠️ This is general advice. Please consult with a qualified financial advisor for personalized guidance."
        
        return formatted_response

class RetirementChatBot:
    """Interactive chatbot for retirement planning questions"""
    
    def __init__(self, ai_advisor: RetirementAIAdvisor, profile: RetirementProfile = None):
        self.ai_advisor = ai_advisor
        self.profile = profile
        self.conversation_history = []
    
    def ask_question(self, question: str) -> str:
        """Ask a retirement planning question"""
        
        if not self.profile:
            return "Please set up your retirement profile first before asking questions."
        
        # Calculate current results for context
        calculator = RetirementCalculator(self.profile)
        needs = calculator.calculate_retirement_needs()
        projections = calculator.calculate_savings_projection()
        
        calculation_results = {
            "needs": needs,
            "projections": projections
        }
        
        # Get AI response
        response = self.ai_advisor.get_retirement_advice(
            self.profile, 
            calculation_results, 
            question
        )
        
        # Store in conversation history
        self.conversation_history.append({
            "question": question,
            "response": response,
            "timestamp": pd.Timestamp.now()
        })
        
        return response
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        
        if not self.conversation_history:
            return "No questions asked yet."
        
        summary = "Conversation Summary:\n\n"
        for i, item in enumerate(self.conversation_history[-5:], 1):  # Last 5 questions
            summary += f"{i}. Q: {item['question'][:50]}...\n"
            summary += f"   A: {item['response'][:100]}...\n\n"
        
        return summary
    
    def update_profile(self, new_profile: RetirementProfile):
        """Update the retirement profile"""
        self.profile = new_profile
        self.conversation_history.append({
            "question": "Profile updated",
            "response": "Retirement profile has been updated. Feel free to ask new questions!",
            "timestamp": pd.Timestamp.now()
        })

# Integration functions for your existing application

def integrate_ai_advisor_with_streamlit(profile: RetirementProfile, ai_client=None):
    """Integration function for Streamlit app"""
    
    # Initialize AI advisor
    ai_advisor = RetirementAIAdvisor(ai_client)
    
    # Get current calculations
    calculator = RetirementCalculator(profile)
    needs = calculator.calculate_retirement_needs()
    projections = calculator.calculate_savings_projection()
    
    calculation_results = {
        "needs": needs,
        "projections": projections,
        "shortfall": projections.get('shortfall', 0),
        "surplus": projections.get('surplus', 0),
        "additional_monthly_needed": projections.get('additional_monthly_needed', 0)
    }
    
    # Streamlit interface
    st.subheader("🤖 AI Retirement Advisor")
    
    # Tabs for different types of advice
    advice_tab1, advice_tab2, advice_tab3 = st.tabs(["General Advice", "Ask Question", "Scenarios"])
    
    with advice_tab1:
        if st.button("Get General Retirement Advice"):
            with st.spinner("Analyzing your retirement plan..."):
                advice = ai_advisor.get_retirement_advice(profile, calculation_results)
                st.write(advice)
    
    with advice_tab2:
        question = st.text_area("Ask a specific retirement planning question:")
        if st.button("Get Answer") and question:
            with st.spinner("Getting personalized advice..."):
                answer = ai_advisor.get_retirement_advice(profile, calculation_results, question)
                st.write("**Answer:**")
                st.write(answer)
    
    with advice_tab3:
        if st.button("Generate Scenario Analysis"):
            with st.spinner("Generating scenarios..."):
                scenarios = ai_advisor.generate_personalized_scenarios(profile)
                
                for scenario in scenarios:
                    with st.expander(scenario['name']):
                        st.write(f"**Description:** {scenario['description']}")
                        st.write(f"**AI Advice:** {scenario['ai_advice']}")

def create_retirement_ai_page():
    """Create a dedicated AI advisor page"""
    
    st.title("🤖 AI Retirement Planning Assistant")
    
    # Check if user has a profile
    if 'retirement_profile' not in st.session_state:
        st.warning("Please complete your retirement profile first.")
        return
    
    profile = st.session_state.retirement_profile
    
    # Initialize chatbot
    if 'retirement_chatbot' not in st.session_state:
        ai_advisor = RetirementAIAdvisor()
        st.session_state.retirement_chatbot = RetirementChatBot(ai_advisor, profile)
    
    chatbot = st.session_state.retirement_chatbot
    
    # Chat interface
    st.subheader("Ask Me Anything About Your Retirement Plan")
    
    # Display conversation history
    if chatbot.conversation_history:
        st.write("**Previous Questions:**")
        for item in chatbot.conversation_history[-3:]:  # Show last 3
            with st.expander(f"Q: {item['question'][:50]}..."):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['response']}")
    
    # New question input
    new_question = st.text_input("Your question:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ask Question") and new_question:
            with st.spinner("Thinking..."):
                answer = chatbot.ask_question(new_question)
                st.write("**Answer:**")
                st.write(answer)
    
    with col2:
        if st.button("Clear History"):
            st.session_state.retirement_chatbot.conversation_history = []
            st.success("Conversation history cleared!")

# Example usage
if __name__ == "__main__":
    # Example of how to use the retirement AI advisor
    
    # Create a sample profile
    profile = RetirementProfile(
        current_age=35,
        retirement_age=65,
        life_expectancy=85,
        current_annual_income=75000,
        desired_retirement_income_ratio=0.8,
        current_savings=50000,
        monthly_contribution=800,
        employer_match_rate=0.5,
        employer_match_limit=0.06,
        pre_retirement_return_rate=0.07,
        post_retirement_return_rate=0.05,
        inflation_rate=0.03
    )
    
    # Initialize AI advisor (without actual AI client for testing)
    ai_advisor = RetirementAIAdvisor()
    
    # Get advice
    calculator = RetirementCalculator(profile)
    needs = calculator.calculate_retirement_needs()
    projections = calculator.calculate_savings_projection()
    
    calculation_results = {"needs": needs, "projections": projections}
    
    advice = ai_advisor.get_retirement_advice(profile, calculation_results)
    print("General Advice:")
    print(advice)
    
    # Ask specific question
    specific_advice = ai_advisor.get_retirement_advice(
        profile, 
        calculation_results, 
        "Should I prioritize paying off my mortgage or increasing my 401k contributions?"
    )
    print("\nSpecific Question Answer:")
    print(specific_advice)