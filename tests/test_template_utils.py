from app.render_environment.template_utils import common_classification, common_classification_description


def test_common_classification(items):
    result = common_classification(items)
    assert result == 'ДК021 22400000-4'


def test_common_classification_description(items):
    result = common_classification_description(items)
    assert result == "Марки, чекові бланки, банкноти, сертифікати акцій, рекламні матеріали, каталоги та посібники"


def test_common_classification_invalid_items(items):
    items.append({
        "id": "1b5d73b21cdb483494d68d09ccf5199a",
        "description": "Сільськогосподарська, фермерська продукція,",
        "classification" : {
            "id": "03000000-1",
            "scheme": "ДК021",
            "description": "Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та супутня" \
                " продукція"
        },
        "quantity": 1
    })
    result = common_classification(items)
    assert result == ""


def test_common_classification_description_invalid_items(items):
    items.append({
        "id": "1b5d73b21cdb483494d68d09ccf5199a",
        "description": "Сільськогосподарська, фермерська продукція,",
        "classification" : {
            "id": "03000000-1",
            "scheme": "ДК021",
            "description": "Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та супутня" \
                " продукція"
        },
        "quantity": 1
    })
    result = common_classification_description(items)
    assert result == ""
