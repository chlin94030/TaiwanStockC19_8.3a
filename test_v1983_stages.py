from dataclasses import asdict
import pandas as pd
from v19_config import Settings
from v1983_stages import STAGES, apply_stage, get_stage, next_stage_key
from v198_universe import progressive_balanced_sample


def fake_catalog(n=900):
    rows=[]
    for i in range(n):
        code=1000+i
        suffix='.TW' if i%2==0 else '.TWO'
        rows.append({'ticker':f'{code:04d}{suffix}','name':str(code),'sector':f'S{i%9}'})
    return rows


def test_stage_sizes_are_strictly_progressive_and_safe_first():
    stocks=[x['stocks'] for x in STAGES]
    dates=[x['dates'] for x in STAGES]
    assert stocks==[40,60,80,100,150]
    assert dates==[4,6,8,12,18]
    assert stocks==sorted(stocks) and dates==sorted(dates)
    s=apply_stage(Settings(),'S1')
    assert s.stocks==40 and s.dates==4 and s.download_batch_size==15
    assert s.progressive_universe and not s.export_full_artifacts and not s.export_history_database
    assert s.factor_audit is False and s.optional_data is False


def test_optional_data_opens_only_after_small_stages():
    s2=apply_stage(Settings(optional_data=True,financial_history=True),'S2',optional_data=True,financial_history=True)
    assert not s2.optional_data and not s2.financial_history
    s3=apply_stage(Settings(optional_data=True,financial_history=True),'S3',optional_data=True,financial_history=True)
    assert not s3.optional_data and not s3.financial_history
    s4=apply_stage(Settings(optional_data=True,financial_history=True),'S4',optional_data=True,financial_history=True)
    assert s4.optional_data and not s4.financial_history
    s5=apply_stage(Settings(optional_data=True,financial_history=True),'S5',optional_data=True,financial_history=True)
    assert s5.optional_data and s5.financial_history and s5.export_full_artifacts and s5.export_history_database


def test_progressive_balanced_sample_is_nested_and_order_invariant():
    src=fake_catalog()
    pools=[]
    for n in (40,60,80,100,150):
        a=progressive_balanced_sample(src,n,1900,'balanced')
        b=progressive_balanced_sample(src[::-1],n,1900,'balanced')
        assert [x['ticker'] for x in a]==[x['ticker'] for x in b]
        pools.append({x['ticker'] for x in a})
    assert all(pools[i] < pools[i+1] for i in range(len(pools)-1))


def test_stage_navigation():
    assert next_stage_key(None)=='S1'
    assert next_stage_key('S1')=='S2'
    assert next_stage_key('S4')=='S5'
    assert next_stage_key('S5')=='S5'
