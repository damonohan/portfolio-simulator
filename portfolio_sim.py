import os
import json
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np

os.makedirs("simulations", exist_ok=True)

# Note payoff for Growth Note with Hard Protection (Buffer)
def simple_note_payoff(start_price, end_price, protection=0.9, rf_rate=0.03):
    bond_return = rf_rate
    sp_return = (end_price - start_price) / start_price
    if sp_return < 0:
        if sp_return < -(1 - protection):
            return bond_return + sp_return + (1 - protection)  # Buffer: absorb loss up to protection
        return bond_return  # No loss within protection
    return bond_return + sp_return * (1 / (1 - protection))  # Upside scaled by inverse protection (simplified)

# Simulator using pre-calculated note data
def simulate_portfolio(start_cash, horizon, protection=0.10, contrib=0, sim_name=None):
    sp500 = pd.read_csv("raw_data/sp500_yearly.csv", index_col=0, parse_dates=True)["Close"]
    yearly_sp500 = sp500.resample("YE").last()
    notes_df = pd.read_csv("note_data/note_payoffs.csv")

    start_year = 1976
    end_year = start_year + horizon
    portfolio_value = start_cash
    data_log = []

    for year in range(start_year, end_year):
        date = pd.Timestamp(f"{year}-12-31")
        if date not in yearly_sp500.index:
            continue
        sp_price = yearly_sp500.loc[date]
        rf_rate = notes_df[notes_df['year'] == year - 1]['rf_rate'].iloc[0] if not notes_df[notes_df['year'] == year - 1].empty else 0.03

        if year == start_year:
            start_sp = sp_price
            print(f"Year {year}: Starting SP500 = {sp_price}")
            continue
        
        sp_return = (sp_price - start_sp) / start_sp
        participation = notes_df[notes_df['year'] == year - 1]['participation_10'].iloc[0] if not notes_df[notes_df['year'] == year - 1].empty else 1.0
        # Debug print to ensure function exists
        print(f"Calling simple_note_payoff with start_sp={start_sp}, sp_price={sp_price}, protection={protection}, rf_rate={rf_rate}")
        note_return = simple_note_payoff(start_sp, sp_price, protection=protection, rf_rate=rf_rate) * participation
        bond_return = rf_rate
        
        equity_value = portfolio_value * 0.4 * (1 + sp_return)
        note_value = portfolio_value * 0.3 * (1 + note_return)
        bond_value = portfolio_value * 0.3 * (1 + bond_return)
        portfolio_value = equity_value + note_value + bond_value + contrib
        
        print(f"Year {year}: SP500 Return = {sp_return:.4f}, Note Return = {note_return:.4f}, Bond Return = {bond_return:.4f}, Portfolio = {portfolio_value:.2f}")
        
        data_log.append({
            "year": year,
            "sp500_price": sp_price,
            "sp500_return": sp_return,
            "note_return": note_return,
            "bond_return": bond_return,
            "portfolio_value": portfolio_value
        })
        start_sp = sp_price
    
    if sim_name is None:
        sim_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    sim_path = f"simulations/sim_{sim_name}"
    
    df = pd.DataFrame(data_log)
    df.to_csv(f"{sim_path}_data.csv", index=False)
    config = {
        "start_cash": start_cash,
        "horizon": horizon,
        "contrib": contrib,
        "protection": protection,
        "allocation": {"sp500": 0.4, "note": 0.3, "bond": 0.3}
    }
    with open(f"{sim_path}_config.json", "w") as f:
        json.dump(config, f, indent=4)
    stats = {
        "total_return": (portfolio_value - (start_cash + contrib * horizon)) / start_cash,
        "annualized_return": ((portfolio_value / start_cash) ** (1 / horizon)) - 1
    }
    pd.DataFrame([stats]).to_csv(f"{sim_path}_stats.csv", index=False)
    
    print(f"Final Portfolio Value: {portfolio_value}, Stats: {stats}")
    return df, stats

# GUI
def run_gui():
    def run_simulation():
        try:
            print("Testing GUI simple_note_payoff:", simple_note_payoff(100, 90, protection=0.10, rf_rate=0.03))
            start_cash = float(entry_cash.get())
            horizon = int(entry_horizon.get())
            protection = float(protection_var.get())
            results = {}
            for p in [0.05, 0.10, 0.15, 0.20]:
                df, stats = simulate_portfolio(start_cash, horizon, protection=p, contrib=10000)
                results[p] = stats['annualized_return']
            result_text = "\n".join([f"Protection {int(p*100)}%: {r:.2%}" for p, r in results.items()])
            print(f"GUI Update: {result_text}")
            result_label.config(text=result_text)
            root.update()
            print(f"Label now says: {result_label.cget('text')}")
        except Exception as e:
            print(f"GUI Error: {e}")
            result_label.config(text=f"Error: {e}")
            root.update()

    def load_simulation():
        selected = combo_sims.get()
        if selected:
            sim_name = selected.split("sim_")[1].split("_data.csv")[0]
            df = pd.read_csv(f"simulations/sim_{sim_name}_data.csv")
            with open(f"simulations/sim_{sim_name}_config.json", "r") as f:
                config = json.load(f)
            stats = pd.read_csv(f"simulations/sim_{sim_name}_stats.csv").iloc[0].to_dict()
            result_label.config(text=f"Loaded {sim_name}: Annualized Return: {stats['annualized_return']:.2%}")
            root.update()

    root = tk.Tk()
    root.title("Portfolio Simulator (1976-2024)")
    root.geometry("800x800")  # Your bigger window
    root.minsize(400, 400)

    tk.Label(root, text="Starting Cash:").pack(pady=5)
    entry_cash = tk.Entry(root)
    entry_cash.insert(0, "100000")
    entry_cash.pack(pady=5)

    tk.Label(root, text="Horizon (years):").pack(pady=5)
    entry_horizon = tk.Entry(root)
    entry_horizon.insert(0, "10")
    entry_horizon.pack(pady=5)

    tk.Label(root, text="Protection Level:").pack(pady=5)
    protection_var = tk.StringVar(value="0.10")
    protection_menu = ttk.Combobox(root, textvariable=protection_var, values=["0.05", "0.10", "0.15", "0.20"])
    protection_menu.pack(pady=5)

    tk.Button(root, text="Run Simulation", command=run_simulation).pack(pady=10)

    tk.Label(root, text="Load Previous Simulation:").pack(pady=5)
    sim_files = glob.glob("simulations/*_data.csv")
    sim_names = [os.path.basename(f) for f in sim_files]
    combo_sims = ttk.Combobox(root, values=sim_names)
    combo_sims.pack(pady=5)
    tk.Button(root, text="Load", command=load_simulation).pack(pady=10)

    result_label = tk.Label(root, text="Results will appear here", font=("Arial", 14, "bold"), fg="blue", justify="left")
    result_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()