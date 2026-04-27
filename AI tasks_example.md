Task name: Case Duration Query  Input:"how long has this case been going?"-the ai will go look in the database to the case table and will look for created_at columns Output: "Case: Ahmed Property Dispute
Reference: CASE-2024-0012
Created: 02/11/2022
Duration: 2 years, 5 months
Status: Active"
Task name:Client Case Count Query  Input: "how many cases have we got from the client?"- the ai will go to the client table and will look for first_name, last_name or perhaps even id if given Output: 
"(this client) has 3 cases"
(cases 1) carted at: 05/04/2022
status: active
(cases2) .... and so on
Task name:Deadline Status Query  Input:"has this case reached the deadline for the court hearing"-the ai will look for the deadline table 
Output: (case deadline is :02/06/2026)
Case: Ahmed Property Dispute
Reference: CASE-2024-0012
Deadline: 02/06/2026
Days Remaining: 92
Status: Pending



does the system know which task to run? Keywords when a user asks "how long has lawyer Ahmed case been going" the ai looks for the keyword structure "Ahmed's case" tells the ai that Ahmed is a lawyer not the clint "been going" carted_at column (if the user did not specify who ahmed is the ai will ask to specify)


What does a structured output look like? "how long has the Ahmed case been going." 
looking at database lawyer Ahmed's case was crated at 2/4/2025
it has now been 7 months 