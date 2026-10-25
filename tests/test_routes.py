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


def test_ugc_viewer_places_models_from_stored_transform(app):
    from flask import render_template

    with app.test_request_context('/'):
        html = render_template(
            'ldd/ldd.html.j2',
            content=[{
                'lot': 14,
                'id': 7,
                'pos': [{
                    'x': 12.5,
                    'y': 3,
                    'z': -4,
                    'rx': 0,
                    'ry': 0.5,
                    'rz': 0,
                    'rw': 1,
                }],
            }],
            lod=0,
        )

    assert '/properties/get_model/7/lxfml/0' in html
    assert '12.5' in html
    assert 'THREE.Matrix4().compose' in html
    assert 'addSceneAsync(entry.url, placement)' in html
    assert 'm.premultiply(bri.placement)' in html
