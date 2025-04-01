# App

This app runs a streamlit app 

# Run

## Prerequisites

*   Docker and Docker Compose must be installed on your system.

## Build and Run the App

1.  **Build the app:**

    ```
    docker-compose build
    ```

2.  **Run the app:**

    ```
    docker-compose up -d
    ```

    The `-d` flag runs the containers in detached mode (in the background).

3.  **Access the app:**

    Once the containers are up and running, the app can be accessed at [http://localhost:8501/](http://localhost:8501/) in your web browser.

## Verify the App is Running

You can verify that the app is running by checking the status of the Docker containers:

```
docker ps
```

This will display a list of running containers, including the app and the database.  You should see something similar to:

```
CONTAINER ID   IMAGE                      COMMAND                  CREATED         STATUS         PORTS                    NAMES
131e0e955de8   portfolio_builder_v2-app   "streamlit run mvp_a…"   4 minutes ago   Up 4 minutes   0.0.0.0:8501->8501/tcp   portfolio_builder_v2-app-1
a16ec1de18ac   postgres:14                "docker-entrypoint.s…"   8 minutes ago   Up 7 minutes   0.0.0.0:5432->5432/tcp   postgres_db
```

## Troubleshooting

*   **App not accessible:** If the app is not accessible at [http://localhost:8501/](http://localhost:8501/), ensure that the Docker containers are running correctly using `docker ps`.  Also, check if any other process is using port 8501 on your host machine.
*   **Build errors:** If you encounter build errors, ensure that your Dockerfile and docker-compose.yml are correctly configured.  Check for any missing dependencies or incorrect paths.
*   **Database connection errors:**  If the app fails to connect to the database, ensure that the database container is running and that the connection details in your app are correct.