# CSCA-5028-Capstone

An NHL stats dashboard built for the CSCA-5028 Capstone project. This application provides insightful analysis and visualizations of NHL player and game statistics.

## Features

- **Player Statistics**: View detailed player performance metrics.
- **Game Data**: Analyze recent and historical game stats.
- **Standings**: Track team performance throughout the season.
- **Monitoring**: Integrated Prometheus and Grafana for real-time monitoring of app performance (see [this repo](https://github.com/RescuedBuffalo/nhl-reporting-prometheus)).
- **Event-driven Forecasting**: A planned feature to predict player performance using advanced machine learning models.

## Setup Instructions

### Development Setup

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd CSCA-5028-Capstone
    ```

2. **Set Up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\\Scripts\\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**:
    Create a `.env` file based on the `.env.example` template, and configure the necessary variables.

5. **Run the Application**:
    ```bash
    flask run
    ```

### Production Setup

1. **Deploy to Heroku**:
    - Ensure the `Procfile` is configured correctly for the app.
    - Push the app to Heroku:
      ```bash
      git push heroku main
      ```

2. **Integrate Monitoring**:
    - Prometheus and Grafana are pre-configured for production monitoring.
    - Ensure the `/metrics` endpoint is accessible.

## Monitoring

The application integrates Prometheus and Grafana for monitoring.

- **Prometheus**:
  - Collects metrics from the `/metrics` endpoint.
  - Configuration file: `prometheus.yml`.

- **Grafana**:
  - Access dashboards for real-time insights.
  - Use Prometheus as the data source.

## Testing

1. **Run Tests**:
    ```bash
    pytest tests/
    ```

2. **Integration Tests**:
    - Mock external dependencies using `pytest-mock` or `unittest.mock`.

## Continuous Deployment

- GitHub Actions is set up for CI/CD.
- Successful builds are automatically deployed to Heroku.

