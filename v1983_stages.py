"""V19.8.3 staged research profiles for memory-constrained Streamlit Cloud.

The profiles are resource controls, not investment parameters.  Cloud stages
stop at 100 equities because recorded 92-symbol research already used roughly
651 MiB peak RSS outside Streamlit.  Larger cohorts remain available through
the staged offline runner and ordinary CLI after smaller stages are stable.
"""
from __future__ import annotations
from dataclasses import replace

RELEASE = '19.8.3a'

STAGES = (
    dict(key='S1', label='第1階段｜微型穩定性檢查', stocks=40, dates=4,
         request_budget=140, batch_size=15, factor_audit=False, search_budget=40,
         optional_allowed=False, finance_allowed=False, full_artifacts=False, cloud_enabled=True),
    dict(key='S2', label='第2階段｜小型穩定性檢查', stocks=60, dates=6,
         request_budget=220, batch_size=20, factor_audit=False, search_budget=48,
         optional_allowed=False, finance_allowed=False, full_artifacts=False, cloud_enabled=True),
    dict(key='S3', label='第3階段｜中小型驗證', stocks=80, dates=8,
         request_budget=300, batch_size=20, factor_audit=False, search_budget=64,
         optional_allowed=False, finance_allowed=False, full_artifacts=False, cloud_enabled=True),
    dict(key='S4', label='第4階段｜100檔驗證', stocks=100, dates=12,
         request_budget=420, batch_size=25, factor_audit=False, search_budget=80,
         optional_allowed=True, finance_allowed=False, full_artifacts=False, cloud_enabled=True),
    dict(key='S5', label='第5階段｜150檔離線擴大研究', stocks=150, dates=18,
         request_budget=650, batch_size=30, factor_audit=True, search_budget=96,
         optional_allowed=True, finance_allowed=True, full_artifacts=True, cloud_enabled=False),
)

OFFLINE_EXTENSIONS = (
    dict(key='L1', label='離線擴大｜300檔', stocks=300, dates=40),
    dict(key='L2', label='離線完整｜600檔', stocks=600, dates=100),
)


def get_stage(key: str):
    for stage in STAGES:
        if stage['key'] == key:
            return dict(stage)
    raise ValueError('UNKNOWN_V1983_STAGE')


def stage_index(key: str) -> int:
    return next(i for i, stage in enumerate(STAGES) if stage['key'] == key)


def apply_stage(cfg, key: str, *, optional_data=False, financial_history=False):
    stage = get_stage(key)
    optional = bool(optional_data and stage['optional_allowed'])
    finance = bool(financial_history and stage['finance_allowed'] and optional)
    return replace(
        cfg,
        stocks=int(stage['stocks']),
        dates=int(stage['dates']),
        request_budget=int(stage['request_budget']),
        download_batch_size=int(stage['batch_size']),
        progressive_universe=True,
        factor_audit=bool(stage['factor_audit']),
        sparse_budget=int(stage['search_budget']),
        optional_data=optional,
        financial_history=finance,
        export_full_artifacts=bool(stage['full_artifacts']),
        export_history_database=bool(stage['full_artifacts']),
        research_stage=str(stage['key']),
    )


def stage_from_settings(settings: dict | None):
    settings = settings or {}
    key = str(settings.get('research_stage') or '')
    if any(stage['key'] == key for stage in STAGES):
        return key
    return None


def next_stage_key(key: str | None):
    if key is None:
        return STAGES[0]['key']
    i = stage_index(key)
    return STAGES[min(i + 1, len(STAGES) - 1)]['key']
