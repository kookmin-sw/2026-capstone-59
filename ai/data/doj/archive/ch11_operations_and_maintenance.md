---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/ch11.htm
---

### CHAPTER 11 OPERATIONS AND MAINTENANCE PHASE

*11.0      [OBJECTIVE](#para11)*

*11.1      [TASKS AND ACTIVITIES](#para11.1)**11.1.1
[Identify Systems Operations](#para11.1.1)**11.1.2
[Maintain Data / Software Administration](#para11.1.2)**11.1.3
[Identify Problem and Modification Process](#para11.1.3)**11.1.4
[Maintain System / Software](#para11.1.4)**11.1.5
[Revise Previous Documentation](#para11.1.5)*

*11.2      [ROLES AND RESPONSIBILITIES](#para11.2)*

*11.3      [DELIVERABLES](#para11.3)**11.3.1
[In-Process Review Report](#para11.3.1)**11.3.2
[User Satisfaction Review Report](#para11.3.2)*

*11.4      [ISSUES FOR CONSIDERATION](#para11.4)*

*11.5      [PHASE REVIEW
ACTIVITY](#para11.5)*

#### 11.0     OBJECTIVE

More than half of the life cycle costs are attributed to the operations and
maintenance of systems. In this phase, it is essential that all facets of operations
and maintenance are performed. The system is being used and scrutinized to ensure
that it meets the needs initially stated in the planning phase. Problems are
detected and new needs arise. This may require modification to existing code,
new code to be developed and/or hardware configuration changes. Providing user
support is an ongoing activity. New users will require training and others will
require training as well. The emphasis of this phase will be to ensure that
the users needs are met and the system continues to perform as specified in
the operational environment. Additionally, as operations and maintenance personnel
monitor the current system they may become aware of better ways to improve the
system and therefore make recommendations. Changes will be required to fix problems,
possibly add features and make improvements to the system. This phase will continue
as long as the system is in use.

#### 11.1    TASKS AND ACTIVITIES

#### 11.1.1 Identify Systems Operations

Operations support is an integral part of the day to day operations of a system.
In small systems, all or part of each task may be done by the same person. But
in large systems, each function may be done by separate individuals or even
separate areas. The Operations Manual is developed in previous SDLC phases.
This documents defines tasks, activities and responsible parties and will need
to be updated as changes occur. Systems operations activities and tasks need
to be scheduled, on a recurring basis, to ensure that the production environment
is fully functional and is performing as specified. The following is a checklist
of systems operations key tasks and activities:

- Ensure that systems and networks are running and available during the defined
  hours of Operations;
- Implement non-emergency requests during scheduled Outages, as prescribed
  in the Operations Manual;
- Ensure all processes, manual and automated, are documented in the operating
  procedures. These processes should comply with the system documentation;
- Acquisition and storage of supplies (i.e. paper, toner, tapes, removable
  disk);
- Perform backups (day-to-day protection, contingency);
- Perform the physical security functions including ensuring adequate UPS,
  Personnel have proper security clearances and proper access privileges etc.;
- Ensure contingency planning for disaster recovery is current and tested
  ;
- Ensure users are trained on current processes and new processes;
- Ensure that service level objectives are kept accurate and are monitored;
- Maintain performance measurements, statistics, and system logs. Examples
  of performance measures include volume and frequency of data to be processed
  in each mode, order and type of operations;
- Monitor the performance statistics, report the results and escalate problems
  when they occur.

#### 11.1.2  Maintain Data / Software Administration

Data / Software Administration is needed to ensure that input data and output
data and data bases are correct and continually checked for accuracy and completeness.
This includes insuring that any regularly scheduled jobs are submitted and completed
correctly. Software and data bases should be maintained at (or near) the current
maintenance level. The backup and recovery processes for data bases are normally
different than the day-to-day DASD volume backups. The backup and recovery process
of the data bases should be done as a Data / Software Administration task by
a data administrator. A checklist of Data / Software Administration tasks and
activities are:

- Performing a periodic Verification / Validation of data, correct data related
  problems;
- Performing production control and quality control functions (Job submission,
  checking and corrections);
- Interfacing with other functional areas for Day-to-day checking / corrections;
- Installing, configuring, upgrading and maintaining data base(s). This includes
  updating processes, data flows, and objects (usually shown in diagrams);
- Developing and performing data / data base backup and recovery routines
  for data integrity and recoverability. Ensure documented properly in the Operations
  Manual;
- Developing and maintaining a performance and tuning plan for online process
  and data bases;
- Performing configuration/design audits to ensure software, system, parameter
  configuration are correct.

#### 11.1.3  Identify Problem and Modification Process

One fact of life with any system is that change is inevitable. Users need an
avenue to suggest change and identified problems. A User Satisfaction Review
(Appendix C-37 ) which can include a Customer Satisfaction Survey, can be designed
and distributed to obtain feedback on operational systems to help determine
if the systems are accurate and reliable. Systems administrators and operators
need to be able to make recommendations for upgrade of hardware, architecture
and streamlining processes. For small in-house systems, modification requests
can be handled by an in-house process. For large integrated systems, modification
requests may be addressed in the Requirements document and may take the form
of a change package or a formal Change Implementation Notice (Appendix C-32)
and may require justification and cost benefits analysis for approval by a review
board. The Requirements document for the project may call for a modification
cut-off and rollout of the system as a first version and all subsequent changes
addressed as a new or enhanced version of the system. A request for modifications
to a system may also generate a new project and require a new project initiation
plan.

#### 11.1.4  Maintain System / Software

Daily operations of the system /software may necessitate that maintenance personnel
identify potential modifications needed to ensure that the system continues
to operate as intended and produces quality data. Daily maintenance activities
for the system, takes place to ensure that any previously undetected errors
are fixed. Maintenance personnel may determine that modifications to the system
and databases are needed to resolve errors or performance problems. Also modifications
may be needed to provide new capabilities or to take advantage of hardware upgrades
or new releases of system software and application software used to operate
the system. New capabilities may take the form of routine maintenance or may
constitute enhancements to the system or database as a response to user requests
for new/improved capabilities. New capabilities needs may begin a new problem
modification process described above.

#### 11.1.5  Revise Previous Documentation

At this phase of the SDLC all security activities have been completed. An update
must be made to the System Security plan; an update and test of the contingency
plan should be completed. Continuous vigilance should be given to virus and
intruder detection. The Project Manager must be sure that security operating
procedures are kept updated accordingly. Review and update documentation from
the previous phases. In particular, the Operations Manual, SBD and Contingency
Plan need to be updated and finalized during the Operations and Maintenance
Phase.

#### 11.2    ROLES AND RESPONSIBILITIES

This list briefly outlines some of the roles and responsibilities for key maintenance
personnel. Some roles may be combined or eliminated depending upon the size
of the system to be maintained. Each system will dictate the necessity for the
roles listed below.

- Systems Manager. The Systems Manager develops, documents and execute plans
  and procedures for conducting activities and tasks of the Maintenance Process.
  To provide for an avenue of problem reporting and customer satisfaction, the
  Systems Manager should create and discuss communications instructions with
  the systems customers.
- Technical Support . Personnel which proved technical support to the program.
  This support may involve granting access rights to the program. Setup of workstations
  or terminals to access the system. Maintaining the operating system for both
  server and workstation. Technical support personnel may be involved with issuing
  user ids or login names and passwords. In a Client server environment technical
  support may perform systems scheduled backups and operating system maintenance
  during downtime.
- Operations or Operators (turn on/off systems, start tasks, backup etc).
  For many mainframe systems, technical support for a program is provided by
  an operator. The operator performs scheduled backup, performs maintenance
  during downtime and is responsible to ensure the system is online and available
  for users. Operators may be involved with issuing user ids or login names
  and passwords for the system.
- Customers. The customer needs to be able to share with the systems manager
  the need for improvements or the existence of problems. Some users live with
  a situation or problem because they feel they must. Customers may feel that
  change will be slow or disruptive. Some feel the need to create work-arounds.
  A customer has the responsibility to report problems or make recommendations
  for changes to a system.
- Program Analysts or Programmer. Interprets user requirements, designs and
  writes the code for specialized programs. User changes, improvements, enhancements
  may be discussed in Joint Application Design sessions. Analysts programs for
  errors, debugs the program and tests program design.
- Process Improvement Review Board. A board of individuals may be convened
  to approve recommendations for changes and improvements to the system. This
  group may be chartered. The charter should outline what should be brought
  before the group for consideration and approval. The board may issue a Change
  Directive.
- Users Group or Team. A group of computer users who share knowledge they
  have gained concerning a program or system. They usually meet to exchange
  information, share programs and can provide expert knowledge for a system
  under consideration for change.
- Contracting Officer. The contracting officer is responsible and accountable
  for the procurement activities and signs contract award.
- Data Administrator. Performs tasks which ensure that accurate and valid
  data are entered into the system. Sometimes this person creates the information
  systems database, maintains the databases security and develops plans for
  disaster recovery. The data administrator may be called upon to create queries
  and reports for a variety of user requests. The data administrator responsibilities
  include maintaining the databases data dictionary. The data dictionary provides
  a description of each field in the database, the field characteristics and
  what data is maintained with the field.
- Telecommunications Analyst and Network System Analyst. Plans, installs,
  configures, upgrades and maintains networks as needed. If the system requires
  it, they ensures that external communications and connectivity are available.
- Computer Systems Security Officer (CSSO). The CSSO has a requirement to
  review system change requests, review and in some cases coordinate the Change
  Impact Assessments, participate in the Configuration Control Board process,
  and conduct and report changes that may be made that effect the security posture
  of the system.

#### 11.3    DELIVERABLES

#### 11.3.1  In-Process Review Report

The In-Process Review (IPR) occurs at predetermined milestones usually quarterly,
but at least once a year. The performance measures should be reviewed along
with the health of the system. Performance measures should be measured against
the baseline measures. Ad hoc reviews should be called when deemed necessary
by either party. Document the results of this review in the IPR Report. Appendix
C-35 provides a template for the IPR Report.

#### 11.3.2  User Satisfaction Review Report

User Satisfaction Reviews can be used as a tool to determine the current user
satisfaction with the performance capabilities of an existing application or
initiate a proposal for a new system. This review can be used as input to the
IPR Report. Appendix C-36 provides a template for the User Satisfaction Review
Report.

#### 11.4    ISSUES FOR CONSIDERATION

#### 11.4.1 Documentation

It can not be stressed enough, that proper documentation for the duties performed
by each individual responsible for system maintenance and operation should be
up-to-date. For smooth day to day operations of any system, as well as disaster
recovery, each individuals role, duties and responsibilities should be outlined
in detail. A systems administrators journal or log of changes performed to the
system software or hardware is invaluable in times of emergencies. Operations
manuals, journals or logs should be readily accessible by maintenance personnel.

#### 11.4.2 Guidelines in determining New Development from Maintenance

Changes to the system should meet the following criteria in order for the change
or modification request to be categorized as Maintenance; otherwise it should
be considered as New Development :

- Estimated cost of modification are below maintenance costs
- Proposed changes can be implemented within 1 system year
- Impact to system is minimal or necessary for accuracy of system output

#### 11.4.3  Security Re-certification

Federal IT security policy requires all IT systems to be accredited prior to
being placed into operation and at least every three years thereafter, or prior
to implementation of a significant change.

#### 11.5    PHASE REVIEW ACTIVITY

Review activities occur several times throughout this phase. Each time the
system is reviewed, one of three of the following decisions will be made:

- The system is operating as intended and meeting performance expectations.
- The system is not operating as intended and needs corrections or modifications.
- The users are/are not satisfied with the operation and performance of the
  system.

The In-Process Review shall be performed to evaluate system performance, user
satisfaction with the system, adaptability to changing business needs, and new
technologies that might improve the system. This review is diagnostic in nature
and can trigger a project to re-enter a previous SDLC phase. Any major system
modifications needed after the system has been implemented will follow the SDLC
process from planning through implementation.