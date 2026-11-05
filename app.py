from flask import Flask, render_template, request, redirect, url_for
from config import get_db_connection

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os

app = Flask(__name__)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# View All Patients
@app.route("/patients")
def patients():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM patients ORDER BY patient_id ASC")
    patients = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("patients.html", patients=patients)


# Add Patient and Create Hospital Visit
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        city = request.form["city"]

        disease = request.form["disease"]
        admission_date = request.form["admission_date"]
        discharge_date = request.form["discharge_date"]

        # Validate dates
        if discharge_date and discharge_date < admission_date:
            return "Error: Discharge date cannot be earlier than admission date!"

        treatment_cost = request.form["treatment_cost"]

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insert patient details
            patient_query = """
                INSERT INTO patients (name, age, gender, city)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                patient_query,
                (name, age, gender, city)
            )

            patient_id = cursor.lastrowid

            # Insert hospital visit
            visit_query = """
                INSERT INTO visits
                (patient_id, disease, admission_date,
                 discharge_date, treatment_cost)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                visit_query,
                (
                    patient_id,
                    disease,
                    admission_date,
                    discharge_date,
                    treatment_cost
                )
            )

            connection.commit()

        except Exception as e:
            connection.rollback()
            return f"Error adding patient and visit: {e}", 500

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("patients"))

    return render_template("add_patient.html")


# Search Patient
@app.route("/search_patient", methods=["GET", "POST"])
def search_patient():

    patient = None
    message = ""

    if request.method == "POST":

        patient_id = request.form["patient_id"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM patients WHERE patient_id = %s",
            (patient_id,)
        )

        patient = cursor.fetchone()

        cursor.close()
        connection.close()

        if patient is None:
            message = "Patient not found."

    return render_template(
        "search_patient.html",
        patient=patient,
        message=message
    )


# Update Patient Age
@app.route("/update_patient", methods=["GET", "POST"])
def update_patient():

    message = ""

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        age = request.form["age"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE patients SET age = %s WHERE patient_id = %s",
            (age, patient_id)
        )

        connection.commit()

        if cursor.rowcount > 0:
            message = "Patient age updated successfully."
        else:
            message = "Patient not found or age unchanged."

        cursor.close()
        connection.close()

    return render_template(
        "update_patient.html",
        message=message
    )


# Update Patient Name
@app.route("/update_patient_name", methods=["GET", "POST"])
def update_patient_name():

    connection = get_db_connection()
    cursor = connection.cursor()

    message = ""

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        new_name = request.form["new_name"].strip()

        if not new_name:
            message = "Patient name cannot be empty."

        else:
            cursor.execute(
                "UPDATE patients SET name = %s WHERE patient_id = %s",
                (new_name, patient_id)
            )

            connection.commit()

            if cursor.rowcount > 0:
                message = "Patient name updated successfully!"
            else:
                message = "Patient ID not found, or the name is unchanged."

    cursor.close()
    connection.close()

    return render_template(
        "update_patient_name.html",
        message=message
    )
# Update Patient Disease
@app.route("/update_patient_disease", methods=["GET", "POST"])
def update_patient_disease():

    message = ""

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        new_disease = request.form["new_disease"].strip()

        if not new_disease:
            message = "Disease cannot be empty."

        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE visits
                    SET disease = %s
                    WHERE patient_id = %s
                    """,
                    (new_disease, patient_id)
                )

                connection.commit()

                if cursor.rowcount > 0:
                    message = "Patient disease updated successfully!"
                else:
                    message = "No visit found for this Patient ID."

            except Exception as e:
                connection.rollback()
                message = f"Error updating disease: {e}"

            finally:
                cursor.close()
                connection.close()

    return render_template(
        "update_patient_disease.html",
        message=message
    )

# Delete Patient
@app.route("/delete_patient", methods=["GET", "POST"])
def delete_patient():
    if request.method == "POST":

        patient_id = request.form["patient_id"]

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Delete linked visits first
            cursor.execute(
                "DELETE FROM visits WHERE patient_id = %s",
                (patient_id,)
            )

            # Delete patient
            cursor.execute(
                "DELETE FROM patients WHERE patient_id = %s",
                (patient_id,)
            )

            connection.commit()

        except Exception as e:
            connection.rollback()
            return f"Error deleting patient: {e}", 500

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("patients"))

    return render_template("delete_patient.html")


# View Hospital Visits
@app.route("/visits")
def visits():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            visits.visit_id,
            patients.name,
            visits.disease,
            visits.admission_date,
            visits.discharge_date,
            visits.treatment_cost
        FROM visits
        JOIN patients
        ON visits.patient_id = patients.patient_id
    """

    cursor.execute(query)
    visit_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "visits.html",
        visits=visit_data
    )


# Generate Graphs
def generate_charts(disease_data, date_wise_visits, city_data):

    chart_folder = os.path.join(
        app.root_path,
        "static",
        "charts"
    )

    os.makedirs(chart_folder, exist_ok=True)

    # 1. Disease-wise Visits Bar Chart
    diseases = [
        item["disease"] or "Not Specified"
        for item in disease_data
    ]

    disease_counts = [
        item["total"]
        for item in disease_data
    ]

    plt.figure(figsize=(12, 6))

    plt.bar(diseases, disease_counts)

    plt.title("Disease-wise Hospital Visits")
    plt.xlabel("Disease")
    plt.ylabel("Number of Visits")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(
        os.path.join(chart_folder, "disease_chart.png")
    )

    plt.close()

    # 2. Date-wise Visits Line Chart
    ordered_visits = list(reversed(date_wise_visits))

    dates = [
        item["admission_date"].strftime("%Y-%m-%d")
        for item in ordered_visits
    ]

    visit_counts = [
        item["total_visits"]
        for item in ordered_visits
    ]

    plt.figure(figsize=(14, 6))

    plt.plot(
        dates,
        visit_counts,
        marker="o"
    )

    plt.title("Date-wise Hospital Visits")
    plt.xlabel("Admission Date")
    plt.ylabel("Number of Visits")

    plt.xticks(rotation=90)
    plt.tight_layout()

    plt.savefig(
        os.path.join(chart_folder, "date_chart.png")
    )

    plt.close()

    # 3. Patients by City Bar Chart
    cities = [
        item["city"] or "Not Specified"
        for item in city_data
    ]

    city_counts = [
        item["total"]
        for item in city_data
    ]

    plt.figure(figsize=(10, 6))

    plt.bar(cities, city_counts)

    plt.title("Patients by City")
    plt.xlabel("City")
    plt.ylabel("Number of Patients")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(
        os.path.join(chart_folder, "city_chart.png")
    )

    plt.close()


# Hospital Data Analysis
@app.route("/analysis")
def analysis():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 1. Total Patients
    cursor.execute(
        "SELECT COUNT(*) AS total_patients FROM patients"
    )

    total_patients = cursor.fetchone()["total_patients"]

    # 2. Total Hospital Visits
    cursor.execute(
        "SELECT COUNT(*) AS total_visits FROM visits"
    )

    total_visits = cursor.fetchone()["total_visits"]

    # 3. Total Treatment Cost
    cursor.execute("""
        SELECT COALESCE(SUM(treatment_cost), 0) AS total_cost
        FROM visits
    """)

    total_cost = cursor.fetchone()["total_cost"]

    # 4. Disease-wise Visit Analysis
    cursor.execute("""
        SELECT disease, COUNT(*) AS total
        FROM visits
        GROUP BY disease
        ORDER BY total DESC
    """)

    disease_data = cursor.fetchall()

    # 5. Today's Hospital Visits
    cursor.execute("""
        SELECT COUNT(*) AS total_visits_today
        FROM visits
        WHERE admission_date = CURDATE()
    """)

    total_visits_today = cursor.fetchone()["total_visits_today"]

    # 6. Date-wise Hospital Visits
    cursor.execute("""
        SELECT admission_date, COUNT(*) AS total_visits
        FROM visits
        GROUP BY admission_date
        ORDER BY admission_date DESC
    """)

    date_wise_visits = cursor.fetchall()

    # 7. Patients by City
    cursor.execute("""
        SELECT city, COUNT(*) AS total
        FROM patients
        GROUP BY city
        ORDER BY total DESC
    """)

    city_data = cursor.fetchall()

    # Generate all three graphs
    generate_charts(
        disease_data,
        date_wise_visits,
        city_data
    )

    # Close database connection
    cursor.close()
    connection.close()

    # Display analysis results
    return render_template(
        "analysis.html",
        total_patients=total_patients,
        total_visits=total_visits,
        total_cost=total_cost,
        disease_data=disease_data,
        total_visits_today=total_visits_today,
        date_wise_visits=date_wise_visits,
        city_data=city_data
    )

if __name__ == "__main__":
    app.run(debug=True)