import os
import time
import logging
import requests
from loading import get_connection, load_emission_factors, load_estimates

BASE_URL = "https://api.climatiq.io/data/v1"
API_KEY = os.environ["CLIMATIQ_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
DATA_VERSION = "20.20"
RECORD_CAP = 500

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SECTORS = ["Energy", "Transport", "Agriculture", "Manufacturing"]


def search_emission_factors(
    sector: str, page: int = 1, results_per_page: int = 50
) -> dict:
    params = {
        "sector": sector,
        "data_version": DATA_VERSION,
        "access_type": "public",
        "page": page,
        "results_per_page": results_per_page,
    }
    resp = requests.get(
        f"{BASE_URL}/search", headers=HEADERS, params=params, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def fetch_all_factors_for_sector(sector: str) -> list[dict]:
    """Pages through search results and returns all factors for a sector."""
    factors, page = [], 1
    while True:
        data = search_emission_factors(sector, page=page)
        results = data.get("results", [])
        factors.extend(results)
        log.info(
            "sector=%s page=%d fetched=%d total_so_far=%d",
            sector,
            page,
            len(results),
            len(factors),
        )
        if (
            len(factors) >= RECORD_CAP
            or len(factors) >= data.get("total_results", 0)
            or not results
        ):
            break
        page += 1
        time.sleep(0.2)  # stay within rate limits
    return factors


def batch_estimate(requests_payload: list[dict]) -> list[dict]:
    """Send up to 100 estimation requests in one call."""
    resp = requests.post(
        f"{BASE_URL}/estimate/batch",
        headers=HEADERS,
        json=requests_payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def build_sample_estimates(factors: list[dict]) -> list[dict]:
    """
    Build a batch payload from factors that use kWh (Energy unit type),
    standardized to 1000 kWh per factor for cross-region comparison.
    """
    payload = []
    for f in factors:
        if f.get("unit_type") != "Energy":
            continue
        payload.append(
            {
                "emission_factor": {
                    "activity_id": f["activity_id"],
                    "data_version": DATA_VERSION,
                    "region": f.get("region"),
                    "year": f.get("year"),
                },
                "parameters": {"energy": 1000, "energy_unit": "kWh"},
            }
        )
        if len(payload) == 100:  # API batch limit
            break
    return payload


if __name__ == "__main__":
    all_factors = []
    for sector in SECTORS:
        log.info("Fetching factors for sector: %s", sector)
        factors = fetch_all_factors_for_sector(sector)
        for f in factors:
            f["_sector"] = sector  # tag source sector before storing
        all_factors.extend(factors)
        log.info("sector=%s total_factors=%d", sector, len(factors))

    log.info("Total factors fetched: %d", len(all_factors))

    conn = get_connection()
    load_emission_factors(conn, all_factors)

    # Sample batch estimate for energy-unit factors
    sample_payload = build_sample_estimates(all_factors)
    print(f"sample_payload length: {len(sample_payload)}")
    if sample_payload:
        log.info("Running batch estimate on %d energy factors", len(sample_payload))
        estimates = batch_estimate(sample_payload)
        log.info("Received %d estimate results", len(estimates))
        for est in estimates[:3]:
            log.info(
                "  activity=%s co2e=%.4f %s",
                est.get("activity_id"),
                est.get("co2e"),
                est.get("co2e_unit"),
            )
        load_estimates(conn, estimates)

    # print(conn)

    # for f in all_factors:
    #     print(f)
