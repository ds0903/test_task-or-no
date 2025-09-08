from pathlib import Path
import pandas as pd
from sqlalchemy import insert
from app.core.db import engine
from app.core.db import Base
from app.models.user import User
from app.models.dictionary import Dictionary
from app.models.credit import Credit
from app.models.payment import Payment
from app.models.plan import Plan

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

def read_csv(name: str) -> pd.DataFrame:
    p = DATA / name
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")

    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        first = f.readline()
    if "\t" in first:
        sep = "\t"
    elif ";" in first:
        sep = ";"
    else:
        sep = ","

    df = pd.read_csv(p, sep=sep, encoding="utf-8-sig")
    df.columns = (
        df.columns
        .str.replace(r"^\ufeff", "", regex=True)  # BOM
        .str.strip()
        .str.lower()
    )
    return df

def df_date(df: pd.DataFrame, col: str, nullable: bool = False):
    if col not in df.columns:
        return
    s = (df[col].astype(str).str.strip()
         .replace({"": None, "nan": None, "NaT": None, "0000-00-00": None}))

    s = pd.to_datetime(s, format="mixed", dayfirst=True, errors="coerce")

    df[col] = s.dt.date.where(~s.isna(), None)

    if not nullable and df[col].isna().any():
        bad = df[df[col].isna()][[col]].head(5)
        raise ValueError(f"{col}: не розпарсились значення.\n{bad}")

def main():
    Base.metadata.create_all(bind=engine)

    users = read_csv("users.csv")
    df_date(users, "registration_date")

    credits = read_csv("credits.csv")
    df_date(credits, "issuance_date", nullable=False)
    df_date(credits, "return_date", nullable=False)
    df_date(credits, "actual_return_date", nullable=True)

    payments = read_csv("payments.csv")
    df_date(payments, "payment_date")

    plans = read_csv("plans.csv")
    df_date(plans, "period")

    dictionary = read_csv("dictionary.csv")
    # Тестово вивід прибрати перед продом
    # print("users.columns =", repr(list(users.columns)))
    # print("sample row    =", users.head(1).to_dict("records"))

    with engine.begin() as conn:
        if not conn.execute(insert(User).prefix_with("IGNORE"), users.to_dict("records")).rowcount:
            pass
        if not conn.execute(insert(Dictionary).prefix_with("IGNORE"), dictionary.to_dict("records")).rowcount:
            pass
        if not conn.execute(insert(Credit).prefix_with("IGNORE"), credits.to_dict("records")).rowcount:
            pass
        if not conn.execute(insert(Payment).prefix_with("IGNORE"), payments.to_dict("records")).rowcount:
            pass
        if not conn.execute(insert(Plan).prefix_with("IGNORE"), plans.to_dict("records")).rowcount:
            pass

if __name__ == "__main__":
    main()
