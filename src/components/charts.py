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
    fig.update