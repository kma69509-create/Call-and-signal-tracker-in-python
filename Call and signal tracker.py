import os 
import pandas as pd

DATA_DIR = 'data'
REPORTS_DIR = 'reports'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, 'data.csv')

APP_NAME = "CALL & Signal tracker"
APP_VERSION = "1.0"

Author = "h4acker_found"
Description = "Analyze your own call logs & mobile network signals"

def show_menu():
    print("=" * 60)
    print(f" {APP_NAME}  v{APP_VERSION}")
    print("1. import Data (CSV/JSON)")
    print("2 VIEW CALL LOGS")
    print("3 VIEW ALL RECORDS")
    print("4 ANALYZE Signal Strength")
    print("5 Export Report (CSV)")
    print("6. Exit")
    print('-' * 60)

def load_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return pd.DataFrame()
    if ext not in (".csv", ".json"):
        print("[!] Unsupported file format. Please use CSV or JSON")
        return pd.DataFrame()
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
    except Exception as e:
        print(f"[!] Error loading the file: {e}")
        return pd.DataFrame()
    if df.empty:
        print("[!] No data found in the file.")
        return pd.DataFrame()

    print(f"[+] Data loaded successfully. Total records: {len(df)}")
    return df


def _has_column(df, column):
    if column not in df.columns:
        print(f"[!] Required column '{column}' was not found.")
        return False
    return True


def import_data():
    print("\n[1] Import CSV file")
    print("[2] Import JSON file")
    choice = input("Select option(1 or 2): ")
    file_path = input("Enter the file path: ").strip()
    if choice == '1' and not file_path.lower().endswith('.csv'):
        print("[!] Please select a CSV file.")
        return pd.DataFrame()
    if choice == '2' and not file_path.lower().endswith('.json'):
        print("[!] Please select a JSON file")
        return pd.DataFrame()
    return load_data(file_path)

def view_al_records(df):
    if df.empty:
        print("[!] No records to view.")
        return
    if not _has_column(df, 'timestamp'):
        return
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.sort_values('timestamp', ascending=False).reset_index(drop=True))

def view_call_logs(df):
    if df.empty:
        print("[!] No call logs to view.")
        return
    if not _has_column(df, 'call_type'):
        return
    calls = df[df['call_type'].astype('string').str.upper().isin(
        ['INCOMING', 'OUTGOING', 'MISSED']
    )]
    if calls.empty:
        print("[!] No call logs to view.")
        return
    if _has_column(calls, 'timestamp'):
        print(calls.sort_values('timestamp', ascending=False).reset_index(drop=True))

def filter_by_data(df):
    start = input("Start date (YYYY-MM-DD HH:MM:SS):").strip()
    end = input("End date (YYYY-MM-DD HH:MM:SS):").strip()
    if df.empty:
        print("[!] No records to filter.")
        return
    if not _has_column(df, 'timestamp'):
        return
    try:
        start_date = pd.to_datetime(start, format='%Y-%m-%d %H:%M:%S')
        end_date = pd.to_datetime(end, format='%Y-%m-%d %H:%M:%S')
        timestamps = pd.to_datetime(df['timestamp'], errors='coerce')
        res = df.loc[(timestamps >= start_date) & (timestamps <= end_date)]
        if res.empty:
            print("[!] No records found in this range")
        else:
            print(res.sort_values('timestamp', ascending=False).reset_index(drop=True))
    except (TypeError, ValueError) as e:
        print(f"[!] Invalid data format or error: {e}")

def analyze_signal_strength(df):
    if df.empty:
        print("[!] No signal to analyze.")
        return
    if not _has_column(df, 'rsrp') or not _has_column(df, 'cell_id'):
        return
    rsrp = pd.to_numeric(df['rsrp'], errors='coerce')
    df = df.loc[rsrp.notna()].copy()
    if df.empty:
        print("[!] No valid RSRP values found.")
        return
    df['rsrp'] = rsrp.loc[df.index]
    max_row = df.loc[df['rsrp'].idxmax()]
    min_row = df.loc[df['rsrp'].idxmin()]
    avg_rsrp = df['rsrp'].mean()
    print("\n================  Signal Strength Analysis  =============")
    print(f"Total records analyzed : {len(df)}")
    print(f"Average RSRP           : {avg_rsrp:.2f} dBm")
    print(f"Strongest Signal       : {max_row['rsrp']} dBm")
    print(f"     Cell ID           : {max_row['cell_id']}")
    print(f"Minimum RSRP           : {min_row['rsrp']:.2f} dBm")
    print(f"     Cell ID           : {min_row['cell_id']}")
    return df

def analyze_analyse_network(df):
    if df.empty:
        print("[!] No data to analyze.")
        return
    if not _has_column(df, 'radio_type'):
        return
    dist = df['radio_type'].value_counts(dropna=False)
    print("\n================  Network Type Distribution  =============")
    for net_type, count in dist.items():
        print(f"{net_type}: <-----    : {count} ")
    return dist

def top_cells_by_signal(df, top_n=5):
    if df.empty:
        print("[!] no data available to analyze")
        return
    if not _has_column(df, 'rsrp') or not _has_column(df, 'cell_id'):
        return
    if top_n <= 0:
        print("[!] top_n must be greater than zero.")
        return
    valid = df.assign(rsrp=pd.to_numeric(df['rsrp'], errors='coerce')).dropna(
        subset=['rsrp', 'cell_id']
    )
    top_cells = valid.groupby('cell_id')['rsrp'].mean().nlargest(top_n)
    print(f"\n============ TOP {top_n} CELLS (by Avg RSRP) ===============")
    for cell_id, avg in top_cells.items():
        print(f"Cell ID: {str(cell_id):<20} Avg RSRP: {avg:.2f} dBm")
    return top_cells


def export_report(df, filename='report.csv'):
    if df.empty:
        print("[!] No data to export")
        return
    try:
        df.to_csv(filename, index=False)
        print(f"[+] Report exported successfully: {filename}")
    except Exception as e:
        print(f"[!] Error exporting report: {e}")

def show_summary(df):
    if df.empty:
        print("[!] No data available")
        return
    if not _has_column(df, 'rsrp') or not _has_column(df, 'cell_id'):
        return
    rsrp = pd.to_numeric(df['rsrp'], errors='coerce')
    valid = df.loc[rsrp.notna()]
    if valid.empty:
        print("[!] No valid RSRP values found.")
        return
    rsrp = rsrp.loc[valid.index]
    strongest_index = rsrp.idxmax()
    weakest_index = rsrp.idxmin()

    print("\n====================== DATA SUMMARY ==================")
    print(f"Total Records           : {len(df)}")
    print(f"Average RSRP (dBm)      : {rsrp.mean():.2f}")
    print(f"Strongest Signal (dBm)  : {rsrp.loc[strongest_index]:.2f} (cell ID: {valid.loc[strongest_index, 'cell_id']})")
    print(f"Weakest Signal (dBm)    : {rsrp.loc[weakest_index]:.2f} (cell ID: {valid.loc[weakest_index, 'cell_id']})")

def main():
    df = pd.DataFrame()
    while True:
        show_menu()
        choice = input("Select an option (1-6): ").strip()
        if choice =='1':
            df = import_data()
        elif choice == '2':
            view_call_logs(df)
        elif choice == '3':
            view_al_records(df)
        elif choice == '4':
            analyze_signal_strength(df)
        elif choice == '5':
            filename = input("Enter report filename(eg. report.csv): ").strip()
            export_report(df, filename)
        elif choice == '6':
            print("[+] Exciting...... stay safe!")
            break
        else:
            print("[!] Invalid option. Please choose 1-6")

if __name__ == '__main__':
    main()
