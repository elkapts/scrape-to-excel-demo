"""
QA automation: automated tests for main.py
 
Run with:
    pytest -v
 
Coverage includes:
- parse_results()  - correct parsing of Adzuna JSON, including incomplete data
- export()         - CSV/XLSX export, expected columns, non-empty file
- fetch_page()      - network handling via mocks (no real API calls)
- scrape_all()      - stops on an empty page, skips a page on network error
 
No real requests are made to Adzuna - every external call is mocked, so the
tests are fast, reproducible, and don't consume the free API quota.
"""
 
import os
import sys
 
import pandas as pd
import pytest
import requests
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402

# ---------- Fixtures (reusable test data) ----------
 
@pytest.fixture
def sample_adzuna_response():
    """A valid Adzuna API response with two vacancies."""
    return {
        "results": [
            {
                "title": "Python Developer",
                "company": {"display_name": "Tech GmbH"},
                "location": {"display_name": "Berlin, Germany"},
                "category": {"label": "IT Jobs"},
                "salary_min": 55000,
                "salary_max": 70000,
                "contract_time": "full_time",
                "created": "2026-07-10T12:00:00Z",
                "redirect_url": "https://adzuna.de/jobs/land/ad/12345",
            },
            {
                "title": "Senior Backend Engineer",
                "company": {"display_name": "DataWorks"},
                "location": {"display_name": "Munich, Germany"},
                "category": {"label": "IT Jobs"},
                "salary_min": 70000,
                "salary_max": 90000,
                "contract_time": "full_time",
                "created": "2026-07-11T09:00:00Z",
                "redirect_url": "https://adzuna.de/jobs/land/ad/67890",
            },
        ]
    }
 
@pytest.fixture
def search_config():
    return {
        "country": "de",
        "what": "python developer",
        "where": "",
        "results_per_page": 50,
        "max_pages": 3,
        "sort_by": "date",
        "max_days_old": 30,
    }
 
 
 # ---------- parse_results() tests ----------
 
class TestParseResults:
 
    def test_parses_all_fields_correctly(self, sample_adzuna_response):
        items = main.parse_results(sample_adzuna_response)
        print("outputs................", items[0])
        assert len(items) == 2
        assert items[0]["Title"] == "Python Developer"
        assert items[0]["Company"] == "Tech GmbH"
        assert items[0]["Location"] == "Berlin, Germany"
        assert items[0]["Salary From"] == 55000
        assert items[0]["Link"] == "https://adzuna.de/jobs/land/ad/12345"
        
    def test_empty_results_returns_empty_list(self):
        assert main.parse_results({"results": []}) == []
    
    def test_missing_results_key_returns_empty_list(self):
        # Adzuna can occasionally return a response without "results" (format error)
        assert main.parse_results({}) == []
 
    def test_none_input_does_not_crash(self):
        # fetch_page() returns None on a network error - parse_results
        # must handle that without raising
        assert main.parse_results(None) == []
 
    def test_missing_nested_fields_do_not_crash(self):
        # a vacancy without company/location - a common real-world case
        broken = {"results": [{"title": "Mystery Job"}]}
        items = main.parse_results(broken)
        assert len(items) == 1
        assert items[0]["Title"] == "Mystery Job"
        assert items[0]["Company"] is None
        assert items[0]["Location"] is None
        
#---------- export() tests ----------
 
class TestExport:
 
    def test_creates_csv_and_xlsx(self, tmp_path, sample_adzuna_response):
        items = main.parse_results(sample_adzuna_response)
        base = str(tmp_path / "test_result")
 
        main.export(items, filename_base=base)
 
        assert os.path.exists(f"{base}.csv")
        assert os.path.exists(f"{base}.xlsx")
 
    def test_csv_contains_expected_columns(self, tmp_path, sample_adzuna_response):
        items = main.parse_results(sample_adzuna_response)
        base = str(tmp_path / "test_result")
        main.export(items, filename_base=base)
 
        df = pd.read_csv(f"{base}.csv")
        expected_columns = {
            "Title", "Company", "Location", "Category",
            "Salary From", "Salary Up", "Employment Type",
            "Publish Date", "Link", "Collection date",
        }
        assert expected_columns.issubset(set(df.columns))
        assert len(df) == 2
 
    def test_export_with_empty_items_does_not_crash(self, tmp_path, capsys):
        base = str(tmp_path / "empty_result")
        main.export([], filename_base=base)
 
        # nothing should be created for an empty list, but the script must not crash
        assert not os.path.exists(f"{base}.csv")
        captured = capsys.readouterr()
        assert "no data" in captured.out
 
 
# ---------- fetch_page() tests with mocked network (no real internet calls) ----------
 
class TestFetchPage:
 
    def test_successful_response_returns_json(self, monkeypatch, search_config,
                                                sample_adzuna_response):
        class FakeResponse:
            def raise_for_status(self):
                pass
 
            def json(self):
                return sample_adzuna_response
 
        def fake_get(url, params=None, timeout=None):
            assert "api.adzuna.com" in url
            assert params["app_id"] == "fake_id"
            return FakeResponse()
 
            monkeypatch.setattr(requests, "get", fake_get)
 
            result = main.fetch_page("fake_id", "fake_key", search_config, page_number=1)
            assert result == sample_adzuna_response
 
        def test_network_error_returns_none(self, monkeypatch, search_config):
            def fake_get(url, params=None, timeout=None):
                raise requests.exceptions.Timeout("simulated timeout")
    
            monkeypatch.setattr(requests, "get", fake_get)
    
            result = main.fetch_page("fake_id", "fake_key", search_config, page_number=1)
            assert result is None
 
        def test_http_error_returns_none(self, monkeypatch, search_config):
            class FakeResponse:
                def raise_for_status(self):
                    raise requests.exceptions.HTTPError("403 Forbidden")
    
            def fake_get(url, params=None, timeout=None):
                return FakeResponse()
    
            monkeypatch.setattr(requests, "get", fake_get)
    
            result = main.fetch_page("bad_id", "bad_key", search_config, page_number=1)
            assert result is None
    
 
# ---------- scrape_all() tests - pagination behavior ----------
 
class TestScrapeAll:
 
    def test_stops_when_page_is_empty(self, monkeypatch, search_config,
                                       sample_adzuna_response):
        # Page 1 has data, page 2 is empty (end of listing)
        call_count = {"n": 0}
 
        def fake_fetch(app_id, app_key, cfg, page_number):
            call_count["n"] += 1
            if page_number == 1:
                return sample_adzuna_response
            return {"results": []}
 
        monkeypatch.setattr(main, "fetch_page", fake_fetch)
        monkeypatch.setattr(main.time, "sleep", lambda x: None)  # don't wait in tests

        full_config = {"search": search_config} 
        items = main.scrape_all(full_config, "id", "key")
 
        assert len(items) == 2  # only from page 1
        assert call_count["n"] == 2  # reached page 2, stopped there
 
    def test_skips_failed_page_and_continues(self, monkeypatch, search_config,
                                              sample_adzuna_response):
        def fake_fetch(app_id, app_key, cfg, page_number):
            if page_number == 1:
                return None  # page 1 failed to load
            if page_number == 2:
                return sample_adzuna_response
            return {"results": []}
 
        monkeypatch.setattr(main, "fetch_page", fake_fetch)
        monkeypatch.setattr(main.time, "sleep", lambda x: None)
        print(search_config, "...........")
        full_config = {"search": search_config} 
        items = main.scrape_all(full_config, "id", "key")
 
        # page 1 was skipped, but collection continued and picked up page 2's data
        assert len(items) == 2
 
 
if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))