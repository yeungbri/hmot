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

class Constants(BaseConstants):
    name_in_url = 'hmot'
    players_per_group = None
    num_rounds = 20

    # Market Type
    loss_possible = False
    audit_services = {
        1: 95,
        2: 80,
        3: 65,
        4: 50
    }

    audit_choices = {}
    for audit_service, accuracy in audit_services.items():
        # [1, 'Service 1: 95%% accurate']
        audit_choices[audit_service] = "Service %s: %s%% accurate" % (audit_service, accuracy)

    project_names = {
        1: 'A',
        2: 'B'
    }

    project_values = {
        1: [[10, 1000], [90, 400]],
        2: [[100, 100]]
    }

    initial_asset_value = 600

class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            roles = itertools.cycle(['manager', 'investor'])
            num_managers = 0
            for player in self.get_players():
                # Assign roles
                player.participant.vars['role'] = next(roles)
                if (player.participant.vars['role'] == 'manager'):
                    num_managers += 1
                
                # Track manager's previous choices
                player.participant.vars['manager_history'] = []
            self.session.vars['num_managers'] = num_managers
            self.session.vars['market_history'] = []
            self.session.vars['project_history'] = []

class Group(BaseGroup):
    def get_bids(self):
        bids = {}
        for player in self.get_players():
            print(player.participant.vars['role'])
            if (player.participant.vars['role'] == 'investor'):
                bids[player.id_in_group] = player.project_bids.split(',')
                # print(player.project_bids)
        winners = {}
        for i in range(1):
            bid_winner = None
            largest_bid = 0
            for bidder, bids in bids.items():
                bid = int(bids[i])
                if bid > largest_bid:
                    bid_winner = bidder
                    largest_bid = bid
            winners[i] = (bid_winner, largest_bid)

        self.session.vars['winners'] = winners
        print(winners)
    pass

class Player(BasePlayer):
    # Manager specific
    audit_choice = models.IntegerField(
        choices= [ [k, Constants.audit_choices[k]] for k in Constants.audit_choices.keys()],
        widget=widgets.RadioSelect
    )

    project_choice = models.IntegerField(
        choices=[
            [1, 'Project A: 50'],
            [2, 'Project B: 10']
        ],
        widget = widgets.RadioSelect
    )

    reported_value = models.IntegerField(
        widget = widgets.RadioSelect
    )

    def reported_value_choices(self):
        return [
            [1, 1600],
            [2, 200]
        ]

    def get_audit_choice(self):
        return "Service %s: %s%% accurate" % (self.audit_choice, Constants.audit_services[self.audit_choice])

    def get_project_choice(self):
        return 'Project %s' % Constants.project_names[self.project_choice]

    # Investor specific
    project_bids = models.StringField()