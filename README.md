# CSCA-5028-Capstone

An NHL stats dashboard built for the CSCA-5028 Capstone project. This application provides insightful analysis and visualizations of NHL player and game statistics.

Check out the hosted version of the app if you don't feel like running it in development!

[Link to the Heroku hosted address.](https://nhl-reporting-app-b1fe017be8db.herokuapp.com/)

## Features

- **Player Statistics**: View career and season metrics for NHL players.
- **Player Analyzer**: Simple analyze endpoint that calculates what current percentile the player is in based on their points. Using Heroku scheduler, I run `PYTHONPATH=. app/scripts/trigger_analyze.py` at 1am PST to have my analyzer endoint create the percentile ranked data.
- **Monitoring**: Integrated Prometheus and Grafana for real-time monitoring of app performance (see [this repo](https://github.com/RescuedBuffalo/nhl-reporting-prometheus)).
- **Event Queue**: Integrated Event Queue using pika and CloudAMQP in Heroku, there is a worker that runs on its own dyno. Using Heroku scheduler, I run `PYTONPATH=. app/scripts/trigger_produce.py` at midnight PST to have my producer endpoint add tasks to the queue to refresh data.

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
    source venv/bin/activate
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
    - Setup your app in heroku.
    - Configure git to push to heroku remote.
    - Push the app to Heroku:
      ```bash
      git push heroku main
      ```

2. **Integrate Monitoring**:
    - Prometheus and Grafana are pre-configured for production monitoring.
    - Ensure the `/metrics` endpoint is accessible.
      ```bash
      curl -X POST [url]/metrics
      ```

## Monitoring

The application integrates Prometheus and Grafana for monitoring.

- **Prometheus**:
  - Collects metrics from the `/metrics` endpoint.
  - Configuration file: `prometheus.yml`
  - Run `prometheus --config.file=prometheus.yml` from the root directory
  - Access prometheus at `http://localhost:9090/`
    - Try `database_connection_count_created`
    - Try `app_request_latency_seconds_created` as a Histogram in the Graph tab
    - Use autocomplete to find other metrics!
- I also have a hosted prometheus server (at least for now):
    - [Prometheus server](https://nhl-reporting-prometheus-e58e22902675.herokuapp.com/graph)

- **Grafana**:
  - Access dashboards for real-time insights.
  - Use Prometheus as the data source.

## Testing

1. **Run Unit Tests**:
    ```bash
    pytest tests/unit
    ```

2. **Integration Tests**:
    ```bash
    pytest tests/integration
    ```


## Continuous Deployment

- GitHub Actions is set up for CI/CD.
- Successful builds are automatically deployed to Heroku.

## TODOS:
- Add more integration tests
- ~~Finish Messaging Queue integration~~
    - ~~Fix worker errors in prod~~
    - ~~Setup endpoint that calls producers.py~~
    - ~~Setup schedule Post to the producer endpoint~~
- ~~Improve Analyzer API~~
    - ~~Add Analyzer Endpoint~~
    - ~~Do some sort of basic analysis~~
- ~~Improve UI a Little~~
    - ~~Instead of search, add table of teams~~
    - ~~Then add table of players~~
    - ~~Then player profiles~~
- Add some more error protection
- Update ReadMe and Internal Documentation More
- High Level Report
    - Whiteboard Diagram + Description
    - Justification for Design Decisions
        Ex) Why Postgres? Why Heroku?
    - System Requirements + How Testable They Were
