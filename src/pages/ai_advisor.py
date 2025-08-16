from flask import Blueprint, render_template, request, jsonify
from services.ai_service import get_ai_advice
from database.db_utils import get_db_session
import pandas as pd

ai_advisor_bp = Blueprint('ai_advisor', __name__)

@ai_advisor_bp.route('/ai_advisor', methods=['GET', 'POST'])
def ai_advisor():
    if request.method == 'POST':
        user_question = request.form.get('question')
        if user_question:
            session = get_db_session()
            expenses = pd.read_sql(session.query(Expense).statement, session.bind)
            income = pd.read_sql(session.query(Income).statement, session.bind)
            assets = pd.read_sql(session.query(Asset).statement, session.bind)
            liabilities = pd.read_sql(session.query(Liability).statement, session.bind)
            family = pd.read_sql(session.query(FamilyMember).statement, session.bind)

            context = {
                "monthly_expenses": expenses['amount'].sum(),
                "monthly_income": income['amount'].sum(),
                "total_assets": assets['current_value'].sum(),
                "total_liabilities": liabilities['amount'].sum(),
                "family_info": family.to_dict(orient='records')
            }

            advice = get_ai_advice(user_question, context)
            return jsonify({'advice': advice})
        else:
            return jsonify({'error': 'Please enter a question.'}), 400

    return render_template('ai_advisor.html')