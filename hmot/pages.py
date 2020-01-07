from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class ManagerSelectionPage(Page):
    # timeout_seconds = 60
    form_model = 'player'
    form_fields = ['audit_choice', 'project_choice']

    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

    def before_next_page(self):
        # calculate actual value
        if self.player.project_choice == 2:
            return Constants.project_values[self.player.project_choice]

class ManagerReportPage(Page):
    form_model = 'player'
    form_fields = ['reported_value']

    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

    def before_next_page(self):
        # audit verification
        audit_service_accuracy = Constants.audit_services[self.player.audit_choice]
        agree = None
        if random.random() <= (0.01 * audit_service_accuracy):
            # audit learns true value
            agree = (true_value == self.player.reported_value)
        else:
            # audit does not learn true value
            agree = True


class InvestorsWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

class InvestorsBiddingPage(Page):
    # timeout_seconds = 60

    def is_displayed(self):
        return self.participant.vars['role'] == 'investor'

class ManagersWaitingPage(WaitPage):
    def is_displayed(self):
        return self.participant.vars['role'] == 'manager'

class Results(Page):
    timeout_seconds = 60

page_sequence = [ManagerSelectionPage, ManagerReportPage, InvestorsWaitingPage, InvestorsBiddingPage, ManagersWaitingPage, Results]
