---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/appendixc15.htm
---

### APPENDIX C-15

### TEST AND EVALUATION MASTER PLAN

**INTRODUCTION**

The Test and Evaluation Master Plan (TEMP) identifies the tasks and activities
needed to be performed so that all aspects of the system are adequately tested
and that the system can be successfully implemented. The TEMP documents the
scope, content, methodology, sequence, management of, and responsibilities for
test activities. The TEMP describes the test activities of the subsystem Integration
Test, the System Test, the User Acceptance Test, and the Security Test in progressively
higher levels of detail as the system is developed.

The TEMP provides guidance for the management of test activities, including
organization, relationships, and responsibilities. The test case procedures
may be included in the TEMP or in a separate document, depending on system size.
The users assist in developing the TEMP, which describes the nature and extent
of tests deemed necessary. This provides a basis for verification of test results
and validation of the system. The validation process ensures that the system
conforms to the functional requirements in the FRD and that other applications
or subsystems are not adversely affected. A test analysis report is developed
at each level of testing to record the results of testing and certify readiness
for system implementation (see the Integration and Test Phase).

Problems, deficiencies, modifications, and refinements identified during testing
or implementation should be tracked under configuration control and tested using
the same test procedures as those described in the TEMP. Specific tests may
need to be added to the plan at that time, and other documentation may need
updating upon implementation. Notification of implemented changes to the initiator
of the change request/problem report and to the users of the system is also
handled as part of the configuration control process.

**1.0      PURPOSE**

In this section, present a clear, concise statement of the purpose for the
project TEMP and identify the application system being tested by name. Include
a summary of the functions of the system and the tests to be performed.

**2.0      BACKGROUND**

This section should provide a brief description of the history and other background
leading up to the system development process. Identify the user organization
and the location where the testing will be performed. Describe any prior testing,
and note results that may affect this testing.

**3.0      SCOPE**

This section describes the projected boundaries of the planned tests. Include
a summary of any constraints imposed on the testing, whether they are because
of a lack of specialized test equipment, or constraints on time or resources.
Describe constraints in greater detail in Section 5.1, Limitations.

**4.0      GLOSSARY**

This section provides a list of all terms and abbreviations used in this document.
If the list is several pages in length, it may be placed as an appendix.

**5.0      LIMITATIONS
AND TRACEABILITY**

This section elaborates on the limitations summarized in Section 3, Scope,
and cross-references the functional requirements and detailed specifications
to the tests that demonstrate or partially demonstrate that capability.

**5.1      Limitations**

This section describes limitations imposed on the testing, whether they are
because of a lack of specialized test equipment, or constraints on time or resources.
Indicate what steps, if any, are being taken to reduce program risk because
of the test limitations(s).

**5.2      Traceability
(Functional Requirements Traceability Matrix)**

This section expands the traceability matrix created in the FRD by including
test activities that address user requirements. The matrix begins with the user
requirements and assists in tracing how the requirements are addressed in subsequent
phases and documents, including the System Design Document and TEMP. The matrix
may be broken up into segments, if appropriate. For example, a separate matrix
of test plan sections that reference particular sections in the system design
document in the Design phase may be provided. The intent is to show that the
test plan covers all functionality, performance, and other requirements associated
with each design element (unit, module, subsystem, and system) in the system
design document.

When a test supports a particular requirement, the relationship should be noted
at their intersection in the matrix. The listed requirements may be explicitly
stated or may be derived or implicit. All explicit requirements must be included.
The granularity of the list should be detailed enough that each requirement
is simple and testable.

**6.0      TEST
PLANS**

This section describes the levels of tests that take place during development:
integration, system security, and user acceptance tests, and the planning that
is needed. The test environment is described in terms of milestones, schedules,
and resources needed to support testing. Include who is responsible for setting
up the test environment, developing test data to be used during the test (if
necessary), developing the tests, and performing the tests.

**6.1      Test
Levels**

This section should include a list of the types of software testing to be performed.
List all applicable levels and enter "Not applicable" if a particular level
of testing does not apply to the project.

> **6.1.1 Subsystem Integration Test**
>
> This section discusses the tests that examine the subsystems make up of
> integrated groupings of software units and modules. This is the first level
> of testing where problem reports are generated; these reports are classified
> by severity, and their resolution is monitored and reported. Subsystem integration
> test results (including the test data sets and outputs produced from the tests)
> may be delivered as part of the final Test Plan, with the integration test
> analysis report or as an appendix.
>
> **6.1.2 System Test**
>
> This section describes the type of testing that determines system compliance
> with standards and satisfaction of functional and technical requirements when
> executed on target hardware using simulated operational data files and prepared
> test data. System documents and training manuals are examined for accuracy,
> validity, completeness, and usability. During this testing period, software
> performance, response time, and ability to operate under stressed conditions
> are tested. External system interfaces are also tested. All findings are recorded
> in a system test analysis report.
>
> **6.1.3 User Acceptance Test**
>
> This section describes the tests performed in a non production environment
> that mirrors the environment in which the system will be fielded. Every system
> feature may be tested for correctness and satisfaction of functional requirements.
> System interoperability, all documentation, system reliability, and the level
> to which the system meets user requirements is evaluated. Performance tests
> may be executed to ensure that screen response time, program run time, operator
> intervention requirements, and reconciliation issues are addressed.
>
> **6.1.4 Security Test**
>
> This section describes the tests performed to determine if the system meets
> all of the security requirements listed in the FRD. Include internal controls
> or application security features mentioned in the context of security testing.
> Security testing is performed in the operational (production) environment
> under the guidance of the security staff.

**6.2      Test
Environment and Schedules**

This section provides a brief description of the inputs, outputs, and functions
of the software being tested.

> **6.2.1 Software Description**
>
> This section lists the software being tested. Provide a description of the
> purpose of the software being tested, and any interfaces to subsystems or
> other components of the system.
>
> **6.2.2 Milestones**
>
> This section lists the milestone events and dates for the testing.
>
> **6.2.3 Organizations and Locations**
>
> This section provides information on the participating organizations and
> the location where the software will be tested .
>
> **6.2.4 Schedule**
>
> This section shows the detailed schedule of dates and events for the testing
> by location. Events should include familiarization, training, test data set
> generation, and collections, as well as the volume and frequency of the input
> for testing.
>
> **6.2.5 Resource Requirements**
>
> This section and associated statements define the resource requirements
> for the testing.
>
> > **6.2.5.1 Equipment**. This section shows the expected period
> > of use,   
> >             
> > types, and quantities of equipment needed.
> >
> > **6.2.5.2 Software**. This section lists other software needed
> > to   
> >             
> > support testing that is not part of the software being tested.   
> >             
> > This should include debugging software and programming   
> >             
> > aids as well as many current programs to be run in parallel   
> >             
> > with the new software to ensure accuracy; any drivers or   
> >             
> > system software to be used in conjunction with the new   
> >             
> > software to ensure compatibility and integration; and any   
> >             
> > software required to operate the equipment and record test   
> >             
> > results.
> >
> > **6.2.5.3 Personnel**. This section lists the number of,
> > skill types of,   
> >             
> > and schedules for personnel - from both the user, database,   
> >             
> > Quality Assurance, security, and development groups -   
> >             
> > who will be involved in the test. Include any special   
> >             
> > requirements, such as multiple-shift operation or key personnel.
>
> **6.2.6 Testing Material**
>
> This section describes the documents needed to perform the tests. It could
> include software, resources, data and other information.
>
> **6.2.7 Test Training**
>
> This section describes or references the plan for providing training in
> the use of the software being tested. Specify the types of training, personnel
> to be trained, and the training staff.
>
> **6.2.8 Test Methods and Evaluation**
>
> This section documents the test methodologies, conditions, test progression
> or sequencing, data recording, constraints, criteria, and data reduction.
>
> > **6.2.8.1 Methodology**. This section describes the general
> >   
> >             
> > methodology or testing strategy for each type of testing   
> >             
> > described in this Test Plan.
> >
> > **6.2.8.2 Conditions**. This section specifies the type of
> > input to be   
> >             
> > used, such as real-time entered test data or canned data for   
> >             
> > batch runs. It describes the volume and frequency of the input,   
> >             
> > such as the number of transactions per second tested, etc.   
> >             
> > Sufficient volumes of test transactions should be used to   
> >             
> > simulate live stress testing and to incorporate a wide range   
> >             
> > of valid and invalid conditions. Data values used should   
> >             
> > simulate live data and also test limited conditions.
> >
> > **6.2.8.3 Test Progression**. This section describes the
> > manner   
> >             
> > in which progression is made from one test to another,   
> >             
> > so the entire cycle is completed.
> >
> > **6.2.8.4 Data Recording**. This section describes the method
> >   
> >             
> > used for recording test results and other information   
> >             
> > about the testing.
> >
> > **6.2.8.5 Constraints**. This section indicates anticipated
> > limitations on   
> >             
> > the test because of test conditions, such as interfaces,  
> >             
> > equipment, personnel, and databases.
> >
> > **6.2.8.6 Criteria**. This section describes the rules to
> > be used to evaluate   
> >             test results,
> > such as range of data values used, combinations of   
> >             input
> > types used, or maximum number or allowable interrupts   
> >             or
> > halts.
> >
> > **6.2.8.7 Data Reduction**. This section describes the techniques
> > that will   
> >             be
> > used for manipulating the test data into a form suitable for   
> >             evaluation
> > - such as manual or automated methods - to allow   
> >             comparison
> > of the results that should be produced to those   
> >             that
> > are produced.

**7.0      TEST
DESCRIPTION**

This section describes each test to be performed. Tests at each level should
include verification of access control and system standards, data security,
functionality, and error processing. As various levels for testing (subsystem
integration, system, user acceptance testing, and security) are completed and
the test results are documented, revisions or increments for the TEMP can be
delivered. The subsections of this section should be repealed for each test
within the project. If there are many tests, place them in an appendix.

**7.1      Test
Name**

This section identifies the test to be performed for the named module, subsystem,
or system and addresses the criteria discussed in the subsequent sections for
each test.

> **7.1.1 Test Description**
>
> Describes the test to be performed. Tests at each level of testing should
> include those designed to verify data security, access control, and system
> standards; system/subsystem/unit functionality; and error processing as required.
>
> **7.1.2 Control**
>
> Describe the test control-such as manual, semiautomatic, or automatic insertion
> of inputs; sequencing of operations; and recording of results.
>
> **7.1.3 Inputs**
>
> Describe the data input commands used during the test. Provide examples
> of input data. At the discretion of the Project Manager, input data listings
> may also be requested in computer readable form for possible future use in
> regression testing.
>
> **7.1.4 Outputs**
>
> Describe the output data expected as a result of the test and any intermediate
> messages or display screens that may be produced.
>
> **7.1.5 Procedures**
>
> Specify the step-by-step procedures to accomplish the test. Include test
> setup, initialization steps, and termination. Also include effectiveness criteria
> or pass criteria for each test procedure.

**Test and Evaluation Master Plan Outline**

**Cover Page  
Table of Contents**

**1.0 PURPOSE**

**2.0 BACKGROUND**

**3.0 SCOPE**

**4.0 GLOSSARY**

**5.0       LIMITATIONS AND TRACEABILITY**  
            5.1Limitations  
            5.2
Traceability (Functional
Requirements Traceability Matrix)

**6.0       TEST PLAN**  
            6.1Test
Levels  
                        6.1.1Subsystem
Integration Test  
                        6.1.2System
Test  
                        6.1.3User
Acceptance Test  
                        6.1.4Security
Test  
            6.2Test
Environment and Schedules  
                        6.2.1Software
Description  
                        6.2.2Milestones  
                        6.2.3Organizations
and Locations  
                        6.2.4Schedule
  
                        6.2.5Resource
Requirements  
                                       6.2.5.1Equipment  
                                       6.2.5.2Software  
                                       6.2.5.3Personnel  
                        6.2.6Testing
Material  
                        6.2.7Test
Training  
                        6.2.8Test
Methods and Evaluation  
                                       6.2.8.1Methodology  
                                       6.2.8.2Conditions  
                                       6.2.8.3Test
Progression  
                                       6.2.8.4Data
Recording  
                                       6.2.8.5Constraints  
                                       6.2.8.6Criteria  
                                       6.2.8.7Data
Reduction

**7.0       TEST DESCRIPTIONS**   
            7.1Test
Name (repeat for each test)  
                        7.1.1Test
Description  
                        7.1.2Control
  
                        7.1.3Inputs  
                        7.1.4Outputs  
                        7.1.5Procedures