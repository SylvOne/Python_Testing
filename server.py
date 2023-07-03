import json
from flask import Flask,render_template,request,redirect,flash,url_for
import os
from datetime import datetime


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
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

     # Vérification du nombre de places demandées
    places_booked = 0
    for booking in club['bookings']:
        if booking['competition'] == competition['name']:
            places_booked += booking['places']

    total_places_required = places_booked + placesRequired
    if total_places_required > 12:
        flash('Cannot book more than 12 places')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification du solde de points disponible
    if placesRequired > point_club_available:
        flash('Cannot book more available points')
        return render_template('welcome.html', club=club, competitions=competitions, date=actual_date)
        
    # Vérification de la date de la compétition
    current_datetime = datetime.now()
    competition_datetime = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_datetime < current_datetime:
        flash('Cannot book places for a past competition!')
        return render_template('welcome.html', club=club, competitions=competitions)

    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points']) - placesRequired

    # Mise à jour de la liste des réservations du club
    club['bookings'].append({'competition': competition['name'], 'places': placesRequired})
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))