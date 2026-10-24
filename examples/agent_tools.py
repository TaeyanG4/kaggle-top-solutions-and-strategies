"""Query tools over kaggle_all_solutions_and_strategies.csv (pandas), small enough to register as LLM agent tools.

Run `python examples/agent_tools.py` for a demo. Every result carries `writeup_url` links: cite them instead of
inventing results. Summaries and techniques are author claims extracted by a model.
"""
from pathlib import Path

import pandas as pd

PATH = Path(__file__).resolve().parents[1] / "data" / "kaggle_all_solutions_and_strategies.csv"
df = pd.read_csv(PATH, low_memory=False)
comps = df[df.record_type == "competition"]
sols = df[df.record_type == "solution"]
strat = df[df.record_type == "strategy"]


def similar(text, n=5):
    words = set(text.lower().split())
    hay = (comps.competition_title.fillna('') + ' ' + comps.target_summary.fillna('')).str.lower()
    score = hay.map(lambda s: len(words & set(s.split())))
    return comps.assign(score=score).sort_values('score', ascending=False)[['competition_slug', 'year', 'metric_name', 'target_summary']].head(n)


def strategies_for(task_type=None, modality=None, max_rank=10,
                   status="final_used", top=15):
    """Most common techniques in matching solutions, one link each."""
    s = strat[strat.usage_status == status]
    if task_type:
        s = s[s.task_type.str.contains(f'"{task_type}"', na=False)]
    if modality:
        s = s[s.modalities.str.contains(f'"{modality}"', na=False)]
    if max_rank:
        s = s[s["rank"] <= max_rank]
    # writeup_url is empty on strategy rows: take it from the solution rows
    links = sols[["writeup_id", "writeup_url"]]
    s = s.drop(columns="writeup_url").merge(links, on="writeup_id")
    out = s.groupby("technique_name").agg(
        solutions=("writeup_id", "nunique"), example=("writeup_url", "first"))
    return out.sort_values("solutions", ascending=False).head(top)


def advise(problem, n_competitions=5, max_rank=20, per_stage=3):
    """Similar competitions -> their solutions up to max_rank -> final techniques by stage, plus dropped ideas."""
    found = similar(problem, n_competitions)
    s = strat[strat.competition_slug.isin(found.competition_slug) & (strat['rank'] <= max_rank)]
    s = s.drop(columns='writeup_url').merge(sols[['writeup_id', 'writeup_url']], on='writeup_id')
    plan = (s[s.usage_status == 'final_used'].groupby(['pipeline_stage', 'technique_name'])
            .agg(solutions=('writeup_id', 'nunique'), example=('writeup_url', 'first'))
            .sort_values('solutions', ascending=False).groupby(level=0).head(per_stage).sort_index(level=0, sort_remaining=False))
    dropped = (s[s.usage_status.isin(['tested_rejected', 'failed'])].groupby('technique_name').writeup_id.nunique()
               .sort_values(ascending=False).head(8).rename('solutions'))
    return found[['competition_slug', 'year', 'metric_name']], plan, dropped


if __name__ == "__main__":
    found, plan, dropped = advise("predict sleep events from wrist accelerometer time series")
    print(found.to_string(), plan.to_string(), dropped.to_string(), sep="\n\n")
