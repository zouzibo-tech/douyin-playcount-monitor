"""聚合分析：总览、日增、分集占比、停涨识别。"""
from datetime import datetime

import store


def _d(s):
    return s or ""


def overview():
    fd = store.latest_date()
    if not fd:
        return {"fetch_date": None, "prev_date": None, "mixes": [],
                "total_play": 0, "total_delta": 0, "mix_count": 0,
                "stop_count": 0, "accounts": []}
    pd_ = store.prev_date(fd)
    rows = store.mix_overview(fd)

    total_play = sum((r.get("play_vv") or 0) for r in rows)
    total_delta = sum((r.get("delta") or 0) for r in rows)

    for r in rows:
        r["episodes"] = store.episodes_of(r["mix_id"], fd)
        r["account"] = r.get("author_name") or "-"

    stop_count = 0
    for r in rows:
        tr = store.mix_trend(r["mix_id"])
        if len(tr) >= 2:
            last2 = tr[-2:]
            a = last2[0].get("play_vv") or 0
            b = last2[1].get("play_vv") or 0
            if b - a == 0:
                stop_count += 1
    accounts = {}
    for r in rows:
        a = accounts.setdefault(r["account"], {"account": r["account"], "mixes": 0,
                                              "play": 0, "delta": 0})
        a["mixes"] += 1
        a["play"] += r.get("play_vv") or 0
        a["delta"] += r.get("delta") or 0

    return {
        "fetch_date": fd, "prev_date": pd_, "mixes": rows,
        "total_play": total_play, "total_delta": total_delta,
        "mix_count": len(rows), "stop_count": stop_count,
        "accounts": sorted(accounts.values(), key=lambda x: x["play"], reverse=True),
    }


def mix_detail(mix_id, mix_row=None):
    """分集明细。mix_row 由调用方传入可避免重复全表查询（n 个合集时是 O(n²)）。"""
    if mix_row is None:
        mix_row = next((m for m in store.mix_overview() if m["mix_id"] == mix_id), {})
    dates = [r["fetch_date"] for r in store.q(
        "SELECT fetch_date FROM mix_snapshots WHERE mix_id=? ORDER BY fetch_date",
        (mix_id,))]
    fd = dates[-1] if dates else store.latest_date()
    pd_ = dates[-2] if len(dates) >= 2 else None

    eps = store.episodes_of(mix_id, fd)
    prev = {e["aweme_id"]: e for e in store.episodes_of(mix_id, pd_)} if pd_ else {}
    total = sum((e.get("play_count") or 0) for e in eps) or 0
    out = []
    for e in eps:
        p = prev.get(e["aweme_id"]) or {}
        pc = e.get("play_count") or 0
        ppc = p.get("play_count")
        out.append({
            **e,
            "delta": (pc - ppc) if ppc is not None else None,
            "share": round(pc / total * 100, 1) if total else 0.0,
        })
    return {"mix": mix_row, "episodes": out, "trend": store.mix_trend(mix_id),
            "fetch_date": fd, "prev_date": pd_}


def watch_stats():
    return store.watchlist_stats()


def recent_runs(n=10):
    return store.last_runs(n)


def health():
    """数据健康度：官方总量与分集求和的差异、最近采集情况。"""
    rows = store.mix_overview()
    issues = []
    for r in rows:
        pv, ps = r.get("play_vv"), r.get("play_sum_calc")
        if pv and ps:
            diff = abs(pv - ps)
            if pv and diff / pv > 0.15:
                issues.append({"mix_name": r.get("mix_name"), "play_vv": pv,
                               "play_sum_calc": ps, "diff": diff})
    runs = store.last_runs(1)
    return {"issues": issues, "last_run": runs[0] if runs else None}
