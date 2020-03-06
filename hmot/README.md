Cycle of Turns

1. Manager
   Choose verification service and project
2. Game
   Determine the outcome of the project
3. Manager
   Choose reported value
4. Investor
   Bid for assets
5. Game
   Determine highest bidder
6. Show results of bidding to investors

Manager's turn
   generate manager's choice tuple for all managers
   (period, project choice, true asset, reported asset, verification service, verification report, high bid, earnings)
ManagerSelectionPage (uses ManagerBasePage) - select a project and verification service
   game determines outcome of the project (calculate_project_result)
   stores result into manager choice tuple
ManagerReportPage (uses ManagerBasePage) - choose reported value

Investor's turn
   complete the manager's choice tuple
InvestorsBiddingPage - bid on all the projects
   select a bid winner

Results
   Market history tuple
   (period, true value, reported value, verification report, verification service, accuracy (yes/no), high bid, high bidder earned)

History:
Managers:
Prev Choices - Able to view all prior choices made by self

All:
Market History - all rounds up to previous actual outcomes,etc...
