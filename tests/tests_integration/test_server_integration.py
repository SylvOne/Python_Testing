def test_full_interaction_scenario(client, clubs, competitions):
    # Test d'index
    result = client.get("/")
    assert result.status_code == 200

    # Test de connexion d'un utilisateur avec une adresse email inconnue
    result = client.post("/showSummary", data={"email": "unknown@random.com"})
    assert result.status_code == 200

    # Test de connexion d'un utilisateur avec une adresse email non trouvée
    result = client.post("/showSummary", data={"email": "unkezezanown@zae.com"})
    assert b"Sorry, that email wasn&#39;t found." in result.data

    # Test de connexion d'un utilisateur avec une adresse email valide
    result = client.post("/showSummary", data={"email": "admin@irontemple.com"})
    assert result.status_code == 200

    # Test d'achat d'un nombre de place = 0
    club = clubs[1]
    comp = competitions[1]
    result = client.post("/purchasePlaces", data={"competition": comp["name"], "club": club["name"], "places": 0})
    assert result.status_code == 200
    assert b"Cannot book less than 1 place" in result.data

    # Test d'achat de plus de 12 places
    club = clubs[0]
    comp = competitions[0]
    result = client.post("/purchasePlaces", data={"competition": comp["name"], "club": club["name"], "places": 13})
    assert result.status_code == 200
    assert b"Cannot book more than 12 places" in result.data

    # Test d'achat de places avec plus de places que disponibles dans la compétition
    competition = competitions[1]
    club = clubs[0]
    result = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": 27
        }
    )
    assert result.status_code == 200
    assert b"Cannot book more places than are available per competition" in result.data

    # Test d'achat de places avec un solde de points insuffisant
    competition = competitions[1]
    club = clubs[1]
    result = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": 5
        }
    )
    assert result.status_code == 200
    assert b"Cannot book more available points" in result.data

    # Test d'achat de places condition normal
    competition = competitions[0]
    club = clubs[0]
    result = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": 7
        }
    )
    assert result.status_code == 200
    assert b"Great-booking complete!" in result.data

    # Test d'achat de places pour une compétition passée
    competition = competitions[1]
    club = clubs[2]
    result = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": 5
        }
    )
    assert result.status_code == 200
    assert b"Cannot book places for a past competition!" in result.data

    # Test d'affichage du tableau du club
    result = client.get("/points")
    assert result.status_code == 200

    # Test de déconnexion
    result = client.get("/logout")
    assert result.status_code == 302
