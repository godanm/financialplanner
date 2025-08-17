from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Existing models (your current financial data models)
class User(Base):
    """User profile"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship("Expense", back_populates="user")
    assets = relationship("Asset", back_populates="user")
    liabilities = relationship("Liability", back_populates="user")
    retirement_profile = relationship("RetirementProfile", back_populates="user", uselist=False)

class Expense(Base):
    """Expense tracking"""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(200))
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="expenses")

class Asset(Base):
    """Asset tracking"""
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    asset_type = Column(String(50), nullable=False)  # savings, investment, property, etc.
    name = Column(String(100), nullable=False)
    current_value = Column(Float, nullable=False)
    purchase_price = Column(Float)
    purchase_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assets")

class Liability(Base):
    """Liability tracking"""
    __tablename__ = 'liabilities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    liability_type = Column(String(50), nullable=False)  # mortgage, credit_card, loan, etc.
    name = Column(String(100), nullable=False)
    current_balance = Column(Float, nullable=False)
    interest_rate = Column(Float)
    minimum_payment = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="liabilities")

# New Retirement Planning Models
class RetirementProfile(Base):
    """User's retirement planning profile"""
    __tablename__ = 'retirement_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, unique=True)
    
    # Personal Information
    current_age = Column(Integer, nullable=False)
    retirement_age = Column(Integer, nullable=False)
    life_expectancy = Column(Integer, nullable=False, default=85)
    
    # Financial Information
    current_annual_income = Column(Float, nullable=False)
    desired_retirement_income_ratio = Column(Float, nullable=False, default=0.8)
    current_savings = Column(Float, nullable=False, default=0.0)
    monthly_contribution = Column(Float, nullable=False, default=0.0)
    
    # Employer Benefits
    employer_match_rate = Column(Float, default=0.0)
    employer_match_limit = Column(Float, default=0.06)
    
    # Investment Assumptions
    pre_retirement_return_rate = Column(Float, default=0.07)
    post_retirement_return_rate = Column(Float, default=0.05)
    inflation_rate = Column(Float, default=0.03)
    
    # Additional Income Sources
    estimated_social_security = Column(Float, default=0.0)
    estimated_healthcare_costs = Column(Float, default=0.0)
    estimated_pension = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="retirement_profile")
    scenarios = relationship("RetirementScenario", back_populates="profile", cascade="all, delete-orphan")
    calculations = relationship("RetirementCalculation", back_populates="profile", cascade="all, delete-orphan")
    accounts = relationship("RetirementAccount", back_populates="profile", cascade="all, delete-orphan")
    goals = relationship("RetirementGoal", back_populates="profile", cascade="all, delete-orphan")

class RetirementScenario(Base):
    """Different retirement planning scenarios"""
    __tablename__ = 'retirement_scenarios'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('retirement_profiles.id'), nullable=False)
    
    scenario_name = Column(String(100), nullable=False)
    description = Column(Text)
    scenario_type = Column(String(50), default='custom')  # conservative, aggressive, custom
    
    # Scenario-specific overrides (JSON format for flexibility)
    parameter_overrides = Column(JSON)
    
    # Calculated Results
    corpus_needed = Column(Float)
    projected_savings = Column(Float)
    shortfall_surplus = Column(Float)
    additional_monthly_needed = Column(Float)
    success_probability = Column(Float)  # Monte Carlo simulation result
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    
    # Relationships
    profile = relationship("RetirementProfile", back_populates="scenarios")

class RetirementCalculation(Base):
    """Historical calculation results"""
    __tablename__ = 'retirement_calculations'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('retirement_profiles.id'), nullable=False)
    
    # Input snapshot
    calculation_date = Column(DateTime, default=datetime.utcnow)
    input_parameters = Column(JSON)
    
    # Key Results
    years_to_retirement = Column(Integer)
    retirement_years = Column(Integer)
    corpus_needed = Column(Float)
    projected_savings = Column(Float)
    shortfall_surplus = Column(Float)
    additional_monthly_needed = Column(Float)
    
    # Detailed Results
    yearly_projections = Column(JSON)
    withdrawal_strategies = Column(JSON)
    sensitivity_analysis = Column(JSON)
    
    # AI Analysis
    ai_insights = Column(Text)
    risk_assessment = Column(String(20))  # low, medium, high
    
    # Relationships
    profile = relationship("RetirementProfile", back_populates="calculations")

class RetirementAccount(Base):
    """Retirement account tracking"""
    __tablename__ = 'retirement_accounts'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('retirement_profiles.id'), nullable=False)
    
    account_type = Column(String(50), nullable=False)  # 401k, IRA, Roth_IRA, etc.
    account_name = Column(String(100))
    provider = Column(String(100))
    account_number_last4 = Column(String(4))
    
    # Financial Details
    current_balance = Column(Float, default=0.0)
    monthly_contribution = Column(Float, default=0.0)
    annual_contribution_limit = Column(Float)
    employer_match = Column(Float, default=0.0)
    vesting_schedule = Column(String(100))
    
    # Tax Details
    is_pre_tax = Column(Boolean, default=True)
    is_roth = Column(Boolean, default=False)
    is_after_tax = Column(Boolean, default=False)
    
    # Investment Details
    expense_ratio = Column(Float, default=0.0)
    expected_return = Column(Float)
    risk_level = Column(String(20))  # conservative, moderate, aggressive
    asset_allocation = Column(JSON)  # stocks, bonds, alternatives percentages
    
    # Status
    is_active = Column(Boolean, default=True)
    is_rollover_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("RetirementProfile", back_populates="accounts")

class RetirementGoal(Base):
    """Retirement goals and milestones"""
    __tablename__ = 'retirement_goals'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('retirement_profiles.id'), nullable=False)
    
    goal_name = Column(String(100), nullable=False)
    description = Column(Text)
    goal_type = Column(String(50))  # corpus, income, expense, lifestyle
    target_amount = Column(Float, nullable=False)
    target_date = Column(DateTime)
    priority = Column(Integer, default=1)  # 1=High, 2=Medium, 3=Low
    
    # Progress Tracking
    current_progress = Column(Float, default=0.0)
    progress_percentage = Column(Float, default=0.0)
    is_achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime)
    
    # Goal Details
    monthly_required = Column(Float)  # Monthly amount needed to achieve goal
    years_to_goal = Column(Float)
    difficulty_score = Column(Float)  # 1-10 scale
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("RetirementProfile", back_populates="goals")

# Analysis and Insights Models
class FinancialInsight(Base):
    """AI-generated financial insights"""
    __tablename__ = 'financial_insights'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    
    insight_type = Column(String(50), nullable=False)  # retirement, budgeting, investment
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Metadata
    generated_date = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    # Action tracking
    recommended_action = Column(String(200))
    action_taken = Column(Boolean, default=False)
    action_date = Column(DateTime)

class MarketData(Base):
    """Market data for analysis"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    data_date = Column(DateTime, nullable=False)
    
    # Market Indicators
    sp500_return = Column(Float)
    bond_yield_10yr = Column(Float)
    inflation_rate = Column(Float)
    unemployment_rate = Column(Float)
    
    # Economic Indicators
    gdp_growth = Column(Float)
    consumer_confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Document and OCR Models
class FinancialDocument(Base):
    """Uploaded financial documents"""
    __tablename__ = 'financial_documents'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    
    document_type = Column(String(50), nullable=False)  # statement, tax_return, paystub
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    # OCR Results
    extracted_text = Column(Text)
    extracted_data = Column(JSON)  # Structured data from OCR
    processing_status = Column(String(20), default='pending')  # pending, processed, error
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

# User Preferences and Settings
class UserPreferences(Base):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, unique=True)
    
    # Display Preferences
    currency = Column(String(3), default='USD')
    date_format = Column(String(20), default='MM/DD/YYYY')
    number_format = Column(String(20), default='US')
    theme = Column(String(20), default='light')
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    retirement_alerts = Column(Boolean, default=True)
    goal_reminders = Column(Boolean, default=True)
    market_updates = Column(Boolean, default=False)
    
    # Privacy Settings
    data_sharing_consent = Column(Boolean, default=False)
    analytics_consent = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper functions for model operations
def create_all_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)

def drop_all_tables(engine):
    """Drop all database tables - use with caution!"""
    Base.metadata.drop_all(engine)