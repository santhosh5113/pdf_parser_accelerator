import json
import pandas as pd

json_path = "shared/output_json/sample_output4.json"  # Change if needed

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

tables = [t for t in data.get("tables", []) if "data" in t and "table_cells" in t["data"] and t["data"]["table_cells"]]

def print_table(table):
    cells = table["data"]["table_cells"]
    if not cells:
        return
    max_row = max(c["end_row_offset_idx"] for c in cells)
    max_col = max(c["end_col_offset_idx"] for c in cells)
    grid = [["" for _ in range(max_col)] for _ in range(max_row)]
    for c in cells:
        for r in range(c["start_row_offset_idx"], c["end_row_offset_idx"]):
            for col in range(c["start_col_offset_idx"], c["end_col_offset_idx"]):
                grid[r][col] = c["text"]
    df = pd.DataFrame(grid)
    print(df.to_markdown(index=False))
    print()

if tables:
    for i, t in enumerate(tables):
        print(f"Table {i+1}:")
        print_table(t)
else:
    print("No tables found")
