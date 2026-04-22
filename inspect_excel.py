import sys
import pandas as pd


def main() -> int:
    path = r"c:\Users\alexa\OneDrive\Área de Trabalho\Projeto Python\Painel SGE\Painel 1 - Copia\AtaMapa (60).xlsx"
    xl = pd.ExcelFile(path)
    print("sheets:", xl.sheet_names)
    df = pd.read_excel(path, sheet_name=xl.sheet_names[0])
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    print("\nhead:")
    print(df.head(5).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

