import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles

# Starter test case
def test_single_regular_local_ride():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": False,
            "commuters": [{"zones": 2, "type": "regular", "blacklisted": False}]
        }
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result["total_fare"] == 4.5
    assert result["status"] == "COMPLETED"

# Test for invalid input manifests or booking fee
def test_invalid_manifest_input():
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest("invalid_list", 2.0)

# Test inactive routes
def test_inactive_route():
    manifests = [
        {
            "route_active": False,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["status"] == "ZERO_RIDERSHIP"
    assert result["total_fare"] == 0.0

# Test route types and passenger discount concessions
def test_express_student_and_priority_boarding():
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "priority_boarding": True,
            "commuters": [
                {"zones": 2, "type": "student", "blacklisted": False}
            ]
        }
    ]
    # base_seat = 6.0, zones = 2 -> (6.0 + 1.0) * 0.50 = 3.50 + priority fee 1.50 = 5.0
    result = process_commute_manifest(manifests, 1.5)
    assert result["total_fare"] == 5.0
    assert result["status"] == "COMPLETED"

def test_shuttle_senior():
    manifests = [
        {
            "route_active": True,
            "route_type": "shuttle",
            "priority_boarding": False,
            "commuters": [
                {"zones": 2, "type": "senior", "blacklisted": False}
            ]
        }
    ]
    # base_seat = 4.0, zones = 2 -> (4.0 + 1.0) * 0.70 = 3.50
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 3.5
    assert result["status"] == "COMPLETED"

# Test invalid route type
def test_unknown_route_type():
    manifests = [
        {
            "route_active": True,
            "route_type": "hyperloop",
            "commuters": [{"zones": 1}]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"

# Test invalid commuter zones (<= 0)
def test_invalid_zones():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 0, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["status"] == "ZERO_RIDERSHIP"

# Test blacklisted passenger on express route (zeros manifest fare and breaks)
def test_blacklisted_card_express():
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular", "blacklisted": True},
                {"zones": 2, "type": "regular", "blacklisted": False}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"

# Test blacklisted passenger on non-express route
def test_blacklisted_card_shuttle():
    manifests = [
        {
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [
                {"zones": 1, "type": "regular", "blacklisted": True},
                {"zones": 1, "type": "regular", "blacklisted": False}
            ]
        }
    ]
    # 0.0 + (4.0 + 1.0) = 5.0
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 5.0
    assert result["status"] == "COMPLETED"

# Test audit rejected status when rejected_rides > 4
def test_audit_rejected():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": -1},
                {"zones": 0},
                {"zones": -2},
                {"zones": -3},
                {"zones": -4}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["status"] == "AUDIT_REJECTED"

# Tests for inspect_smartcard_turnstiles
def test_turnstiles_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"

def test_turnstiles_jam():
    # Streak reaches >= 2 consecutive failures > 3
    matrix = [
        [1, 4, 5, 2]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "TURNSTILE_JAM"

def test_turnstiles_operational_with_streak_reset():
    # Failure > 3 followed by <= 3, resetting streak
    matrix = [
        [4, 2, 4]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "OPERATIONAL"
