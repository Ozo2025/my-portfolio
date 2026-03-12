"""Build Top Opportunity SKU rankings from shopping list intent data."""

from __future__ import annotations

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


def _safe_rank(series: pd.Series) -> pd.Series:
    if series.nunique(dropna=True) <= 1:
        return pd.Series([1.0] * len(series), index=series.index)
    return series.rank(pct=True, method="average")


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build top opportunity SKU rankings")
    parser.add_argument(
        "--input",
        type=Path,
        default=base / "data" / "processed" / "shopping_list_products.csv",
        help="Path to merged shopping list + product CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "outputs" / "top_opportunity_skus.csv",
        help="Path for ranked Top Opportunity SKU output",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=base / "stories" / "top_opportunity_skus_summary.md",
        help="Path for markdown summary output",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=50,
        help="Number of SKUs to include in output",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input, dtype=str)

    sku_col = _find_column(df, ["Sku"])
    name_col = _find_column(df, ["Name"])

    brand_col = None
    for candidate in ["Brand"]:
        if candidate in df.columns:
            brand_col = candidate
            break

    mfg_col = None
    for candidate in ["Mfg"]:
        if candidate in df.columns:
            mfg_col = candidate
            break

    list_col = _find_column(df, ["ShoppingList-Name", "ShoppingListName"])

    identity_col = None
    for candidate in ["Email", "User Name", "UserName"]:
        if candidate in df.columns:
            identity_col = candidate
            break

    for col in [sku_col, name_col, list_col]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    if identity_col:
        df[identity_col] = df[identity_col].fillna("").astype(str).str.strip()

    matched = df[(df[sku_col] != "") & (df[name_col] != "")].copy()

    if matched.empty:
        raise ValueError("No matched SKU rows found in input dataset.")

    group_cols = [sku_col, name_col]
    if brand_col:
        matched[brand_col] = matched[brand_col].fillna("").astype(str).str.strip()
        group_cols.append(brand_col)
    if mfg_col:
        matched[mfg_col] = matched[mfg_col].fillna("").astype(str).str.strip()
        group_cols.append(mfg_col)

    grouped = matched.groupby(group_cols, dropna=False).agg(
        IntentEvents=(sku_col, "size"),
        ShoppingListCount=(list_col, pd.Series.nunique),
    )

    if identity_col:
        grouped["AccountCount"] = matched.groupby(group_cols, dropna=False)[identity_col].nunique()
    else:
        grouped["AccountCount"] = grouped["ShoppingListCount"]

    ranked = grouped.reset_index()

    ranked["IntentRank"] = _safe_rank(ranked["IntentEvents"])
    ranked["BreadthRank"] = _safe_rank(ranked["ShoppingListCount"])
    ranked["AccountRank"] = _safe_rank(ranked["AccountCount"])

    ranked["OpportunityScore"] = (
        ranked["IntentRank"] * 0.5
        + ranked["BreadthRank"] * 0.3
        + ranked["AccountRank"] * 0.2
    ) * 100

    ranked = ranked.sort_values(
        ["OpportunityScore", "IntentEvents", "ShoppingListCount", "AccountCount"],
        ascending=[False, False, False, False],
    )

    top = ranked.head(max(1, args.top_n)).copy()
    top["OpportunityScore"] = top["OpportunityScore"].round(2)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    top.to_csv(args.output, index=False)

    total_rows = len(df)
    matched_rows = len(matched)
    match_rate = (matched_rows / total_rows) * 100 if total_rows else 0
    distinct_matched_skus = matched[sku_col].nunique()

    top_sku = top.iloc[0]
    top_sku_id = top_sku[sku_col]
    top_sku_name = top_sku[name_col]
    top_sku_score = float(top_sku["OpportunityScore"])

    if brand_col and brand_col in top.columns:
        brand_summary = (
            top.groupby(brand_col, dropna=False)["IntentEvents"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
    else:
        brand_summary = pd.DataFrame(columns=["Brand", "IntentEvents"])

    summary_lines = [
        "# Top Opportunity SKU Summary",
        "",
        "## Dataset Health",
        f"- Total rows analyzed: {total_rows:,}",
        f"- Matched rows used for opportunity model: {matched_rows:,}",
        f"- Match rate: {match_rate:.1f}%",
        f"- Distinct matched SKUs: {distinct_matched_skus:,}",
        "",
        "## Opportunity Model",
        "- Score formula: 50% intent volume + 30% list breadth + 20% account breadth.",
        "- Intent volume = total shopping-list events per SKU.",
        "- List breadth = distinct shopping lists containing SKU.",
        "- Account breadth = distinct users/emails associated to SKU activity.",
        "",
        "## Top Signal",
        f"- Highest-ranked SKU: {top_sku_id} — {top_sku_name}",
        f"- Opportunity score: {top_sku_score:.2f}",
        "",
        "## Top Brands in Opportunity Set",
    ]

    if not brand_summary.empty:
        for _, row in brand_summary.iterrows():
            brand_name = row.iloc[0] if str(row.iloc[0]).strip() else "(Unspecified)"
            summary_lines.append(f"- {brand_name}: {int(row['IntentEvents']):,} intent events")
    else:
        summary_lines.append("- Brand data unavailable in source file.")

    summary_lines.extend(
        [
            "",
            "## Output Files",
            f"- Ranked opportunities: {args.output}",
            f"- Summary brief: {args.summary}",
            "",
            "## Privacy Note",
            "- Outputs are aggregate-level and do not publish raw email or username values.",
        ]
    )

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(summary_lines), encoding="utf-8")

    print(f"Saved ranked opportunities: {args.output}")
    print(f"Saved summary: {args.summary}")
    print(f"Rows analyzed: {total_rows:,}")
    print(f"Matched rows: {matched_rows:,} ({match_rate:.1f}%)")
    print(f"Distinct matched SKUs: {distinct_matched_skus:,}")


if __name__ == "__main__":
    main()
