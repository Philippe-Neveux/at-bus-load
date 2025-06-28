# Testing Guide for at-bus-load

This directory contains comprehensive unit tests for the at-bus-load project using pytest.

## Test Structure

```
tests/
├── __init__.py              # Makes tests a Python package
├── conftest.py              # Common fixtures and test configuration
├── test_get_at_api_data.py  # Tests for API data retrieval functions
├── test_move_gcs_data_to_bq.py  # Tests for GCS to BigQuery operations
├── test_gcp.py              # Tests for GCP connection utilities
├── run_tests.py             # Test runner script
└── README.md                # This file
```

## Running Tests

### Using Make Commands (Recommended)

```bash
# Run all tests with coverage
make test

# Run only unit tests
make test-unit

# Generate detailed coverage reports
make test-coverage

# Run tests in watch mode (re-runs on file changes)
make test-watch

# Run all quality checks (ruff, mypy, tests)
make quality
```

### Using pytest directly

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=src/at_bus_load --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_gcp.py -v

# Run specific test class
uv run pytest tests/test_gcp.py::TestConnectGCS -v

# Run specific test method
uv run pytest tests/test_gcp.py::TestConnectGCS::test_connect_gcs_with_token -v

# Run tests matching a pattern
uv run pytest tests/ -k "gcp" -v

# Run tests with markers
uv run pytest tests/ -m unit -v
```

### Using the test runner script

```bash
# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py unit
```

## Test Coverage

The tests are designed to achieve high coverage of the main functionality:

- **get_at_api_data.py**: API data retrieval, filtering, and GCS upload
- **move_gcs_data_to_bq.py**: GCS to BigQuery data movement operations
- **gcp.py**: GCP authentication and client connection utilities

### Coverage Reports

After running tests, coverage reports are generated in:
- `htmlcov/` - HTML coverage report (open `htmlcov/index.html` in browser)
- `coverage.xml` - XML coverage report for CI/CD integration

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `mock_env_vars`: Mock environment variables
- `sample_stops_data`: Sample Polars DataFrame for stops data
- `sample_trips_data`: Sample Polars DataFrame for trips data
- `mock_storage_client`: Mock Google Cloud Storage client
- `mock_bigquery_client`: Mock Google BigQuery client
- `mock_requests_response`: Mock HTTP response for API testing
- `mock_gcp_credentials`: Mock GCP credentials

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual functions and methods in isolation
- Use mocks to isolate dependencies
- Fast execution, no external dependencies

### Integration Tests (`@pytest.mark.integration`)
- Test interactions between multiple components
- May require external services (marked as slow)

### Slow Tests (`@pytest.mark.slow`)
- Tests that take longer to execute
- May involve real API calls or database operations

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<function_name>_<scenario>`

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, patch

from at_bus_load.your_module import your_function


class TestYourFunction:
    """Test cases for your_function."""
    
    def test_your_function_success(self, mock_fixture):
        """Test successful execution of your_function."""
        # Arrange
        expected_result = "expected"
        
        # Act
        result = your_function()
        
        # Assert
        assert result == expected_result
    
    def test_your_function_exception_handling(self):
        """Test exception handling in your_function."""
        with pytest.raises(ValueError, match="Expected error message"):
            your_function()
```

### Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test both success and failure scenarios**
4. **Use mocks to isolate units under test**
5. **Test edge cases and error conditions**
6. **Keep tests independent and isolated**
7. **Use fixtures for common setup**

## Mocking Guidelines

### API Calls
```python
@patch('at_bus_load.get_at_api_data.requests.get')
def test_api_call(self, mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}
    mock_get.return_value = mock_response
```

### GCP Services
```python
@patch('at_bus_load.gcp.storage.Client')
def test_gcs_connection(self, mock_storage_client):
    mock_client_instance = Mock()
    mock_storage_client.return_value = mock_client_instance
```

### Environment Variables
```python
def test_with_env_vars(self, mock_env_vars):
    # mock_env_vars fixture provides test environment variables
    pass
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run tests
  run: |
    make test
    make test-coverage
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're running tests from the project root
2. **Missing dependencies**: Run `uv sync` to install test dependencies
3. **Mock issues**: Check that mocks are applied to the correct import path

### Debug Mode

Run tests with increased verbosity for debugging:

```bash
uv run pytest tests/ -vvv -s
```

### Test Discovery

To see which tests would be discovered:

```bash
uv run pytest tests/ --collect-only
```

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Update this README if adding new test patterns or fixtures 