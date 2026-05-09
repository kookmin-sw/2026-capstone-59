---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/ch9.htm
---

### CHAPTER 9 INTEGRATION AND TEST PHASE

*9.0       [OBJECTIVE](#para9)*

*9.1       [TASKS AND
ACTIVITIES](#para9.1)**9.1.1
[Establish the Test Environment](#para9.1.1)**9.1.2
[Conduct Integration Tests](#para9.1.2)**9.1.3
[Conduct Subsystem/System Testing](#para9.1.3)**9.1.4
[Conduct Security Testing](#para9.1.4)**9.1.5
[Conduct Acceptance Testing](#para9.1.5)**9.1.6
[Revise Previous Documentation](#para9.1.6)*

*9.2       [ROLES AND
RESPONSIBILITIES](#para9.2)*

*9.3       [DELIVERABLES](#para9.3)**[9.3.1
Test Analysis Report](#para9.3.1)**[9.3.2
Test Analysis Approval Determination](#para9.3.2)**[9.3.3
Test Problem Report](#para9.3.3)**[9.3.4
IT Systems Security Certification & Accreditation](#para9.3.4)*

*9.4       [ISSUES FOR
CONSIDERATIONS](#para9.4)*

*9.5      [PHASE REVIEW
ACTIVITY](#para9.5)*

#### 9.0       OBJECTIVE

The objective of this phase is to prove that the developed system satisfies
the requirements defined in the FRD. Several types of tests will be conducted
in this phase. First, subsystem integration tests shall be executed and evaluated
by the development team to prove that the program components integrate properly
into the subsystems and that the subsystems integrate properly into an application.
Next, the testing team conducts and evaluates system tests to ensure the developed
system meets all technical requirements, including performance requirements.
Next, the testing team and the Security Program Manager conduct security tests
to validate that the access and data security requirements are met. Finally,
users participate in acceptance testing to confirm that the developed system
meets all user requirements as stated in the FRD. Acceptance testing shall be
done in a simulated “real” user environment with the users using
simulated or real target platforms and infrastructures.

#### 9.1       TASKS AND ACTIVITIES

#### 9.1.1    Establish the Test Environment

Establish the various test teams and ensure the test system(s) are ready.

#### 9.1.2    Conduct Integration Tests

The test and evaluation team is responsible for creating/loading the test database(s)
and executing the integration test(s). This is to ensure that program components
integrate properly into the subsystems and the subsystems integrate properly
into an application.

#### 9.1.3    Conduct Subsystem/System Testing

The test and evaluation team is responsible for creating/loading the test database(s)
and executing the system test(s). All results should be documented on the Test
Analysis Report (Appendix C-28), Test Problem Report (Appendix C-30) and on
the Test Analysis Approval Determination (Appendix C-29). Any failed components
should be migrated back to the development phase for rework, and the passed
components should be migrated ahead for security testing.

#### 9.1.4    Conduct Security Testing

The test and evaluation team will again create or load the test database(s)
and execute security (penetration) test(s). All tests will be documented, similar
to those above. Failed components will be migrated back to the development phase
for rework, and passed components will be migrated ahead for acceptance testing.

#### 9.1.5    Conduct Acceptance Testing

The test and evaluation team will create/load the test database(s) and execute
the acceptance test(s). All tests will be documented , similar to those above.
Failed components will be migrated back to the development phase for rework,
and passed components will migrate ahead for implementation.

#### 9.1.6    Revise previous documentation

During this phase, the Systems Technical Lead or the Developers will finalize
the Software Development Document from the Development Phase. He/They will also
finalize the Operations or Systems Administration Manual, User Manual, Training
Plan, Maintenance Manual, Conversion Plan, Implementation Plan, Contingency
Plan and Update the Interface Control Document from the Design Phase. The Project
Manager should finalize the System Security Plan and the Security Risk Assessment
from the Requirements Analysis Phase and the Project Management Plan from the
Planning Phase. The Configuration Manager should finalize the Configuration
Management Plan from the Planning Phase. The Quality Assurance office/person
should finalize the Quality Assurance Plan from the Planning Phase. And finally,
the Project Manager should finalize the Cost Benefit Analysis and the Risk Management
Plan from the System Concept Development Phase.

#### 9.2       ROLES AND RESPONSIBILITIES

- Project Manager. The project manager is responsible and accountable for
  the successful execution of the Integration and Test Phase. The project
  manager is responsible for leading the team that accomplishes the tasks
  shown above. The Project Manager is also responsible for reviewing deliverables
  for accuracy, approving deliverables and providing status reports to management.
- Project Team. The project team members (regardless of the organization of
  permanent assignment) are responsible for accomplishing assigned tasks as
  directed by the project manager. This includes establishing the test environment.
- Contracting Officer. The contracting officer is responsible and accountable
  for the procurement activities and signs contract awards.
- Security Program Manager. The Security Program Manager is responsible for
  conducting security tests according to the Systems Security Plan.
- Oversight Activities. Agency oversight activities, including the IRM office,
  provide advice and counsel for the project manager on the conduct and requirements
  of the Integration and Test Phase. Additionally, oversight activities provide
  information, judgements, and recommendations to the agency decision makers
  during project reviews and in support of project decision milestones.
- User. Users participate in acceptance testing to ensure systems perform
  as expected.

#### 9.3       DELIVERABLES

The following deliverables shall be initiated during the Integration and Test
Phase:

#### 9.3.1    Test Analysis Report

This report documents each test - unit/module, subsystem integration, system,
user acceptance and security. Appendix C-29 provides a template for the Test
Analysis Report.

#### 9.3.2    Test Analysis Approval Determination

Attached to the test analysis report as a final result of the test reviews
and testing levels above the integration test; briefly summarizes the perceived
readiness for migration of the software. Appendix
C-30 provides a template for the Test Analysis Approval Determination.

#### 9.3.3    Test Problem Report

Document problems encountered during testing; the form is attached to the test
analysis reports. Appendix C-31provides a template for a Test Problem Report.

#### 9.3.4    IT Systems Security Certification & Accreditation

The documents needed to obtain certification and accreditation of an information
system before it becomes operational. They include: System Security Plan; Rules
of Behavior; Configuration Management Plan, Risk Assessment; Security Test &
Evaluation; Contingency Plan; Privacy Impact Assessments; and the certification
and accreditation memorandums. The Systems Security Plan and certification/accreditation
package should be approved prior to implementation and every three years thereafter.

#### 9.4       ISSUES FOR CONSIDERATION

Security controls shall be tested before system implementation to uncover all
design and implementation flaws that would violate security policy. Security
Test and Evaluation (ST&E) involves determining a system’s security
mechanisms adequacy for completeness and correctness, and the degree of consistency
between system documentation and actual implementation. This shall be accomplished
through a variety of assurance methods such as analysis of system design documentation,
inspection of test documentation, and independent execution of function testing
and penetration testing. Results of the ST&E effect security activities
developed earlier in the life cycle such as security risk assessment, sensitive
system security plan, and contingency plan. Each of these activities will be
updated in this phase based on the results of the ST&E. Build on the security
testing recorded in the software development documents, unit testing, integration
testing, and system testing.

#### 9.5       PHASE REVIEW ACTIVITY

Upon completion of all Integration and Test Phase tasks and receipt of resources
for the next phase, the Project Manger, together with the project team should
prepare and present a project status review for the decision maker and project
stakeholders. The review should address: (1) Integration and Test Phase activities
status, (2) planning status for all subsequent life cycle phases (with significant
detail on the next phase, to include the status of pending contract actions),
(3) resource availability status, and (4) acquisition risk assessments of subsequent
life cycle phases given the planned acquisition strategy.