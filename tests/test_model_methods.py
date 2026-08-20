from datetime import datetime

from conftest import create_card, create_user


def test_completed_status_zaehlt_erledigte_und_gesamtzahl_der_meilensteine_korrekt(app):
    card = create_card('P', 'S1', milestone_descriptions=['M1', 'M2', 'M3'])
    card.milestones[0].finished = datetime.now()
    card.milestones[1].finished = datetime.now()
    # M3 bleibt offen

    completed, total = card.completed_status()

    assert completed == 2
    assert total == 3


def test_completed_milestones_liefert_nur_die_tatsaechlich_erledigten_meilensteine(app):
    card = create_card('P', 'S1', milestone_descriptions=['M1', 'M2'])
    card.milestones[0].finished = datetime.now()
    # M2 bleibt offen

    completed = card.completed_milestones()

    assert [m.description for m in completed] == ['M1']


def test_visible_cards_liefert_nur_sichtbare_karten_des_nutzers(app):
    user = create_user('u1')
    visible = create_card('P', 'Sichtbar', users=[user], is_visible=True)
    create_card('P', 'Versteckt', users=[user], is_visible=False)

    result = user.visible_cards()

    assert [c.student_name for c in result] == [visible.student_name]


def test_clean_copy_uebernimmt_meilenstein_beschreibungen_und_nutzer_aber_nicht_den_abschluss(app):
    owner = create_user('owner')
    vorlage = create_card('P', 'Vorlage', milestone_descriptions=['M1', 'M2'], users=[owner])
    vorlage.milestones[0].finished = datetime.now()
    vorlage.milestones[0].signed_by = 'owner'

    kopie = vorlage.clean_copy(pname='P', sname='Kopie')

    assert kopie.project_name == 'P'
    assert kopie.student_name == 'Kopie'
    assert {m.description for m in kopie.milestones} == {'M1', 'M2'}
    assert all(m.finished is None for m in kopie.milestones)
    assert all(m.signed_by is None for m in kopie.milestones)
    assert {u.uid for u in kopie.users} == {owner.uid}
