from ibm_watsonx_orchestrate.agent_builder.tools import tool
import pandas as pd

@tool
def get_employee_leave_balance(employee_id: str) -> dict:
    """
    Retrieves leave balance information for a specified employee (case-insensitive) from a CSV file (mocked as a DataFrame).

    Summary of Leave Balance Data:
        - Annual leave (total, used, available)
        - Sick leave (total, used, available)
        - Personal leave (total, used, available)
        - Floating holidays (total, used, available)
        - Bereavement leave available
        - Jury duty leave available
        - Last updated date

    Args:
        employee_id (str): Employee ID to look up (case-insensitive, e.g., 'EMP001').

    Returns:
        dict: Dictionary with leave balance details for an employee, or empty dict if not found.
    """
    try:
        # Read the CSV file
        df = pd.read_csv('employee_leave_balance.csv')  # Replace with your CSV filename

        # Case-insensitive match for employee_id
        mask = df['employee_id'].str.lower() == employee_id.lower()
        filtered_df = df[mask]

        # Check if any rows match
        if filtered_df.empty:
            print(f"No employee with ID {employee_id} found")
            return {}

        # Convert the first matching row to dictionary
        result_dict = filtered_df.iloc[0].to_dict()

        return result_dict

    except FileNotFoundError:
        print("CSV file not found")
        return {}
    except KeyError as e:
        print(f"Column not found: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Example usage:
if __name__ == "__main__":
    employee_id = "EMP001"
    employee_data = get_employee_leave_balance(employee_id)
    if employee_data:
        print("Employee EMP001 data:")
        for key, value in employee_data.items():
            print(f"{key}: {value}")
    else:
        print("No data retrieved")
