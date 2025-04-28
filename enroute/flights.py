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
from datetime import datetime, timezone
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
        "SELECT * FROM flight WHERE user_id = ? ORDER BY departure_time ASC",
        (g.user["id"],),
    ).fetchall()

    upcoming = []
    past = []

    now = datetime.now(timezone.utc)

    for flight in flights:
        departure_time = flight["departure_time"].replace(tzinfo=timezone.utc)

        if departure_time > now:
            upcoming.append(flight)
        else:
            past.append(flight)

    return render_template("flights/index.html", upcoming=upcoming, past=past)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_flight():
    if request.method == "POST":
        flight_number = request.form["flight_number"]
        flyer_name = request.form.get("flyer") or g.user["username"]
        db = get_db()

        existing_flight = db.execute(
            "SELECT id FROM flight WHERE user_id = ? AND flyer_name = ? AND flight_number = ?",
            (g.user["id"], flyer_name, flight_number),
        ).fetchone()

        if existing_flight:
            flash(
                f"You already have flight {flight_number} for {flyer_name} saved.",
                "warning",
            )
            return redirect(url_for("flights.index"))

        aviationstack_api_key = os.getenv("AVIATIONSTACK_API_KEY")
        url = f"http://api.aviationstack.com/v1/flights?access_key={aviationstack_api_key}&flight_iata={flight_number}"
        response = requests.get(url)
        print("response", response.json())

        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                # TODO: Add more fields
                flight_info = data["data"][0]
                airline = flight_info["airline"]["name"]
                flight_date = flight_info["flight_date"]
                departure_airport = flight_info["departure"]["airport"]
                arrival_airport = flight_info["arrival"]["airport"]
                departure_time = flight_info["departure"]["scheduled"]
                arrival_time = flight_info["arrival"]["scheduled"]
                departure_timezone = flight_info["departure"]["timezone"]
                arrival_timezone = flight_info["arrival"]["timezone"]
                flight_status = flight_info["flight_status"]
            else:
                flash("No flight data found.", "error")
                return render_template("flights/add.html")
        else:
            flash("Error retrieving flight data from AviationStack.", "error")
            return render_template("flights/add.html")

        print(f"Adding flight {flight_number} to db")
        db.execute(
            "INSERT INTO flight (user_id, airline, flight_number, flight_date, departure_airport, arrival_airport, departure_time, arrival_time, departure_timezone, arrival_timezone, status, flyer_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                g.user["id"],
                airline,
                flight_number,
                flight_date,
                departure_airport,
                arrival_airport,
                departure_time,
                arrival_time,
                departure_timezone,
                arrival_timezone,
                flight_status,
                flyer_name,
            ),
        )
        db.commit()
        return redirect(url_for("flights.index"))

    return render_template("flights/add.html")


@bp.route("/<int:id>")
@login_required
def view_flight(id):
    db = get_db()
    flight = db.execute(
        "SELECT * FROM flight WHERE id = ? AND user_id = ?", (id, g.user["id"])
    ).fetchone()

    if flight is None:
        flash("Flight not found.", "error")
        return redirect(url_for("flights.index"))

    aviationstack_api_key = os.getenv("AVIATIONSTACK_API_KEY")
    url = f"http://api.aviationstack.com/v1/flights?access_key={aviationstack_api_key}&flight_iata={flight['flight_number']}"
    response = requests.get(url)

    live_info = None

    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            live_info = data["data"][0]
        else:
            flash("No live flight data found.", "warning")
    else:
        flash("Error retrieving flight data from AviationStack.", "warning")

    return render_template("flights/detail.html", live_info=live_info)


@bp.route("/<int:id>/delete", methods=["POST"])  # delete a flight
def delete_flight(id):
    pass


@bp.route("/<int:id>/edit", methods=["GET", "POST"])  # edit a flight
def edit_flight(id):
    pass


def db_get_existing_flight(user_id, flyer_name, flight_number):
    db = get_db()
    existing_flight = db.execute(
        "SELECT id FROM flight WHERE user_id = ? AND flyer_name = ? AND flight_number = ?",
        (user_id, flyer_name, flight_number),
    ).fetchone()

    return existing_flight
