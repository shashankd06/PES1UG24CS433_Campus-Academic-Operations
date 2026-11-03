import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


# --- process_commute_manifest Tests ---

def test_manifest_invalid_manifest_type():
    # Branch: not isinstance(manifests, list) -> True
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest("not-a-list", 10.0)


def test_manifest_negative_booking_fee():
    # Branch: isinstance(manifests, list) -> True, booking_fee < 0 -> True
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest([], -1.0)


def test_manifest_empty_manifests():
    # Branch: empty manifests loop -> loop does not execute
    result = process_commute_manifest([], 5.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_manifest_inactive_route():
    # Branch: not manifest.get("route_active", False) -> True
    manifests = [
        {"route_active": False, "route_type": "express", "commuters": [{"zones": 2}]}
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_manifest_express_route_student():
    # Branch: route_type == 'express', passenger_type == 'student', priority_boarding == False
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "priority_boarding": False,
            "commuters": [{"zones": 2, "type": "student", "blacklisted": False}]
        }
    ]
    # base_seat = 6.0, (6.0 + 2 * 0.5) * 0.50 = 3.50
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_manifest_shuttle_route_senior_with_priority():
    # Branch: route_type == 'shuttle', passenger_type == 'senior', priority_boarding == True
    manifests = [
        {
            "route_active": True,
            "route_type": "shuttle",
            "priority_boarding": True,
            "commuters": [{"zones": 2, "type": "senior", "blacklisted": False}]
        }
    ]
    # base_seat = 4.0, (4.0 + 2 * 0.5) * 0.70 = 3.50, + booking_fee 2.50 = 6.0
    result = process_commute_manifest(manifests, 2.5)
    assert result == {"total_fare": 6.0, "status": "COMPLETED"}


def test_manifest_local_route_regular():
    # Branch: route_type == 'local', passenger_type == 'regular' (else branch)
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": False,
            "commuters": [{"zones": 3, "type": "regular", "blacklisted": False}]
        }
    ]
    # base_seat = 2.5, 2.5 + 3 * 1.0 = 5.5
    result = process_commute_manifest(manifests, 1.0)
    assert result == {"total_fare": 5.5, "status": "COMPLETED"}


def test_manifest_invalid_route_type():
    # Branch: invalid route_type -> else branch (rejected_rides += 1, continue)
    manifests = [
        {"route_active": True, "route_type": "monorail", "commuters": [{"zones": 1}]}
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_manifest_invalid_zones_zero_and_negative():
    # Branch: zones <= 0 -> True (rejected_rides += 1, continue)
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 0}, {"zones": -2}]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_manifest_blacklisted_on_express_breaks():
    # Branch: has_blacklisted_card -> True, route_type == 'express' -> True (breaks commuter loop)
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular", "blacklisted": True},
                {"zones": 2, "type": "regular", "blacklisted": False}  # unreachable due to break
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_manifest_blacklisted_on_local_continues():
    # Branch: has_blacklisted_card -> True, route_type != 'express' -> True
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 1, "type": "regular", "blacklisted": True},
                {"zones": 1, "type": "regular", "blacklisted": False}
            ]
        }
    ]
    # 0.0 + (2.5 + 1.0) = 3.5
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_manifest_audit_rejected_more_than_four_rejections():
    # Branch: rejected_rides > 4 -> True
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": -1},
                {"zones": -2},
                {"zones": -3},
                {"zones": -4},
                {"zones": -5}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "AUDIT_REJECTED"}


# --- inspect_smartcard_turnstiles Tests ---

def test_turnstiles_no_data_empty_or_none():
    # Branch: not turnstile_matrix -> True
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles(None) == "NO_DATA"


def test_turnstiles_operational():
    # Branch: all readings <= 3 -> always else branch (tap_failure_streak = 0)
    matrix = [
        [0, 1, 2, 3],
        [1, 2]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "OPERATIONAL"


def test_turnstiles_single_failure_does_not_jam():
    # Branch: failures > 3 -> True, tap_failure_streak >= 2 -> False
    # Followed by failures <= 3 -> streak reset to 0
    matrix = [
        [4, 1, 2],
        [5]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "OPERATIONAL"


def test_turnstiles_consecutive_failures_jam():
    # Branch: failures > 3 -> True, tap_failure_streak >= 2 -> True
    matrix = [
        [1, 4, 5, 2]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "TURNSTILE_JAM"
