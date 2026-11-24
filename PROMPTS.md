PROMPTS.md

Emirates Agent Gatekeeper --- Prompt Record

Student: Anuj Prashar

Enrolment Number: PGD202566060

Company selected: Emirates

Project: Emirates Agent Gatekeeper

Important: This is a prepared prompt record/template. Keep only

prompts that you actually entered into your coding assistant. Edit the

wording if your actual prompts were different. Do not claim that a

prompt was used if you did not use it.

Prompt 1 --- Create the basic application

Create a small educational prototype called Emirates Agent Gatekeeper

using Python and Streamlit. The app should demonstrate how an airline

can decide whether a customer's AI agent request should be ALLOW, ASK

CUSTOMER, or BLOCK. Display the project name and enrolment number

PGD202566060. Do not connect to Emirates systems or process real

payments.

Prompt 2 --- Add the decision rules

Add these classroom-simulation rules: - R1: Block an unknown or

unregistered agent. - R2: Block a revoked agent. - R3: Allow a

registered active agent to view fares. - R4: Allow a booking only when

the amount is within the customer's authorised spending limit. - R5: Ask

the customer to confirm a booking above the authorised limit. Use

₹20,000 as the sample limit when no lower customer-authorised limit

applies. - R6: Ask the customer to confirm a flight-change request. -

R7: Ask the customer to confirm a refund request. - R8: Block missing or

invalid details and unsupported actions.

Show the decision, rule number, and a short reason for every request.

Treat these as prototype rules, not official Emirates policies.

Prompt 3 --- Add agent registration

Add an Agent Management section. Let the user register an AI agent

against a customer name and set a customer-authorised spending limit.

Store the agent's status as ACTIVE. Save registered agents so that they

remain available after the app is restarted.

Prompt 4 --- Add agent revocation

Add a way to revoke a registered agent. When an agent is revoked, save

the revocation date and time. A revoked agent must always be blocked

from making new requests. Keep the old registration and revocation

records for audit purposes.

Prompt 5 --- Add the audit log

Create an audit log that records the date and time, customer, agent,

requested action, amount, decision, rule number, and reason. Also record

agent registration and revocation events. Keep the log available in the

app and preserve earlier records.

Prompt 6 --- Add the request dashboard

Create a simple dashboard with fields for customer, registered agent

selection, action (View fares, Book flight, Change flight, Refund), and

amount in INR. Add a Check Request button. Show the decision clearly as

ALLOW, ASK CUSTOMER, or BLOCK, along with the applicable rule and

explanation.

Prompt 7 --- Test and correct the application

Help me test these six cases and fix any errors: 1. Registered active

agent views fares --- expected ALLOW, R3. 2. Unknown agent attempts a

booking --- expected BLOCK, R1. 3. Registered agent requests a booking

above the authorised limit --- expected ASK CUSTOMER, R5. 4. Registered

agent requests a booking within the authorised limit --- expected ALLOW,

R4. 5. Revoked agent attempts a booking --- expected BLOCK, R2. 6. A

different registered active agent requests a flight change --- expected

ASK CUSTOMER, R6.





