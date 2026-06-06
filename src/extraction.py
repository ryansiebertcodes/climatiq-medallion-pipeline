import os
import time
import logging
import requests
from loading import get_connection, load_emission_factors, load_estimates

BASE_URL = "https://api.climatiq.io/data/v1"
API_KEY = os.environ["CLIMATIQ_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
DATA_VERSION = "20.20"
RECORD_CAP = 9999999

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Test data
# SECTORS = ["Energy", "Transport"]
SECTORS = [
    "Agriculture/Hunting/Forestry/Fishing",
    "Buildings and Infrastructure",
    "Consumer Goods and Services",  
    "Education",
    "Energy",
    "Equipment",
    "Health and Social Care",
    "Information and Communication",
    "Insurance and Financial Services",
    "Land Use",
    "Materials and Manufacturing",
    "Organizational Activities",
    "Refrigerants and Fugitive Gases",
    "Restaurants and Accommodation",
    "Transport",
    "Waste",
    "Water",
]


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


def fetch_all_estimates(factors: list[dict]) -> list[dict]:
    """
    Fetch estimates for all energy-unit factors in chunks of 100 (API batch limit),
    standardized to 1000 kWh per factor for cross-region comparison.
    """
    energy_factors = [f for f in factors if f.get("unit_type") == "Energy"]
    all_estimates = []
    for i in range(0, len(energy_factors), 100):
        chunk = energy_factors[i:i + 100]
        payload = [
            {
                "emission_factor": {
                    "activity_id": f["activity_id"],
                    "data_version": DATA_VERSION,
                    "region": f.get("region"),
                    "year": f.get("year"),
                },
                "parameters": {"energy": 1000, "energy_unit": "kWh"},
            }
            for f in chunk
        ]
        estimates = batch_estimate(payload)
        all_estimates.extend(estimates)
        log.info("Fetched estimates chunk %d-%d, total so far: %d", i, i + 100, len(all_estimates))
        time.sleep(0.5)
    return all_estimates


if __name__ == "__main__":
    all_factors = []
    for sector in SECTORS:
        log.info("Fetching factors for sector: %s", sector)
        factors = fetch_all_factors_for_sector(sector)
        for f in factors:
            f["_sector"] = sector
        all_factors.extend(factors)
        log.info("sector=%s total_factors=%d", sector, len(factors))

    log.info("Total factors fetched: %d", len(all_factors))

    conn = get_connection()
    load_emission_factors(conn, all_factors)

    estimates = fetch_all_estimates(all_factors)
    log.info("Total estimates fetched: %d", len(estimates))
    if estimates:
        load_estimates(conn, estimates)
