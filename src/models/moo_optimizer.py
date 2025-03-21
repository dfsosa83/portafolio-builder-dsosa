import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import io
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.bounds_repair import BoundsRepair
from pymoo.optimize import minimize
from pymoo.core.callback import Callback
from pypfopt import expected_returns, risk_models  # Added missing imports

class WeightRepair(BoundsRepair):
    def _do(self, problem, X, **kwargs):
        X[X < 0.0] = 0.0
        sums = X.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1e-12
        X = X / sums
        return X

class PortfolioOptimization(ElementwiseProblem):
    def __init__(self, mu, cov, returns, **params):
        self.params = params
        self.returns = returns.values
        self.mu = mu.values
        self.cov = cov.values
        self.x0 = np.array([1/len(mu)]*len(mu))  # Equal initial weights
        
        super().__init__(
            n_var=len(mu),
            n_obj=2,
            n_constr=2,
            xl=0.001,
            xu=0.999
        )

    def _evaluate(self, x, out, *args, **kwargs):
        portfolio_return = x @ self.mu
        sharpe_ratio = calculate_sharpe_ratio(x, self.mu, self.cov, self.params['risk_free_rate'])
        
        turnover = np.sum(np.abs(x - self.x0)) 
        max_dd = calculate_max_drawdown(x, self.returns)
        
        out["F"] = [-portfolio_return, -sharpe_ratio]
        out["G"] = [
            turnover - self.params['max_turnover'],
            max_dd - self.params['max_drawdown']
        ]

class ConvergenceCallback(Callback):
    def __init__(self):
        super().__init__()
        self.data["gen"] = []
        self.data["f_min"] = []

    def notify(self, algorithm):
        self.data["gen"].append(algorithm.n_gen)
        self.data["f_min"].append(algorithm.pop.get("F").min(axis=0))

@st.cache_data
def portfolio_optimizer(symbols, **user_params):
    start_date = (datetime.now() - relativedelta(years=5)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    df = yf.download(
        tickers=symbols,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=True,
        progress=False
    )['Close'].dropna()
    
    # Calculate financial metrics using PyPortfolioOpt
    mu = expected_returns.mean_historical_return(df)
    cov = risk_models.sample_cov(df)
    returns = df.pct_change().dropna()
    
    # Optimization setup
    problem = PortfolioOptimization(mu=mu, cov=cov, returns=returns, **user_params)
    algorithm = NSGA2(
        pop_size=100,
        crossover=SBX(eta=15, prob=0.9),
        mutation=PM(eta=10, prob=0.1),
        repair=WeightRepair(),
        eliminate_duplicates=True
    )

    res = minimize(problem, algorithm, ('n_gen', 200), seed=1, verbose=False)
    
    # Extract results
    sharpe_values = -res.F[:, 1]
    best_idx = np.argmax(sharpe_values)
    optimal_weights = res.X[best_idx]
    
    # Calculate returns and metrics
    portfolio_returns = returns @ optimal_weights
    cumulative_returns = (1 + portfolio_returns).cumprod() - 1
    
    # Equal weight comparison
    equal_weights = np.ones(len(symbols)) / len(symbols)
    equal_returns = returns @ equal_weights
    equal_cumulative = (1 + equal_returns).cumprod() - 1
    
    # Generate comparison plot
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_returns.index, cumulative_returns, label='Optimal Portfolio')
    plt.plot(equal_cumulative.index, equal_cumulative, label='Equal Weight')
    plt.title("Portfolio Performance vs Equal Weight")
    plt.ylabel("Return")
    plt.xlabel("Date")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    plt.close()
    
    # Prepare output
    return {
        'sharpe': calculate_sharpe_ratio(optimal_weights, mu.values, cov.values, user_params['risk_free_rate']),
        'annual_return': np.prod(1 + portfolio_returns) ** (252/len(portfolio_returns)) - 1,
        'annual_volatility': np.std(portfolio_returns) * np.sqrt(252),
        'max_drawdown': calculate_max_drawdown(optimal_weights, returns.values),
        'cumulative_returns': cumulative_returns,
        'equal_cumulative': equal_cumulative,
        'allocation_df': pd.DataFrame({
            'Ticker': symbols,
            'Weight': optimal_weights,
            'Amount ($)': optimal_weights * 10000
        }),
        'weights_df': pd.DataFrame(optimal_weights, index=symbols, columns=['Weight']),
        'img_buffer': img_buffer  # Now includes matplotlib figure
    }

# Helper functions
def calculate_sharpe_ratio(weights, mu, cov, risk_free_rate):
    port_return = weights @ mu
    port_vol = np.sqrt(weights.T @ cov @ weights)
    return (port_return - risk_free_rate) / port_vol if port_vol != 0 else 0

def calculate_max_drawdown(weights, returns):
    pf_returns = returns @ weights
    cumulative = (1 + pd.Series(pf_returns)).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()
