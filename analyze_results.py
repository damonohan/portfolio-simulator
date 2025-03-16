#!/usr/bin/env python3
"""
Portfolio Simulator - Result Analysis Utilities

This script provides utilities for analyzing portfolio simulation results
stored in the SQLite database.
"""

import os
import sys
import argparse
import yaml
import logging
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_simulation_data(db_path):
    """
    Load simulation data from the SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database
        
    Returns:
        tuple: (simulations_df, yearly_results_df, market_conditions_df)
    """
    logger.info(f"Loading simulation data from {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Load simulations table
        simulations_df = pd.read_sql_query("SELECT * FROM simulations", conn)
        
        # Load yearly results table
        yearly_results_df = pd.read_sql_query("SELECT * FROM yearly_results", conn)
        
        # Load market conditions table
        market_conditions_df = pd.read_sql_query("SELECT * FROM market_conditions", conn)
        
        conn.close()
        
        logger.info(f"Loaded {len(simulations_df)} simulations and {len(yearly_results_df)} yearly records")
        
        return simulations_df, yearly_results_df, market_conditions_df
        
    except Exception as e:
        logger.error(f"Error loading simulation data: {e}")
        raise

def analyze_success_rates(simulations_df, output_dir=None):
    """
    Analyze success rates by various parameters.
    
    Args:
        simulations_df (DataFrame): DataFrame containing simulation results
        output_dir (str): Directory to save output files
    
    Returns:
        dict: Dictionary containing success rate analysis results
    """
    logger.info("Analyzing success rates")
    
    try:
        # Calculate overall success rate
        total_simulations = len(simulations_df)
        successful_simulations = len(simulations_df[simulations_df['success_flag'] == 1])
        overall_success_rate = successful_simulations / total_simulations if total_simulations > 0 else 0
        
        logger.info(f"Overall success rate: {overall_success_rate:.2%} ({successful_simulations}/{total_simulations})")
        
        # Success rates by portfolio type
        success_by_portfolio = simulations_df.groupby('portfolio_type')['success_flag'].mean()
        
        # Success rates by protection level (for portfolios with notes)
        notes_df = simulations_df[simulations_df['note_allocation'] > 0]
        success_by_protection = notes_df.groupby('protection_level')['success_flag'].mean()
        
        # Success rates by withdrawal rate
        success_by_withdrawal = simulations_df.groupby('withdrawal_rate')['success_flag'].mean()
        
        # Success rates by start year
        success_by_start_year = simulations_df.groupby('start_year')['success_flag'].mean()
        
        # Success rates by time horizon
        success_by_horizon = simulations_df.groupby('time_horizon')['success_flag'].mean()
        
        # Success rates by portfolio type and withdrawal rate
        success_by_portfolio_withdrawal = simulations_df.groupby(['portfolio_type', 'withdrawal_rate'])['success_flag'].mean().unstack()
        
        # Create analysis results dictionary
        results = {
            'overall_success_rate': overall_success_rate,
            'success_by_portfolio': success_by_portfolio,
            'success_by_protection': success_by_protection,
            'success_by_withdrawal': success_by_withdrawal,
            'success_by_start_year': success_by_start_year,
            'success_by_horizon': success_by_horizon,
            'success_by_portfolio_withdrawal': success_by_portfolio_withdrawal
        }
        
        # Save results to CSV if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save overall results
            overall_df = pd.DataFrame({
                'metric': ['overall_success_rate'],
                'value': [overall_success_rate]
            })
            overall_df.to_csv(os.path.join(output_dir, 'overall_success_rate.csv'), index=False)
            
            # Save grouped results
            success_by_portfolio.to_csv(os.path.join(output_dir, 'success_by_portfolio.csv'))
            success_by_protection.to_csv(os.path.join(output_dir, 'success_by_protection.csv'))
            success_by_withdrawal.to_csv(os.path.join(output_dir, 'success_by_withdrawal.csv'))
            success_by_start_year.to_csv(os.path.join(output_dir, 'success_by_start_year.csv'))
            success_by_horizon.to_csv(os.path.join(output_dir, 'success_by_horizon.csv'))
            success_by_portfolio_withdrawal.to_csv(os.path.join(output_dir, 'success_by_portfolio_withdrawal.csv'))
            
            logger.info(f"Success rate analysis results saved to {output_dir}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error analyzing success rates: {e}")
        raise

def analyze_terminal_values(simulations_df, output_dir=None):
    """
    Analyze terminal values by various parameters.
    
    Args:
        simulations_df (DataFrame): DataFrame containing simulation results
        output_dir (str): Directory to save output files
    
    Returns:
        dict: Dictionary containing terminal value analysis results
    """
    logger.info("Analyzing terminal values")
    
    try:
        # Overall statistics
        overall_stats = simulations_df['terminal_value'].describe()
        inflation_adjusted_stats = simulations_df['inflation_adjusted_terminal'].describe()
        
        logger.info(f"Overall terminal value statistics:\n{overall_stats}")
        
        # Terminal values by portfolio type
        terminal_by_portfolio = simulations_df.groupby('portfolio_type')['terminal_value'].mean()
        
        # Terminal values by protection level (for portfolios with notes)
        notes_df = simulations_df[simulations_df['note_allocation'] > 0]
        terminal_by_protection = notes_df.groupby('protection_level')['terminal_value'].mean()
        
        # Terminal values by withdrawal rate
        terminal_by_withdrawal = simulations_df.groupby('withdrawal_rate')['terminal_value'].mean()
        
        # Terminal values by start year
        terminal_by_start_year = simulations_df.groupby('start_year')['terminal_value'].mean()
        
        # Terminal values by time horizon
        terminal_by_horizon = simulations_df.groupby('time_horizon')['terminal_value'].mean()
        
        # Terminal values by portfolio type and withdrawal rate
        terminal_by_portfolio_withdrawal = simulations_df.groupby(['portfolio_type', 'withdrawal_rate'])['terminal_value'].mean().unstack()
        
        # Create analysis results dictionary
        results = {
            'overall_stats': overall_stats,
            'inflation_adjusted_stats': inflation_adjusted_stats,
            'terminal_by_portfolio': terminal_by_portfolio,
            'terminal_by_protection': terminal_by_protection,
            'terminal_by_withdrawal': terminal_by_withdrawal,
            'terminal_by_start_year': terminal_by_start_year,
            'terminal_by_horizon': terminal_by_horizon,
            'terminal_by_portfolio_withdrawal': terminal_by_portfolio_withdrawal
        }
        
        # Save results to CSV if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save overall results
            overall_stats.to_csv(os.path.join(output_dir, 'terminal_value_stats.csv'))
            inflation_adjusted_stats.to_csv(os.path.join(output_dir, 'inflation_adjusted_terminal_stats.csv'))
            
            # Save grouped results
            terminal_by_portfolio.to_csv(os.path.join(output_dir, 'terminal_by_portfolio.csv'))
            terminal_by_protection.to_csv(os.path.join(output_dir, 'terminal_by_protection.csv'))
            terminal_by_withdrawal.to_csv(os.path.join(output_dir, 'terminal_by_withdrawal.csv'))
            terminal_by_start_year.to_csv(os.path.join(output_dir, 'terminal_by_start_year.csv'))
            terminal_by_horizon.to_csv(os.path.join(output_dir, 'terminal_by_horizon.csv'))
            terminal_by_portfolio_withdrawal.to_csv(os.path.join(output_dir, 'terminal_by_portfolio_withdrawal.csv'))
            
            logger.info(f"Terminal value analysis results saved to {output_dir}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error analyzing terminal values: {e}")
        raise

def plot_portfolio_growth(yearly_results_df, simulations_df, output_dir=None, selected_sim_ids=None):
    """
    Plot portfolio growth for selected simulations.
    
    Args:
        yearly_results_df (DataFrame): DataFrame containing yearly results
        simulations_df (DataFrame): DataFrame containing simulation parameters
        output_dir (str): Directory to save output files
        selected_sim_ids (list): List of simulation IDs to plot (if None, selects representative examples)
    
    Returns:
        dict: Dictionary containing generated plot file paths
    """
    logger.info("Plotting portfolio growth")
    
    try:
        # If no specific simulations are selected, choose representative examples
        if selected_sim_ids is None:
            # Sample one simulation for each portfolio type with 4% withdrawal rate and 10% protection
            selected_sim_ids = []
            for portfolio_type in simulations_df['portfolio_type'].unique():
                filtered = simulations_df[
                    (simulations_df['portfolio_type'] == portfolio_type) & 
                    (simulations_df['withdrawal_rate'] == 0.04)
                ]
                
                if not filtered.empty:
                    # For portfolios with notes, select one with 10% protection if available
                    if portfolio_type != 'traditional':
                        note_sim = filtered[filtered['protection_level'] == 0.10]
                        if not note_sim.empty:
                            selected_sim_ids.append(note_sim.iloc[0]['sim_id'])
                            continue
                    
                    # Otherwise just select the first one
                    selected_sim_ids.append(filtered.iloc[0]['sim_id'])
        
        # Create output directory if provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        plot_files = {}
        
        # Plot each selected simulation
        for sim_id in selected_sim_ids:
            # Get simulation details
            sim_details = simulations_df[simulations_df['sim_id'] == sim_id].iloc[0]
            
            # Get yearly results for this simulation
            sim_results = yearly_results_df[yearly_results_df['sim_id'] == sim_id].sort_values('year')
            
            if sim_results.empty:
                logger.warning(f"No yearly results found for simulation {sim_id}")
                continue
            
            # Plot portfolio growth
            plt.figure(figsize=(12, 8))
            
            # Plot total portfolio value
            plt.plot(sim_results['year'], sim_results['ending_value'], 
                    label='Portfolio Value', linewidth=2)
            
            # Plot component values
            plt.plot(sim_results['year'], sim_results['equity_value'], 
                    label='Equity', linestyle='--')
            plt.plot(sim_results['year'], sim_results['note_value'], 
                    label='Structured Notes', linestyle='--')
            plt.plot(sim_results['year'], sim_results['bond_value'], 
                    label='Bonds', linestyle='--')
            
            # Plot cumulative withdrawals
            cumulative_withdrawals = sim_results['withdrawal_amount'].cumsum()
            plt.plot(sim_results['year'], cumulative_withdrawals, 
                    label='Cumulative Withdrawals', linestyle=':')
            
            # Add labels and title
            plt.xlabel('Year')
            plt.ylabel('Value ($)')
            
            portfolio_type = sim_details['portfolio_type']
            withdrawal_rate = sim_details['withdrawal_rate'] * 100
            protection_level = sim_details['protection_level'] * 100 if sim_details['protection_level'] is not None else None
            start_year = sim_details['start_year']
            
            if protection_level is not None:
                title = f"Portfolio Growth - {portfolio_type.capitalize()} ({protection_level:.0f}% Protection) - {withdrawal_rate:.1f}% Withdrawal - Starting {start_year}"
            else:
                title = f"Portfolio Growth - {portfolio_type.capitalize()} - {withdrawal_rate:.1f}% Withdrawal - Starting {start_year}"
            
            plt.title(title)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save plot if output_dir is provided
            if output_dir:
                plot_file = os.path.join(output_dir, f"portfolio_growth_{sim_id}.png")
                plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                plot_files[sim_id] = plot_file
                plt.close()
                logger.info(f"Saved portfolio growth plot to {plot_file}")
            else:
                plt.show()
        
        return plot_files
    
    except Exception as e:
        logger.error(f"Error plotting portfolio growth: {e}")
        raise

def compare_protection_levels(yearly_results_df, simulations_df, output_dir=None):
    """
    Compare the performance of different protection levels for structured notes.
    
    Args:
        yearly_results_df (DataFrame): DataFrame containing yearly results
        simulations_df (DataFrame): DataFrame containing simulation parameters
        output_dir (str): Directory to save output files
    
    Returns:
        DataFrame: Comparison of protection levels
    """
    logger.info("Comparing protection levels")
    
    try:
        # Filter to only include simulations with notes
        notes_df = simulations_df[simulations_df['note_allocation'] > 0]
        
        # Group by relevant parameters and calculate mean terminal value
        comparison = notes_df.groupby(['portfolio_type', 'protection_level', 'withdrawal_rate', 'time_horizon'])['terminal_value'].mean().reset_index()
        
        # Calculate success rates
        success_rates = notes_df.groupby(['portfolio_type', 'protection_level', 'withdrawal_rate', 'time_horizon'])['success_flag'].mean().reset_index()
        success_rates.rename(columns={'success_flag': 'success_rate'}, inplace=True)
        
        # Merge the results
        comparison = pd.merge(comparison, success_rates, on=['portfolio_type', 'protection_level', 'withdrawal_rate', 'time_horizon'])
        
        # Save to CSV if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            csv_path = os.path.join(output_dir, 'protection_level_comparison.csv')
            comparison.to_csv(csv_path, index=False)
            logger.info(f"Protection level comparison saved to {csv_path}")
            
            # Create a pivot table for easier visualization
            pivot = pd.pivot_table(
                comparison, 
                values=['terminal_value', 'success_rate'],
                index=['portfolio_type', 'withdrawal_rate', 'time_horizon'],
                columns=['protection_level']
            )
            
            pivot_path = os.path.join(output_dir, 'protection_level_pivot.csv')
            pivot.to_csv(pivot_path)
            logger.info(f"Protection level pivot table saved to {pivot_path}")
            
            # Plot the comparison
            plt.figure(figsize=(12, 8))
            
            for portfolio_type in comparison['portfolio_type'].unique():
                for withdrawal_rate in comparison['withdrawal_rate'].unique():
                    for horizon in comparison['time_horizon'].unique():
                        subset = comparison[
                            (comparison['portfolio_type'] == portfolio_type) &
                            (comparison['withdrawal_rate'] == withdrawal_rate) &
                            (comparison['time_horizon'] == horizon)
                        ]
                        
                        if not subset.empty:
                            label = f"{portfolio_type.capitalize()} - {withdrawal_rate*100:.1f}% - {horizon}yr"
                            plt.plot(subset['protection_level'] * 100, subset['terminal_value'], 
                                    marker='o', label=label)
            
            plt.xlabel('Protection Level (%)')
            plt.ylabel('Average Terminal Value ($)')
            plt.title('Average Terminal Value by Protection Level')
            plt.grid(True, alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plot_path = os.path.join(output_dir, 'protection_level_comparison.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Protection level comparison plot saved to {plot_path}")
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error comparing protection levels: {e}")
        raise

def compare_portfolio_types(simulations_df, output_dir=None):
    """
    Compare the performance of different portfolio types.
    
    Args:
        simulations_df (DataFrame): DataFrame containing simulation parameters
        output_dir (str): Directory to save output files
    
    Returns:
        DataFrame: Comparison of portfolio types
    """
    logger.info("Comparing portfolio types")
    
    try:
        # Group by relevant parameters and calculate mean terminal value
        comparison = simulations_df.groupby(['portfolio_type', 'withdrawal_rate', 'time_horizon'])['terminal_value'].mean().reset_index()
        
        # Calculate success rates
        success_rates = simulations_df.groupby(['portfolio_type', 'withdrawal_rate', 'time_horizon'])['success_flag'].mean().reset_index()
        success_rates.rename(columns={'success_flag': 'success_rate'}, inplace=True)
        
        # Calculate risk metrics
        volatility = simulations_df.groupby(['portfolio_type', 'withdrawal_rate', 'time_horizon'])['volatility'].mean().reset_index()
        max_drawdown = simulations_df.groupby(['portfolio_type', 'withdrawal_rate', 'time_horizon'])['max_drawdown'].mean().reset_index()
        
        # Merge the results
        comparison = pd.merge(comparison, success_rates, on=['portfolio_type', 'withdrawal_rate', 'time_horizon'])
        comparison = pd.merge(comparison, volatility, on=['portfolio_type', 'withdrawal_rate', 'time_horizon'])
        comparison = pd.merge(comparison, max_drawdown, on=['portfolio_type', 'withdrawal_rate', 'time_horizon'])
        
        # Save to CSV if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            csv_path = os.path.join(output_dir, 'portfolio_type_comparison.csv')
            comparison.to_csv(csv_path, index=False)
            logger.info(f"Portfolio type comparison saved to {csv_path}")
            
            # Create a pivot table for easier visualization
            pivot = pd.pivot_table(
                comparison, 
                values=['terminal_value', 'success_rate', 'volatility', 'max_drawdown'],
                index=['withdrawal_rate', 'time_horizon'],
                columns=['portfolio_type']
            )
            
            pivot_path = os.path.join(output_dir, 'portfolio_type_pivot.csv')
            pivot.to_csv(pivot_path)
            logger.info(f"Portfolio type pivot table saved to {pivot_path}")
            
            # Plot terminal values comparison
            plt.figure(figsize=(12, 8))
            
            for withdrawal_rate in comparison['withdrawal_rate'].unique():
                for horizon in comparison['time_horizon'].unique():
                    subset = comparison[
                        (comparison['withdrawal_rate'] == withdrawal_rate) &
                        (comparison['time_horizon'] == horizon)
                    ]
                    
                    if not subset.empty:
                        label = f"{withdrawal_rate*100:.1f}% - {horizon}yr"
                        plt.bar(
                            x=subset['portfolio_type'], 
                            height=subset['terminal_value'],
                            label=label,
                            alpha=0.7
                        )
            
            plt.xlabel('Portfolio Type')
            plt.ylabel('Average Terminal Value ($)')
            plt.title('Average Terminal Value by Portfolio Type')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plot_path = os.path.join(output_dir, 'portfolio_type_terminal_comparison.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Plot success rate comparison
            plt.figure(figsize=(12, 8))
            
            for withdrawal_rate in comparison['withdrawal_rate'].unique():
                for horizon in comparison['time_horizon'].unique():
                    subset = comparison[
                        (comparison['withdrawal_rate'] == withdrawal_rate) &
                        (comparison['time_horizon'] == horizon)
                    ]
                    
                    if not subset.empty:
                        label = f"{withdrawal_rate*100:.1f}% - {horizon}yr"
                        plt.bar(
                            x=subset['portfolio_type'], 
                            height=subset['success_rate'] * 100,
                            label=label,
                            alpha=0.7
                        )
            
            plt.xlabel('Portfolio Type')
            plt.ylabel('Success Rate (%)')
            plt.title('Success Rate by Portfolio Type')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plot_path = os.path.join(output_dir, 'portfolio_type_success_comparison.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Portfolio type comparison plots saved to {output_dir}")
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error comparing portfolio types: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Analyze portfolio simulation results')
    parser.add_argument('--db', type=str, required=True,
                        help='Path to the SQLite database')
    parser.add_argument('--output', type=str, default=None,
                        help='Directory to save output files')
    parser.add_argument('--plot-growth', action='store_true',
                        help='Plot portfolio growth curves')
    parser.add_argument('--compare-protection', action='store_true',
                        help='Compare different protection levels')
    parser.add_argument('--compare-portfolios', action='store_true',
                        help='Compare different portfolio types')
    parser.add_argument('--all', action='store_true',
                        help='Run all analyses')
    args = parser.parse_args()
    
    try:
        # Create output directory if provided
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(args.output, f"analysis_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = None
        
        # Load simulation data
        simulations_df, yearly_results_df, market_conditions_df = load_simulation_data(args.db)
        
        # Run analyses based on arguments
        if args.all or args.plot_growth:
            plot_growth_dir = os.path.join(output_dir, "portfolio_growth") if output_dir else None
            plot_portfolio_growth(yearly_results_df, simulations_df, plot_growth_dir)
        
        if args.all or args.compare_protection:
            protection_dir = os.path.join(output_dir, "protection_comparison") if output_dir else None
            compare_protection_levels(yearly_results_df, simulations_df, protection_dir)
        
        if args.all or args.compare_portfolios:
            portfolio_dir = os.path.join(output_dir, "portfolio_comparison") if output_dir else None
            compare_portfolio_types(simulations_df, portfolio_dir)
        
        # Always run these basic analyses
        success_dir = os.path.join(output_dir, "success_rates") if output_dir else None
        analyze_success_rates(simulations_df, success_dir)
        
        terminal_dir = os.path.join(output_dir, "terminal_values") if output_dir else None
        analyze_terminal_values(simulations_df, terminal_dir)
        
        if output_dir:
            logger.info(f"All analyses complete. Results saved to {output_dir}")
        else:
            logger.info("All analyses complete. No output directory provided.")
        
    except Exception as e:
        logger.error(f"Error in analysis process: {e}")
        raise

if __name__ == "__main__":
    main()