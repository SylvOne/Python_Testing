from . import conftest
from Python_Testing.server import loadClubs, loadCompetitions
import datetime
import json
import pytest


"""
BUG: Point updates are not reflected
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
