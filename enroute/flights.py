from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
import os
import requests

from dotenv import load_dotenv

from .auth import login_required
from .db import get_db

bp = Blueprint("flights", __name__)

load_dotenv()


@bp.route("/")
@login_required
def index():
    db = get_db()
    flights = db.execute(
        "SELECT * FROM flight WHERE user_id = ?", (g.user["id"],)
    ).fetchall()
    return render_template("flights/index.html", flights=flights)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_flight():
    print("adding flight")
    if request.method == "POST":
        print("Post method")
        flight_number = request.form["flight_number"]
        print("Flight number", flight_number)

        aviationstack_api_key = os.getenv("AVIATIONSTACK_API_KEY")
        url = f"http://api.aviationstack.com/v1/flights?access_key={aviationstack_api_key}&flight_iata={flight_number}"
        response = requests.get(url)
        print("response", response.json())

        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                # TODO: Add more fields
                flight_info = data["data"][0]
                airline = flight_info["airline"]["name"]
            else:
                flash("No flight data found.", "error")
                return render_template("flights/add.html")
        else:
            flash("Error retrieving flight data from AviationStack.", "error")
            return render_template("flights/add.html")

        db = get_db()
        print(f"Adding flight {flight_number} to db")
        db.execute(
            "INSERT INTO flight (user_id, airline, flight_number) VALUES (?, ?, ?)",
            (g.user["id"], airline, flight_number),
        )
        db.commit()
        return redirect(url_for("flights.index"))

    return render_template("flights/add.html")


@bp.route("/<int:id>")  # view one flight
def view_flight(id):
    pass


@bp.route("/<int:id>/delete", methods=["POST"])  # delete a flight
def delete_flight(id):
    pass


@bp.route("/<int:id>/edit", methods=["GET", "POST"])  # edit a flight
def edit_flight(id):
    pass
