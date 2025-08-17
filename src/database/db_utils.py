import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    Base, User, Expense, Asset, Liability,
    RetirementProfile, RetirementScenario, RetirementCalculation,
    RetirementAccount, RetirementGoal, FinancialInsight,
    MarketData, FinancialDocument, UserPreferences
)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///financial_planner.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create default user if not exists
        session = SessionLocal()
        default_user = session.query(User).filter_by(user_id="default_user").first()
        if not default_user:
            default_user = User(
                user_id="default_user",
                name="Demo User",
                email="demo@example.com"
            )
            session.add(default_user)
            session.commit()
        session.close()
        
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def get_db_session(db_path="financial.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    return Session()

# User Management Functions
def get_or_create_user(session: Session, user_id: str, name: str = None, email: str = None) -> User:
    """Get existing user or create new one"""
    user = session.query(User).filter_by(user_id=user_id).first()
    
    if not user:
        user = User(user_id=user_id, name=name, email=email)
        session.add(user)
        session.commit()
    
    return user

def get_user_financial_summary(session: Session, user_id: str) -> Dict:
    """Get comprehensive financial summary for user"""
    
    # Get total assets
    total_assets = session.query(func.sum(Asset.current_value)).filter_by(user_id=user_id).scalar() or 0
    
    # Get total liabilities
    total_liabilities = session.query(func.sum(Liability.current_balance)).filter_by(user_id=user_id).scalar() or 0
    
    # Get monthly expenses (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.user_id == user_id, Expense.date >= thirty_days_ago)
    ).scalar() or 0
    
    # Get retirement savings
    retirement_profile = session.query(RetirementProfile).filter_by(user_id=user_id).first()
    retirement_savings = retirement_profile.current_savings if retirement_profile else 0
    
    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': total_assets - total_liabilities,
        'monthly_expenses': monthly_expenses,
        'retirement_savings': retirement_savings,
        'last_updated': datetime.utcnow()
    }

# Retirement Profile Functions
def save_retirement_profile(session: Session, user_id: str, profile_data: Dict) -> RetirementProfile:
    """Save or update retirement profile"""
    
    existing_profile = session.query(RetirementProfile).filter_by(user_id=user_id).first()
    
    if existing_profile:
        # Update existing profile
        for key, value in profile_data.items():
            if hasattr(existing_profile, key) and key not in ['id', 'user_id']:
                setattr(existing_profile, key, value)
        existing_profile.updated_at = datetime.utcnow()
        profile = existing_profile
    else:
        # Create new profile
        profile_data['user_id'] = user_id
        profile = RetirementProfile(**profile_data)
        session.add(profile)
    
    session.commit()
    return profile

def get_retirement_profile(session: Session, user_id: str) -> Optional[RetirementProfile]:
    """Get user's retirement profile"""
    return session.query(RetirementProfile).filter_by(user_id=user_id, is_active=True).first()

def delete_retirement_profile(session: Session, user_id: str) -> bool:
    """Delete user's retirement profile and related data"""
    try:
        profile = session.query(RetirementProfile).filter_by(user_id=user_id).first()
        if profile:
            session.delete(profile)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False

# Retirement Calculation Functions
def save_retirement_calculation(session: Session, profile_id: int, calculation_data: Dict) -> RetirementCalculation:
    """Save calculation results"""
    
    calculation = RetirementCalculation(
        profile_id=profile_id,
        input_parameters=calculation_data.get('inputs', {}),
        years_to_retirement=calculation_data.get('years_to_retirement'),
        retirement_years=calculation_data.get('retirement_years'),
        corpus_needed=calculation_data.get('corpus_needed'),
        projected_savings=calculation_data.get('projected_savings'),
        shortfall_surplus=calculation_data.get('shortfall_surplus'),
        additional_monthly_needed=calculation_data.get('additional_monthly_needed'),
        yearly_projections=calculation_data.get('yearly_projections', []),
        withdrawal_strategies=calculation_data.get('withdrawal_strategies', {}),
        sensitivity_analysis=calculation_data.get('sensitivity_analysis', {}),
        ai_insights=calculation_data.get('ai_insights'),
        risk_assessment=calculation_data.get('risk_assessment', 'medium')
    )
    
    session.add(calculation)
    session.commit()
    return calculation

def get_calculation_history(session: Session, profile_id: int, limit: int = 10) -> List[RetirementCalculation]:
    """Get calculation history for a profile"""
    return session.query(RetirementCalculation).filter_by(
        profile_id=profile_id
    ).order_by(RetirementCalculation.calculation_date.desc()).limit(limit).all()

def get_latest_calculation(session: Session, profile_id: int) -> Optional[RetirementCalculation]:
    """Get the most recent calculation"""
    return session.query(RetirementCalculation).filter_by(
        profile_id=profile_id
    ).order_by(RetirementCalculation.calculation_date.desc()).first()

# Retirement Scenario Functions
def save_retirement_scenario(session: Session, scenario_data: Dict) -> RetirementScenario:
    """Save retirement planning scenario"""
    
    scenario = RetirementScenario(**scenario_data)
    session.add(scenario)
    session.commit()
    return scenario

def get_user_scenarios(session: Session, profile_id: int) -> List[RetirementScenario]:
    """Get all scenarios for a user"""
    return session.query(RetirementScenario).filter_by(
        profile_id=profile_id
    ).order_by(RetirementScenario.created_at.desc()).all()

def update_scenario_results(session: Session, scenario_id: int, results: Dict) -> RetirementScenario:
    """Update scenario calculation results"""
    scenario = session.query(RetirementScenario).get(scenario_id)
    if scenario:
        scenario.corpus_needed = results.get('corpus_needed')
        scenario.projected_savings = results.get('projected_savings')
        scenario.shortfall_surplus = results.get('shortfall_surplus')
        scenario.additional_monthly_needed = results.get('additional_monthly_needed')
        scenario.success_probability = results.get('success_probability')
        session.commit()
    return scenario

def delete_retirement_scenario(session: Session, scenario_id: int) -> bool:
    """Delete a retirement scenario"""
    try:
        scenario = session.query(RetirementScenario).get(scenario_id)
        if scenario:
            session.delete(scenario)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False

# Retirement Account Functions
def save_retirement_accounts(session: Session, profile_id: int, accounts_data: List[Dict]) -> List[RetirementAccount]:
    """Save multiple retirement accounts"""
    
    # Mark existing accounts as inactive
    session.query(RetirementAccount).filter_by(
        profile_id=profile_id
    ).update({'is_active': False})
    
    # Add new accounts
    accounts = []
    for account_data in accounts_data:
        account_data['profile_id'] = profile_id
        account = RetirementAccount(**account_data)
        session.add(account)
        accounts.append(account)
    
    session.commit()
    return accounts

def get_retirement_accounts(session: Session, profile_id: int) -> List[RetirementAccount]:
    """Get active retirement accounts for a user"""
    return session.query(RetirementAccount).filter_by(
        profile_id=profile_id,
        is_active=True
    ).all()

def update_account_balance(session: Session, account_id: int, new_balance: float) -> RetirementAccount:
    """Update account balance"""
    account = session.query(RetirementAccount).get(account_id)
    if account:
        account.current_balance = new_balance
        account.updated_at = datetime.utcnow()
        session.commit()
    return account

def get_total_retirement_savings(session: Session, profile_id: int) -> float:
    """Get total retirement savings across all accounts"""
    total = session.query(func.sum(RetirementAccount.current_balance)).filter_by(
        profile_id=profile_id, is_active=True
    ).scalar()
    return total or 0.0

# Retirement Goal Functions
def create_retirement_goal(session: Session, goal_data: Dict) -> RetirementGoal:
    """Create a new retirement goal"""
    
    goal = RetirementGoal(**goal_data)
    session.add(goal)
    session.commit()
    return goal

def update_goal_progress(session: Session, goal_id: int, progress: float) -> RetirementGoal:
    """Update progress on a retirement goal"""
    
    goal = session.query(RetirementGoal).get(goal_id)
    if goal:
        goal.current_progress = progress
        goal.progress_percentage = min((progress / goal.target_amount) * 100, 100)
        
        if progress >= goal.target_amount and not goal.is_achieved:
            goal.is_achieved = True
            goal.achieved_date = datetime.utcnow()
        
        goal.updated_at = datetime.utcnow()
        session.commit()
    
    return goal

def get_user_goals(session: Session, profile_id: int, include_achieved: bool = True) -> List[RetirementGoal]:
    """Get retirement goals for a user"""
    query = session.query(RetirementGoal).filter_by(profile_id=profile_id)
    
    if not include_achieved:
        query = query.filter_by(is_achieved=False)
    
    return query.order_by(
        RetirementGoal.priority.asc(), 
        RetirementGoal.target_date.asc()
    ).all()

def delete_retirement_goal(session: Session, goal_id: int) -> bool:
    """Delete a retirement goal"""
    try:
        goal = session.query(RetirementGoal).get(goal_id)
        if goal:
            session.delete(goal)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False

# Financial Insight Functions
def save_financial_insight(session: Session, user_id: str, insight_data: Dict) -> FinancialInsight:
    """Save an AI-generated financial insight"""
    
    insight_data['user_id'] = user_id
    insight = FinancialInsight(**insight_data)
    session.add(insight)
    session.commit()
    return insight

def get_user_insights(session: Session, user_id: str, limit: int = 10, unread_only: bool = False) -> List[FinancialInsight]:
    """Get financial insights for a user"""
    query = session.query(FinancialInsight).filter_by(user_id=user_id, is_dismissed=False)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    return query.order_by(
        FinancialInsight.priority.desc(),
        FinancialInsight.generated_date.desc()
    ).limit(limit).all()

def mark_insight_read(session: Session, insight_id: int) -> bool:
    """Mark an insight as read"""
    try:
        insight = session.query(FinancialInsight).get(insight_id)
        if insight:
            insight.is_read = True
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False

def dismiss_insight(session: Session, insight_id: int) -> bool:
    """Dismiss an insight"""
    try:
        insight = session.query(FinancialInsight).get(insight_id)
        if insight:
            insight.is_dismissed = True
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False

# User Preferences Functions
def get_user_preferences(session: Session, user_id: str) -> UserPreferences:
    """Get user preferences, create default if not exists"""
    preferences = session.query(UserPreferences).filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreferences(user_id=user_id)
        session.add(preferences)
        session.commit()
    
    return preferences

def update_user_preferences(session: Session, user_id: str, preferences_data: Dict) -> UserPreferences:
    """Update user preferences"""
    preferences = get_user_preferences(session, user_id)
    
    for key, value in preferences_data.items():
        if hasattr(preferences, key):
            setattr(preferences, key, value)
    
    preferences.updated_at = datetime.utcnow()
    session.commit()
    return preferences

# Analytics and Reporting Functions
def get_retirement_readiness_metrics(session: Session, user_id: str) -> Dict:
    """Calculate retirement readiness metrics"""
    
    profile = get_retirement_profile(session, user_id)
    if not profile:
        return {'score': 0, 'details': 'No retirement profile found'}
    
    # Calculate basic metrics
    years_to_retirement = profile.retirement_age - profile.current_age
    retirement_years = profile.life_expectancy - profile.retirement_age
    
    # Savings rate
    monthly_income = profile.current_annual_income / 12
    savings_rate = (profile.monthly_contribution / monthly_income) * 100 if monthly_income > 0 else 0
    
    # Time factor (more time = better score)
    time_score = min((years_to_retirement / 30) * 40, 40)  # Max 40 points
    
    # Savings rate score
    savings_score = min((savings_rate / 15) * 30, 30)  # Max 30 points (15% savings rate)
    
    # Current savings score
    annual_income_multiplier = profile.current_savings / profile.current_annual_income
    current_savings_score = min(annual_income_multiplier * 10, 30)  # Max 30 points
    
    total_score = time_score + savings_score + current_savings_score
    
    return {
        'score': min(total_score, 100),
        'time_score': time_score,
        'savings_rate_score': savings_score,
        'current_savings_score': current_savings_score,
        'savings_rate': savings_rate,
        'years_to_retirement': years_to_retirement,
        'details': f"Time: {time_score:.1f}, Savings Rate: {savings_score:.1f}, Current Savings: {current_savings_score:.1f}"
    }

def get_user_dashboard_data(session: Session, user_id: str) -> Dict:
    """Get comprehensive dashboard data for user"""
    
    # Financial summary
    financial_summary = get_user_financial_summary(session, user_id)
    
    # Retirement readiness
    retirement_metrics = get_retirement_readiness_metrics(session, user_id)
    
    # Recent insights
    recent_insights = get_user_insights(session, user_id, limit=5)
    
    # Goals progress
    profile = get_retirement_profile(session, user_id)
    goals = get_user_goals(session, profile.id, include_achieved=False) if profile else []
    
    return {
        'financial_summary': financial_summary,
        'retirement_readiness': retirement_metrics,
        'recent_insights': [
            {
                'title': insight.title,
                'content': insight.content[:100] + '...',
                'priority': insight.priority,
                'date': insight.generated_date
            } for insight in recent_insights
        ],
        'active_goals': len(goals),
        'achieved_goals': len([g for g in goals if g.is_achieved])
    }

# Data Export/Import Functions
def export_user_data(session: Session, user_id: str) -> Dict:
    """Export all user data"""
    
    # Get user
    user = session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return {}
    
    # Get retirement profile
    retirement_profile = get_retirement_profile(session, user_id)
    
    # Get accounts
    accounts = get_retirement_accounts(session, retirement_profile.id) if retirement_profile else []
    
    # Get goals
    goals = get_user_goals(session, retirement_profile.id) if retirement_profile else []
    
    # Get scenarios
    scenarios = get_user_scenarios(session, retirement_profile.id) if retirement_profile else []
    
    # Get calculation history
    calculations = get_calculation_history(session, retirement_profile.id) if retirement_profile else []
    
    return {
        'user': {
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        },
        'retirement_profile': {
            'current_age': retirement_profile.current_age,
            'retirement_age': retirement_profile.retirement_age,
            'life_expectancy': retirement_profile.life_expectancy,
            'current_annual_income': retirement_profile.current_annual_income,
            'desired_retirement_income_ratio': retirement_profile.desired_retirement_income_ratio,
            'current_savings': retirement_profile.current_savings,
            'monthly_contribution': retirement_profile.monthly_contribution
        } if retirement_profile else None,
        'accounts': [
            {
                'account_type': acc.account_type,
                'account_name': acc.account_name,
                'current_balance': acc.current_balance,
                'monthly_contribution': acc.monthly_contribution
            } for acc in accounts
        ],
        'goals': [
            {
                'goal_name': goal.goal_name,
                'target_amount': goal.target_amount,
                'current_progress': goal.current_progress,
                'is_achieved': goal.is_achieved
            } for goal in goals
        ],
        'export_date': datetime.utcnow().isoformat()
    }

# Database maintenance functions
def cleanup_old_calculations(session: Session, days_old: int = 90):
    """Clean up old calculation records"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    deleted_count = session.query(RetirementCalculation).filter(
        RetirementCalculation.calculation_date < cutoff_date
    ).delete()
    
    session.commit()
    return deleted_count

def backup_database(backup_path: str) -> bool:
    """Create database backup"""
    try:
        # Implementation depends on database type
        # For SQLite, copy the file
        if DATABASE_URL.startswith('sqlite'):
            import shutil
            db_path = DATABASE_URL.replace('sqlite:///', '')
            shutil.copy2(db_path, backup_path)
            return True
        
        # For PostgreSQL/MySQL, would use pg_dump/mysqldump
        return False
    except Exception:
        return False

# Error handling decorator
def handle_db_errors(func):
    """Decorator to handle database errors"""
    def wrapper(*args, **kwargs):
        session = args[0] if args and isinstance(args[0], Session) else None
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            print(f"Database error in {func.__name__}: {e}")
            return None
        except Exception as e:
            if session:
                session.rollback()
            print(f"Unexpected error in {func.__name__}: {e}")
            return None
    return wrapper

# Initialize database on import
if __name__ == "__main__":
    init_database()