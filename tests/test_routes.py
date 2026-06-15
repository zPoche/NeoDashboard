def test_accounts_index_requires_login(client):
    response = client.get('/accounts/', follow_redirects=False)
    assert response.status_code in (302, 401)


def test_leaderboards_requires_login(client):
    response = client.get('/leaderboards/', follow_redirects=False)
    assert response.status_code in (302, 401)


def test_announcements_requires_login(client):
    response = client.get('/announcements/', follow_redirects=False)
    assert response.status_code in (302, 401)


def test_main_index_accessible(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code in (200, 302)
