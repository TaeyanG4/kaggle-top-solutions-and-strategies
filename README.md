# Kaggle Top Solutions and Strategies

**Kaggle dataset:** [taeyangg4/kaggle-top-solutions-and-strategies](https://www.kaggle.com/datasets/taeyangg4/kaggle-top-solutions-and-strategies) · **Example notebook:** [Kaggle](https://www.kaggle.com/code/taeyangg4/getting-started-with-kaggle-top-solutions) · **License:** CC BY-NC-SA 4.0

## Repository layout

| path | what it is |
|---|---|
| `data/kaggle_all_solutions_and_strategies_merged.csv` | the main file: every record type merged in one CSV (`record_type`) |
| `data/competitions.csv`, `data/solutions.csv`, `data/strategies.csv` | the same rows split by record type |
| `data/column_descriptions.json` | every column of every file with its meaning and a real example value |
| `notebooks/getting_started.ipynb` | loading the file, interactive charts, agent tools |
| `examples/agent_tools.py` | `similar`, `strategies_for` and `advise` as plain Python functions |
| `CHANGELOG.md` | what changed in each version |

The collection pipeline that builds this file (Kaggle API collectors, LLM extraction and validation) is not part of
this repository.

**Public solution writeups of finished Kaggle competitions — all ranks, not only the winners — with a short summary
of each approach and the techniques it used.** 678 competitions (2010–2026), 7,237
solution writeups and 62,661 technique rows, each linked back to the original writeup: in one merged CSV
(the main file) and, the same rows, in three split CSVs.

> **About the name:** the title and URL say "Top", but the dataset is not limited to top teams: it collects every
> public solution writeup that could be found, of any rank (920 solutions ranked beyond 100 and
> 282 of unknown rank are included). The name stays because Kaggle dataset URLs cannot be renamed.

Built for people and **AI agents** looking for proven strategies: *"which techniques did top-10 teams use in image
segmentation competitions?"*, *"what did teams ranked beyond 100 do differently from the winners?"*, *"what did the
winners of competitions like mine do?"*.

## What you can do with it

- **Find what worked**: the `final_used` techniques of top-ranked solutions in competitions like yours, by pipeline stage.
- **Find what did not work**: `tested_rejected` and `failed` rows are ideas that strong teams tried and dropped.
- **Compare ranks**: solutions of every rank are included, so top-10 and beyond-100 solutions of the same
  competition can be compared.
- **Go to the source**: every solution and strategy row links to the original writeup (`writeup_url`).

```text
your problem: "predict sleep events from wrist accelerometer data"
    │
    ▼
1. similar competitions  competition rows: task_type, modalities,
    │                    metric_name, target_summary
    ▼
2. their solutions       solution rows: rank (any), solution_summary,
    │                    frameworks_libraries, compute
    ▼
3. techniques            strategy rows: pipeline_stage, usage_status
    │                    (final_used / tested_rejected / failed)
    ▼
4. plan with sources     group by pipeline_stage, compare ranks,
                         cite writeup_url, read the writeups
```

## Use it with an AI agent

The files are self-describing CSVs, so an LLM agent with a Python or SQL tool can query them directly. Three
patterns work well:

1. **Give the agent a table tool** (pandas or DuckDB over the CSVs) and instructions like these:

```text
You can query Kaggle solution writeups in competitions.csv, solutions.csv
and strategies.csv (the same rows are in one merged file, filtered by
record_type). To advise on a new problem:
1. Find 5-10 similar competitions (competitions: task_type, modalities,
   metric_name, target_summary).
2. Read their solutions with rank <= 20 and the strategies of those
   solutions.
3. Recommend techniques by pipeline_stage from usage_status ==
   "final_used"; list "tested_rejected" and "failed" techniques
   separately as ideas that did not help.
4. Cite the writeup_url behind every recommendation. Summaries are author
   claims extracted by a model: do not invent scores or results.
```

2. **Give it a ready-made function** that counts techniques and returns links (uses `sols` and `strat` from the
   Quick start below):

```python
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

strategies_for("segmentation", "image")  # what top-10 teams used
strategies_for("segmentation", "image", status="failed")  # dropped ideas
```

3. **Retrieval (RAG)**: embed `competition_title` + `target_summary` (competitions) and `solution_summary`
   (solutions), retrieve the nearest competitions for a new problem, then pull their strategies by
   `competition_slug`. Every strategy row carries its solution's `writeup_url`, so each answer can cite it.

Tips: ask for `usage_status` explicitly (final use versus dropped), use `constraints` (`runtime_limit`, `internet`,
`gpu`) to skip ideas that a code competition does not allow, and group by `technique_id` to merge synonyms. The
[example notebook](https://www.kaggle.com/code/taeyangg4/getting-started-with-kaggle-top-solutions) has these functions, a small "advise me" pipeline
and interactive Plotly charts.

## At a glance

| | |
|---|---:|
| Competitions with an official final leaderboard (plus judged 2025–2026 hackathons) | 678 |
| Competitions with at least one solution writeup | 602 |
| Solution writeups | 7,237 |
| Solution writeups with a model-written summary | 7,144 |
| Ranks 1–10 / 11–100 / beyond 100 / unknown | 3,149 / 2,886 / 920 / 282 |
| Ranks taken from official Meta Kaggle team data | 6,016 |
| Technique rows (one technique in one solution) | 62,661 |
| Distinct techniques (project taxonomy + new names) | 15,387 (273 + 15,114) |
| Years | 2010–2026 |

Solution writeups by final rank:

```text
rank 1-10        ████████████████████████████████  3,149
rank 11-100      █████████████████████████████▍    2,886
rank beyond 100  █████████▍                          920
rank unknown     ██▉                                 282
```

Competitions by segment: Featured 315, Research 186, Playground 160, Recruitment 17. Modalities: tabular 382, image 176, text 128, time_series 81, signal 26, geospatial 21, audio 18, video 13. Task types: classification 329, regression 163, ranking 55, forecasting 45, optimization 38, generation 28, segmentation 28, object_detection 17.

## The files

The **main file** `kaggle_all_solutions_and_strategies_merged.csv` stacks the three kinds of rows in one table; the `record_type` column says which kind a
row is. The **split files** hold the same rows by kind, with only the columns that apply, so they have no
not-applicable blanks. Use whichever is easier.

| file | rows | one row is | columns |
|---|---:|---|---:|
| `kaggle_all_solutions_and_strategies_merged.csv` (main) | 70,576 | any of the three below, marked by `record_type` | 44 |
| `competitions.csv` | 678 | a competition: official facts, task type, modalities, metric, rules summary | 17 |
| `solutions.csv` | 7,237 | a solution writeup: rank, medal, link, summary, frameworks, models, compute | 23 |
| `strategies.csv` | 62,661 | one technique in one solution: pipeline stage and whether it was used, rejected or failed | 18 |

How the record types fit together:

```text
competition     678 rows  competitions.csv: official facts, task_type,
    │  competition_slug      modalities, metric
    ▼
solution      7,237 rows  solutions.csv: one writeup of any rank: rank,
    │  writeup_id            medal, writeup_url, summary, stack
    ▼
strategy     62,661 rows  strategies.csv: one technique: pipeline_stage,
                             usage_status (used / dropped / failed)
```

How to read it:

1. **In the merged file, filter on `record_type` first.** A column that does not apply to a record type is empty
   there (the split files leave such columns out); the column table below says which split files have each column.
2. **Join keys**: `competition_slug` links everything to its competition, and `writeup_id` links strategies to
   their solution. Solutions and strategies repeat `year`, `task_type` and `modalities` (strategies also
   `writeup_url`, `rank`, `rank_status` and `medal`), so most questions need no join. `strategy_id` in
   strategies.csv is the `record_id` of the merged file.
3. **List and object columns are JSON strings** (`task_type`, `modalities`, `domain`, `competition_tags`,
   `constraints`, `field_sources`, `hint_tags`, `frameworks_libraries`, `models_pretrained`, `external_data`):
   parse them with `json.loads`.
4. **Empty means unknown or not stated** — never zero and never "not used". `rank` is empty when the rank is unknown;
   `rank_status` says how a rank was established. `medal` is `none` for an officially ranked team without a medal
   and empty only when the medal is unknown; `metric_name` is empty for judged hackathons (no leaderboard), and
   `reward_quantity` when the prize is not cash (`reward_type`).
5. **Summaries and techniques are author claims extracted by a model** (`claim_type`, `review_status`). Open
   `writeup_url` for the details.

## Example rows (real data)

**A `competition` row** (`child-mind-institute-detect-sleep-states`; empty columns left out):

| column | value |
|---|---|
| `record_type` | `competition` |
| `record_id` | `child-mind-institute-detect-sleep-states` |
| `competition_slug` | `child-mind-institute-detect-sleep-states` |
| `competition_title` | Child Mind Institute - Detect Sleep States |
| `year` | `2023` |
| `segment` | `Featured` |
| `total_teams` | `1877` |
| `reward_quantity` | `50000` |
| `reward_type` | `USD` |
| `competition_url` | https://www.kaggle.com/competitions/child-mind-institute-detect-sleep-states |
| `competition_tags` | `["subject > health and fitness > health", "task > multiclass classification", "technique > time series analysis"]` |
| `task_type` | `["classification", "forecasting"]` |
| `modalities` | `["time_series"]` |
| `domain` | `["health"]` |
| `metric_name` | `Event Detection AP` |
| `metric_direction` | `higher_is_better` |
| `target_summary` | Detect sleep-onset and wakeup events, their timesteps, and confidence scores from wrist-worn accelerometer time series. Scoring uses event average precision averaged across timestamp tolerances and event classes. |
| `constraints` | {"code_competition": true, "external_data": "Freely and publicly available external data allowed", "gpu": "GPU notebooks permitted", "internet": "Internet access disabled", "max_daily_submissions": 5, "max_team_size": 5, "pretrained_models": "Freely and publicly available pre-trained models allowed", "public_leaderboard_percentage": 25, "runtime_limit": "CPU/GPU notebook &lt;= 9 hours", "submission_format": "Notebook submission producing submission.csv with row_id,series_id,step,event,score"} |
| `field_sources` | `{"constraints": "official_fields + llm_competition_card", "domain": "kaggle_tag", "modalities": "kaggle_tag", "official": "Meta Kaggle Competitions", "target_summary": "llm_competition_card", "task_type": "kaggle_tag"}` |

**A `solution` row** (rank 1 of that competition):

| column | value |
|---|---|
| `record_type` | `solution` |
| `record_id` | `writeup-0012fd4602c0b062b5f4a8ad` |
| `competition_slug` | `child-mind-institute-detect-sleep-states` |
| `year` | `2023` |
| `task_type` | `["classification", "forecasting"]` |
| `modalities` | `["time_series"]` |
| `writeup_id` | `writeup-0012fd4602c0b062b5f4a8ad` |
| `writeup_url` | https://www.kaggle.com/competitions/child-mind-institute-detect-sleep-states/discussion/459715 |
| `solution_title` | 1st place solution |
| `rank` | `1` |
| `rank_status` | `official_meta_kaggle` |
| `medal` | `gold` |
| `source_type` | `kaggle_official_writeup` |
| `team_link` | `official_team_link` |
| `source_license` | `kaggle_platform_terms` |
| `text_secured` | `true` |
| `hint_tags` | `["catboost", "cnn", "lightgbm", "transformer"]` |
| `solution_summary` | The solution used a downsampling CNN, residual GRU layers, and an upsampling CNN to detect sleep events from overlapping daily sensor chunks. Minute embeddings, periodicity filtering, and progressively sharpened event targets substantially improved the first-stage model. Second-stage tree and sequence models converted candidate regions into minute-level event probabilities. A greedy tolerance-aware selection procedure raised public and private scores from 0.768 and 0.829 to 0.790 and 0.852. |
| `writeup_kind` | `solution_writeup` |
| `claim_type` | `author_claim` |
| `review_status` | `llm_extracted_code_validated` |
| `frameworks_libraries` | `["LightGBM", "CatBoost"]` |

**`strategy` rows** (4 techniques of that solution; every strategy row also repeats `competition_slug`, `writeup_id`, `year`, `task_type`, `modalities`, `rank`, `rank_status` and `medal`):

| technique_id | technique_name | pipeline_stage | usage_status | technique_summary |
|---|---|---|---|---|
| `gru` | GRU | `modeling` | `final_used` | Combined downsampling and upsampling CNNs with residual GRU layers. |
| `feature-engineering` | Feature engineering | `feature-engineering` | `final_used` | Added minute embeddings directly to the final layer to capture event timing bias. |
| `rolling-window-features` | Rolling-window features | `feature-engineering` | `final_used` | Used rolling sensor statistics and a rolling median of absolute angle differences. |
| `sliding-window-inference` | Sliding-window inference | `inference` | `final_used` | Averaged overlapping daily chunks after trimming 30 minutes from their edges. |

## Columns (all 45, with a real example value)

The merged file has every column except `strategy_id`. `split files`: comp = competitions.csv, sol = solutions.csv,
strat = strategies.csv. The same descriptions, with the example, are attached to each column in the Data Explorer.

| column | split files | description | example |
|---|---|---|---|
| `record_type` | merged only | Row kind: competition (one per competition), solution (one per solution writeup) or strategy (one technique used or tried in one solution). Filter on this first. | `competition / solution / strategy` |
| `record_id` | merged only | Unique id of the row within its record_type (competition slug, writeup id, or strategy id). | `child-mind-institute-detect-sleep-states (competition) · writeup-0012fd4602c0b062b5f4a8ad…` |
| `competition_slug` | comp sol strat | Kaggle competition slug; joins all record types. URL: kaggle.com/competitions/{slug}. | `child-mind-institute-detect-sleep-states` |
| `competition_title` | comp | Official competition title (Meta Kaggle). Competition rows. | Child Mind Institute - Detect Sleep States |
| `year` | comp sol strat | Year of the competition deadline. | `2023` |
| `segment` | comp | Kaggle host segment: Featured, Research, Playground or Recruitment. Competition rows. | `Featured` |
| `total_teams` | comp | Number of teams on the final leaderboard (Meta Kaggle). Competition rows. | `1877` |
| `reward_quantity` | comp | Prize amount as reported by Meta Kaggle (currency not normalized); empty when there is no cash amount (see reward_type). Competition rows. | `50000` |
| `reward_type` | comp | Prize type as reported by Meta Kaggle: USD, EUR, Swag, Knowledge, Jobs, Kudos or Prizes; empty = not reported. Competition rows. | `USD` |
| `competition_url` | comp | Competition page URL. Competition rows. | https://www.kaggle.com/competitions/child-mind-institute-detect-sleep-states |
| `competition_tags` | comp | JSON list of official Kaggle tags of the competition. | `["subject > health and fitness > health", "task > multiclass classification", "technique…` |
| `task_type` | comp sol strat | JSON list of task types: classification, regression, ranking, segmentation, object_detection, generation, forecasting, optimization, reinforcement_learning, clustering, other. See field_sources. | `["classification", "forecasting"]` |
| `modalities` | comp sol strat | JSON list of data modalities: tabular, image, text, audio, video, time_series, graph, signal, geospatial, 3d, multimodal, other. | `["time_series"]` |
| `domain` | comp | JSON list of 1-3 subject words (e.g. medicine, finance), model-assigned from the official description. | `["health"]` |
| `metric_name` | comp | Official evaluation metric name (Meta Kaggle); empty for judged hackathons, which have no leaderboard metric. Competition rows. | `Event Detection AP` |
| `metric_direction` | comp | higher_is_better or lower_is_better (Meta Kaggle); empty for judged hackathons. Competition rows. | `higher_is_better` |
| `target_summary` | comp | One or two sentences on what is predicted, from what input, and how it is scored (model-written from the official overview, quote-checked). Competition rows. | Detect sleep-onset and wakeup events, their timesteps, and confidence scores from wrist-w… |
| `constraints` | comp | JSON object of competition rules: code_competition, max_daily_submissions, max_team_size, public_leaderboard_percentage (official) and submission_format, runtime_limit, gpu, internet, external_data, pretrained_models (model-extracted from the rules text, quote-checked; null = not stated). | `{"code_competition": true, "external_data": "Freely and publicly available external data…` |
| `field_sources` | comp | JSON object saying where inferred competition fields come from (official field, Kaggle tag, metric rule or llm_competition_card), so inferred values are not mistaken for official ones. | `{"constraints": "official_fields + llm_competition_card", "domain": "kaggle_tag", "modali…` |
| `writeup_id` | sol strat | Stable id of the solution writeup; joins solution and strategy rows. | `writeup-0012fd4602c0b062b5f4a8ad` |
| `writeup_url` | sol strat | Link to the original solution writeup (Kaggle discussion / writeup page, GitHub, or blog); strategy rows repeat the link of their solution. | https://www.kaggle.com/competitions/child-mind-institute-detect-sleep-states/discussion/4… |
| `solution_title` | sol | Title of the writeup as posted (for a GitHub README without one: its first heading); empty when neither exists. | 1st place solution |
| `rank` | sol strat | Final private leaderboard rank of the team (see rank_status). Empty when unknown. | `1` |
| `rank_status` | sol strat | official_meta_kaggle = rank from official Meta Kaggle team data; reported_only = rank stated by the author or a source only (with an empty rank: the reported ranks disagree, so none is chosen); bound_only = only a bound such as top 10; unknown. | `official_meta_kaggle` |
| `medal` | sol strat | Official medal of the team: gold, silver or bronze; none = officially ranked without a medal (outside the medal zone, or a competition without medals); empty = unknown (the rank is not official). | `gold` |
| `source_type` | sol | Where the writeup lives: kaggle_official_writeup, kaggle_discussion_unlinked, kaggle_writeup_page, kaggle_notebook, kaggle_other_page, kaggle_blog_legacy, github_repo, external_web. | `kaggle_official_writeup` |
| `team_link` | sol | official_team_link = the writeup is tied to the official team; claimed_only = only the author's claim links it; unknown. | `official_team_link` |
| `source_license` | sol | License of the source text when known (kaggle_platform_terms for Kaggle pages, SPDX-like id for GitHub repositories); empty = unknown. The original text is not included here. | `kaggle_platform_terms` |
| `text_secured` | sol | true when the writeup text was available to build the summary and techniques. | `true` |
| `hint_tags` | sol | JSON list of technique hints from third-party annotation datasets (unverified hints). | `["catboost", "cnn", "lightgbm", "transformer"]` |
| `solution_summary` | sol | 3-5 sentence English summary of the final approach, what mattered and notable results (model-written from the writeup; an author claim, not independently verified). Solution rows. | The solution used a downsampling CNN, residual GRU layers, and an upsampling CNN to detec… |
| `writeup_kind` | sol | solution_writeup = describes the team's solution; partial_solution = an approach or part of a pipeline; not_a_solution = a ranked team's post that does not describe the solution itself (often only links to code, slides or a blog: follow writeup_url). Solution rows with a summary. | `solution_writeup` |
| `technique_id` | strat | Technique concept id from the project taxonomy, or new:{name} for a technique outside it. Strategy rows. | `gru` |
| `technique_name` | strat | Readable technique name. Strategy rows. | GRU |
| `technique_category` | strat | Concept category (model, technique, library, task) or proposed for new:{name}. Strategy rows. | `model` |
| `pipeline_stage` | strat | Where the technique sits: data-selection, preprocessing, feature-engineering, augmentation, modeling, training, validation, ensemble, postprocessing, inference. Strategy rows. | `modeling` |
| `usage_status` | strat | final_used = in the final solution; tested_rejected = tried and not kept; failed = did not work; mentioned = no use claimed; unknown. Strategy rows. | `final_used` |
| `technique_summary` | strat | One-line description of how the technique was used in this solution. Strategy rows. | Combined downsampling and upsampling CNNs with residual GRU layers. |
| `claim_type` | sol strat | author_claim = what the writeup's authors state (extracted by a model); third_party_annotation = from an annotation dataset only. | `author_claim` |
| `review_status` | sol strat | How the row was checked: llm_extracted_code_validated (every technique and stack item had to match the writeup text), llm_extracted_summary_has_unverified_terms (summary keeps a term not found literally in the text, often an expanded abbreviation), assistant_reviewed, unreviewed. | `llm_extracted_code_validated` |
| `frameworks_libraries` | sol | JSON list of frameworks and libraries named in the writeup. Solution rows. | `["LightGBM", "CatBoost"]` |
| `models_pretrained` | sol | JSON list of models / pretrained weights named in the writeup. Solution rows. | `["DeepChem/ChemBERTa-77M-MTR"]` |
| `compute` | sol | Hardware and training time as stated in the writeup (e.g. 4x A100, 2 days); empty = not stated (never assumed to be zero). Solution rows. | About two hours for inference. |
| `external_data` | sol | JSON list of external datasets named in the writeup. Solution rows. | `["2018 external data"]` |
| `strategy_id` | strat | Unique id of the strategy row (one technique in one solution); record_id of the merged file. | `card-strategy-ecd35cf7e0080fba06d483a1` |

## Values of the categorical columns

`usage_status` (strategy rows)

| value | rows | meaning |
|---|---:|---|
| `final_used` | 53,977 | in the final solution |
| `tested_rejected` | 4,286 | tried and not kept |
| `failed` | 2,731 | tried and did not work |
| `unknown` | 1,005 | use not clear from the writeup |
| `mentioned` | 662 | mentioned, no use claimed |

`rank_status` (solution rows)

| value | rows | meaning |
|---|---:|---|
| `official_meta_kaggle` | 6,016 | rank from official Meta Kaggle team data |
| `reported_only` | 942 | rank stated by the author or a source only (empty `rank`: the reports disagree) |
| `unknown` | 279 | rank not known (`rank` is empty) |

`writeup_kind` (solution rows)

| value | rows | meaning |
|---|---:|---|
| `solution_writeup` | 6,437 | describes the team's solution |
| `partial_solution` | 434 | an approach or part of a pipeline |
| `not_a_solution` | 273 | a ranked team's post that does not describe the solution (follow the link) |
| `no_card` | 93 | empty: no summary (text not retrievable or not processed) |

`pipeline_stage` (strategy rows): modeling 15,874, training 10,265, ensemble 6,972, feature-engineering 6,552, inference 4,761, preprocessing 4,637, postprocessing 4,483, validation 4,065, augmentation 2,972, data-selection 2,080.

`source_type` (solution rows): kaggle_official_writeup 6,047, kaggle_discussion_unlinked 802, github_repo 240, kaggle_blog_legacy 90, kaggle_writeup_page 22, kaggle_notebook 21, external_web 15.

## Coverage by year

Solution writeups by competition deadline year (with the number of competitions in that year):

```text
2010 ·   7 comps  ▌                                    17
2011 ·  15 comps  █▍                                   43
2012 ·  36 comps  █                                    32
2013 ·  36 comps  █▊                                   58
2014 ·  30 comps  ██▎                                  74
2015 ·  38 comps  ████▎                               135
2016 ·  33 comps  ██████▏                             199
2017 ·  37 comps  ████████▏                           263
2018 ·  46 comps  ████████████▍                       399
2019 ·  54 comps  ████████████████████▊               668
2020 ·  51 comps  ████████████████████▊               670
2021 ·  54 comps  ██████████████████████▉             739
2022 ·  51 comps  ████████████████████▉               672
2023 ·  62 comps  ████████████████████████████████  1,031
2024 ·  43 comps  ██████████████████████▏             712
2025 ·  46 comps  ███████████████████▉                641
2026 ·  39 comps  ███████████████████████████▍        884
```

## Most frequent techniques in final solutions

Strategy rows with `usage_status = final_used`, project taxonomy concepts only:

```text
Feature engineering      ████████████████████████████████  1,813
Ensembling               ████████████████████████▏         1,366
Data augmentation        ██████████████████████▍           1,270
Post-processing          ██████████████████████            1,246
Weighted averaging       ███████████████████▏              1,087
LightGBM                 █████████████████▋                  998
K-fold cross-validation  ███████████████▏                    857
Prediction averaging     ██████████████                      796
Stacking                 █████████████▎                      752
Test-time augmentation   █████████████▎                      752
XGBoost                  ████████████▊                       722
External data            ███████████▉                        673
```

## Quick start

```python
import json
import pandas as pd

DATA = "data/"
comps = pd.read_csv(DATA + "competitions.csv")
sols = pd.read_csv(DATA + "solutions.csv")
strat = pd.read_csv(DATA + "strategies.csv")
# or the merged main file, filtered by record_type:
# df = pd.read_csv(DATA + "kaggle_all_solutions_and_strategies_merged.csv",
#                  low_memory=False)
# sols = df[df.record_type == "solution"]

# List columns are JSON strings
comps = comps.assign(task_type=comps.task_type.map(json.loads),
                     modalities=comps.modalities.map(json.loads))

# 1. Techniques used by top-10 solutions of image segmentation competitions
seg = strat[strat.task_type.str.contains("segmentation", na=False)
            & strat.modalities.str.contains("image", na=False)
            & (strat["rank"] <= 10) & (strat.usage_status == "final_used")]
print(seg.technique_name.value_counts().head(15))

# 2. All solutions of one competition, best rank first (any rank)
slug = "child-mind-institute-detect-sleep-states"
cols = ["rank", "solution_title", "writeup_url", "solution_summary"]
print(sols[sols.competition_slug == slug].sort_values("rank")[cols])

# 3. Ideas that top teams tried and dropped (useful negatives)
dropped = strat[strat.usage_status.isin(["tested_rejected", "failed"])
                & (strat["rank"] <= 20)]
print(dropped[["competition_slug", "technique_name", "technique_summary"]])

# 4. One solution with its techniques
first = sols[(sols.competition_slug == slug) & (sols["rank"] == 1)]
cols = ["pipeline_stage", "technique_name", "usage_status"]
print(strat[strat.writeup_id == first.writeup_id.iloc[0]][cols])
```

## Example questions answered from the file

Counted from this version (number of distinct solutions in brackets):

- **Which techniques did top-10 solutions of image segmentation competitions use?** U-Net architecture (78), Test-time augmentation (73), Data augmentation (71), Post-processing (53), Ensembling (43), Threshold optimization (38), Pseudo-labeling (35), Binary cross-entropy (31), Dice loss (28), Prediction averaging (26).
- **Which techniques appear in top-10 solutions of tabular competitions?** Feature engineering (587), LightGBM (307), XGBoost (298), Stacking (253), Aggregation features (226), Feature selection (224), Ensembling (220), Post-processing (207).
- **…and in tabular solutions ranked beyond 100?** Feature engineering (95), LightGBM (73), XGBoost (60), Feature selection (47), Weighted averaging (47), K-fold cross-validation (46), CatBoost (42), Aggregation features (35).
- **What did top-10 teams most often try and drop (tested_rejected or failed)?** Pseudo-labeling (87), Feature engineering (61), Ensembling (54), Data augmentation (53), Stacking (52), Test-time augmentation (52), External data (46), Post-processing (40), Neural network (35), Transformer (33).
- **Which libraries do top-10 solutions name most often?** LightGBM (594), XGBoost (508), PyTorch (317), CatBoost (300), NumPy (157), scikit-learn (146), Optuna (140), Keras (125), TensorFlow (101), OpenCV (83).
- **Which competitions have the most solution writeups?** `ai-agent-security-multi-step-tool-attacks` (104), `rogii-wellbore-geology-prediction` (68), `icr-identify-age-related-conditions` (57), `feedback-prize-english-language-learning` (55), `commonlit-evaluate-student-summaries` (53).

## How it was built

1. **Competitions and ranks**: official Meta Kaggle tables (Competitions, Teams, Tags) give titles, metrics, deadlines,
   final private ranks and medals. Only finished competitions with official final leaderboards are included,
   plus judged 2025–2026 hackathons.
2. **Solution writeups**: links come from official Kaggle writeups and discussion topics (official Kaggle API),
   public solution-annotation datasets, winners' blog posts and GitHub READMEs. Writeups of **every rank** are kept,
   not only the top 100. Duplicates of the same writeup are removed; a rank is never guessed (`rank_status`).
3. **Summaries and techniques**: an LLM read each collected writeup (first 20,000 characters) and produced a
   summary, up to 12 key techniques with pipeline stage and usage status, frameworks, models, compute and external
   data. Code accepted a card only if **every technique and stack item came with a quote found verbatim in that
   writeup**; failures were regenerated in single-writeup sessions. Summaries were checked so that numbers and
   names appear in the writeup; the few that keep a term not found literally (usually an expanded abbreviation)
   are marked in `review_status`.
4. **Quality checks**: a separate LLM session re-read a random sample of 200 writeups and compared them with their cards (2026-10-23): 99.0% of technique entries were judged correct and 195 of 200 summaries fully supported (same model family, not a human review; cards regenerated or added after the sample was drawn were not re-checked). A 30-writeup test on cards of the first prompt version found no content mixed between writeups processed in the same session.

No writeup text is redistributed: the file holds links, short model-written summaries, tags and official facts.

## Limitations

- Summaries and techniques are **author claims extracted by a model**, not verified results. Open the link for details.
- `strategy` rows list the *key* techniques of a solution (up to 12), not every detail.
- Writeups longer than 20,000 characters were summarized from their beginning.
- Some competitions have no public solutions; some writeups could not be retrieved (deleted or private).
- Posts that turned out not to be solutions (questions, announcements) are excluded, except posts by a ranked team,
  which are kept with `writeup_kind = not_a_solution` because their links often lead to code, slides or a blog.
- Solutions with an empty `writeup_kind` have a link and rank but no summary (text not retrievable or not processed).
- Task type, modality and domain partly come from rules or a model; `field_sources` says which.

## Sources and credits

Meta Kaggle (Kaggle, Apache 2.0); solution writeups by the Kaggle community (linked, not copied); Kaggle solution
annotation datasets and winners' interview posts used for discovery and hints. Please credit the original authors
through the `writeup_url` links when you use their ideas.

## File names

The main file is `kaggle_all_solutions_and_strategies_merged.csv`: "all" because writeups of all ranks are collected, "merged" because it holds every record
type in one table. Earlier names: kaggle_top_solutions_and_strategies.csv (0.4.0 and earlier), kaggle_all_solutions_and_strategies.csv (0.5.0 and Kaggle v4). The split files `competitions.csv`, `solutions.csv` and
`strategies.csv` were added with Kaggle version 5. The title and URL keep "Top" because Kaggle dataset URLs cannot be
renamed. This card describes version 0.6.0.

## 한국어 소개

캐글 대회의 공개 풀이 글(순위와 관계없이 모두)을 모아 풀이별 짧은 요약과 사용한 기법을 정리한 데이터입니다.
모든 행을 합친 기본 파일(`kaggle_all_solutions_and_strategies_merged.csv`)과, 같은 행을 종류별로 나눈
`competitions.csv`·`solutions.csv`·`strategies.csv`가 함께 있습니다.
사람이나 AI 에이전트가 "비슷한 대회에서 상위 팀은 무엇을 썼고, 무엇을 시도했다가 버렸는지"를 빠르게 찾을 수 있게
만들었습니다. 원문은 복사하지 않고 링크(`writeup_url`)로 연결합니다. 같은 데이터는
[Kaggle 데이터셋](https://www.kaggle.com/datasets/taeyangg4/kaggle-top-solutions-and-strategies)에도 있으며, 매월 갱신을 목표로 합니다. 데이터를 모으고
정리하는 수집 코드는 이 저장소에 포함하지 않았습니다.

## Example notebook

**[Open the example notebook: Getting Started with Kaggle Top Solutions](https://www.kaggle.com/code/taeyangg4/getting-started-with-kaggle-top-solutions)**
loads the file and shows interactive charts and ready-made tools for AI agents. Use *Copy & Edit* to run it yourself; a copy is in `notebooks/getting_started.ipynb`.

## Update log

| date (UTC) | version | what changed |
|---|---|---|
| 2026-10-24 | 0.6.0 (Kaggle v6) | Added competitions.csv, solutions.csv and strategies.csv: the same rows as the merged main file (now kaggle_all_solutions_and_strategies_merged.csv) without not-applicable columns. Filled 283 empty solution titles (official Kaggle post titles, README headings), medal none for 1,089 officially ranked solutions without a medal, writeup_url on every strategy row, and a new reward_type column; empty metric and prize values are explained in the column descriptions. |
| 2026-10-24 | 20261024T054530Z (Kaggle v4) | Added rsna-knee-abnormality-detection (ended 2026-10-22): 19 solution writeups and 215 technique rows; ranks come from the writeup titles until Kaggle publishes the final leaderboard. kaggriculture ranks and medals are now official (Meta Kaggle 2364). One more Cassava writeup summarized. |
| 2026-10-24 | 0.5.0 (Kaggle v3) | Same rows as 0.4.0; the file is now kaggle_all_solutions_and_strategies.csv. Data card: example rows, an example value for every column, a usage and AI agent guide, diagrams, charts and this log. Example notebook: interactive charts and agent tools. |
| 2026-10-23 | 0.4.0 (Kaggle v2) | First full release: solution writeups of all ranks for 677 finished competitions (2010-2026) with short summaries and techniques, in one CSV with links instead of writeup text. |
| 2026-10-23 | 0.3.0-pilot.1 (Kaggle v1) | Pilot: 50 reviewed method applications from 7 solution READMEs and a historical solution index. |

New versions are uploaded after the owner reviews an update. Each version replaces the files; earlier
versions stay in the version history.
