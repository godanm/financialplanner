import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def create_retirement_projection_chart(yearly_data: List[Dict], profile) -> go.Figure:
    """Create retirement savings projection chart"""
    
    if not yearly_data:
        return go.Figure()
    
    df = pd.DataFrame(yearly_data)
    
    # Split data by phase
    accumulation = df[df['phase'] == 'accumulation']
    withdrawal = df[df['phase'] == 'withdrawal']
    
    fig = go.Figure()
    
    # Accumulation phase
    if not accumulation.empty:
        fig.add_trace(go.Scatter(
            x=accumulation['age'],
            y=accumulation['balance'],
            mode='lines+markers',
            name='Accumulation Phase',
            line=dict(color='#2E8B57', width=4),
            marker=dict(size=6),
            hovertemplate='<b>Age %{x}</b><br>' +
                         'Balance: $%{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
    
    # Withdrawal phase
    if not withdrawal.empty:
        fig.add_trace(go.Scatter(
            x=withdrawal['age'],
            y=withdrawal['balance'],
            mode='lines+markers',
            name='Withdrawal Phase',
            line=dict(color='#DC143C', width=4),
            marker=dict(size=6),
            hovertemplate='<b>Age %{x}</b><br>' +
                         'Balance: $%{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
    
    # Add retirement age marker
    retirement_balance = df[df['age'] == profile.retirement_age]['balance'].iloc[0] if not df[df['age'] == profile.retirement_age].empty else 0
    
    fig.add_shape(
        type="line",
        x0=profile.retirement_age,
        y0=0,
        x1=profile.retirement_age,
        y1=retirement_balance,
        line=dict(color="orange", width=3, dash="dash"),
    )
    
    fig.add_annotation(
        x=profile.retirement_age,
        y=retirement_balance * 1.1,
        text=f"Retirement<br>Age {profile.retirement_age}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="orange",
        bgcolor="white",
        bordercolor="orange",
        borderwidth=2
    )
    
    # Styling
    fig.update_layout(
        title={
            'text': 'Retirement Savings Projection Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Age",
        yaxis_title="Balance ($)",
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=500
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    fig.update_xaxis(dtick=5)
    
    # Add fill under curves
    if not accumulation.empty:
        fig.add_trace(go.Scatter(
            x=accumulation['age'],
            y=accumulation['balance'],
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(46, 139, 87, 0.1)',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return fig

def create_sensitivity_chart(sensitivity_data: Dict, base_value: float) -> go.Figure:
    """Create sensitivity analysis chart"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Investment Return Impact', 'Inflation Rate Impact', 
                       'Retirement Age Impact', 'Monthly Contribution Impact'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Define chart positions
    chart_positions = [
        ('pre_retirement_return_rate', 1, 1, 'Investment Return Change (%)', 100),
        ('inflation_rate', 1, 2, 'Inflation Rate Change (%)', 100),
        ('retirement_age', 2, 1, 'Retirement Age Change (years)', 1),
        ('monthly_contribution', 2, 2, 'Monthly Contribution Change ($)', 1)
    ]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, (key, row, col, x_title, multiplier) in enumerate(chart_positions):
        if key in sensitivity_data:
            data = sensitivity_data[key]
            
            x_vals = [d['change'] * multiplier for d in data]
            y_vals = [d['total_projected'] for d in data]
            
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines+markers',
                    name=key.replace('_', ' ').title(),
                    line=dict(color=colors[i], width=3),
                    marker=dict(size=8),
                    showlegend=False
                ),
                row=row, col=col
            )
            
            # Add baseline reference
            fig.add_hline(
                y=base_value,
                line_dash="dash",
                line_color="red",
                opacity=0.7,
                row=row, col=col
            )
            
            # Update subplot axes
            fig.update_xaxes(title_text=x_title, row=row, col=col)
            fig.update_yaxes(title_text="Total Projected ($)", tickformat="$,.0f", row=row, col=col)
    
    fig.update_layout(
        title={
            'text': 'Sensitivity Analysis - Impact on Total Retirement Savings',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=600,
        template='plotly_white'
    )
    
    return fig

def create_monte_carlo_chart(monte_carlo_results: Dict) -> go.Figure:
    """Create Monte Carlo simulation results chart"""
    
    # This would show distribution of outcomes
    # For now, create a simple success rate gauge
    
    success_rate = monte_carlo_results.get('success_rate', 0)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=success_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Retirement Success Probability"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 90], 'color': "lightgreen"},
                {'range': [90, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_withdrawal_strategy_comparison(strategies: Dict) -> go.Figure:
    """Create withdrawal strategy comparison chart"""
    
    strategy_names = []
    success_rates = []
    initial_withdrawals = []
    
    for key, strategy in strategies.items():
        strategy_names.append(strategy['name'])
        success_rates.append(strategy.get('success_rate', 0))
        
        if 'initial_withdrawal' in strategy:
            initial_withdrawals.append(strategy['initial_withdrawal'])
        elif 'annual_income' in strategy:
            initial_withdrawals.append(strategy['annual_income'])
        else:
            initial_withdrawals.append(0)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Success Rates', 'Annual Income'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Success rates
    fig.add_trace(
        go.Bar(
            x=strategy_names,
            y=success_rates,
            name='Success Rate (%)',
            marker_color='lightblue',
            text=[f"{rate}%" for rate in success_rates],
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Annual withdrawals
    fig.add_trace(
        go.Bar(
            x=strategy_names,
            y=initial_withdrawals,
            name='Annual Income ($)',
            marker_color='lightgreen',
            text=[f"${val:,.0f}" for val in initial_withdrawals],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title={
            'text': 'Withdrawal Strategy Comparison',
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        height=400,
        template='plotly_white'
    )
    
    fig.update_yaxes(title_text="Success Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Annual Income ($)", tickformat="$,.0f", row=1, col=2)
    
    return fig

def create_savings_breakdown_chart(projections: Dict) -> go.Figure:
    """Create savings breakdown pie chart"""
    
    current_savings_fv = projections.get('current_savings_future_value', 0)
    contributions_fv = projections.get('contributions_future_value', 0)
    
    labels = ['Current Savings Growth', 'Future Contributions']
    values = [current_savings_fv, contributions_fv]
    colors = ['#FF6B6B', '#4ECDC4']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': 'Retirement Savings Breakdown',
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        height=400
    )
    
    return fig

def create_goal_progress_chart(goals: List[Dict]) -> go.Figure:
    """Create goal progress chart"""
    
    if not goals:
        return go.Figure()
    
    goal_names = [goal['goal_name'] for goal in goals]
    target_amounts = [goal['target_amount'] for goal in goals]
    current_progress = [goal.get('current_progress', 0) for goal in goals]
    progress_percentages = [
        (progress / target * 100) if target > 0 else 0 
        for progress, target in zip(current_progress, target_amounts)
    ]
    
    fig = go.Figure()
    
    # Target amounts (background bars)
    fig.add_trace(go.Bar(
        x=goal_names,
        y=target_amounts,
        name='Target Amount',
        marker_color='lightgray',
        opacity=0.6
    ))
    
    # Current progress (overlay bars)
    fig.add_trace(go.Bar(
        x=goal_names,
        y=current_progress,
        name='Current Progress',
        marker_color='green',
        text=[f"{pct:.1f}%" for pct in progress_percentages],
        textposition='auto'
    ))
    
    fig.update_layout(
        title={
            'text': 'Retirement Goals Progress',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Goals",
        yaxis_title="Amount ($)",
        template='plotly_white',
        barmode='overlay',
        height=400
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    
    return fig

def create_cash_flow_chart(yearly_data: List[Dict]) -> go.Figure:
    """Create cash flow chart showing contributions and withdrawals"""
    
    if not yearly_data:
        return go.Figure()
    
    df = pd.DataFrame(yearly_data)
    
    fig = go.Figure()
    
    # Contributions (positive cash flow)
    contributions = df[df['contribution'] > 0]
    if not contributions.empty:
        fig.add_trace(go.Bar(
            x=contributions['age'],
            y=contributions['contribution'],
            name='Contributions',
            marker_color='green',
            opacity=0.7
        ))
    
    # Withdrawals (negative cash flow)
    withdrawals = df[df['withdrawal'] > 0]
    if not withdrawals.empty:
        fig.add_trace(go.Bar(
            x=withdrawals['age'],
            y=-withdrawals['withdrawal'],
            name='Withdrawals',
            marker_color='red',
            opacity=0.7
        ))
    
    # Investment returns
    fig.add_trace(go.Scatter(
        x=df['age'],
        y=df['investment_return'],
        mode='lines',
        name='Investment Returns',
        line=dict(color='blue', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title={
            'text': 'Retirement Cash Flow Analysis',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Age",
        yaxis_title="Cash Flow ($)",
        template='plotly_white',
        height=500,
        yaxis2=dict(
            title="Investment Returns ($)",
            overlaying='y',
            side='right',
            tickformat="$,.0f"
        )
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    
    return fig

def create_inflation_impact_chart(base_amount: float, years: int, inflation_rate: float) -> go.Figure:
    """Create chart showing inflation impact over time"""
    
    years_range = list(range(0, years + 1))
    real_values = [base_amount / ((1 + inflation_rate) ** year) for year in years_range]
    nominal_values = [base_amount for _ in years_range]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years_range,
        y=nominal_values,
        mode='lines',
        name='Nominal Value',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years_range,
        y=real_values,
        mode='lines',
        name='Real Value (Inflation Adjusted)',
        line=dict(color='red', width=3),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.1)'
    ))
    
    fig.update_layout(
        title={
            'text': f'Impact of {inflation_rate*100:.1f}% Inflation Over Time',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Years",
        yaxis_title="Value ($)",
        template='plotly_white',
        height=400
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    
    return fig

def create_account_allocation_chart(accounts: List[Dict]) -> go.Figure:
    """Create account allocation chart"""
    
    if not accounts:
        return go.Figure()
    
    account_types = [acc['account_type'] for acc in accounts]
    balances = [acc['current_balance'] for acc in accounts]
    
    # Color map for different account types
    color_map = {
        '401k': '#FF6B6B',
        'IRA': '#4ECDC4',
        'Roth_IRA': '#45B7D1',
        'Roth_401k': '#96CEB4',
        'HSA': '#FECA57',
        'Taxable': '#FF9FF3'
    }
    
    colors = [color_map.get(acc_type, '#95A5A6') for acc_type in account_types]
    
    fig = go.Figure(data=[go.Pie(
        labels=account_types,
        values=balances,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Balance: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': 'Retirement Account Allocation',
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        height=400
    )
    
    return fig

def create_tax_analysis_chart(tax_analysis: Dict) -> go.Figure:
    """Create tax analysis chart"""
    
    current_rate = tax_analysis.get('current_tax_rate', 0) * 100
    retirement_rate = tax_analysis.get('retirement_tax_rate', 0) * 100
    
    categories = ['Current Tax Rate', 'Retirement Tax Rate']
    rates = [current_rate, retirement_rate]
    colors = ['blue', 'orange']
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=rates,
        marker_color=colors,
        text=[f"{rate:.1f}%" for rate in rates],
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': 'Tax Rate Comparison',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title="Tax Rate (%)",
        template='plotly_white',
        height=300
    )
    
    return fig

def create_scenario_comparison_chart(scenarios: List[Dict]) -> go.Figure:
    """Create scenario comparison chart"""
    
    if not scenarios:
        return go.Figure()
    
    scenario_names = [s['scenario_name'] for s in scenarios]
    corpus_needed = [s.get('corpus_needed', 0) for s in scenarios]
    projected_savings = [s.get('projected_savings', 0) for s in scenarios]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=scenario_names,
        y=corpus_needed,
        name='Corpus Needed',
        marker_color='lightcoral',
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        x=scenario_names,
        y=projected_savings,
        name='Projected Savings',
        marker_color='lightblue',
        opacity=0.8
    ))
    
    fig.update_layout(
        title={
            'text': 'Scenario Comparison',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Scenarios",
        yaxis_title="Amount ($)",
        template='plotly_white',
        barmode='group',
        height=400
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    
    return fig

def create_risk_assessment_radar(risk_factors: Dict) -> go.Figure:
    """Create risk assessment radar chart"""
    
    categories = list(risk_factors.keys())
    values = list(risk_factors.values())
    
    # Close the radar chart
    categories += [categories[0]]
    values += [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Risk Profile',
        line_color='red',
        fillcolor='rgba(255,0,0,0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        title={
            'text': 'Retirement Risk Assessment',
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        height=400
    )
    
    return fig

def create_milestone_timeline(milestones: List[Dict]) -> go.Figure:
    """Create milestone timeline chart"""
    
    if not milestones:
        return go.Figure()
    
    ages = [m['target_age'] for m in milestones]
    amounts = [m['target_amount'] for m in milestones]
    names = [m['goal_name'] for m in milestones]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ages,
        y=amounts,
        mode='markers+lines+text',
        text=names,
        textposition='top center',
        marker=dict(size=12, color='blue'),
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title={
            'text': 'Retirement Milestones Timeline',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Age",
        yaxis_title="Target Amount ($)",
        template='plotly_white',
        height=400
    )
    
    fig.update_yaxis(tickformat="$,.0f")
    
    return fig

# Utility functions for chart creation
def format_hover_template(template: str) -> str:
    """Format hover template for consistency"""
    return template + '<extra></extra>'

def get_color_palette(n_colors: int) -> List[str]:
    """Get a color palette for charts"""
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    return colors[:n_colors] * (n_colors // len(colors) + 1)

def apply_chart_theme(fig: go.Figure, title: str = None) -> go.Figure:
    """Apply consistent theme to charts"""
    
    fig.update_layout(
        template='plotly_white',
        font=dict(size=12),
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='#2E4057')
        ) if title else None,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# Export function for external use
def create_comprehensive_retirement_report(results: Dict, profile) -> List[go.Figure]:
    """Create all charts for comprehensive report"""
    
    charts = []
    
    # Main projection chart
    if results.get('yearly_projections'):
        charts.append(create_retirement_projection_chart(results['yearly_projections'], profile))
    
    # Sensitivity analysis
    if results.get('sensitivity_analysis'):
        charts.append(create_sensitivity_chart(results['sensitivity_analysis'], 
                                             results['savings_projections']['total_projected_savings']))
    
    # Monte Carlo results
    if results.get('monte_carlo_results'):
        charts.append(create_monte_carlo_chart(results['monte_carlo_results']))
    
    # Withdrawal strategies
    if results.get('withdrawal_strategies'):
        charts.append(create_withdrawal_strategy_comparison(results['withdrawal_strategies']))
    
    # Savings breakdown
    if results.get('savings_projections'):
        charts.append(create_savings_breakdown_chart(results['savings_projections']))
    
    # Cash flow analysis
    if results.get('yearly_projections'):
        charts.append(create_cash_flow_chart(results['yearly_projections']))
    
    return charts