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

class Project:
    def __init__(self, name, cost, probability):
        self.name = name
        self.cost = cost
        # list of [probability (%), value] for each project
        self.probability = probability
    
    def get_choice_str(self):
        return f'Project {self.name}: {self.cost}'

    def get_project_name(self):
        return f'Project {self.name}'
    
    def get_explanation(self):
        result = f'Project {self.name} costs {self.cost} and has a '
        for idx, outcome in enumerate(self.probability):
            prob, change = outcome
            prob = '%.2f'%(prob/100)
            result += f'{prob} chance of changing your asset value by {change}'
            if idx != len(self.probability) - 1:
                result += ' and a '
        return result

class Constants(BaseConstants):
    name_in_url = 'hmot'
    players_per_group = None
    num_rounds = 20

    # Market Type
    loss_possible = False

    # Manager's initial asset value
    initial_asset_value = 600

    # Service id and accuracy (probability of finding true asset value)
    audit_services = {
        1: 95,
        2: 80,
        3: 65,
        4: 50
    }
    # Display values for audit services
    audit_choices = {}
    for audit_service, accuracy in audit_services.items():
        # [1, 'Service 1: 95%% accurate']
        audit_choices[audit_service] = "Service %s: %s%% accurate" % (audit_service, accuracy)
    
    projects = None
    if loss_possible:
        projects = {
            1: Project('A', 50, [[10, 1000], [90, -400]]),
            2: Project('B', 100, [[100, -400]])
        }
    else:
        projects = {
            1: Project('A', 50, [[10, 1000], [90, 400]]),
            2: Project('B', 100, [[100, 100]])
        }

    def generate_report_values(projects, initial_asset_value):
        vals = set() # all unique possible values
        for key, project in projects.items():
            for outcome in project.probability:
                prob, change = outcome
                vals.add(initial_asset_value + change)
        return dict(enumerate(vals))

    # Manager report values
    report_values = generate_report_values(projects, initial_asset_value)

class Subsession(BaseSubsession):
    # Initialize session wide variables and participant roles
    def creating_session(self):
        if self.round_number == 1:
            roles = itertools.cycle(['manager', 'investor'])
            num_managers = 0
            project_idx_to_manager_id = {}
            for player in self.get_players():
                # Assign roles
                player.participant.vars['role'] = next(roles)
                # print(player.participant.id_in_session)
                # print(player.participant.vars['role'])
                if (player.participant.vars['role'] == 'manager'):
                    project_idx_to_manager_id[num_managers] = player.participant.id_in_session
                    num_managers += 1

            self.session.vars['project_idx_to_manager_id'] = project_idx_to_manager_id
            # stores total number of managers so correct number of projects can be bid on for investor template
            self.session.vars['num_managers'] = num_managers
            # list of ProjectHistory objects, used for displaying manager history and market history
            self.session.vars['project_history'] = []

class Group(BaseGroup):
    # Append bid data (list of tuples container investor id and bid amount) to project history
    def set_project_bids(self):
        project_bids = {} # manager_id to list of bids
        for player in self.get_players():
            if (player.participant.vars['role'] == 'investor'):
                investor_id = player.participant.id_in_session
                for idx, bid in enumerate(player.project_bids.split(',')):
                    bid = int(bid)
                    manager_id = self.session.vars['project_idx_to_manager_id'][idx]
                    if manager_id not in project_bids.keys():
                        project_bids[manager_id] = []
                    project_bids[manager_id].append((investor_id, bid))

        # manager_id is used to identify each project for current round
        for ph in [ph for ph in self.session.vars['project_history'] if ph.period == self.round_number]:
            ph.set_bids(project_bids[ph.manager_id])

# Fields used for retrieving data from forms, comprehensive data stored in session.vars['project_history']
class Player(BasePlayer):
    # Manager specific fields (not used by investor players)

    # Id of audit service choosen by a manager
    audit_choice = models.IntegerField(
        choices = [[k, Constants.audit_choices[k]] for k in Constants.audit_choices.keys()],
        widget = widgets.RadioSelect
    )
    # Id of project choosen by a manager
    project_choice = models.IntegerField(
        choices = [[k, Constants.projects[k].get_choice_str()] for k in Constants.projects.keys()],
        widget = widgets.RadioSelect
    )
    # Reported asset value choosen by manager
    reported_value = models.IntegerField(
        widget = widgets.RadioSelect
    )

    # TODO: move this to constants
    # oTree method for providing choices to reported value
    def reported_value_choices(self):
        return [[k, Constants.report_values[k]] for k in Constants.report_values.keys()]

    # Display value of audit choice
    def get_audit_choice(self):
        return "Service %s: %s%% accurate" % (self.audit_choice, Constants.audit_services[self.audit_choice])

    # Display value of project choice
    def get_project_choice(self):
        return Constants.projects[self.project_choice].get_project_name()

    # Investor specific fields (not used by manager players)

    # Serialized bids for all available projects as comma separated list, see InvestorsBiddingPage for implementation
    project_bids = models.StringField()