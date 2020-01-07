from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class ManagerSelectionPage(Page):
    # timeout_seconds = 60
    form_model = 'player'
    form_fields = ['selected_project', 'selected_auditor', 'audit_choice', 'project_choice']

    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

    def before_next_page(self):
        # calculate auditing
        pass

class InvestorsWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

class InvestorsBiddingPage(Page):
    timeout_seconds = 60

    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

class ManagersWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

class Results(Page):
    timeout_seconds = 60


page_sequence = [ManagerSelectionPage, InvestorsWaitingPage, InvestorsBiddingPage, ManagersWaitingPage, Results]
