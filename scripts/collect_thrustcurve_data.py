"""Collects motor data from the ThrustCurve.org API and derives hardware weights.

Queries all AeroTech motors (reloads and single-use) across standard diameters,
calculates hardware weight as totalWeight - propWeight, and groups reload motors
by caseInfo to build a hardware catalog.

Output:
  data/thrustcurve_motors.json    — raw motor data from ThrustCurve
  data/hardware_weights.json      — derived hardware weights grouped by case
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict
from statistics import mean, stdev

API_BASE = "https://www.thrustcurve.org/api/v1"
SEARCH_URL = f"{API_BASE}/search.json"

# Standard AeroTech motor diameters
DIAMETERS = [18, 24, 29, 38, 54, 75, 98]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def search_motors(manufacturer="AeroTech", diameter=None, motor_type=None, max_results=500):
    """Query ThrustCurve search API for motors matching criteria."""
    params = {"manufacturer": manufacturer, "maxResults": max_results}
    if diameter is not None:
        params["diameter"] = diameter
    if motor_type is not None:
        params["type"] = motor_type

    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(SEARCH_URL, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("results", [])
    except urllib.error.URLError as e:
        print(f"  Error querying diameter={diameter}, type={motor_type}: {e}")
        return []


def collect_all_motors():
    """Collect all AeroTech motors across all diameters."""
    all_motors = []
    seen_ids = set()

    for diameter in DIAMETERS:
        for motor_type in ["reload", "SU"]:
            print(f"Querying diameter={diameter}mm, type={motor_type}...")
            motors = search_motors(diameter=diameter, motor_type=motor_type)
            for m in motors:
                mid = m.get("motorId", "")
                if mid not in seen_ids:
                    seen_ids.add(mid)
                    all_motors.append({
                        "motorId": mid,
                        "manufacturer": m.get("manufacturer", ""),
                        "manufacturerAbbrev": m.get("manufacturerAbbrev", ""),
                        "designation": m.get("designation", ""),
                        "commonName": m.get("commonName", ""),
                        "impulseClass": m.get("impulseClass", ""),
                        "diameter": m.get("diameter", 0),
                        "length": m.get("length", 0),
                        "totalWeightG": m.get("totalWeightG", 0),
                        "propWeightG": m.get("propWeightG", 0),
                        "type": m.get("type", ""),
                        "caseInfo": m.get("caseInfo", ""),
                        "propInfo": m.get("propInfo", ""),
                        "avgThrustN": m.get("avgThrustN", 0),
                        "maxThrustN": m.get("maxThrustN", 0),
                        "totImpulseNs": m.get("totImpulseNs", 0),
                        "burnTimeS": m.get("burnTimeS", 0),
                        "availability": m.get("availability", ""),
                    })
            print(f"  Found {len(motors)} motors")
            time.sleep(0.5)  # Be polite to the API

    print(f"\nTotal unique motors collected: {len(all_motors)}")
    return all_motors


def derive_hardware_weights(motors):
    """Group motors by caseInfo and calculate average hardware weights."""
    case_groups = defaultdict(list)

    for m in motors:
        total = m.get("totalWeightG", 0)
        prop = m.get("propWeightG", 0)
        case_info = m.get("caseInfo", "")

        if total and prop and total > prop:
            hw_weight = total - prop
            entry = {
                "designation": m["designation"],
                "commonName": m["commonName"],
                "totalWeightG": total,
                "propWeightG": prop,
                "hardwareWeightG": round(hw_weight, 2),
                "diameter": m["diameter"],
                "length": m["length"],
                "type": m["type"],
                "propInfo": m.get("propInfo", ""),
            }

            if case_info and m["type"] == "reload":
                case_groups[case_info].append(entry)
            elif m["type"] == "SU":
                # Single-use motors get their own entry keyed by designation
                case_groups[f"SU-{m['designation']}"].append(entry)

    # Build summary per case
    hardware_catalog = {}
    for case_key, entries in case_groups.items():
        weights = [e["hardwareWeightG"] for e in entries]
        diameters = [e["diameter"] for e in entries]
        lengths = [e["length"] for e in entries]

        avg_weight = round(mean(weights), 1)
        weight_std = round(stdev(weights), 1) if len(weights) > 1 else 0.0
        max_length = max(lengths) if lengths else 0

        # Parse max impulse from case designation if possible (e.g., "RMS-54/1706" -> 1706)
        max_impulse = 0
        if "/" in case_key:
            try:
                max_impulse = int(case_key.split("/")[-1])
            except ValueError:
                pass

        hardware_catalog[case_key] = {
            "designation": case_key,
            "type": "SU" if case_key.startswith("SU-") else "RMS",
            "diameter": diameters[0] if diameters else 0,
            "maxLength": max_length,
            "maxTotalImpulse": max_impulse,
            "avgHardwareWeightG": avg_weight,
            "hardwareWeightStdG": weight_std,
            "sampleCount": len(entries),
            "motors": [e["designation"] for e in entries],
            "entries": entries,
        }

    return hardware_catalog


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("ThrustCurve.org Data Collection for openMotor")
    print("=" * 60)

    # Collect motor data
    motors = collect_all_motors()

    # Save raw motor data
    motors_path = os.path.join(OUTPUT_DIR, "thrustcurve_motors.json")
    with open(motors_path, "w") as f:
        json.dump(motors, f, indent=2)
    print(f"\nSaved {len(motors)} motors to {motors_path}")

    # Derive hardware weights
    hardware = derive_hardware_weights(motors)

    # Save hardware catalog
    hardware_path = os.path.join(OUTPUT_DIR, "hardware_weights.json")
    with open(hardware_path, "w") as f:
        json.dump(hardware, f, indent=2)
    print(f"Saved {len(hardware)} hardware entries to {hardware_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Hardware Weight Summary (Reloadable Cases)")
    print("=" * 60)
    rms_cases = {k: v for k, v in hardware.items() if not k.startswith("SU-")}
    for case_key in sorted(rms_cases.keys()):
        info = rms_cases[case_key]
        print(f"  {case_key:20s}  {info['avgHardwareWeightG']:7.1f}g "
              f"(±{info['hardwareWeightStdG']:5.1f}g, n={info['sampleCount']})")


if __name__ == "__main__":
    main()
