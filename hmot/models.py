from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
import itertools

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'hmot'
    players_per_group = None
    num_rounds = 20

    audit_services = {
        1: 95,
        2: 80,
        3: 65,
        4: 50
    }

    audit_choices = []
    for audit_service, accuracy in audit_services.items():
        # [1, 'Service 1: 95%% accurate']
        audit_choices.append([audit_service, "Service %s: %s%% accurate" % (audit_service, accuracy)])

class Subsession(BaseSubsession):
    def creating_session(self):
        # randomize to treatments
        if self.round_number == 1:
            roles = itertools.cycle(['manager', 'investor'])
            for player in self.get_players():
                player.participant.vars['role'] = next(roles)
                print("set participant['role'] to", player.participant.vars['role'])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    role = models.StringField()
    selected_project = models.StringField()
    selected_auditor = models.StringField()

    audit_choice = models.IntegerField(
        choices=Constants.audit_choices,
        widget=widgets.RadioSelect
    )

    project_choice = models.IntegerField(
        choices=[
            [1, 'Project A: 50'],
            [2, 'Project B: 10']
        ],
        widget = widgets.RadioSelect
    )
