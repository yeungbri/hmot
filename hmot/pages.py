from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import random

class ManagerChoice:
    def __init__(self, period, verification_service, project_choice, asset_change):
        self.period = period
        self.verification_service = verification_service
        self.project_choice = project_choice
        self.asset_change = asset_change
        self.true_asset_value = Constants.initial_asset_value + self.asset_change
        
    def set_reported_asset_value(self, reported_asset_value):
        self.reported_asset_value = reported_asset_value
    
    def set_verification_report(self, verification_report):
        self.verification_report = verification_report
    
    def set_high_bid(self, high_bid):
        self.high_bid = high_bid
        # TODO: fix
        self.earnings = high_bid # - Constants.verification_service_cost - 

class ManagerBasePage(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

    def vars_for_template(self):
        return dict(
            # manager_history = self.participant.vars['manager_history'],
            previous_choices = self.generate_previous_choices()
        )

    def generate_previous_choices(self):
        result = []
        
        for choice in self.participant.vars['manager_history'][:-1]:
            single = [
                choice.period,
                Constants.project_names[choice.project_choice],
                choice.true_asset_value,
                choice.reported_asset_value,
                Constants.audit_choices[choice.verification_service],
                'AGREE' if choice.verification_report else 'DISAGREE',
                choice.high_bid,
                choice.earnings
            ]
            result.append(single)
        print(result)
        return result

class ManagerSelectionPage(ManagerBasePage):
    # timeout_seconds = 60
    form_fields = ['audit_choice', 'project_choice']

    def vars_for_template(self):
        my_vars = dict(
            # market_history = self.session.vars['market_history']
        )
        my_vars.update(super().vars_for_template())
        return my_vars

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

    def before_next_page(self):
        asset_change = self.calculate_project_result()
        new_choice = ManagerChoice(
            self.player.round_number,
            self.player.audit_choice,
            self.player.project_choice,
            asset_change
        )
        self.participant.vars['manager_history'].append(new_choice)

class ManagerReportPage(ManagerBasePage):
    form_fields = ['reported_value']

    def vars_for_template(self):
        my_vars = dict(
            asset_change = self.participant.vars['manager_history'][self.player.round_number - 1].asset_change,
            initial_asset_value = Constants.initial_asset_value
        )
        my_vars.update(super().vars_for_template())
        return my_vars

    def audit_reported_value(self, true_asset_value):
        audit_service_accuracy = Constants.audit_services[self.player.audit_choice]
        agree = None
        if random.random() <= (0.01 * audit_service_accuracy):
            # audit learns true value
            agree = (true_asset_value == self.player.reported_value)
        else:
            # audit does not learn true value
            agree = True
        return agree

    def before_next_page(self):
        manager_choice = self.participant.vars['manager_history'][self.player.round_number - 1]
        manager_choice.set_reported_asset_value(self.player.reported_value)
        audit_result = self.audit_reported_value(manager_choice.true_asset_value)
        manager_choice.set_verification_report(audit_result)
        self.session.vars['market_history'].append(manager_choice)

class InvestorsWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

class InvestorsBiddingPage(Page):
    # timeout_seconds = 60
    form_model = 'player'
    form_fields = ['project_bids']

    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

    def vars_for_template(self):
        return dict(
            num_managers = range(self.session.vars['num_managers']),
            market_history = self.session.vars['market_history']
        )

    def deserialize_bids(self, bids):
        bids_list = bids.split(',')
        

    def before_next_page(self):
        self.player.project_bids

class ManagersWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

class Results(Page):
    timeout_seconds = 60

page_sequence = [ManagerSelectionPage, ManagerReportPage, InvestorsWaitingPage, InvestorsBiddingPage, ManagersWaitingPage, Results]
