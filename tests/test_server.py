from . import conftest
from Python_Testing.server import loadClubs, loadCompetitions
import datetime
import json
import pytest


"""
BUG: bug/Point_updates_are_not_reflected
"""


def test_purchasePlaces_deduction(client, clubs, competitions):
    # Given
    club = 'Simply Lift'
    competition_name = 'Spring Festival'
    places = 2
    original_places = None
    original_points = None

    # Obtention du nombre original de places (compétitions) et de points (points club)
    for comp in competitions:
        if comp['name'] == competition_name:
            original_places = int(comp['numberOfPlaces'])
            break

    for club_data in clubs:
        if club_data['name'] == club:
            original_points = int(club_data['points'])
            break

    # Vérifier si la compétition est future
    competition_date = datetime.datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.datetime.now():
        pytest.skip("Skipping past date : test for a past competition")

    # When
    response = client.post('/purchasePlaces', data={'club': club, 'competition': competition_name, 'places': places})

    # Then
    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data

    # Accès aux competitions, clubs apres modification
    from Python_Testing.server import competitions, clubs
    updated_competitions = competitions
    updated_clubs = clubs

    # Calculs des points et places attendus
    expected_places = int(original_places) - places
    expected_points = int(original_points) - places

    assert expected_places == int(updated_competitions[0]['numberOfPlaces'])
    assert expected_points == int(updated_clubs[0]['points'])

    # Je reinitialise les modification apportée pour ne pas interférer avec les autres tests
    competitions.clear()
    clubs.clear()
    competitions.extend(loadCompetitions())
    clubs.extend(loadClubs())


"""
BUG: bug/Booking_places_in_past_competitions
"""


def test_purchasePlaces_past_competition(client):
    # Given
    club = 'Simply Lift'
    competition = 'Fall Classic'
    places = 2

    # When
    response = client.post('/purchasePlaces', data={'club': club, 'competition': competition, 'places': places})

    # Then
    assert response.status_code == 200
    assert b'Cannot book places for a past competition!' in response.data


"""
BUG: Clubs shouldn't be able to book more than 12 places per competition
"""


def test_purchasePlaces_more_than_12_places(client, competitions, clubs):
    # Given
    club = 'Simply Lift'
    competition_name = 'Spring Festival'
    places = 13
    competition = None

    # Obtention de la compétition correpondante à competition_name
    for comp in competitions:
        if comp['name'] == competition_name:
            competition = comp
            break

    # Vérifier si la compétition est future
    competition_date = datetime.datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.datetime.now():
        pytest.skip("Skipping past date : test for a more than 12 places")

    # When
    response = client.post('/purchasePlaces', data={'club': club, 'competition': competition_name, 'places': places})

    # Then
    assert response.status_code == 200
    assert b'Cannot book more than 12 places' in response.data

    competitions.clear()
    clubs.clear()
    competitions.extend(loadCompetitions())
    clubs.extend(loadClubs())


"""
BUG: Clubs shouldn't be able to book more than 12 places per competition (multiple_place_purchases)
"""
def test_multiple_place_purchases(client, clubs, competitions):
    # Given
    club = 'Simply Lift'
    competition = 'Spring Festival'
    places1 = 6
    places2 = 7

    # je recupere les infos de la competition à l'etat initiale
    initial_competition = [c for c in competitions if c['name'] == competition][0]
    initial_places_competition = initial_competition['numberOfPlaces']

    # Vérifier si la compétition est future
    competition_date = datetime.datetime.strptime(initial_competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.datetime.now():
        pytest.skip("Skipping past date : test for a more than 12 places (multiple places purchases)")

    # Effectuez le premier achat de 6 places sachant que le club a déja acheté auparavant 3 place pour cette compétition
    response1 = client.post('/purchasePlaces', data={'club': club, 'competition': competition, 'places': places1})
    assert response1.status_code == 200
    assert b'Great-booking complete!' in response1.data

    # Accès aux competitions, clubs apres modification 1
    from Python_Testing.server import competitions, clubs
    updated_competitions = competitions
    updated_clubs = clubs
    
    # Vérifiez que le nombre de places disponibles pour la compétition a été correctement mis à jour
    updated_competition = [c for c in updated_competitions if c['name'] == competition][0]
    expected_places1 = int(initial_places_competition) - places1
    assert expected_places1 == int(updated_competition['numberOfPlaces'])

    # Effectuez le deuxième achat de 7 places
    response2 = client.post('/purchasePlaces', data={'club': club, 'competition': competition, 'places': places2})
    assert response2.status_code == 200
    assert b'Cannot book more than 12 places' in response2.data

    # Accès aux competitions, clubs apres modification 2
    from Python_Testing.server import competitions, clubs
    updated_competitions = competitions
    updated_clubs = clubs
    # Vérifiez que le nombre de places disponibles pour la compétition reste inchangé
    updated_competition = [c for c in updated_competitions if c['name'] == competition][0]
    assert expected_places1 == int(updated_competition['numberOfPlaces'])

    # Je reinitialise les modification apportée pour ne pas interférer avec les autres tests 
    competitions.clear()
    clubs.clear()
    competitions.extend(loadCompetitions())
    clubs.extend(loadClubs())
