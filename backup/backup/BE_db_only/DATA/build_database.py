#!/usr/bin/env python3
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# --------- CONFIG ----------
DATA_DIR = Path("DATA/TABLE")
DB_PATH = Path("data.db")

# File paths
ATTENDANCE_DIR = DATA_DIR / "ATTENDANCE" / "การมาเรียน 2019-2025"
FOOD_DIR = DATA_DIR / "FOOD"
HOSPITAL_PATH = DATA_DIR / "HOSPITAL" / "การใช้บริการห้องพยาบาล.xlsx"
LIBRARY_DIR = DATA_DIR / "LIBRARY" / "การเข้าใช้งานห้องสมุด 2019-2025"
SCORING_PATH = DATA_DIR / "SCORING" / "คะแนนและเกรดนักเรียน 2019-2024.xlsx"
SEMESTER_FEE_PATH = DATA_DIR / "SEMESTER_FEE" / "ชำระค่าเทอม.xlsx"
STUDENT_PATH = DATA_DIR / "STUDENT" / "student_info_2568.xlsx"

print(f"Attendance data path: {ATTENDANCE_DIR.resolve()}")
print(f"Food data path: {FOOD_DIR.resolve()}")  
print(f"Hospital data path: {HOSPITAL_PATH.resolve()}")
print(f"Library data path: {LIBRARY_DIR.resolve()}")  
print(f"Scoring data path: {SCORING_PATH.resolve()}")
print(f"Semester fee data path: {SEMESTER_FEE_PATH.resolve()}")
print(f"Student data path: {STUDENT_PATH.resolve()}")

# ---------- CLEANING HELPERS ----------
HIDDEN_CHARS = {
    "\u200b",  # zero width space
    "\ufeff",  # BOM
    "\u00a0",  # non-breaking space
}

def clean_text(x):
    """Remove hidden Unicode, normalize internal whitespace, strip."""
    if pd.isna(x):
        return x
    s = str(x)
    for ch in HIDDEN_CHARS:
        s = s.replace(ch, "")
    return " ".join(s.split()).strip()

def clean_df_text_columns(df, cols):
    """Apply clean_text to a list of columns if present."""
    for c in cols:
        if c in df.columns:
            df[c] = df[c].apply(clean_text)
    return df

def standardize_date(date_val):
    """Standardize various date formats to YYYY-MM-DD"""
    if pd.isna(date_val):
        return None
    
    try:
        # If it's already a datetime object
        if isinstance(date_val, (pd.Timestamp, datetime)):
            return date_val.strftime('%Y-%m-%d')
        
        # Convert to string and clean
        date_str = clean_text(str(date_val))
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', 
            '%Y/%m/%d', '%d-%m-%Y', '%Y%m%d',
            '%d/%m/%y', '%m/%d/%y', '%y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try pandas to_datetime as fallback
        return pd.to_datetime(date_val, errors='coerce').strftime('%Y-%m-%d')
    except:
        return None

def to_numeric_safe(val):
    """Convert to numeric, return NaN if conversion fails"""
    try:
        if pd.isna(val):
            return np.nan
        return float(val)
    except:
        return np.nan

# ---------- LOAD FUNCTIONS ----------

def load_attendance():
    """Load and combine all attendance files"""
    print("Loading ATTENDANCE data...")
    attendance_files = list(ATTENDANCE_DIR.glob("*.xlsx"))
    
    dfs = []
    for file in attendance_files:
        print(f"  Processing {file.name}")
        try:
            df = pd.read_excel(file)
            df.columns = [clean_text(str(c)) for c in df.columns]
            df = df.rename(columns={"ประเภท ( ขาด ลา มาสาย)": "ประเภท"})
            
            # Expected columns: วันที่, ปีการศึกษา, ภาคเรียน, รหัสนักเรียน, ประเภท ( ขาด ลา มาสาย)
            expected_cols = ['วันที่', 'ปีการศึกษา', 'ภาคเรียน', 'รหัสนักเรียน']
            
            # Check if we have the expected structure
            has_expected = any(col in df.columns for col in expected_cols)
            if not has_expected:
                print(f"    Warning: {file.name} doesn't have expected Thai columns, skipping")
                continue
            
            # Standardize date column
            date_col = None
            for col in ['วันที่', 'date', 'Date']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                df[date_col] = df[date_col].apply(standardize_date)
            
            dfs.append(df)
            print(f"    Loaded {len(df)} records")
            
        except Exception as e:
            print(f"    Error processing {file.name}: {e}")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        # Clean text columns
        text_cols = combined.select_dtypes(include=['object']).columns
        combined = clean_df_text_columns(combined, text_cols)
        return combined
    return pd.DataFrame()

def standardize_product_categories(category):
    """Map original categories to standardized categories"""
    if pd.isna(category):
        return "อื่นๆ"
    
    category = str(category).strip()
    
    # Category mapping dictionary
    category_mapping = {
        # ผลไม้ (Fruits)
        "ผลไม้": "ผลไม้",
        
        # อาหาร (Food)
        "อาหาร": "อาหาร",
        
        # อาหารทานเล่น (Snack Food)
        "อาหารทานเล่น": "อาหารทานเล่น",
        "ท็อปปิ้ง": "อาหารทานเล่น",
        
        # ขนม (Snacks)
        "สินค้าขนม": "ขนม",
        
        # เครื่องดื่ม (Beverages)
        "เครื่องดื่ม": "เครื่องดื่ม",
        "สินค้าเครื่องดื่ม": "เครื่องดื่ม",
        
        # เบเกอรี่ (Bakery)
        "เบเกอรี่": "เบเกอรี่",
        
        # ไอศกรีม (Ice Cream)
        "สินค้าไอศกรีม": "ไอศกรีม",
        
        # อุปกรณ์นักเรียน (Student Supplies)
        "สินค้ากระเป๋านักเรียน": "อุปกรณ์นักเรียน",
        "สินค้าชุดนักเรียน": "อุปกรณ์นักเรียน",
        "สินค้าอุปกรณ์เครื่องแบบลูกเสือ/เนตรนารี": "อุปกรณ์นักเรียน",
        "สินค้าเครื่องแบบนักเรียน": "อุปกรณ์นักเรียน",
        "สินค้าโรงเรียน": "อุปกรณ์นักเรียน",
        
        # อุปกรณ์เครื่องเขียน (Stationery)
        "สินค้าสมุด": "อุปกรณ์เครื่องเขียน",
        "สินค้าอุปกรณ์เครื่องเขียน": "อุปกรณ์เครื่องเขียน",
        
        # อุปกรณ์กีฬา (Sports Equipment)
        "สินค้ากีฬา": "อุปกรณ์กีฬา",
        "สินค้าชุดพละ": "อุปกรณ์กีฬา",
        "สินค้าชุดว่ายน้ำ": "อุปกรณ์กีฬา",
        
        # อุปโภค (Consumer Goods)
        "สินค้าอุปโภค": "อุปโภค",
        
        # อื่นๆ (Others)
        "สินค้ากิ๊ฟช้อป": "อื่นๆ",
        "สินค้าของที่ระลึก": "อื่นๆ",
        "สินค้าชุดพื้นเมือง": "อื่นๆ",
        "สินค้าน้ำท่วมลดราคา": "อื่นๆ",
        "สินค้าฝากขาย": "อื่นๆ"
    }
    
    # Return mapped category or "อื่นๆ" if not found
    return category_mapping.get(category, "อื่นๆ")

def load_food():
    """Load and combine all food-related data with proper joins and standardized categories"""
    print("Loading FOOD data...")
    
    # Load product/menu reference tables
    try:
        product_minimart = pd.read_excel(FOOD_DIR / "ข้อมูลการซื้อสินค้าในมินิมาร์ท" / "product_minimart.xlsx")
        menu_online = pd.read_excel(FOOD_DIR / "สั่งอาหารออนไลน์" / "menu_online.xlsx")
        menu_canteen = pd.read_excel(FOOD_DIR / "ข้อมูลการซื้ออาหาร" / "menu_canteen.xlsx")
    except Exception as e:
        print(f"Error loading menu/product files: {e}")
        return pd.DataFrame()
    
    # Clean column names
    for df in [product_minimart, menu_online, menu_canteen]:
        df.columns = [clean_text(str(c)) for c in df.columns]
    
    all_transactions = []
    
    # 1. Process minimart transactions
    try:
        transaction_minimart = pd.read_excel(FOOD_DIR / "ข้อมูลการซื้อสินค้าในมินิมาร์ท" / "transaction_minimart.xlsx")
        transaction_minimart.columns = [clean_text(str(c)) for c in transaction_minimart.columns]
        
        # Join with product data
        minimart_joined = transaction_minimart.merge(
            product_minimart, 
            left_on=transaction_minimart.columns[1],  # product_id
            right_on=product_minimart.columns[0],     # product_id
            how='left'
        )
        
        # Standardize columns
        minimart_final = pd.DataFrame({
            'transaction_date': minimart_joined.iloc[:, 0].apply(standardize_date),
            'product_id': minimart_joined.iloc[:, 1].astype(str),
            'product_name': minimart_joined.iloc[:, -2] if len(minimart_joined.columns) > 5 else np.nan,
            'product_categories': minimart_joined.iloc[:, -1].apply(standardize_product_categories) if len(minimart_joined.columns) > 5 else np.nan,
            'amount': minimart_joined.iloc[:, 2].apply(to_numeric_safe),
            'unit_price': minimart_joined.iloc[:, 3].apply(to_numeric_safe),
            'total_price': minimart_joined.iloc[:, 4].apply(to_numeric_safe),
            # 'student_id': np.nan,
            'source': 'minimart'  # To identify source
        })
        all_transactions.append(minimart_final)
        print(f"  Minimart: {len(minimart_final)} records")
    except Exception as e:
        print(f"  Error processing minimart: {e}")
    
    # 2. Process online transactions
    try:
        transaction_online = pd.read_excel(FOOD_DIR / "สั่งอาหารออนไลน์" / "transaction_online.xlsx")
        transaction_online.columns = [clean_text(str(c)) for c in transaction_online.columns]
        
        # Join with menu data
        online_joined = transaction_online.merge(
            menu_online,
            left_on=transaction_online.columns[2],  # id_item
            right_on=menu_online.columns[0],        # id_item
            how='left'
        )
        
        # Standardize columns
        online_final = pd.DataFrame({
            'transaction_date': online_joined.iloc[:, 0].apply(standardize_date),
            'product_id': online_joined.iloc[:, 2].astype(str),
            'product_name': online_joined.iloc[:, -2] if len(online_joined.columns) > 5 else np.nan,
            'product_categories': online_joined.iloc[:, -1].apply(standardize_product_categories) if len(online_joined.columns) > 5 else np.nan,
            'amount': online_joined.iloc[:, 3].apply(to_numeric_safe),
            'unit_price': online_joined.iloc[:, 4].apply(to_numeric_safe),
            'total_price': online_joined.iloc[:, 3].apply(to_numeric_safe) * online_joined.iloc[:, 4].apply(to_numeric_safe),
            # 'student_id': online_joined.iloc[:, 1].apply(to_numeric_safe),
            'source': 'online'  # To identify source
        })
        all_transactions.append(online_final)
        print(f"  Online: {len(online_final)} records")
    except Exception as e:
        print(f"  Error processing online: {e}")
    
    # 3. Process canteen transactions
    try:
        transaction_canteen = pd.read_excel(FOOD_DIR / "ข้อมูลการซื้ออาหาร" / "transaction_canteen.xlsx")
        transaction_canteen.columns = [clean_text(str(c)) for c in transaction_canteen.columns]
        
        # Join with menu data
        canteen_joined = transaction_canteen.merge(
            menu_canteen,
            left_on=transaction_canteen.columns[2],  # id_menu
            right_on=menu_canteen.columns[0],        # id_menu
            how='left'
        )
        
        # Standardize columns
        canteen_final = pd.DataFrame({
            'transaction_date': canteen_joined.iloc[:, 0].apply(standardize_date),
            'product_id': canteen_joined.iloc[:, 2].astype(str),
            'product_name': canteen_joined.iloc[:, -2] if len(canteen_joined.columns) > 5 else np.nan,
            'product_categories': canteen_joined.iloc[:, -1].apply(standardize_product_categories) if len(canteen_joined.columns) > 5 else np.nan,
            'amount': canteen_joined.iloc[:, 3].apply(to_numeric_safe),
            'unit_price': canteen_joined.iloc[:, 4].apply(to_numeric_safe),
            'total_price': canteen_joined.iloc[:, 3].apply(to_numeric_safe) * canteen_joined.iloc[:, 4].apply(to_numeric_safe),
            # 'student_id': canteen_joined.iloc[:, 1].apply(to_numeric_safe),
            'source': 'canteen'  # To identify source
        })
        all_transactions.append(canteen_final)
        print(f"  Canteen: {len(canteen_final)} records")
    except Exception as e:
        print(f"  Error processing canteen: {e}")
    
    # Combine all transactions
    if all_transactions:
        combined_food = pd.concat(all_transactions, ignore_index=True)
        # Clean text columns
        text_cols = ['product_name', 'product_categories']
        combined_food = clean_df_text_columns(combined_food, text_cols)
        return combined_food
    
    return pd.DataFrame()

def load_hospital():
    """Load hospital data"""
    print("Loading HOSPITAL data...")
    try:
        df = pd.read_excel(HOSPITAL_PATH)
        df.columns = [clean_text(str(c)) for c in df.columns]
        
        # Clean text columns
        text_cols = df.select_dtypes(include=['object']).columns
        df = clean_df_text_columns(df, text_cols)
        
        # Standardize date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'วัน' in col]
        for col in date_cols:
            df[col] = df[col].apply(standardize_date)
        
        return df
    except Exception as e:
        print(f"Error loading hospital data: {e}")
        return pd.DataFrame()

def load_library():
    """Load and combine all library files"""
    print("Loading LIBRARY data...")
    library_files = list(LIBRARY_DIR.glob("*.xlsx"))
    
    dfs = []
    for file in library_files:
        print(f"  Processing {file.name}")
        try:
            df = pd.read_excel(file)
            df.columns = [clean_text(str(c)) for c in df.columns]
            
            # Expected columns: วันเวลาที่เข้าห้องสมุด, รหัสประจำตัวนักเรียน
            expected_cols = ['วันเวลาที่เข้าห้องสมุด', 'รหัสประจำตัวนักเรียน']
            
            # Check if we have the expected structure
            has_expected = any(col in df.columns for col in expected_cols)
            if not has_expected:
                print(f"    Warning: {file.name} doesn't have expected Thai columns, skipping")
                continue
            
            # Standardize datetime column
            datetime_col = None
            for col in ['วันเวลาที่เข้าห้องสมุด', 'datetime', 'date_time', 'วันที่']:
                if col in df.columns:
                    datetime_col = col
                    break
            
            if datetime_col:
                df[datetime_col] = df[datetime_col].apply(standardize_date)
            
            # Add year from filename for reference
            year = file.stem
            df['file_year'] = year
            
            dfs.append(df)
            print(f"    Loaded {len(df)} records")
            
        except Exception as e:
            print(f"    Error processing {file.name}: {e}")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        # Clean text columns
        text_cols = combined.select_dtypes(include=['object']).columns
        combined = clean_df_text_columns(combined, text_cols)
        return combined
    return pd.DataFrame()

def load_scoring():
    """Load scoring data"""
    print("Loading SCORING data...")
    try:
        df = pd.read_excel(SCORING_PATH)
        df.columns = [clean_text(str(c)) for c in df.columns]
        
        # Expected columns: รหัสประจำตัวนักเรียน, ปีการศึกษา, คะแนนเต็ม, คะแนนที่ได้, ร้อยละ, เกรด, รหัสวิชา, ชื่อวิชา, ชื่อวิชาภาษาอังกฤษ
        expected_cols = ['รหัสประจำตัวนักเรียน', 'ปีการศึกษา', 'คะแนนเต็ม', 'รหัสวิชา']
        
        # Check if we have the expected structure
        has_expected = any(col in df.columns for col in expected_cols)
        if not has_expected:
            print(f"    Warning: SCORING file doesn't have expected Thai columns")
            print(f"    Found columns: {list(df.columns)}")
            return pd.DataFrame()
        
        # Clean text columns
        text_cols = df.select_dtypes(include=['object']).columns
        df = clean_df_text_columns(df, text_cols)
        
        # Convert numeric columns
        numeric_cols = ['คะแนนเต็ม', 'คะแนนที่ได้', 'ร้อยละ', 'ปีการศึกษา']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"    Loaded {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error loading scoring data: {e}")
        return pd.DataFrame()
    

def load_semester_fee():
    """Load semester fee data"""
    print("Loading SEMESTER FEE data...")
    try:
        df = pd.read_excel(SEMESTER_FEE_PATH)
        df.columns = [clean_text(str(c)) for c in df.columns]
        
        # Expected columns: รหัสประจำตัวนักเรียน, ปีการศึกษา, คะแนนเต็ม, คะแนนที่ได้, ร้อยละ, เกรด, รหัสวิชา, ชื่อวิชา, ชื่อวิชาภาษาอังกฤษ
        # expected_cols = ['รหัสประจำตัวนักเรียน', 'ปีการศึกษา', 'คะแนนเต็ม', 'รหัสวิชา']
        
        # # Check if we have the expected structure
        # has_expected = any(col in df.columns for col in expected_cols)
        # if not has_expected:
        #     print(f"    Warning: SCORING file doesn't have expected Thai columns")
        #     print(f"    Found columns: {list(df.columns)}")
        #     return pd.DataFrame()
        
        # Clean text columns
        text_cols = df.select_dtypes(include=['object']).columns
        df = clean_df_text_columns(df, text_cols)
        
        # Convert numeric columns
        numeric_cols = ['รหัสประจำตัว',	'ปีการศึกษา',	'ภาคเรียน',	'จำนวนเงิน',	'ชำระแล้ว',	'ค้างชำระ']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"    Loaded {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error loading scoring data: {e}")
        return pd.DataFrame()

def load_student():
    """Load student data"""
    print("Loading STUDENT data...")
    try:
        df = pd.read_excel(STUDENT_PATH)
        df.columns = [clean_text(str(c)) for c in df.columns]
        
        # Clean text columns
        text_cols = df.select_dtypes(include=['object']).columns
        df = clean_df_text_columns(df, text_cols)
        
        # Standardize date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'วัน' in col or 'เกิด' in col]
        for col in date_cols:
            df[col] = df[col].apply(standardize_date)
        
        return df
    except Exception as e:
        print(f"Error loading student data: {e}")
        return pd.DataFrame()

# ---------- DB CREATION ----------
def create_database(attendance_df, food_df, hospital_df, library_df, scoring_df, student_df, semester_fee_df):
    """Create SQLite database with all tables"""
    print("\nCreating database...")
    
    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create tables
        tables_created = 0
        
        if not attendance_df.empty:
            attendance_df.to_sql('ATTENDANCE', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  ATTENDANCE table created: {len(attendance_df)} records")
        
        if not food_df.empty:
            food_df.to_sql('FOOD', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  FOOD table created: {len(food_df)} records")
        
        if not hospital_df.empty:
            hospital_df.to_sql('HOSPITAL', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  HOSPITAL table created: {len(hospital_df)} records")
        
        if not library_df.empty:
            library_df.to_sql('LIBRARY', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  LIBRARY table created: {len(library_df)} records")
        
        if not scoring_df.empty:
            scoring_df.to_sql('SCORING', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  SCORING table created: {len(scoring_df)} records")

        if not semester_fee_df.empty:
            semester_fee_df.to_sql('SEMESTER_FEE', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  SEMESTER_FEE table created: {len(semester_fee_df)} records")
        
        if not student_df.empty:
            student_df.to_sql('STUDENT', conn, if_exists='replace', index=False)
            tables_created += 1
            print(f"  STUDENT table created: {len(student_df)} records")
        
        print(f"\nTotal tables created: {tables_created}")
        
        # Create some useful indexes
        cursor = conn.cursor()
        
        # Indexes for FOOD table
        if not food_df.empty:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_food_date ON FOOD(transaction_date);")
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_food_student ON FOOD(student_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_food_product ON FOOD(product_id);")
        
        # Indexes for STUDENT table
        if not student_df.empty:
            # Find the student ID column (could be Thai or English)
            student_id_cols = ['student_id', 'รหัสประจำตัว', 'รหัสนักเรียน']
            student_id_col = None
            for col in student_id_cols:
                if col in student_df.columns:
                    student_id_col = col
                    break
            
            if student_id_col:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_student_id ON STUDENT([{student_id_col}]) WHERE [{student_id_col}] IS NOT NULL;")
        
        conn.commit()
        print("Indexes created successfully")
        
    finally:
        conn.close()

# ---------- MAIN ----------
def main():
    print("=== Comprehensive Database Builder ===")
    print(f"Data directory: {DATA_DIR.resolve()}")
    print(f"Output database: {DB_PATH.resolve()}")
    print()
    
    # Load all data
    attendance_df = load_attendance()
    food_df = load_food()
    hospital_df = load_hospital()
    library_df = load_library()
    scoring_df = load_scoring()
    semester_fee_df = load_semester_fee()
    student_df = load_student()
    
    # Summary
    print(f"\nData Summary:")
    print(f"  ATTENDANCE: {len(attendance_df)} records")
    print(f"  FOOD: {len(food_df)} records")
    print(f"  HOSPITAL: {len(hospital_df)} records")
    print(f"  LIBRARY: {len(library_df)} records")
    print(f"  SCORING: {len(scoring_df)} records")
    print(f"  SEMESTER FEE: {len(semester_fee_df)} records")
    print(f"  STUDENT: {len(student_df)} records")
    
    # Create database
    create_database(attendance_df, food_df, hospital_df, library_df, scoring_df, student_df, semester_fee_df)
    
    print(f"\n✅ Database created successfully: {DB_PATH.resolve()}")
    
    # Quick validation
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    print(f"📋 Tables in database: {[table[0] for table in tables]}")

if __name__ == "__main__":
    main()
