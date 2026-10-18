# Unit 7 acceptance checklist (manual walkthrough)

Use synthetic IDs only (P90 to P93). Start with a fresh database: close the app, delete
`instance/capstone.db`, then run `python app.py` and open http://127.0.0.1:5000.

| ID | Requirement | Steps | Expected result | Result |
| --- | --- | --- | --- | --- |
| A1 | FR1 consent first | Enter P90 but leave the consent box empty, then click Start | Message says consent is required. The test does not open | |
| A2 | FR6 no personal data | Enter an email address as the ID, check consent, click Start | Message says the ID is invalid. Nothing is saved | |
| A3 | FR1, FR2 pre-assessment | Enter P90, check consent, click Start | The pre-assessment opens with 10 questions and "0 of 10 questions answered" | |
| A4 | Usability fix I3 | Answer Q1 and rate it | The counter changes to "1 of 10 questions answered" | |
| A5 | Usability fix I4 | Skip Q3, answer the rest, click Submit | Q3 is highlighted and the message lists Q3. Nothing is saved | |
| A6 | FR5 answers recorded | Answer Q3 and submit | The score is shown with a link to the training lesson | |
| A7 | FR3 training lesson | Read the lesson page | All six parts and "Stop, Verify, Report" are shown | |
| A8 | FR4 post-assessment | Continue to the post-assessment, answer all, submit | 10 questions, then the score and a Continue button | |
| A9 | Feedback | Pick an ease rating and click Finish | "Thank you" message | |
| A10 | FR2 rule | Open http://127.0.0.1:5000/test/post?pid=P91 after registering P91 only | Message says the pre-assessment has to be finished first | |
| A11 | FR7, FR8 dashboard | Open http://127.0.0.1:5000/admin (no password is needed on your own computer) | P90 is counted, the success criteria and the five warning signs are shown | |
| A12 | NFR5 safety | Click on each screenshot in the questions | Nothing opens. The screenshots are images only | |

Tester: Frank Lin. Date: ______. Overall result: ______.
