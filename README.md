# Hospital Patient Data Analysis System

## About the Project

The Hospital Patient Data Analysis System is a Python-based application designed to manage hospital patient information and hospital visit records. It connects to a MySQL database and uses Flask to provide a web interface for performing patient management operations and viewing hospital data analysis.

This project is being developed as a college team project.

## Features

* View all patient records
* Add new patients
* Search for patients
* Update patient information
* Delete patient records
* View hospital visit records
* View hospital statistics and analysis
* Visualize hospital data using graphs

## Technologies Used

* **Python** — application logic
* **Flask** — web application framework
* **MySQL** — database management
* **Matplotlib** — graph generation
* **HTML** — web page structure
* **Git and GitHub** — version control and collaboration

## Project Structure

```text
Hospital_Patient_data_analysis/
├── app.py
├── main.py
├── config_example.py
├── .gitignore
├── database/
├── Templates/
└── static/
    └── charts/
```

## Requirements

* Python
* MySQL Server
* PyCharm or another Python editor
* Git

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yaswanthbondigala/Hospital_Patient_data_analysis.git
```

Open the downloaded project folder in PyCharm.

### 2. Install the Required Python Packages

Open the terminal in the project folder and install the packages required by the application.

For example:

```bash
pip install flask mysql-connector-python matplotlib
```

### 3. Configure MySQL

1. Start your local MySQL Server.
2. Create the `hospital_db` database.
3. Create the tables required by the application.
4. Open `config_example.py` and use it as a reference for the database connection settings.
5. Create your own local `config.py` with your MySQL username, password, and database name.

**Important:** Do not upload your real MySQL password to GitHub.

### 4. Run the Application

Open the project in PyCharm and run:

```bash
python app.py
```

Open the local address shown in the terminal in your browser. For a typical Flask development server, this is:

```text
http://127.0.0.1:5000/
```

## Application Pages

The application includes routes for:

* `/` — Home
* `/patients` — View patients
* `/add_patient` — Add a patient
* `/search_patient` — Search for a patient
* `/update_patient` — Update a patient's age
* `/update_patient_name` — Update a patient's name
* `/delete_patient` — Delete a patient
* `/visits` — View hospital visits
* `/analysis` — View hospital statistics and graphs

## Team Collaboration

This repository is used to share the project source code among team members.

Team members should clone the repository, configure their own MySQL database connection, install the required dependencies, and run the application locally.

## Project Status

The project is under development. Features and analysis capabilities may be improved as development continues.
