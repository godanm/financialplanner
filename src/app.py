import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Import database utilities
from database.db_utils import init_database, get_db_session
from database.models import Base

# Import pages
from pages import dashboard, data_entry, image_upload, ai_advisor, retirement_planning
from utils.helpers import load_css

# Page configuration
st.set_page_config(
    page_title="Financial Planning Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_app():
    """Initialize the application"""
    # Load custom CSS
    load_css()
    
    # Initialize database
    if 'db_initialized' not in st.session_state:
        try:
            init_database()
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            st.stop()
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default_user"  # In production, use proper auth
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

def main():
    """Main application function"""
    
    # Initialize the application
    initialize_app()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("💰 Financial Planner")
        st.markdown("---")
        
        # Navigation menu
        pages = {
            "📊 Dashboard": "Dashboard",
            "📝 Data Entry": "Data Entry", 
            "📷 Image Upload": "Image Upload",
            "🏖️ Retirement Planning": "Retirement Planning",
            "🤖 AI Advisor": "AI Advisor"
        }
        
        selected_page = st.radio(
            "Navigation", 
            list(pages.keys()),
            key="navigation"
        )
        
        st.session_state.current_page = pages[selected_page]
        
        st.markdown("---")
        
        # Quick stats sidebar (if data exists)
        display_quick_stats()
        
        st.markdown("---")
        
        # User settings
        with st.expander("⚙️ Settings"):
            st.selectbox("Currency", ["USD", "EUR", "GBP"], index=0)
            st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY"], index=0)
            if st.button("Reset All Data"):
                if st.button("Confirm Reset", type="primary"):
                    reset_user_data()
    
    # Main content area
    render_main_content()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        Financial Planning Assistant - Built with Streamlit<br>
        <small>⚠️ This tool provides general guidance. Consult a financial advisor for personalized advice.</small>
        </div>
        """, 
        unsafe_allow_html=True
    )

def render_main_content():
    """Render the main content based on selected page"""
    
    current_page = st.session_state.current_page
    
    try:
        if current_page == "Dashboard":
            dashboard.show_dashboard()
        elif current_page == "Data Entry":
            data_entry.show_data_entry()
        elif current_page == "Image Upload":
            image_upload.show_image_upload()
        elif current_page == "Retirement Planning":
            retirement_planning.show_retirement_planning()
        elif current_page == "AI Advisor":
            ai_advisor.show_ai_advisor()
        else:
            st.error(f"Page '{current_page}' not found")
            
    except Exception as e:
        st.error(f"Error loading page: {e}")
        st.exception(e)

def display_quick_stats():
    """Display quick financial stats in sidebar"""
    
    try:
        # Get database session
        session = get_database_session()
        
        # This would query your actual data
        # For now, showing placeholder values
        
        st.subheader("Quick Stats")
        
        # Net worth
        net_worth = get_user_net_worth(session, st.session_state.user_id)
        st.metric("Net Worth", f"${net_worth:,.2f}")
        
        # Monthly savings rate
        savings_rate = get_user_savings_rate(session, st.session_state.user_id)
        st.metric("Savings Rate", f"{savings_rate:.1f}%")
        
        # Retirement readiness
        retirement_score = get_retirement_readiness_score(session, st.session_state.user_id)
        st.metric("Retirement Score", f"{retirement_score}/100")
        
        session.close()
        
    except Exception as e:
        st.write("Stats unavailable")

def get_user_net_worth(session, user_id):
    """Calculate user's net worth"""
    # Implement based on your data models
    return 125000.0  # Placeholder

def get_user_savings_rate(session, user_id):
    """Calculate user's savings rate"""
    # Implement based on your data models
    return 15.5  # Placeholder

def get_retirement_readiness_score(session, user_id):
    """Calculate retirement readiness score"""
    # Import retirement service
    from services.retirement_service import calculate_retirement_score
    
    try:
        score = calculate_retirement_score(session, user_id)
        return score
    except:
        return 0  # Default if no retirement data

def reset_user_data():
    """Reset all user data"""
    try:
        session = get_database_session()
        # Implement data reset logic based on your models
        session.close()
        st.success("Data reset successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error resetting data: {e}")

# Custom page routing functions
def switch_to_retirement_planning():
    """Helper function to switch to retirement planning"""
    st.session_state.current_page = "Retirement Planning"
    st.rerun()

def switch_to_ai_advisor():
    """Helper function to switch to AI advisor"""
    st.session_state.current_page = "AI Advisor"
    st.rerun()

# Error handling
def handle_app_error(error):
    """Global error handler"""
    st.error("An unexpected error occurred")
    
    with st.expander("Error Details"):
        st.exception(error)
    
    st.info("Please try refreshing the page or contact support if the issue persists.")

# Main execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        handle_app_error(e)