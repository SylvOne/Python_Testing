import json
from flask import Flask,render_template,request,redirect,flash,url_for
import os
from datetime import datetime
from flask import jsonify
from flask_caching import Cache


actual_date = str(datetime.now())

def loadClubs():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clubs.json')) as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(os.path.join(os.path.dirname(__file__), 'competitions.json')) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']]
    if club:
        club = club[0]
        return render_template('welcome.html',club=club,competitions=competitions, date=actual_date)
    else:
        flash("Sorry, that email wasn't found.")
        return render_template('index.html')


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)


# Phase 2, route for feature : points display board
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.route('/points', methods=['GET'])
@cache.cached(timeout=60)  # cache pendant 60 secondes
def points():
    clubs_points = {club['name']: club['points'] for club in clubs}
    return render_template('points.html', clubs=clubs_points)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    point_club_available = int(club['points'])

    if placesRequired < 1:
        flash('Cannot book less than 1 place')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)
    
    # Vérification que le nombre de place demandé 
    # ne soit pas supérieur au nombre de places disponible pour la compétition
    if placesRequired > placesCompetition:
        flash('Cannot book more places than are available per competition')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)

    # Vérification du nombre de places demandées
    places_booked = 0
    for booking in club['bookings']:
        if booking['competition'] == competition['name']:
            places_booked += booking['places']

    total_places_required = places_booked + placesRequired
    if total_places_required > 12:
        flash('Cannot book more than 12 places')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)

    # Vérification du solde de points disponible
    if placesRequired > point_club_available:
        flash('Cannot book more available points')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)

    # Vérification de la date de la compétition
    current_datetime = datetime.now()
    competition_datetime = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_datetime < current_datetime:
        flash('Cannot book places for a past competition!')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)

    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points']) - placesRequired

    # Mise à jour de la liste des réservations du club
    club['bookings'].append({'competition': competition['name'], 'places': placesRequired})
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))