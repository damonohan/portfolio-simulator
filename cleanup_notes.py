import os
import glob

def cleanup_old_note_files():
    # Get the script's directory and move up one level
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.join(script_dir, "..")
    note_data_dir = os.path.join(parent_dir, "note_data")
    
    # Pattern to match timestamped note files
    pattern = os.path.join(note_data_dir, "note_participation_rates_*.csv")
    
    # Find and delete matching files
    for file_path in glob.glob(pattern):
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"\nCurrent note data should be in: {os.path.join(note_data_dir, 'growth_notes.csv')}")

if __name__ == "__main__":
    response = input("This will delete all timestamped note participation rate files. Continue? (y/n): ")
    if response.lower() == 'y':
        cleanup_old_note_files()
        print("Cleanup complete!")
    else:
        print("Cleanup cancelled.")