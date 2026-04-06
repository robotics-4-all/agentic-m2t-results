FROM python:3.11-slim

WORKDIR /app

# Create results output directory with correct permissions
RUN mkdir -p /results

# Install dependencies — copy requirements first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir textx pytest pytest-json-report \
    && if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy generated code and test file
COPY output.py test_model_7_complex_conditions.py ./

# Run as non-root for security
RUN useradd --create-home --shell /bin/bash testrunner \
    && chown -R testrunner:testrunner /app /results
USER testrunner

# Run tests and write results to mounted volume
CMD ["pytest", "test_model_7_complex_conditions.py", "-v", \
     "--json-report", "--json-report-file=/results/report.json", \
     "--tb=short"]