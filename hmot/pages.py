from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import random

# Data structure for storing project outcomes
class ProjectHistory:
    # Constructor for initial manager selfs (project and audit/verification service)
    def __init__(self, manager_id, period, project_choice, verification_service, asset_change):
        self.manager_id = manager_id
        self.period = period
        self.project_choice = project_choice
        self.verification_service = verification_service
        self.asset_change = asset_change # project success/failure

        self.manager_cost = Constants.initial_asset_value 
        self.true_asset_value = self.manager_cost + self.asset_change
        
    # Set during manager's asset reporting phase
    def set_reported_asset_value(self, reported_asset_value):
        self.reported_asset_value = reported_asset_value
    
    # Set after game runs verification service on reported value
    def set_verification_report(self, verification_report, verification_accurate):
        self.verification_report = verification_report
        self.verification_accurate = verification_accurate
    
    # Set after all investors have bid
    def set_bids(self, bids):
        self.bids = bids # list of (investor, bid) tuples
        # calculate bid winner, high bid, manager earnings, high bidder earnings
        high_bidder = None
        high_bid = 0
        for bid_tuple in bids:
            investor, bid = bid_tuple
            if bid > high_bid:
                high_bid = bid
                high_bidder = investor

        self.high_bidder = high_bidder
        self.high_bid = high_bid
        self.high_bidder_earnings = self.true_asset_value - self.high_bid
        self.manager_earnings = self.high_bid - self.manager_cost
    
    def get_verification_report(self):
        return 'AGREE' if self.verification_report else 'DISAGREE'
    
    def get_verification_accurate(self):
        return 'YES' if self.verification_accurate else 'NO'

    # format data for manager history display in template
    def gen_manager_history_row(self):
        return [
            self.period,
            Constants.project_names[self.project_choice],
            self.true_asset_value,
            self.reported_asset_value,
            Constants.audit_choices[self.verification_service],
            self.get_verification_report(),
            self.high_bid,
            self.manager_earnings
        ]
    
    # formate data for market history display in template
    def gen_market_history_row(self):
        return [
            self.period,
            self.true_asset_value,
            self.reported_asset_value,
            self.get_verification_report(),
            Constants.audit_choices[self.verification_service],
            self.get_verification_accurate(),
            self.high_bid,
            self.high_bidder_earnings
        ]

# Append market history method to base Page class
def generate_market_history(self):
    result = []
    for ph in [ph for ph in self.session.vars['project_history'] if ph.period != self.round_number]:
        result.append(ph.gen_market_history_row)
    return result

setattr(Page, 'generate_market_history', generate_market_history)

# Shared base class for both manager phases
class ManagerBasePage(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

    def vars_for_template(self):
        return dict(
            previous_choices = self.generate_manager_history(),
            market_history = self.generate_market_history()
        )

    # helper method to generate manager's history for template
    def generate_manager_history(self):
        result = []
        for ph in [ph for ph in self.session.vars['project_history'] if ph.period < self.player.round_number]:
            if ph.manager_id == self.participant.id_in_session:
                result.append(ph.gen_manager_history_row)
        return result

# Phase where Manager selects a project and a verification service 
class ManagerSelectionPage(ManagerBasePage):
    # timeout_seconds = 60
    form_fields = ['audit_choice', 'project_choice']

    def vars_for_template(self):
        my_vars = dict()
        my_vars.update(super().vars_for_template())
        return my_vars

    # Determines success/failure of project and associated change in asset value
    def calculate_project_result(self):
        probability_distribution = Constants.project_values[self.player.project_choice]
        # assumes maximum of two probabilities in distribution
        choice1_prob = probability_distribution[0][0]/100.0
        asset_change = None
        if random.random() <= choice1_prob:
            asset_change = probability_distribution[0][1]
        else:
            asset_change = probability_distribution[1][1]
        return asset_change

    # Append new project to project history
    def before_next_page(self):
        asset_change = self.calculate_project_result()
        new_ph = ProjectHistory(
            self.participant.id_in_session,
            self.player.round_number,
            self.player.project_choice,
            self.player.audit_choice,
            asset_change
        )
        self.session.vars['project_history'].append(new_ph)

# Phase where manager selects which value to report
class ManagerReportPage(ManagerBasePage):
    # timeout_seconds = 60
    form_fields = ['reported_value']

    def vars_for_template(self):
        phs = [ph.asset_change for ph in self.session.vars['project_history'] 
                if ph.manager_id == self.participant.id_in_session and ph.period == self.player.round_number - 1]
        ac = phs[0] if phs else 0
        my_vars = dict(
            asset_change = ac,
            initial_asset_value = Constants.initial_asset_value
        )
        my_vars.update(super().vars_for_template())
        return my_vars

    # Run audit returns tuple of verification report and verification accuracy
    def audit_reported_value(self, true_asset_value):
        audit_service_accuracy = Constants.audit_services[self.player.audit_choice]
        verification_report = None
        verification_accuracy = None
        if random.random() <= (0.01 * audit_service_accuracy):
            verification_report = (true_asset_value == self.player.reported_value)
            verification_accuracy = True # audit learns true value
        else:
            verification_report = True # audit always succeeds when verification fails
            verification_accuracy = False # audit does not learn true value
        return (verification_report, verification_accuracy)

    # Add audit outcome to project history
    def before_next_page(self):
        phs = [ph for ph in self.session.vars['project_history'] 
                if ph.manager_id == self.participant.id_in_session and ph.period == self.player.round_number]
        ph = phs[0] if phs else []
        ph.set_reported_asset_value(self.player.reported_value)
        verification_report, verification_accuracy = self.audit_reported_value(ph.true_asset_value)
        ph.set_verification_report(verification_report, verification_accuracy)

# Where investors wait while managers make their choices
class InvestorsWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

# Bidding Phase
class InvestorsBiddingPage(Page):
    # timeout_seconds = 60
    form_model = 'player'
    form_fields = ['project_bids']

    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

    def vars_for_template(self):
        return dict(
            num_managers = range(self.session.vars['num_managers']),
            # market_history = self.generate_market_history()
        )

# Aggregate bids (not visible)
class InvestorResultsPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'
    
    # get bid winners of each project
    after_all_players_arrive = 'set_project_bids'

# Where managers wait while investors bid
class ManagersWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

# Display some results before next round
class Results(Page):
    timeout_seconds = 60
    
    def before_next_page(self):
        pass
        # print(self.session.vars['project_history'])

page_sequence = [
    ManagerSelectionPage, 
    ManagerReportPage, 
    InvestorsWaitingPage, 
    InvestorsBiddingPage, 
    InvestorResultsPage, 
    ManagersWaitingPage, 
    Results
]
