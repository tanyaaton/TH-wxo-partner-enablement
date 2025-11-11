import os
import pandas as pd

# Path to your folder
folder_path = "การเข้าใช้งานห้องสมุด 2019-2025"

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".xls"):
        xls_path = os.path.join(folder_path, filename)
        xlsx_path = os.path.join(folder_path, filename.replace(".xls", ".xlsx"))

        try:
            # Read and save as XLSX
            df = pd.read_excel(xls_path)
            df.to_excel(xlsx_path, index=False)
            print(f"✅ Converted: {filename} → {os.path.basename(xlsx_path)}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")
