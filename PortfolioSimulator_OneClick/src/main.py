import os
import logging
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from .data_processing import load_sp500_data, load_bond_returns, load_structured_notes, align_data
from .simulation import PortfolioSimulation

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Portfolio Simulator')
    
    # Data input files
    parser.add_argument('--sp500_file', default='data/sp500_returns.csv',
                        help='Path to S&P 500 returns CSV file')
    parser.add_argument('--bond_file', default='data/bond_returns.csv',
                        help='Path to bond returns CSV file')
    parser.add_argument('--notes_file', default='data/structured_notes.csv',
                        help='Path to structured notes CSV file')
    
    # Simulation parameters
    parser.add_argument('--start_year', type=int, default=2000,
                        help='First year of simulation')
    parser.add_argument('--end_year', type=int, default=2020,
                        help='Last year of simulation')
    parser.add_argument('--initial_value', type=float, default=1000000,
                        help='Initial portfolio value')
    
    # Portfolio allocation
    parser.add_argument('--trad_sp500', type=float, default=0.6,
                        help='Traditional portfolio allocation to S&P 500')
    parser.add_argument('--trad_bonds', type=float, default=0.4,
                        help='Traditional portfolio allocation to bonds')
    
    parser.add_argument('--struct_sp500', type=float, default=0.4,
                        help='Structured portfolio allocation to S&P 500')
    parser.add_argument('--struct_bonds', type=float, default=0.3,
                        help='Structured portfolio allocation to bonds')
    parser.add_argument('--struct_notes', type=float, default=0.3,
                        help='Structured portfolio allocation to structured notes')
    
    # Structured note parameters
    parser.add_argument('--protection_level', type=float, default=0.1,
                        help='Target protection level for structured notes (as decimal)')
    
    # Withdrawal parameters
    parser.add_argument('--withdrawal_rate', type=float, default=0.04,
                        help='Annual withdrawal rate (as decimal)')
    parser.add_argument('--withdrawal_type', choices=['fixed_percent', 'fixed_dollar', 'rmd'],
                        default='fixed_percent', help='Withdrawal strategy type')
    parser.add_argument('--initial_age', type=int, default=65,
                        help='Initial age for RMD calculations')
    
    # Output options
    parser.add_argument('--output_dir', default='results',
                        help='Directory to save results')
    parser.add_argument('--plot', action='store_true',
                        help='Generate and save plots')
    
    return parser.parse_args()

def setup_portfolios(args):
    """Set up portfolio allocations based on command line arguments."""
    portfolio_allocations = {
        'traditional': {
            'sp500': args.trad_sp500,
            'bonds': args.trad_bonds
        },
        'structured': {
            'sp500': args.struct_sp500,
            'bonds': args.struct_bonds,
            'notes': args.struct_notes
        }
    }
    
    return portfolio_allocations

def setup_withdrawal_params(args):
    """Set up withdrawal parameters based on command line arguments."""
    if args.withdrawal_rate == 0:
        return None
    
    params = {
        'type': args.withdrawal_type,
        'rate': args.withdrawal_rate,
        'start_year': args.start_year
    }
    
    if args.withdrawal_type == 'rmd':
        params['initial_age'] = args.initial_age
    
    return params

def save_results(simulation, args):
    """Save simulation results to files."""
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save detailed results to CSV
    results_df = simulation.get_results_dataframe()
    results_path = os.path.join(args.output_dir, f'simulation_results_{timestamp}.csv')
    results_df.to_csv(results_path, index=False)
    logger.info(f"Saved detailed results to {results_path}")
    
    # Save summary statistics to CSV
    summary = simulation.calculate_summary_statistics()
    summary_df = pd.DataFrame.from_dict(summary, orient='index')
    summary_path = os.path.join(args.output_dir, f'simulation_summary_{timestamp}.csv')
    summary_df.to_csv(summary_path)
    logger.info(f"Saved summary statistics to {summary_path}")
    
    # Generate plots if requested
    if args.plot:
        plot_results(results_df, args.output_dir, timestamp)

def plot_results(results_df, output_dir, timestamp):
    """Generate and save plots of simulation results."""
    # Define a vibrant, modern color palette
    colors = {
        'traditional': '#FF6B6B',  # Vibrant coral red
        'structured': '#4ECDC4',   # Bright teal
        'background': '#F7FFF7',   # Light mint background
        'grid': '#CFD8DC',         # Soft blue-gray
        'text': '#2E3D49',         # Dark blue-gray text
        'title': '#2D3142'         # Deep navy for titles
    }
    
    # Set plotting style for more attractive charts
    plt.style.use('ggplot')
    
    # Set larger font sizes globally
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 24,       # Larger title
        'axes.labelsize': 20,       # Larger axis labels
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 18,
        'figure.facecolor': colors['background'],
        'axes.facecolor': colors['background'],
        'axes.edgecolor': colors['text'],
        'axes.labelcolor': colors['text'],
        'xtick.color': colors['text'],
        'ytick.color': colors['text'],
        'text.color': colors['text'],
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.color': colors['grid'],
    })
    
    # Create a figure for portfolio values - increased by 30%
    plt.figure(figsize=(16, 10))
    
    # Get unique portfolios
    portfolios = results_df['portfolio'].unique()
    
    # Plot portfolio values over time with vibrant colors
    for i, portfolio in enumerate(portfolios):
        portfolio_data = results_df[results_df['portfolio'] == portfolio]
        color = colors['traditional'] if portfolio == 'traditional' else colors['structured']
        plt.plot(portfolio_data['year'], portfolio_data['portfolio_value'], 
                 label=portfolio.capitalize(), 
                 linewidth=4,  # Thicker lines
                 color=color,
                 marker='o',   # Add markers
                 markersize=8, # Larger markers
                 alpha=0.9)    # Slight transparency
    
    plt.title('Portfolio Values Over Time', fontsize=24, fontweight='bold', color=colors['title'], pad=20)
    plt.xlabel('Year', fontsize=20, fontweight='bold', color=colors['title'], labelpad=15)
    plt.ylabel('Portfolio Value ($)', fontsize=20, fontweight='bold', color=colors['title'], labelpad=15)
    
    # Add grid for readability but make it subtle
    plt.grid(True, linestyle='--', alpha=0.3, linewidth=0.8)
    
    # Add a subtle shadow effect to the plot area
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(colors['grid'])
        spine.set_linewidth(1.5)
    
    # Enhanced legend with shadow and rounded corners
    legend = plt.legend(fontsize=18, loc='upper left', facecolor=colors['background'], 
                     framealpha=0.9, edgecolor=colors['grid'], fancybox=True, shadow=True)
    
    # Add y-axis formatter for dollar values
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '${:,.0f}'.format(x)))
    
    # Add a subtle fill between the x-axis and the line for better visual effect
    for i, portfolio in enumerate(portfolios):
        portfolio_data = results_df[results_df['portfolio'] == portfolio]
        color = colors['traditional'] if portfolio == 'traditional' else colors['structured']
        plt.fill_between(portfolio_data['year'], 
                       0, 
                       portfolio_data['portfolio_value'], 
                       alpha=0.1, 
                       color=color)
    
    # Save figure with high resolution
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f'portfolio_values_{timestamp}.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved portfolio values plot to {plot_path}")
    
    # Create a figure for annual returns - increased by 30%
    plt.figure(figsize=(16, 10))
    
    # Plot annual returns over time with vibrant colors
    for i, portfolio in enumerate(portfolios):
        portfolio_data = results_df[results_df['portfolio'] == portfolio]
        color = colors['traditional'] if portfolio == 'traditional' else colors['structured']
        plt.plot(portfolio_data['year'], portfolio_data['annual_return'], 
                 label=portfolio.capitalize(), 
                 linewidth=4,  # Thicker lines
                 color=color,
                 marker='o',   # Add markers
                 markersize=8, # Larger markers
                 alpha=0.9)    # Slight transparency
    
    plt.title('Annual Portfolio Returns', fontsize=24, fontweight='bold', color=colors['title'], pad=20)
    plt.xlabel('Year', fontsize=20, fontweight='bold', color=colors['title'], labelpad=15)
    plt.ylabel('Annual Return (%)', fontsize=20, fontweight='bold', color=colors['title'], labelpad=15)
    
    # Add grid for readability but make it subtle
    plt.grid(True, linestyle='--', alpha=0.3, linewidth=0.8)
    
    # Add a subtle shadow effect to the plot area
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(colors['grid'])
        spine.set_linewidth(1.5)
    
    # Enhanced legend with shadow and rounded corners
    legend = plt.legend(fontsize=18, loc='upper left', facecolor=colors['background'], 
                     framealpha=0.9, edgecolor=colors['grid'], fancybox=True, shadow=True)
    
    # Add y-axis formatter for percentage values
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '{:.1f}%'.format(x * 100)))
    
    # Add reference line at y=0
    plt.axhline(y=0, color=colors['grid'], linestyle='-', linewidth=1.5, alpha=0.7)
    
    # Add a subtle fill between 0 and the line for better visual effect
    # Use different fill for positive and negative values
    for i, portfolio in enumerate(portfolios):
        portfolio_data = results_df[results_df['portfolio'] == portfolio]
        years = portfolio_data['year']
        returns = portfolio_data['annual_return']
        color = colors['traditional'] if portfolio == 'traditional' else colors['structured']
        
        # Fill positive returns
        plt.fill_between(years, 0, returns, 
                       where=(returns >= 0),
                       alpha=0.15, 
                       color=color)
        
        # Fill negative returns with a darker shade
        plt.fill_between(years, 0, returns, 
                       where=(returns < 0),
                       alpha=0.15, 
                       color=color)
    
    # Save figure with high resolution
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f'annual_returns_{timestamp}.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved annual returns plot to {plot_path}")

def main():
    """Main entry point for portfolio simulation."""
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info("Starting Portfolio Simulator")
    logger.info(f"Simulation period: {args.start_year} to {args.end_year}")
    
    try:
        # Load data
        logger.info("Loading market data and structured notes...")
        sp500_returns = load_sp500_data(args.sp500_file)
        bond_returns = load_bond_returns(args.bond_file)
        notes_data = load_structured_notes(args.notes_file)
        
        # Align data to ensure consistent years
        valid_years, aligned_sp500, aligned_bonds, aligned_notes = align_data(
            sp500_returns, bond_returns, notes_data, 
            args.start_year, args.end_year
        )
        
        start_year = max(args.start_year, min(valid_years))
        end_year = min(args.end_year, max(valid_years))
        
        if start_year != args.start_year or end_year != args.end_year:
            logger.warning(f"Adjusted simulation period to {start_year}-{end_year} based on available data")
        
        # Set up portfolio allocations
        portfolio_allocations = setup_portfolios(args)
        
        # Set up withdrawal parameters
        withdrawal_params = setup_withdrawal_params(args)
        
        # Set up note selection parameters
        note_selection_params = {
            'protection_level': args.protection_level
        }
        
        # Create and run simulation
        logger.info("Running portfolio simulation...")
        simulation = PortfolioSimulation(
            aligned_sp500, aligned_bonds, aligned_notes,
            start_year, end_year, args.initial_value,
            portfolio_allocations,
            note_selection_params=note_selection_params,
            withdrawal_params=withdrawal_params
        )
        
        simulation.run_simulation()
        
        # Save results
        save_results(simulation, args)
        
        logger.info("Simulation completed successfully")
        
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 