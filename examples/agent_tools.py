"""Query tools over the split CSVs in data/ (pandas), small enough to register as LLM agent tools.

Run `python examples/agent_tools.py` for a demo. Every result carries `writeup_url` links: cite them instead of
inventing results. Summaries and techniques are author claims extracted by a model.
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
comps = pd.read_csv(DATA / "competitions.csv")
sols = pd.read_csv(DATA / "solutions.csv")
strat = pd.read_csv(DATA / "strategies.csv")  # every row carries its solution's writeup_url


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
    out = s.groupby("technique_name").agg(  # each strategy row has its link
        solutions=("writeup_id", "nunique"), example=("writeup_url", "first"))
    return out.sort_values("solutions", ascending=False).head(top)


def advise(problem, n_competitions=5, max_rank=20, per_stage=3):
    """Similar competitions -> their solutions up to max_rank -> final techniques by stage, plus dropped ideas."""
    found = similar(problem, n_competitions)
    s = strat[strat.competition_slug.isin(found.competition_slug) & (strat['rank'] <= max_rank)]
    plan = (s[s.usage_status == 'final_used'].groupby(['pipeline_stage', 'technique_name'])
            .agg(solutions=('writeup_id', 'nunique'), example=('writeup_url', 'first'))
            .sort_values('solutions', ascending=False).groupby(level=0).head(per_stage).sort_index(level=0, sort_remaining=False))
    dropped = (s[s.usage_status.isin(['tested_rejected', 'failed'])].groupby('technique_name').writeup_id.nunique()
               .sort_values(ascending=False).head(8).rename('solutions'))
    return found[['competition_slug', 'year', 'metric_name']], plan, dropped


if __name__ == "__main__":
    found, plan, dropped = advise("predict sleep events from wrist accelerometer time series")
    print(found.to_string(), plan.to_string(), dropped.to_string(), sep="\n\n")
