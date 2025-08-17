import math
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from database.models import RetirementProfile, RetirementCalculation
from database.db_utils import save_retirement_calculation, get_retirement_profile

@dataclass
class RetirementInputs:
    """Retirement planning input parameters"""
    current_age: int
    retirement_age: int
    life_expectancy: int
    current_annual_income: float
    desired_retirement_income_ratio: float
    current_savings: float
    monthly_contribution: float
    employer_match_rate: float
    employer_match_limit: float
    pre_retirement_return_rate: float
    post_retirement_return_rate: float
    inflation_rate: float
    estimated_social_security: float = 0.0
    estimated_healthcare_costs: float = 0.0
    estimated_pension: float = 0.0

class RetirementCalculationEngine:
    """Core retirement calculation engine"""
    
    def __init__(self, inputs: RetirementInputs):
        self.inputs = inputs
        self.results = {}
    
    def calculate_comprehensive_plan(self) -> Dict:
        """Calculate comprehensive retirement plan"""
        
        # Basic calculations
        needs = self.calculate_retirement_needs()
        projections = self.calculate_savings_projections()
        strategies = self.analyze_withdrawal_strategies()
        
        # Advanced calculations
        sensitivity = self.perform_sensitivity_analysis()
        monte_carlo = self.run_monte_carlo_simulation()
        tax_analysis = self.analyze_tax_implications()
        
        # Yearly projections
        yearly_data = self.generate_yearly_projections()
        
        self.results = {
            'retirement_needs': needs,
            'savings_projections': projections,
            'withdrawal_strategies': strategies,
            'sensitivity_analysis': sensitivity,
            'monte_carlo_results': monte_carlo,
            'tax_analysis': tax_analysis,
            'yearly_projections': yearly_data,
            'calculation_date': datetime.utcnow(),
            'input_parameters': self.inputs.__dict__
        }
        
        return self.results
    
    def calculate_retirement_needs(self) -> Dict:
        """Calculate total retirement corpus needed"""
        
        years_to_retirement = self.inputs.retirement_age - self.inputs.current_age
        retirement_years = self.inputs.life_expectancy - self.inputs.retirement_age
        
        # Calculate desired annual income in today's dollars
        desired_income = self.inputs.current_annual_income * self.inputs.desired_retirement_income_ratio
        
        # Subtract other income sources
        net_income_needed = desired_income - self.inputs.estimated_social_security - self.inputs.estimated_pension
        net_income_needed = max(net_income_needed, 0)
        
        # Add healthcare costs
        total_annual_need = net_income_needed + self.inputs.estimated_healthcare_costs
        
        # Adjust for inflation at retirement
        inflation_factor = (1 + self.inputs.inflation_rate) ** years_to_retirement
        future_annual_need = total_annual_need * inflation_factor
        
        # Calculate present value of retirement corpus needed
        real_return_rate = self.inputs.post_retirement_return_rate - self.inputs.inflation_rate
        
        if real_return_rate <= 0:
            # If no real return, simple multiplication
            retirement_corpus = future_annual_need * retirement_years
        else:
            # Present value of annuity formula
            pv_factor = (1 - (1 + real_return_rate) ** -retirement_years) / real_return_rate
            retirement_corpus = future_annual_need * pv_factor
        
        return {
            'desired_annual_income_today': desired_income,
            'net_income_needed': net_income_needed,
            'total_annual_need_today': total_annual_need,
            'future_annual_need': future_annual_need,
            'retirement_corpus_needed': retirement_corpus,
            'years_to_retirement': years_to_retirement,
            'retirement_years': retirement_years,
            'inflation_factor': inflation_factor
        }
    
    def calculate_savings_projections(self) -> Dict:
        """Project savings growth until retirement"""
        
        years_to_retirement = self.inputs.retirement_age - self.inputs.current_age
        
        # Current savings future value
        current_savings_fv = self.inputs.current_savings * \
            (1 + self.inputs.pre_retirement_return_rate) ** years_to_retirement
        
        # Calculate effective monthly contribution with employer match
        effective_monthly = self._calculate_effective_monthly_contribution()
        
        # Future value of monthly contributions (annuity)
        annual_contribution = effective_monthly * 12
        if self.inputs.pre_retirement_return_rate == 0:
            contributions_fv = annual_contribution * years_to_retirement
        else:
            contributions_fv = annual_contribution * \
                (((1 + self.inputs.pre_retirement_return_rate) ** years_to_retirement - 1) / 
                 self.inputs.pre_retirement_return_rate)
        
        total_projected = current_savings_fv + contributions_fv
        
        # Calculate gap
        needs = self.calculate_retirement_needs()
        corpus_needed = needs['retirement_corpus_needed']
        gap = corpus_needed - total_projected
        
        # Additional monthly savings needed
        additional_monthly = 0
        if gap > 0 and years_to_retirement > 0:
            if self.inputs.pre_retirement_return_rate == 0:
                additional_monthly = gap / (years_to_retirement * 12)
            else:
                monthly_rate = self.inputs.pre_retirement_return_rate / 12
                months = years_to_retirement * 12
                additional_monthly = gap * monthly_rate / \
                    ((1 + monthly_rate) ** months - 1)
        
        return {
            'current_savings_future_value': current_savings_fv,
            'contributions_future_value': contributions_fv,
            'total_projected_savings': total_projected,
            'corpus_needed': corpus_needed,
            'shortfall': max(gap, 0),
            'surplus': max(-gap, 0),
            'additional_monthly_needed': additional_monthly,
            'effective_monthly_contribution': effective_monthly,
            'savings_rate_percentage': (effective_monthly * 12 / self.inputs.current_annual_income) * 100
        }
    
    def analyze_withdrawal_strategies(self) -> Dict:
        """Analyze different withdrawal strategies"""
        
        needs = self.calculate_retirement_needs()
        corpus = needs['retirement_corpus_needed']
        retirement_years = needs['retirement_years']
        
        strategies = {}
        
        # 4% Rule
        strategies['four_percent_rule'] = {
            'name': '4% Rule',
            'description': 'Withdraw 4% of initial portfolio annually',
            'initial_withdrawal': corpus * 0.04,
            'pros': ['Simple to implement', 'Historically successful', 'Widely accepted'],
            'cons': ['May not adapt to market volatility', 'Fixed percentage'],
            'success_rate': 95,  # Historical success rate
            'sustainability_years': 30
        }
        
        # Dynamic Withdrawal (3-5% based on portfolio)
        strategies['dynamic_withdrawal'] = {
            'name': 'Dynamic Withdrawal',
            'description': 'Adjust withdrawal based on portfolio performance',
            'initial_withdrawal_rate': 0.04,
            'adjustment_mechanism': 'Portfolio performance based',
            'pros': ['Adapts to market conditions', 'Can extend portfolio life'],
            'cons': ['Variable income', 'More complex'],
            'success_rate': 98
        }
        
        # Bond Ladder
        bond_ladder_corpus = corpus * 1.1  # Slightly higher for safety
        strategies['bond_ladder'] = {
            'name': 'Bond Ladder',
            'description': 'Match bond maturities to yearly expenses',
            'required_corpus': bond_ladder_corpus,
            'annual_income': needs['future_annual_need'],
            'pros': ['Very predictable income', 'Low volatility risk'],
            'cons': ['Lower returns', 'Inflation risk', 'Higher corpus needed'],
            'success_rate': 90
        }
        
        # Bucket Strategy
        strategies['bucket_strategy'] = {
            'name': 'Bucket Strategy',
            'description': 'Divide portfolio into short, medium, and long-term buckets',
            'bucket_allocation': {
                'short_term': {'percentage': 20, 'years': 5, 'investments': 'Cash, CDs'},
                'medium_term': {'percentage': 30, 'years': 10, 'investments': 'Bonds, Conservative funds'},
                'long_term': {'percentage': 50, 'years': 20, 'investments': 'Stocks, Growth funds'}
            },
            'pros': ['Balanced approach', 'Reduces sequence risk', 'Maintains growth'],
            'cons': ['Complex management', 'Rebalancing required'],
            'success_rate': 92
        }
        
        return strategies
    
    def perform_sensitivity_analysis(self) -> Dict:
        """Perform sensitivity analysis on key variables"""
        
        base_projections = self.calculate_savings_projections()
        base_corpus_needed = base_projections['corpus_needed']
        base_projected = base_projections['total_projected_savings']
        
        sensitivity_results = {}
        
        # Variables to test
        variables = {
            'pre_retirement_return_rate': [-0.02, -0.01, 0, 0.01, 0.02],
            'inflation_rate': [-0.01, -0.005, 0, 0.005, 0.01],
            'retirement_age': [-5, -2, 0, 2, 5],
            'monthly_contribution': [-200, -100, 0, 100, 200]
        }
        
        for variable, changes in variables.items():
            variable_results = []
            
            for change in changes:
                # Create modified inputs
                modified_inputs = RetirementInputs(**self.inputs.__dict__)
                
                if variable == 'retirement_age':
                    modified_inputs.retirement_age = max(50, self.inputs.retirement_age + change)
                elif variable == 'monthly_contribution':
                    modified_inputs.monthly_contribution = max(0, self.inputs.monthly_contribution + change)
                else:
                    current_value = getattr(modified_inputs, variable)
                    setattr(modified_inputs, variable, current_value + change)
                
                # Calculate with modified inputs
                temp_engine = RetirementCalculationEngine(modified_inputs)
                temp_projections = temp_engine.calculate_savings_projections()
                
                variable_results.append({
                    'change': change,
                    'total_projected': temp_projections['total_projected_savings'],
                    'gap_change': (temp_projections['total_projected_savings'] - base_projected),
                    'percentage_change': ((temp_projections['total_projected_savings'] / base_projected - 1) * 100) if base_projected > 0 else 0
                })
            
            sensitivity_results[variable] = variable_results
        
        return sensitivity_results
    
    def run_monte_carlo_simulation(self, num_simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation for retirement success probability"""
        
        years_to_retirement = self.inputs.retirement_age - self.inputs.current_age
        retirement_years = self.inputs.life_expectancy - self.inputs.retirement_age
        
        if years_to_retirement <= 0 or retirement_years <= 0:
            return {'success_rate': 0, 'error': 'Invalid time parameters'}
        
        successful_scenarios = 0
        final_balances = []
        
        # Monte Carlo parameters
        return_std = 0.15  # Standard deviation of returns
        inflation_std = 0.02  # Standard deviation of inflation
        
        np.random.seed(42)  # For reproducible results
        
        for _ in range(num_simulations):
            # Generate random return sequences
            accumulation_returns = np.random.normal(
                self.inputs.pre_retirement_return_rate, 
                return_std, 
                years_to_retirement
            )
            
            withdrawal_returns = np.random.normal(
                self.inputs.post_retirement_return_rate,
                return_std,
                retirement_years
            )
            
            inflation_rates = np.random.normal(
                self.inputs.inflation_rate,
                inflation_std,
                years_to_retirement + retirement_years
            )
            
            # Simulate accumulation phase
            balance = self.inputs.current_savings
            effective_monthly = self._calculate_effective_monthly_contribution()
            annual_contribution = effective_monthly * 12
            
            for year, annual_return in enumerate(accumulation_returns):
                balance = balance * (1 + annual_return) + annual_contribution
                # Adjust contribution for inflation
                annual_contribution *= (1 + inflation_rates[year])
            
            # Simulate withdrawal phase
            needs = self.calculate_retirement_needs()
            annual_withdrawal = needs['future_annual_need']
            
            portfolio_survived = True
            
            for year, annual_return in enumerate(withdrawal_returns):
                # Adjust withdrawal for inflation during retirement
                inflation_adjusted_withdrawal = annual_withdrawal * \
                    (1 + inflation_rates[years_to_retirement + year]) ** year
                
                balance = balance * (1 + annual_return) - inflation_adjusted_withdrawal
                
                if balance <= 0:
                    portfolio_survived = False
                    break
            
            if portfolio_survived and balance > 0:
                successful_scenarios += 1
            
            final_balances.append(max(balance, 0))
        
        success_rate = (successful_scenarios / num_simulations) * 100
        
        return {
            'success_rate': success_rate,
            'num_simulations': num_simulations,
            'average_final_balance': np.mean(final_balances),
            'median_final_balance': np.median(final_balances),
            'percentile_10': np.percentile(final_balances, 10),
            'percentile_90': np.percentile(final_balances, 90),
            'scenarios_succeeded': successful_scenarios,
            'risk_assessment': self._assess_risk_level(success_rate)
        }
    
    def analyze_tax_implications(self) -> Dict:
        """Analyze tax implications of retirement planning"""
        
        # Simplified tax analysis - in reality, this would be much more complex
        current_income = self.inputs.current_annual_income
        retirement_income = current_income * self.inputs.desired_retirement_income_ratio
        
        # Estimate current tax bracket (simplified)
        current_tax_rate = self._estimate_tax_rate(current_income)
        retirement_tax_rate = self._estimate_tax_rate(retirement_income)
        
        # Annual contributions tax savings
        effective_monthly = self._calculate_effective_monthly_contribution()
        annual_contribution = effective_monthly * 12
        current_tax_savings = annual_contribution * current_tax_rate
        
        # Retirement tax burden
        taxable_retirement_income = retirement_income - self.inputs.estimated_social_security * 0.85  # Assume 85% of SS is taxable
        annual_retirement_taxes = taxable_retirement_income * retirement_tax_rate
        
        return {
            'current_tax_rate': current_tax_rate,
            'retirement_tax_rate': retirement_tax_rate,
            'annual_contribution_tax_savings': current_tax_savings,
            'annual_retirement_tax_burden': annual_retirement_taxes,
            'tax_rate_difference': retirement_tax_rate - current_tax_rate,
            'recommendations': self._get_tax_recommendations(current_tax_rate, retirement_tax_rate)
        }
    
    def generate_yearly_projections(self) -> List[Dict]:
        """Generate detailed year-by-year projections"""
        
        projections = []
        current_age = self.inputs.current_age
        balance = self.inputs.current_savings
        effective_monthly = self._calculate_effective_monthly_contribution()
        annual_contribution = effective_monthly * 12
        
        needs = self.calculate_retirement_needs()
        
        while current_age <= self.inputs.life_expectancy:
            year_data = {
                'age': current_age,
                'year': datetime.now().year + (current_age - self.inputs.current_age),
                'balance': balance
            }
            
            if current_age < self.inputs.retirement_age:
                # Accumulation phase
                investment_return = balance * self.inputs.pre_retirement_return_rate
                balance += investment_return + annual_contribution
                
                year_data.update({
                    'phase': 'accumulation',
                    'contribution': annual_contribution,
                    'investment_return': investment_return,
                    'withdrawal': 0,
                    'net_change': investment_return + annual_contribution
                })
                
                # Adjust contribution for inflation
                annual_contribution *= (1 + self.inputs.inflation_rate)
                
            else:
                # Withdrawal phase
                years_since_retirement = current_age - self.inputs.retirement_age
                annual_withdrawal = needs['future_annual_need'] * \
                    (1 + self.inputs.inflation_rate) ** years_since_retirement
                
                investment_return = balance * self.inputs.post_retirement_return_rate
                balance = max(0, balance + investment_return - annual_withdrawal)
                
                year_data.update({
                    'phase': 'withdrawal',
                    'contribution': 0,
                    'investment_return': investment_return,
                    'withdrawal': annual_withdrawal,
                    'net_change': investment_return - annual_withdrawal
                })
            
            projections.append(year_data)
            current_age += 1
            
            # Stop if balance reaches zero
            if balance <= 0:
                break
        
        return projections
    
    def _calculate_effective_monthly_contribution(self) -> float:
        """Calculate effective monthly contribution including employer match"""
        
        annual_salary = self.inputs.current_annual_income
        monthly_contribution = self.inputs.monthly_contribution
        annual_contribution = monthly_contribution * 12
        
        # Calculate contribution rate
        contribution_rate = annual_contribution / annual_salary if annual_salary > 0 else 0
        
        # Employer match is limited by match rate and salary limit
        match_rate = min(contribution_rate, self.inputs.employer_match_limit)
        employer_match_annual = annual_salary * match_rate * self.inputs.employer_match_rate
        
        total_annual = annual_contribution + employer_match_annual
        return total_annual / 12
    
    def _estimate_tax_rate(self, income: float) -> float:
        """Estimate tax rate based on income (simplified)"""
        
        # Simplified tax brackets (2024 single filer)
        if income <= 11000:
            return 0.10
        elif income <= 44725:
            return 0.12
        elif income <= 95375:
            return 0.22
        elif income <= 182050:
            return 0.24
        elif income <= 231250:
            return 0.32
        elif income <= 578125:
            return 0.35
        else:
            return 0.37
    
    def _get_tax_recommendations(self, current_rate: float, retirement_rate: float) -> List[str]:
        """Get tax optimization recommendations"""
        
        recommendations = []
        
        if current_rate > retirement_rate:
            recommendations.extend([
                "Consider maximizing traditional 401(k) contributions to reduce current taxes",
                "Traditional IRA contributions may provide tax deductions",
                "Consider tax-deferred investment strategies"
            ])
        elif retirement_rate > current_rate:
            recommendations.extend([
                "Consider Roth 401(k) contributions to pay taxes now at lower rate",
                "Roth IRA conversions may be beneficial",
                "Mix of traditional and Roth accounts provides tax flexibility"
            ])
        else:
            recommendations.extend([
                "Consider a balanced approach with both traditional and Roth accounts",
                "Tax diversification provides flexibility in retirement"
            ])
        
        # Universal recommendations
        recommendations.extend([
            "Maximize employer matching contributions",
            "Consider HSA contributions for triple tax advantage",
            "Review tax-loss harvesting opportunities in taxable accounts"
        ])
        
        return recommendations
    
    def _assess_risk_level(self, success_rate: float) -> str:
        """Assess risk level based on success rate"""
        
        if success_rate >= 90:
            return 'low'
        elif success_rate >= 75:
            return 'medium'
        elif success_rate >= 60:
            return 'high'
        else:
            return 'very_high'

class RetirementGoalTracker:
    """Track progress toward retirement goals"""
    
    def __init__(self, session: Session, user_id: str):
        self.session = session
        self.user_id = user_id
    
    def create_milestone_goals(self, profile: RetirementProfile) -> List[Dict]:
        """Create age-based milestone goals"""
        
        current_age = profile.current_age
        retirement_age = profile.retirement_age
        annual_income = profile.current_annual_income
        
        milestones = []
        
        # Age-based savings milestones (common financial planning rules)
        milestone_ages = [30, 35, 40, 45, 50, 55, 60, retirement_age]
        multipliers = [1, 2, 3, 4, 6, 7, 8, 10]  # Times annual salary
        
        for age, multiplier in zip(milestone_ages, multipliers):
            if age > current_age and age <= retirement_age:
                target_amount = annual_income * multiplier
                years_to_goal = age - current_age
                
                milestones.append({
                    'goal_name': f"Age {age} Milestone",
                    'description': f"Have {multiplier}x annual salary saved by age {age}",
                    'target_amount': target_amount,
                    'target_age': age,
                    'years_to_goal': years_to_goal,
                    'priority': 1 if years_to_goal <= 5 else 2,
                    'goal_type': 'milestone'
                })
        
        # Final retirement goal
        engine = RetirementCalculationEngine(RetirementInputs(**profile.__dict__))
        needs = engine.calculate_retirement_needs()
        
        milestones.append({
            'goal_name': 'Retirement Corpus',
            'description': f"Total savings needed for retirement at age {retirement_age}",
            'target_amount': needs['retirement_corpus_needed'],
            'target_age': retirement_age,
            'years_to_goal': retirement_age - current_age,
            'priority': 1,
            'goal_type': 'final_corpus'
        })
        
        return milestones
    
    def calculate_goal_feasibility(self, goal_amount: float, years_to_goal: int, 
                                 current_savings: float, monthly_contribution: float) -> Dict:
        """Calculate if a goal is feasible with current savings rate"""
        
        if years_to_goal <= 0:
            return {'feasible': False, 'reason': 'No time remaining'}
        
        # Assume 7% annual return
        annual_return = 0.07
        
        # Future value of current savings
        current_fv = current_savings * (1 + annual_return) ** years_to_goal
        
        # Future value of monthly contributions
        annual_contribution = monthly_contribution * 12
        if annual_return == 0:
            contributions_fv = annual_contribution * years_to_goal
        else:
            contributions_fv = annual_contribution * \
                (((1 + annual_return) ** years_to_goal - 1) / annual_return)
        
        total_projected = current_fv + contributions_fv
        
        feasible = total_projected >= goal_amount
        gap = goal_amount - total_projected
        
        # Calculate additional monthly needed
        additional_monthly = 0
        if gap > 0:
            if annual_return == 0:
                additional_monthly = gap / (years_to_goal * 12)
            else:
                monthly_rate = annual_return / 12
                months = years_to_goal * 12
                additional_monthly = gap * monthly_rate / \
                    ((1 + monthly_rate) ** months - 1)
        
        return {
            'feasible': feasible,
            'projected_amount': total_projected,
            'gap': max(gap, 0),
            'additional_monthly_needed': additional_monthly,
            'success_probability': min(total_projected / goal_amount * 100, 100) if goal_amount > 0 else 100
        }

# Service functions for integration
def calculate_retirement_plan(session: Session, user_id: str) -> Dict:
    """Calculate comprehensive retirement plan for user"""
    
    profile = get_retirement_profile(session, user_id)
    if not profile:
        return {'error': 'No retirement profile found'}
    
    # Convert profile to inputs
    inputs = RetirementInputs(
        current_age=profile.current_age,
        retirement_age=profile.retirement_age,
        life_expectancy=profile.life_expectancy,
        current_annual_income=profile.current_annual_income,
        desired_retirement_income_ratio=profile.desired_retirement_income_ratio,
        current_savings=profile.current_savings,
        monthly_contribution=profile.monthly_contribution,
        employer_match_rate=profile.employer_match_rate,
        employer_match_limit=profile.employer_match_limit,
        pre_retirement_return_rate=profile.pre_retirement_return_rate,
        post_retirement_return_rate=profile.post_retirement_return_rate,
        inflation_rate=profile.inflation_rate,
        estimated_social_security=profile.estimated_social_security,
        estimated_healthcare_costs=profile.estimated_healthcare_costs,
        estimated_pension=profile.estimated_pension
    )
    
    # Calculate comprehensive plan
    engine = RetirementCalculationEngine(inputs)
    results = engine.calculate_comprehensive_plan()
    
    # Save calculation to database
    save_retirement_calculation(session, profile.id, results)
    
    return results

def calculate_retirement_score(session: Session, user_id: str) -> int:
    """Calculate retirement readiness score (0-100)"""
    
    profile = get_retirement_profile(session, user_id)
    if not profile:
        return 0
    
    try:
        inputs = RetirementInputs(**profile.__dict__)
        engine = RetirementCalculationEngine(inputs)
        
        # Get basic calculations
        needs = engine.calculate_retirement_needs()
        projections = engine.calculate_savings_projections()
        monte_carlo = engine.run_monte_carlo_simulation()
        
        # Score components (total 100 points)
        
        # 1. Time to retirement (20 points)
        years_to_retirement = needs['years_to_retirement']
        time_score = min((years_to_retirement / 30) * 20, 20)
        
        # 2. Savings rate (25 points)
        savings_rate = projections['savings_rate_percentage']
        savings_score = min((savings_rate / 15) * 25, 25)
        
        # 3. Current progress (25 points)
        if needs['retirement_corpus_needed'] > 0:
            progress_ratio = projections['total_projected_savings'] / needs['retirement_corpus_needed']
            progress_score = min(progress_ratio * 25, 25)
        else:
            progress_score = 25
        
        # 4. Monte Carlo success rate (20 points)
        mc_score = (monte_carlo['success_rate'] / 100) * 20
        
        # 5. Diversification and employer match (10 points)
        match_score = 10 if profile.employer_match_rate > 0 else 5
        
        total_score = time_score + savings_score + progress_score + mc_score + match_score
        
        return min(int(total_score), 100)
        
    except Exception as e:
        print(f"Error calculating retirement score: {e}")
        return 0

def generate_retirement_recommendations(session: Session, user_id: str) -> List[Dict]:
    """Generate personalized retirement recommendations"""
    
    profile = get_retirement_profile(session, user_id)
    if not profile:
        return []
    
    try:
        results = calculate_retirement_plan(session, user_id)
        projections = results['savings_projections']
        monte_carlo = results['monte_carlo_results']
        
        recommendations = []
        
        # Shortfall recommendations
        if projections['shortfall'] > 0:
            recommendations.append({
                'type': 'critical',
                'title': 'Increase Retirement Savings',
                'description': f"You have a ${projections['shortfall']:,.0f} retirement shortfall. Consider increasing monthly contributions by ${projections['additional_monthly_needed']:,.0f}.",
                'action_items': [
                    f"Increase monthly contribution by ${projections['additional_monthly_needed']:,.0f}",
                    "Review budget for potential savings opportunities",
                    "Consider working 1-2 additional years if feasible"
                ],
                'priority': 1
            })
        
        # Low success rate recommendations
        if monte_carlo['success_rate'] < 75:
            recommendations.append({
                'type': 'high',
                'title': 'Improve Retirement Success Probability',
                'description': f"Your retirement plan has a {monte_carlo['success_rate']:.1f}% success rate. Consider risk reduction strategies.",
                'action_items': [
                    "Increase savings rate",
                    "Consider more conservative withdrawal rate",
                    "Diversify investment portfolio",
                    "Plan for part-time work in early retirement"
                ],
                'priority': 2
            })
        
        # Employer match recommendations
        if profile.employer_match_rate > 0:
            max_match = profile.current_annual_income * profile.employer_match_limit * profile.employer_match_rate
            current_match = min(profile.monthly_contribution * 12, profile.current_annual_income * profile.employer_match_limit) * profile.employer_match_rate
            
            if current_match < max_match:
                recommendations.append({
                    'type': 'medium',
                    'title': 'Maximize Employer Match',
                    'description': f"You're missing ${max_match - current_match:,.0f} in free employer matching.",
                    'action_items': [
                        f"Increase 401(k) contribution to at least {profile.employer_match_limit*100:.0f}% of salary",
                        "This is free money from your employer"
                    ],
                    'priority': 1
                })
        
        # Age-based recommendations
        if profile.current_age >= 50:
            recommendations.append({
                'type': 'medium',
                'title': 'Utilize Catch-Up Contributions',
                'description': "You're eligible for catch-up contributions to retirement accounts.",
                'action_items': [
                    "Consider additional $7,500 401(k) catch-up contribution",
                    "Consider additional $1,000 IRA catch-up contribution",
                    "Review if higher contribution limits fit your budget"
                ],
                'priority': 2
            })
        
        return recommendations[:5]  # Return top 5 recommendations
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []

# Initialize service
def init_retirement_service():
    """Initialize retirement service"""
    print("Retirement service initialized")
    return True

if __name__ == "__main__":
    # Test the service
    test_inputs = RetirementInputs(
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
    
    engine = RetirementCalculationEngine(test_inputs)
    results = engine.calculate_comprehensive_plan()
    
    print("Retirement Calculation Results:")
    print(f"Corpus Needed: ${results['retirement_needs']['retirement_corpus_needed']:,.2f}")
    print(f"Projected Savings: ${results['savings_projections']['total_projected_savings']:,.2f}")
    print(f"Success Rate: {results['monte_carlo_results']['success_rate']:.1f}%")