import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import math

def format_currency(amount: float, precision: int = 0) -> str:
    """Format currency with proper formatting"""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    else:
        return f"${amount:,.{precision}f}"

def format_percentage(value: float, precision: int = 1) -> str:
    """Format percentage with proper formatting"""
    return f"{value:.{precision}f}%"

def calculate_inflation_impact(amount: float, years: int, inflation_rate: float) -> Dict[str, float]:
    """Calculate inflation impact on a given amount"""
    
    future_value = amount * (1 + inflation_rate) ** years
    purchasing_power = amount / (1 + inflation_rate) ** years
    inflation_erosion = amount - purchasing_power
    
    return {
        'original_amount': amount,
        'future_nominal_value': future_value,
        'future_purchasing_power': purchasing_power,
        'inflation_erosion': inflation_erosion,
        'erosion_percentage': (inflation_erosion / amount) * 100 if amount > 0 else 0
    }

def calculate_compound_growth(principal: float, rate: float, time: int, contributions: float = 0) -> Dict[str, float]:
    """Calculate compound growth with optional regular contributions"""
    
    if rate == 0:
        final_value = principal + (contributions * time)
        growth = contributions * time
    else:
        # Future value of principal
        fv_principal = principal * (1 + rate) ** time
        
        # Future value of annuity (contributions)
        if contributions > 0:
            fv_contributions = contributions * (((1 + rate) ** time - 1) / rate)
        else:
            fv_contributions = 0
        
        final_value = fv_principal + fv_contributions
        growth = final_value - principal - (contributions * time)
    
    return {
        'principal': principal,
        'total_contributions': contributions * time,
        'investment_growth': growth,
        'final_value': final_value,
        'total_return_percentage': ((final_value / (principal + contributions * time)) - 1) * 100 if (principal + contributions * time) > 0 else 0
    }

def calculate_required_savings_rate(current_income: float, retirement_income_goal: float, 
                                  years_to_retirement: int, current_savings: float,
                                  return_rate: float = 0.07) -> Dict[str, float]:
    """Calculate required savings rate to meet retirement income goal"""
    
    # Assume 4% withdrawal rate for retirement corpus calculation
    withdrawal_rate = 0.04
    required_corpus = retirement_income_goal / withdrawal_rate
    
    # Subtract future value of current savings
    current_savings_fv = current_savings * (1 + return_rate) ** years_to_retirement
    additional_corpus_needed = max(0, required_corpus - current_savings_fv)
    
    # Calculate required annual savings
    if return_rate == 0:
        required_annual_savings = additional_corpus_needed / years_to_retirement
    else:
        required_annual_savings = additional_corpus_needed * return_rate / ((1 + return_rate) ** years_to_retirement - 1)
    
    required_savings_rate = (required_annual_savings / current_income) * 100 if current_income > 0 else 0
    
    return {
        'required_corpus': required_corpus,
        'current_savings_fv': current_savings_fv,
        'additional_corpus_needed': additional_corpus_needed,
        'required_annual_savings': required_annual_savings,
        'required_monthly_savings': required_annual_savings / 12,
        'required_savings_rate_percentage': required_savings_rate,
        'is_feasible': required_savings_rate <= 50  # Assume 50% savings rate is maximum feasible
    }

def calculate_retirement_income_replacement(expenses: List[Dict], retirement_adjustments: Dict = None) -> Dict[str, float]:
    """Calculate retirement income replacement needs based on expenses"""
    
    if not retirement_adjustments:
        retirement_adjustments = {
            'housing': 0.8,  # 20% reduction (mortgage paid off)
            'transportation': 0.6,  # 40% reduction (no commuting)
            'food': 0.9,  # 10% reduction
            'healthcare': 1.5,  # 50% increase
            'entertainment': 1.2,  # 20% increase
            'other': 1.0  # No change
        }
    
    current_expenses = {}
    retirement_expenses = {}
    
    for expense in expenses:
        category = expense.get('category', 'other').lower()
        amount = expense.get('amount', 0)
        
        current_expenses[category] = current_expenses.get(category, 0) + amount
        
        adjustment_factor = retirement_adjustments.get(category, 1.0)
        retirement_expenses[category] = current_expenses[category] * adjustment_factor
    
    total_current = sum(current_expenses.values())
    total_retirement = sum(retirement_expenses.values())
    
    return {
        'current_monthly_expenses': total_current,
        'retirement_monthly_expenses': total_retirement,
        'annual_retirement_expenses': total_retirement * 12,
        'replacement_ratio': (total_retirement / total_current) if total_current > 0 else 0,
        'expense_breakdown': retirement_expenses
    }

def assess_retirement_risk_factors(profile_data: Dict, market_conditions: Dict = None) -> Dict[str, int]:
    """Assess retirement risk factors (1-10 scale, 10 being highest risk)"""
    
    current_age = profile_data.get('current_age', 35)
    retirement_age = profile_data.get('retirement_age', 65)
    savings_rate = profile_data.get('savings_rate_percentage', 10)
    investment_return = profile_data.get('pre_retirement_return_rate', 0.07) * 100
    
    risk_factors = {}
    
    # Time horizon risk (less time = higher risk)
    years_to_retirement = retirement_age - current_age
    if years_to_retirement < 5:
        risk_factors['time_horizon'] = 9
    elif years_to_retirement < 10:
        risk_factors['time_horizon'] = 7
    elif years_to_retirement < 20:
        risk_factors['time_horizon'] = 4
    else:
        risk_factors['time_horizon'] = 2
    
    # Savings rate risk
    if savings_rate < 5:
        risk_factors['savings_rate'] = 9
    elif savings_rate < 10:
        risk_factors['savings_rate'] = 6
    elif savings_rate < 15:
        risk_factors['savings_rate'] = 3
    else:
        risk_factors['savings_rate'] = 1
    
    # Investment return assumptions risk
    if investment_return > 10:
        risk_factors['return_assumptions'] = 8
    elif investment_return > 8:
        risk_factors['return_assumptions'] = 5
    elif investment_return > 6:
        risk_factors['return_assumptions'] = 3
    else:
        risk_factors['return_assumptions'] = 2
    
    # Market conditions risk
    if market_conditions:
        volatility = market_conditions.get('volatility', 'medium')
        if volatility == 'high':
            risk_factors['market_conditions'] = 8
        elif volatility == 'medium':
            risk_factors['market_conditions'] = 5
        else:
            risk_factors['market_conditions'] = 3
    else:
        risk_factors['market_conditions'] = 5  # Default moderate risk
    
    # Inflation risk
    inflation_rate = profile_data.get('inflation_rate', 0.03) * 100
    if inflation_rate > 4:
        risk_factors['inflation'] = 7
    elif inflation_rate > 3:
        risk_factors['inflation'] = 4
    else:
        risk_factors['inflation'] = 2
    
    # Longevity risk
    life_expectancy = profile_data.get('life_expectancy', 85)
    retirement_years = life_expectancy - retirement_age
    if retirement_years > 30:
        risk_factors['longevity'] = 7
    elif retirement_years > 25:
        risk_factors['longevity'] = 5
    elif retirement_years > 20:
        risk_factors['longevity'] = 3
    else:
        risk_factors['longevity'] = 2
    
    return risk_factors

def generate_retirement_milestones(current_age: int, retirement_age: int, current_income: float) -> List[Dict]:
    """Generate age-based retirement milestones"""
    
    milestones = []
    
    # Common financial planning milestones
    milestone_rules = [
        (25, 0.5), (30, 1), (35, 2), (40, 3), (45, 4),
        (50, 6), (55, 7), (60, 8), (retirement_age, 10)
    ]
    
    for age, multiplier in milestone_rules:
        if current_age < age <= retirement_age:
            target_amount = current_income * multiplier
            years_to_milestone = age - current_age
            
            milestones.append({
                'age': age,
                'target_amount': target_amount,
                'years_to_milestone': years_to_milestone,
                'description': f"Have {multiplier}x annual salary by age {age}",
                'priority': 'high' if years_to_milestone <= 5 else 'medium'
            })
    
    return milestones

def calculate_catch_up_strategies(shortfall: float, years_remaining: int, current_monthly: float) -> List[Dict]:
    """Generate catch-up strategies for retirement shortfall"""
    
    strategies = []
    
    if shortfall <= 0:
        return strategies
    
    # Strategy 1: Increase monthly savings
    if years_remaining > 0:
        additional_monthly = shortfall / (years_remaining * 12) / (1.07 ** (years_remaining / 2))  # Rough discount
        strategies.append({
            'strategy': 'Increase Monthly Savings',
            'description': f'Increase monthly contribution by ${additional_monthly:,.0f}',
            'additional_monthly': additional_monthly,
            'total_additional': additional_monthly * 12 * years_remaining,
            'feasibility': 'high' if additional_monthly < current_monthly * 0.5 else 'medium'
        })
    
    # Strategy 2: Work longer
    for extra_years in [1, 2, 3]:
        if years_remaining + extra_years > 0:
            new_additional_monthly = shortfall / ((years_remaining + extra_years) * 12) / (1.07 ** ((years_remaining + extra_years) / 2))
            strategies.append({
                'strategy': f'Work {extra_years} More Year{"s" if extra_years > 1 else ""}',
                'description': f'Delay retirement by {extra_years} year{"s" if extra_years > 1 else ""} and increase monthly savings by ${new_additional_monthly:,.0f}',
                'additional_monthly': new_additional_monthly,
                'extra_years': extra_years,
                'feasibility': 'high' if new_additional_monthly < additional_monthly * 0.7 else 'medium'
            })
    
    # Strategy 3: Reduce retirement expenses
    expense_reductions = [0.1, 0.15, 0.2]
    for reduction in expense_reductions:
        reduced_shortfall = shortfall * (1 - reduction)
        reduced_additional_monthly = reduced_shortfall / (years_remaining * 12) / (1.07 ** (years_remaining / 2))
        strategies.append({
            'strategy': f'Reduce Retirement Expenses by {reduction*100:.0f}%',
            'description': f'Lower retirement lifestyle expectations and increase monthly savings by ${reduced_additional_monthly:,.0f}',
            'additional_monthly': reduced_additional_monthly,
            'expense_reduction': reduction,
            'feasibility': 'medium' if reduction <= 0.15 else 'low'
        })
    
    return strategies

def calculate_social_security_estimate(birth_year: int, annual_earnings: List[float], retirement_age: int = 67) -> Dict[str, float]:
    """Estimate Social Security benefits (simplified calculation)"""
    
    # This is a very simplified estimate - actual SS calculation is complex
    current_year = datetime.now().year
    
    # Calculate average indexed monthly earnings (AIME) - simplified
    # In reality, this involves wage indexing and using highest 35 years
    avg_annual_earnings = sum(annual_earnings[-10:]) / min(len(annual_earnings), 10)  # Use last 10 years
    aime = avg_annual_earnings / 12
    
    # Primary Insurance Amount (PIA) calculation - 2024 bend points
    # This is simplified - actual calculation uses wage-indexed bend points
    if aime <= 1174:
        pia = aime * 0.9
    elif aime <= 7078:
        pia = 1174 * 0.9 + (aime - 1174) * 0.32
    else:
        pia = 1174 * 0.9 + (7078 - 1174) * 0.32 + (aime - 7078) * 0.15
    
    # Adjust for retirement age
    full_retirement_age = 67  # For people born 1960 or later
    if retirement_age < full_retirement_age:
        # Early retirement reduction
        months_early = (full_retirement_age - retirement_age) * 12
        reduction = min(0.25, months_early * 0.0055)  # Simplified reduction
        pia *= (1 - reduction)
    elif retirement_age > full_retirement_age:
        # Delayed retirement credits
        years_delayed = retirement_age - full_retirement_age
        pia *= (1 + years_delayed * 0.08)
    
    return {
        'monthly_benefit': pia,
        'annual_benefit': pia * 12,
        'full_retirement_age': full_retirement_age,
        'aime': aime,
        'note': 'This is a simplified estimate. Actual benefits may vary.'
    }

def create_retirement_calendar(profile_data: Dict) -> List[Dict]:
    """Create a retirement planning calendar with key dates and milestones"""
    
    current_age = profile_data.get('current_age', 35)
    retirement_age = profile_data.get('retirement_age', 65)
    current_year = datetime.now().year
    
    calendar_events = []
    
    # Age-based milestones
    milestone_ages = [50, 55, 59.5, 62, 65, 67, 70, 72]
    milestone_descriptions = {
        50: "Eligible for catch-up contributions ($7,500 401(k), $1,000 IRA)",
        55: "Can withdraw from 401(k) without penalty if you separate from service",
        59.5: "Can withdraw from IRA/401(k) without 10% early withdrawal penalty",
        62: "Eligible for early Social Security benefits (reduced amount)",
        65: "Eligible for Medicare",
        67: "Full retirement age for Social Security (for those born 1960+)",
        70: "Maximum Social Security benefits (delayed retirement credits end)",
        72: "Required Minimum Distributions (RMDs) begin"
    }
    
    for age in milestone_ages:
        if current_age <= age:
            year = current_year + (age - current_age)
            calendar_events.append({
                'age': age,
                'year': year,
                'event_type': 'milestone',
                'title': f"Age {age} Milestone",
                'description': milestone_descriptions.get(age, ""),
                'importance': 'high' if age in [59.5, 65, 67] else 'medium'
            })
    
    # Retirement date
    retirement_year = current_year + (retirement_age - current_age)
    calendar_events.append({
        'age': retirement_age,
        'year': retirement_year,
        'event_type': 'retirement',
        'title': 'Planned Retirement Date',
        'description': f"Target retirement at age {retirement_age}",
        'importance': 'critical'
    })
    
    # Annual review dates
    for i in range(0, retirement_age - current_age + 5, 1):
        if i > 0:  # Skip current year
            calendar_events.append({
                'age': current_age + i,
                'year': current_year + i,
                'event_type': 'review',
                'title': 'Annual Plan Review',
                'description': 'Review and update retirement plan, rebalance portfolio',
                'importance': 'medium'
            })
    
    return sorted(calendar_events, key=lambda x: x['year'])

def validate_retirement_inputs(inputs: Dict) -> Dict[str, List[str]]:
    """Validate retirement planning inputs and return errors/warnings"""
    
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['current_age', 'retirement_age', 'life_expectancy', 'current_annual_income']
    for field in required_fields:
        if not inputs.get(field) or inputs[field] <= 0:
            errors.append(f"{field.replace('_', ' ').title()} is required and must be positive")
    
    # Logical validations
    if inputs.get('current_age') and inputs.get('retirement_age'):
        if inputs['current_age'] >= inputs['retirement_age']:
            errors.append("Retirement age must be greater than current age")
        elif inputs['retirement_age'] - inputs['current_age'] < 5:
            warnings.append("Very short time to retirement - consider if goals are realistic")
    
    if inputs.get('retirement_age') and inputs.get('life_expectancy'):
        if inputs['retirement_age'] >= inputs['life_expectancy']:
            errors.append("Life expectancy must be greater than retirement age")
        elif inputs['life_expectancy'] - inputs['retirement_age'] < 10:
            warnings.append("Short retirement period - consider increasing life expectancy assumption")
    
    # Return rate validations
    pre_return = inputs.get('pre_retirement_return_rate', 0)
    if pre_return < 0 or pre_return > 0.15:
        warnings.append("Pre-retirement return rate seems unrealistic (typically 4-12%)")
    
    post_return = inputs.get('post_retirement_return_rate', 0)
    if post_return < 0 or post_return > 0.12:
        warnings.append("Post-retirement return rate seems unrealistic (typically 3-8%)")
    
    # Inflation rate
    inflation = inputs.get('inflation_rate', 0)
    if inflation < 0 or inflation > 0.08:
        warnings.append("Inflation rate seems unrealistic (typically 2-4%)")
    
    # Savings rate
    monthly_contribution = inputs.get('monthly_contribution', 0)
    annual_income = inputs.get('current_annual_income', 1)
    if monthly_contribution > 0 and annual_income > 0:
        savings_rate = (monthly_contribution * 12) / annual_income
        if savings_rate > 0.5:
            warnings.append("Savings rate over 50% may not be sustainable")
        elif savings_rate < 0.1:
            warnings.append("Savings rate below 10% may be insufficient for retirement")
    
    # Employer match
    match_rate = inputs.get('employer_match_rate', 0)
    match_limit = inputs.get('employer_match_limit', 0)
    if match_rate > 1:
        warnings.append("Employer match rate over 100% seems unrealistic")
    if match_limit > 0.15:
        warnings.append("Employer match limit over 15% of salary seems unrealistic")
    
    return {'errors': errors, 'warnings': warnings}

def calculate_retirement_readiness_score(profile_data: Dict, calculation_results: Dict) -> Dict[str, Any]:
    """Calculate comprehensive retirement readiness score"""
    
    score_components = {}
    total_score = 0
    max_score = 100
    
    # Time factor (20 points max)
    years_to_retirement = profile_data.get('retirement_age', 65) - profile_data.get('current_age', 35)
    if years_to_retirement >= 30:
        time_score = 20
    elif years_to_retirement >= 20:
        time_score = 15
    elif years_to_retirement >= 10:
        time_score = 10
    elif years_to_retirement >= 5:
        time_score = 5
    else:
        time_score = 0
    
    score_components['time_factor'] = {'score': time_score, 'max': 20}
    total_score += time_score
    
    # Savings rate (25 points max)
    monthly_contribution = profile_data.get('monthly_contribution', 0)
    annual_income = profile_data.get('current_annual_income', 1)
    savings_rate = (monthly_contribution * 12) / annual_income if annual_income > 0 else 0
    
    if savings_rate >= 0.15:
        savings_score = 25
    elif savings_rate >= 0.12:
        savings_score = 20
    elif savings_rate >= 0.10:
        savings_score = 15
    elif savings_rate >= 0.08:
        savings_score = 10
    elif savings_rate >= 0.05:
        savings_score = 5
    else:
        savings_score = 0
    
    score_components['savings_rate'] = {'score': savings_score, 'max': 25}
    total_score += savings_score
    
    # Current progress (25 points max)
    current_savings = profile_data.get('current_savings', 0)
    annual_income = profile_data.get('current_annual_income', 1)
    current_age = profile_data.get('current_age', 35)
    
    # Expected savings by age (rough benchmark)
    expected_multiple = max(0, (current_age - 25) * 0.5)  # 0.5x salary per year after 25
    expected_savings = annual_income * expected_multiple
    
    if expected_savings > 0:
        progress_ratio = current_savings / expected_savings
        if progress_ratio >= 1.2:
            progress_score = 25
        elif progress_ratio >= 1.0:
            progress_score = 20
        elif progress_ratio >= 0.8:
            progress_score = 15
        elif progress_ratio >= 0.6:
            progress_score = 10
        elif progress_ratio >= 0.4:
            progress_score = 5
        else:
            progress_score = 0
    else:
        progress_score = 10 if current_savings > 0 else 0
    
    score_components['current_progress'] = {'score': progress_score, 'max': 25}
    total_score += progress_score
    
    # Plan feasibility (20 points max)
    if calculation_results.get('savings_projections'):
        projections = calculation_results['savings_projections']
        shortfall = projections.get('shortfall', 0)
        corpus_needed = projections.get('corpus_needed', 1)
        
        if shortfall <= 0:
            feasibility_score = 20
        else:
            shortfall_ratio = shortfall / corpus_needed
            if shortfall_ratio <= 0.1:
                feasibility_score = 15
            elif shortfall_ratio <= 0.2:
                feasibility_score = 10
            elif shortfall_ratio <= 0.4:
                feasibility_score = 5
            else:
                feasibility_score = 0
    else:
        feasibility_score = 10  # Default if no calculation available
    
    score_components['plan_feasibility'] = {'score': feasibility_score, 'max': 20}
    total_score += feasibility_score
    
    # Diversification and risk management (10 points max)
    diversification_score = 5  # Base score
    
    # Employer match utilization
    if profile_data.get('employer_match_rate', 0) > 0:
        diversification_score += 3
    
    # Multiple account types (would need account data)
    diversification_score += 2  # Assume some diversification
    
    score_components['diversification'] = {'score': diversification_score, 'max': 10}
    total_score += diversification_score
    
    # Calculate overall grade
    percentage = (total_score / max_score) * 100
    
    if percentage >= 90:
        grade = 'A'
        assessment = 'Excellent'
    elif percentage >= 80:
        grade = 'B'
        assessment = 'Good'
    elif percentage >= 70:
        grade = 'C'
        assessment = 'Fair'
    elif percentage >= 60:
        grade = 'D'
        assessment = 'Needs Improvement'
    else:
        grade = 'F'
        assessment = 'Critical'
    
    return {
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
        'grade': grade,
        'assessment': assessment,
        'components': score_components,
        'recommendations': generate_score_based_recommendations(score_components)
    }

def generate_score_based_recommendations(score_components: Dict) -> List[str]:
    """Generate recommendations based on score components"""
    
    recommendations = []
    
    # Time factor recommendations
    if score_components['time_factor']['score'] < 10:
        recommendations.append("Consider aggressive savings strategies due to limited time horizon")
        recommendations.append("Evaluate if working a few extra years is feasible")
    
    # Savings rate recommendations
    if score_components['savings_rate']['score'] < 15:
        recommendations.append("Increase monthly retirement contributions")
        recommendations.append("Review budget for potential expense reductions")
        recommendations.append("Consider automatic contribution increases")
    
    # Current progress recommendations
    if score_components['current_progress']['score'] < 15:
        recommendations.append("Focus on building retirement savings foundation")
        recommendations.append("Consider catch-up contributions if eligible")
    
    # Plan feasibility recommendations
    if score_components['plan_feasibility']['score'] < 15:
        recommendations.append("Revise retirement goals or timeline")
        recommendations.append("Consider part-time work in early retirement")
        recommendations.append("Explore ways to reduce retirement expenses")
    
    # Diversification recommendations
    if score_components['diversification']['score'] < 8:
        recommendations.append("Maximize employer 401(k) matching")
        recommendations.append("Consider diversifying across account types (traditional, Roth)")
        recommendations.append("Review investment allocation for age-appropriate risk")
    
    return recommendations

def format_financial_summary(data: Dict) -> str:
    """Format financial data into readable summary"""
    
    summary_parts = []
    
    if 'net_worth' in data:
        summary_parts.append(f"Net Worth: {format_currency(data['net_worth'])}")
    
    if 'monthly_expenses' in data:
        summary_parts.append(f"Monthly Expenses: {format_currency(data['monthly_expenses'])}")
    
    if 'savings_rate' in data:
        summary_parts.append(f"Savings Rate: {format_percentage(data['savings_rate'])}")
    
    if 'retirement_readiness' in data:
        summary_parts.append(f"Retirement Score: {data['retirement_readiness']}/100")
    
    return " | ".join(summary_parts)

def export_retirement_data_to_csv(data: Dict, filename: str = None) -> str:
    """Export retirement data to CSV format"""
    
    if not filename:
        filename = f"retirement_plan_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Convert yearly projections to DataFrame
    if 'yearly_projections' in data:
        df = pd.DataFrame(data['yearly_projections'])
        
        # Add summary data as additional rows
        summary_data = {
            'age': ['Summary', 'Corpus Needed', 'Projected Savings', 'Shortfall/Surplus'],
            'balance': [
                '',
                data.get('retirement_needs', {}).get('retirement_corpus_needed', 0),
                data.get('savings_projections', {}).get('total_projected_savings', 0),
                data.get('savings_projections', {}).get('shortfall', 0) - data.get('savings_projections', {}).get('surplus', 0)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        df = pd.concat([df, summary_df], ignore_index=True)
        
        # Save to CSV (in a real app, you'd return the file or save it)
        csv_content = df.to_csv(index=False)
        return csv_content
    
    return "No data available for export"

def calculate_tax_efficiency_score(account_allocation: Dict) -> Dict[str, Any]:
    """Calculate tax efficiency score based on account allocation"""
    
    total_balance = sum(account_allocation.values())
    
    if total_balance == 0:
        return {'score': 0, 'recommendations': ['Start contributing to retirement accounts']}
    
    # Calculate allocation percentages
    traditional_pct = (account_allocation.get('401k', 0) + account_allocation.get('traditional_ira', 0)) / total_balance
    roth_pct = (account_allocation.get('roth_401k', 0) + account_allocation.get('roth_ira', 0)) / total_balance
    taxable_pct = account_allocation.get('taxable', 0) / total_balance
    
    score = 0
    recommendations = []
    
    # Diversification across account types (40 points)
    if traditional_pct > 0 and roth_pct > 0:
        score += 30
        if 0.3 <= traditional_pct <= 0.7 and 0.3 <= roth_pct <= 0.7:
            score += 10  # Bonus for balanced allocation
    elif traditional_pct > 0 or roth_pct > 0:
        score += 15
        recommendations.append("Consider diversifying between traditional and Roth accounts")
    
    # Tax-advantaged account usage (40 points)
    tax_advantaged_pct = traditional_pct + roth_pct
    if tax_advantaged_pct >= 0.9:
        score += 40
    elif tax_advantaged_pct >= 0.8:
        score += 35
    elif tax_advantaged_pct >= 0.7:
        score += 30
    elif tax_advantaged_pct >= 0.6:
        score += 20
    else:
        score += tax_advantaged_pct * 30
        recommendations.append("Maximize tax-advantaged account contributions before taxable accounts")
    
    # HSA usage (20 points) - would need HSA data
    # For now, give partial credit
    score += 10
    recommendations.append("Consider HSA contributions if eligible for triple tax advantage")
    
    return {
        'score': min(score, 100),
        'traditional_percentage': traditional_pct * 100,
        'roth_percentage': roth_pct * 100,
        'taxable_percentage': taxable_pct * 100,
        'recommendations': recommendations
    }

# Streamlit helper functions
def display_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Display a metric card with consistent formatting"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            help=help_text
        )

def create_progress_bar(current: float, target: float, label: str = "Progress"):
    """Create a progress bar with current vs target"""
    
    progress = min(current / target, 1.0) if target > 0 else 0
    
    st.write(f"**{label}**")
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"Current: {format_currency(current)}")
    with col2:
        st.write(f"Target: {format_currency(target)}")
    with col3:
        st.write(f"Progress: {progress*100:.1f}%")

def display_risk_indicator(risk_level: str):
    """Display risk level with appropriate color coding"""
    
    risk_colors = {
        'low': '🟢',
        'medium': '🟡', 
        'high': '🟠',
        'very_high': '🔴'
    }
    
    color_indicator = risk_colors.get(risk_level, '⚪')
    st.write(f"{color_indicator} **Risk Level:** {risk_level.replace('_', ' ').title()}")

def load_css():
    """Load custom CSS for retirement planning interface"""
    
    st.markdown("""
    <style>
    .retirement-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .metric-positive {
        color: #28a745;
        font-weight: bold;
    }
    
    .metric-negative {
        color: #dc3545;
        font-weight: bold;
    }
    
    .progress-good {
        background-color: #28a745;
    }
    
    .progress-warning {
        background-color: #ffc107;
    }
    
    .progress-danger {
        background-color: #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)

# Constants and configuration
RETIREMENT_ACCOUNT_TYPES = [
    '401(k)', 'Roth 401(k)', 'Traditional IRA', 'Roth IRA',
    'SEP-IRA', 'SIMPLE IRA', 'HSA', 'Taxable Investment',
    'Pension', 'Annuity', 'Other'
]

DEFAULT_RETIREMENT_ASSUMPTIONS = {
    'pre_retirement_return': 0.07,
    'post_retirement_return': 0.05,
    'inflation_rate': 0.03,
    'withdrawal_rate': 0.04,
    'life_expectancy': 85,
    'healthcare_cost_inflation': 0.05
}

RISK_TOLERANCE_PROFILES = {
    'conservative': {
        'stocks': 0.3,
        'bonds': 0.6,
        'cash': 0.1,
        'expected_return': 0.05
    },
    'moderate': {
        'stocks': 0.6,
        'bonds': 0.35,
        'cash': 0.05,
        'expected_return': 0.07
    },
    'aggressive': {
        'stocks': 0.8,
        'bonds': 0.15,
        'cash': 0.05,
        'expected_return': 0.09
    }
}