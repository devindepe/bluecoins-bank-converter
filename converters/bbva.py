import os
import sys
from datetime import datetime

try:
    import pandas as pd
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: Missing dependencies. Please run: pip install -r requirements.txt")
    sys.exit(1)

# === LOAD CONFIGURATION ===
load_dotenv()

ACCOUNT_NAME = os.getenv("ACCOUNT_NAME_BBVA", "BBVA Account")
ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE_BBVA", "Bank")
OUTPUT_NAME_BASE = os.getenv("OUTPUT_NAME_BBVA", "bbva_bluecoins")

# === ARGUMENT CHECK ===
if len(sys.argv) < 3:
    print("❌ Error: Missing arguments.")
    print("Usage: python bbva.py <input_file> <output_folder>")
    sys.exit(1)

input_xlsx = sys.argv[1]
output_dir = sys.argv[2]

# === VALIDATE FILE EXTENSION ===
valid_extensions = ('.xlsx', '.xls')
if not input_xlsx.lower().endswith(valid_extensions):
    print(f"❌ Error: The provided file is not a valid Excel: {input_xlsx}")
    sys.exit(1)

if not os.path.isfile(input_xlsx):
    print(f"❌ Error: The file does not exist at path: {input_xlsx}")
    sys.exit(1)

# === CONFIGURATION ===
current_date = datetime.now().strftime("%Y-%m-%d")
output_filename = f"{OUTPUT_NAME_BASE.replace('.csv', '')}_{current_date}.csv"
OUTPUT_CSV = os.path.join(output_dir, output_filename)

# === READ EXCEL ===
# Read all data first to find where the actual table starts
df_raw = pd.read_excel(input_xlsx, header=None)

# Find the row that contains "Fecha" or "F.Valor" (header row)
header_row = None
for idx, row in df_raw.iterrows():
    row_str = ' '.join([str(x) for x in row if pd.notna(x)])
    if 'Fecha' in row_str and 'Importe' in row_str:
        header_row = idx
        break

if header_row is None:
    print("❌ Error: Could not find header row with 'Fecha' and 'Importe'")
    sys.exit(1)

# Read again with the correct header
df = pd.read_excel(input_xlsx, header=header_row)

# Clean column names (remove extra spaces, newlines)
df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]

# Try to identify columns by their content
# Looking for: F.Valor, Fecha, Concepto, Movimiento, Importe, Divisa, Disponible, Divisa, Observaciones
col_mapping = {}
for i, col in enumerate(df.columns):
    col_lower = str(col).lower()
    if 'f.valor' in col_lower or 'f valor' in col_lower:
        col_mapping['f_valor'] = col
    elif 'fecha' in col_lower and 'generación' not in col_lower:
        col_mapping['fecha'] = col
    elif 'concepto' in col_lower:
        col_mapping['concepto'] = col
    elif 'movimiento' in col_lower:
        col_mapping['movimiento'] = col
    elif 'importe' in col_lower:
        col_mapping['importe'] = col
    elif 'disponible' in col_lower:
        col_mapping['disponible'] = col
    elif 'observa' in col_lower:
        col_mapping['observaciones'] = col

# Verify we have the essential columns
if 'fecha' not in col_mapping or 'importe' not in col_mapping:
    print("❌ Error: Could not find essential columns (Fecha, Importe)")
    print("Available columns:", list(df.columns))
    sys.exit(1)

# === ROBUST CURRENCY CLEANING ===
def clean_currency(value):
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    s = str(value).strip()
    s = s.replace('€', '').replace(' ', '')
    s = s.replace('.', '').replace(',', '.')
    
    try:
        return float(s)
    except ValueError:
        return None

# Apply cleaning to amount and balance
df[col_mapping['importe']] = df[col_mapping['importe']].apply(clean_currency)
if 'disponible' in col_mapping:
    df[col_mapping['disponible']] = df[col_mapping['disponible']].apply(clean_currency)

# Drop rows where amount is not a valid number
df = df.dropna(subset=[col_mapping['importe']])

# === BLUECOINS CONVERSION ===
out = pd.DataFrame()

out["(1)Type"] = df[col_mapping['importe']].apply(
    lambda x: "e" if x < 0 else "i"
)

dt_series = pd.to_datetime(df[col_mapping['fecha']], dayfirst=True, errors="coerce")
out["(2)Date"] = dt_series.apply(lambda x: f"{x.month}/{x.day}/{x.year}" if pd.notnull(x) else "")

# Build Item or Payee
if 'concepto' in col_mapping and 'movimiento' in col_mapping:
    out["(3)Item or Payee"] = (
        df[col_mapping['concepto']].astype(str) + " - " + 
        df[col_mapping['movimiento']].astype(str)
    )
elif 'concepto' in col_mapping:
    out["(3)Item or Payee"] = df[col_mapping['concepto']].astype(str)
elif 'movimiento' in col_mapping:
    out["(3)Item or Payee"] = df[col_mapping['movimiento']].astype(str)
else:
    out["(3)Item or Payee"] = "Transaction"

out["(4)Amount"] = df[col_mapping['importe']].abs()

out["(5)Parent Category"] = ""
out["(6)Category"] = ""
out["(7)Account Type"] = ACCOUNT_TYPE
out["(8)Account"] = ACCOUNT_NAME

# Notes
notes_parts = []
if 'observaciones' in col_mapping:
    notes_parts.append("Obs: " + df[col_mapping['observaciones']].astype(str))
if 'disponible' in col_mapping:
    notes_parts.append("Balance: " + df[col_mapping['disponible']].astype(str))

if notes_parts:
    out["(9)Notes"] = notes_parts[0]
    for part in notes_parts[1:]:
        out["(9)Notes"] = out["(9)Notes"] + " | " + part
else:
    out["(9)Notes"] = ""

out["(10) Label"] = ""
out["(11) Status"] = ""
out["(12) Split"] = ""

# === SAVE CSV ===
try:
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ CSV generated correctly: {OUTPUT_CSV}")
    print(f"📊 Total transactions: {len(out)}")
except Exception as e:
    print(f"❌ Error saving CSV: {e}")