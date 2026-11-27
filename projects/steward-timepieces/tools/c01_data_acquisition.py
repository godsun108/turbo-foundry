"""WP-49 traceable chronograph-control instrumentation and DAQ analysis."""
from __future__ import annotations
import math

class AcquisitionError(ValueError): pass

def _finite(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise AcquisitionError(f"{name} must be finite numeric")
    return float(v)

def _required(record,fields,label):
    for f in fields:
        if not record.get(f): raise AcquisitionError(f"{label}: {f} is required")

def validate_run_manifest(m):
    errors=[]
    for f in ("run_id","candidate_id","candidate_revision","article_id","fixture_id","fixture_revision",
              "procedure_id","procedure_revision","test_condition_id","evidence_id","source_revision",
              "operator_id","started_at_utc"):
        if not m.get(f): errors.append(f"missing {f}")
    channels=m.get("channels",[]); ids=[c.get("channel_id") for c in channels]
    if not channels: errors.append("at least one channel is required")
    if len(set(ids))!=len(ids): errors.append("channel IDs must be unique")
    for i,c in enumerate(channels):
        for f in ("channel_id","measurand","unit","instrument_id","calibration_id","calibration_status",
                  "sampling_method","evidence_id","source_revision"):
            if not c.get(f): errors.append(f"channels[{i}] missing {f}")
        if c.get("calibration_status")!="current": errors.append(f"channels[{i}] calibration is not current")
        if c.get("sample_rate_hz") is not None:
            try:
                if _finite(c["sample_rate_hz"],"sample_rate_hz")<=0: errors.append(f"channels[{i}] sample rate must be positive")
            except AcquisitionError as e: errors.append(str(e))
    return {"valid":not errors,"errors":errors,"measurement_approval_implied":False}

def validate_samples(samples,channel_id):
    if not isinstance(samples,list) or len(samples)<2: raise AcquisitionError("at least two samples required")
    out=[]; prev=None
    for i,s in enumerate(samples):
        t=_finite(s.get("time_s"),f"{channel_id}[{i}].time_s")
        v=_finite(s.get("value"),f"{channel_id}[{i}].value")
        if prev is not None and t<=prev: raise AcquisitionError("sample times must strictly increase")
        prev=t; out.append({"time_s":t,"value":v})
    return out

def apply_clock_correction(samples,offset_s,drift_s_per_s,evidence_id,source_revision):
    b=_finite(offset_s,"offset_s"); d=_finite(drift_s_per_s,"drift_s_per_s")
    if not evidence_id or not source_revision: raise AcquisitionError("clock-correction provenance required")
    raw=validate_samples(samples,"clock")
    corrected=[{"time_s":s["time_s"]+b+d*s["time_s"],"value":s["value"]} for s in raw]
    if any(corrected[i]["time_s"]<=corrected[i-1]["time_s"] for i in range(1,len(corrected))):
        raise AcquisitionError("clock correction makes time non-monotonic")
    return {"samples":corrected,"offset_s":b,"drift_s_per_s":d,"evidence_id":evidence_id,
      "source_revision":source_revision,"note":"Correction requires measured reference-timebase evidence."}

def interpolate_at(samples,target_times):
    src=validate_samples(samples,"interpolation"); out=[]; j=0
    for tv in target_times:
        t=_finite(tv,"target_time")
        if t<src[0]["time_s"] or t>src[-1]["time_s"]: raise AcquisitionError("extrapolation prohibited")
        while j+1<len(src) and src[j+1]["time_s"]<t: j+=1
        if src[j]["time_s"]==t: v=src[j]["value"]
        elif src[j+1]["time_s"]==t: v=src[j+1]["value"]
        else:
            a,b=src[j],src[j+1]
            v=a["value"]+(b["value"]-a["value"])*(t-a["time_s"])/(b["time_s"]-a["time_s"])
        out.append({"time_s":t,"value":v})
    return out

def force_travel_metrics(samples,evidence_id,source_revision):
    if not isinstance(samples,list) or len(samples)<2: raise AcquisitionError("at least two samples required")
    rows=[]
    for i,s in enumerate(samples):
        t=_finite(s.get("time_s"),f"sample[{i}].time_s")
        x=_finite(s.get("travel_mm"),f"sample[{i}].travel_mm")
        f=_finite(s.get("force_n"),f"sample[{i}].force_n")
        if f<0: raise AcquisitionError("force must be nonnegative")
        if rows and t<=rows[-1]["time_s"]: raise AcquisitionError("time must strictly increase")
        rows.append({"time_s":t,"travel_mm":x,"force_n":f})
    work=sum((a["force_n"]+b["force_n"])*.5*(b["travel_mm"]-a["travel_mm"])
             for a,b in zip(rows,rows[1:]))
    return {"sample_count":len(rows),"peak_sampled_force_n":max(r["force_n"] for r in rows),
      "travel_min_mm":min(r["travel_mm"] for r in rows),"travel_max_mm":max(r["travel_mm"] for r in rows),
      "signed_force_travel_work_j":work/1000.0,"evidence_id":evidence_id,"source_revision":source_revision,
      "limitations":["Signed trapezoidal integration in acquisition order; return stroke may subtract work.",
      "Sampled peak may miss a transient peak.","No filtering, compliance correction or uncertainty propagation."]}

def angular_error_deg(measured_deg,zero_deg):
    a=_finite(measured_deg,"measured_deg"); z=_finite(zero_deg,"zero_deg")
    return (a-z+180.0)%360.0-180.0

def reset_zero_result(observations_deg,zero_datum_deg,evidence_id,source_revision):
    if not isinstance(observations_deg,list) or not observations_deg: raise AcquisitionError("reset observations required")
    errors=[angular_error_deg(v,zero_datum_deg) for v in observations_deg]
    sx=sum(math.sin(math.radians(v)) for v in errors); cx=sum(math.cos(math.radians(v)) for v in errors)
    mean=math.degrees(math.atan2(sx,cx))
    arithmetic=sum(errors)/len(errors)
    sd=(math.sqrt(sum((v-arithmetic)**2 for v in errors)/(len(errors)-1)) if len(errors)>1 else None)
    return {"signed_errors_deg":errors,"circular_mean_error_deg":mean,
      "maximum_absolute_error_deg":max(abs(v) for v in errors),"sample_standard_deviation_deg":sd,
      "evidence_id":evidence_id,"source_revision":source_revision,
      "limitations":["Angular uncertainty and zero-datum calibration are not included."]}

def event_latency(events,source_event,target_event,evidence_id,source_revision):
    src=[_finite(e["time_s"],"source time") for e in events if e.get("event_id")==source_event]
    dst=[_finite(e["time_s"],"target time") for e in events if e.get("event_id")==target_event]
    if len(src)!=1 or len(dst)!=1: raise AcquisitionError("each event ID must occur exactly once")
    if not evidence_id or not source_revision: raise AcquisitionError("event timing provenance required")
    return {"source_event":source_event,"target_event":target_event,"latency_s":dst[0]-src[0],
      "evidence_id":evidence_id,"source_revision":source_revision,
      "note":"Valid only after channels share a corrected timebase."}

def validate_comparison(a,b):
    fields=("procedure_id","procedure_revision","test_condition_id","fixture_id","fixture_revision")
    mismatch=[f for f in fields if a.get(f)!=b.get(f)]
    return {"comparable_on_declared_fields":not mismatch,"mismatches":mismatch,
      "candidate_ids":[a.get("candidate_id"),b.get("candidate_id")],
      "note":"Metadata check only; engineering review must assess confounders."}
