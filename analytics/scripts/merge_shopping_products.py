"""Merge shopping list SKUs with product master data."""

from pathlib import Path
import argparse

import pandas as pd


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    normalized = {c.strip().lower(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]
    raise ValueError(f"Missing expected column. Tried: {candidates}. Found: {list(df.columns)}")


def _read_csv_fallback(path: Path) -> pd.DataFrame:
    for encoding in ["utf-8", "utf-8-sig", "cp1252", "latin1"]:
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV with tried encodings: {path}")


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    raw_dir = base / "data" / "raw"
    processed_dir = base / "data" / "processed"

    parser = argparse.ArgumentParser(description="Merge shopping list and products on SKU")
    parser.add_argument(
        "--shopping",
        type=Path,
        default=Path.home() / "OneDrive" / "Desktop" / "SFS 2" / "shopping_list_items.csv",
        help="Path to shopping list CSV",
    )
    parser.add_argument(
        "--products",
        type=Path,
        default=Path.home() / "OneDrive" / "Desktop" / "SFS 2" / "products.csv",
        help="Path to products CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=processed_dir / "shopping_list_products.csv",
        help="Output merged CSV",
    )
    parser.add_argument(
        "--out-unmatched",
        type=Path,
        default=processed_dir / "unmatched_skus.csv",
        help="Output unmatched SKU summary CSV",
    )
    args = parser.parse_args()

    processed_dir.mkdir(parents=True, exist_ok=True)

    shopping = _read_csv_fallback(args.shopping)
    products = _read_csv_fallback(args.products)

    shopping_sku_col = _find_column(shopping, ["ShoppingListItem-Sku", "Sku"])
    product_sku_col = _find_column(products, ["Sku"])

    shopping[shopping_sku_col] = shopping[shopping_sku_col].fillna("").astype(str).str.strip().str.upper()
    products[product_sku_col] = products[product_sku_col].fillna("").astype(str).str.strip().str.upper()

    if shopping_sku_col != "Sku":
        shopping = shopping.rename(columns={shopping_sku_col: "Sku"})
    if product_sku_col != "Sku":
        products = products.rename(columns={product_sku_col: "Sku"})

    # Keep one best product record per SKU to avoid one-to-many merge expansion.
    product_info_cols = [c for c in ["Name", "Brand", "Mfg"] if c in products.columns]
    if product_info_cols:
        products["_completeness"] = products[product_info_cols].notna().sum(axis=1)
        products = (
            products.sort_values(["Sku", "_completeness"], ascending=[True, False])
            .drop_duplicates(subset=["Sku"], keep="first")
            .drop(columns=["_completeness"])
        )
    else:
        products = products.drop_duplicates(subset=["Sku"], keep="first")

    keep_cols = [c for c in ["Sku", "Name", "Brand", "Mfg"] if c in products.columns]
    merged = shopping.merge(products[keep_cols], on="Sku", how="left")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out, index=False)

    missing_product_count = int(merged["Name"].isna().sum()) if "Name" in merged.columns else 0

    if "Name" in merged.columns:
        unmatched = merged[merged["Name"].isna()].copy()
        unmatched_summary = (
            unmatched.groupby("Sku", dropna=False)
            .size()
            .reset_index(name="ShoppingListRowCount")
            .sort_values("ShoppingListRowCount", ascending=False)
        )
        args.out_unmatched.parent.mkdir(parents=True, exist_ok=True)
        unmatched_summary.to_csv(args.out_unmatched, index=False)

    print(f"Saved merged file: {args.out}")
    print(f"Rows: {len(merged):,}")
    print(f"Rows missing product match: {missing_product_count:,}")
    if "Name" in merged.columns:
        print(f"Saved unmatched SKU summary: {args.out_unmatched}")
        print(f"Distinct unmatched SKUs: {len(unmatched_summary):,}")


if __name__ == "__main__":
    main()
