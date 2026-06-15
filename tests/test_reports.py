from app.reports import graph_color_from_label


def test_graph_color_from_label_long_name():
    color = graph_color_from_label('Brick 2x4 Red')
    assert color.startswith('#')
    assert len(color) == 7


def test_graph_color_from_label_short_name():
    color = graph_color_from_label('A')
    assert color == '#414141'


def test_graph_color_from_label_stable():
    assert graph_color_from_label('Test') == graph_color_from_label('Test')
