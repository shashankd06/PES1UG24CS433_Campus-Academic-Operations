"""Manage campus parking permits and persist validated records as JSON."""

import json
import secrets
from datetime import date, timedelta

PERMITS = {}
ZONES = ("A", "B", "C")


def validate_plate(vehicle_plate):
    """Reject missing or blank vehicle identifiers."""
    if not isinstance(vehicle_plate, str) or not vehicle_plate.strip():
        raise ValueError("Vehicle plate must be a non-empty string.")


def validate_zone(zone_id):
    """Require a supported campus parking zone."""
    if zone_id not in ZONES:
        raise ValueError("Zone must be A, B, or C.")


def parse_expiry(date_text):
    """Parse a canonical ISO calendar date or raise ValueError."""
    if not isinstance(date_text, str):
        raise ValueError("Expiry must be an ISO date string.")
    expiry = date.fromisoformat(date_text)
    if expiry.isoformat() != date_text:
        raise ValueError("Expiry must use YYYY-MM-DD.")
    return expiry


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Issue a random permit, optionally recording the registration."""
    validate_plate(vehicle_plate)
    validate_zone(zone_id)
    if zone_records is None:
        zone_records = []
    permit_no = "P" + secrets.token_hex(16)
    while any(record["permit"] == permit_no for record in PERMITS.values()):
        permit_no = "P" + secrets.token_hex(16)
    expiry = date.today() + timedelta(days=180)
    PERMITS[vehicle_plate] = {
        "zone": zone_id,
        "permit": permit_no,
        "expiry": expiry.isoformat(),
    }
    zone_records.append((vehicle_plate, zone_id))
    return permit_no


def revoke_permit(vehicle_plate):
    """Remove a permit; revoking an unknown plate is harmless."""
    PERMITS.pop(vehicle_plate, None)


def is_expired(vehicle_plate):
    """Treat missing or malformed expiry records as expired."""
    try:
        return parse_expiry(PERMITS[vehicle_plate]["expiry"]) < date.today()
    except (KeyError, TypeError, ValueError):
        return True


def scan_zone(zone_id, plates_seen):
    """Return plates without a valid permit for the requested zone."""
    validate_zone(zone_id)
    return [
        plate for plate in plates_seen
        if plate not in PERMITS
        or PERMITS[plate]["zone"] != zone_id
        or is_expired(plate)
    ]


def validate_database(database):
    """Validate all loaded records before replacing in-memory state."""
    if not isinstance(database, dict):
        raise ValueError("Permit database must be a JSON object.")
    for plate, record in database.items():
        validate_plate(plate)
        if not isinstance(record, dict):
            raise ValueError("Each permit record must be an object.")
        if not {"zone", "permit", "expiry"}.issubset(record):
            raise ValueError("Permit record is missing required fields.")
        validate_zone(record["zone"])
        if not isinstance(record["permit"], str) or not record["permit"]:
            raise ValueError("Permit identifier must be a non-empty string.")
        parse_expiry(record["expiry"])


def load_permit_database(file="permits.json"):
    """Load valid records; only a missing file starts an empty database."""
    try:
        with open(file, encoding="utf-8") as database_file:
            database = json.load(database_file)
    except FileNotFoundError:
        database = {}
    validate_database(database)
    PERMITS.clear()
    PERMITS.update(database)


def save_permit_database(file="permits.json"):
    """Save the permit database with guaranteed file closure."""
    validate_database(PERMITS)
    with open(file, "w", encoding="utf-8") as database_file:
        json.dump(PERMITS, database_file, indent=2)


def set_expiry(vehicle_plate, date_text):
    """Update an existing permit only after validating its expiry."""
    expiry = parse_expiry(date_text)
    PERMITS[vehicle_plate]["expiry"] = expiry.isoformat()


def main():
    """Demonstrate registration, expiry, scanning and revocation."""
    try:
        load_permit_database()
        register_permit("KA01AB1234", "A")
        register_permit("KA05XY9999", "B")
        set_expiry("KA01AB1234", "2020-01-01")
        revoke_permit("MH12ZZ0000")
        observed = ["KA01AB1234", "KA05XY9999", "TN09QQ1111"]
        print("Flagged in zone A:", scan_zone("A", observed))
        plate = input("Plate to revoke (Enter to skip): ").strip()
        if plate:
            revoke_permit(plate)
        save_permit_database()
        print("Permits on file:", len(PERMITS))
    except (OSError, ValueError) as error:
        print(f"Unable to process permit database: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
