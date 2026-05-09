---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/appendixc21.htm
---

### APPENDIX C-21

### MAINTENANCE MANUAL

The Maintenance Manual provides maintenance personnel with the information
necessary to maintain the system effectively. The manual provides the definition
of the software support environment, the roles and responsibilities of maintenance
personnel, and the regular activities essential to the support and maintenance
of program modules, job streams, and database structures.

In addition to the items identified for inclusion in the Maintenance Manual,
additional information may be provided to facilitate the maintenance and modification
of the system. Appendices to document various maintenance procedures, standards,
or other essential information may be added to this document as needed.

**1.0      INTRODUCTION**

This section provides general reference information regarding the Maintenance
Manual. Whenever appropriate, additional information may be added to this section.

**1.1      Purpose**

In this section, describe the purpose of the manual and reference the system
name and identifying information about the system and its programs.

**1.2      Points of Contact**

This section identifies the organization(s) responsible for system development,
maintenance, and use. This section also identifies points of contact (and alternate
if appropriate) for the system within each organization.

**1.3      Project Reference**

This section provides a bibliography of key project references and deliverables
produced during the information system development life cycle. If appropriate,
reference the FRD, Systems Design Document, Test Plan, Test Analysis Report(s),
Operations Manual, User Manual, load module description, source code description,
and job control language (JCL) description.

**1.4      Glossary**

Provide a glossary with definitions of all terms, abbreviations, and acronyms
used in the manual. If the glossary is several pages in length, place it as
an appendix.

**2.0      SYSTEM DESCRIPTION**

The subsequent sections provide an overview of the system to be maintained.

**2.1      System Application**

This section provides a brief description of the purpose of the system, the
functions it performs, and the business processes that the system is intended
to support. If the system is a database or an information system, include a
general description of the type of data maintained, and the operational sources
and uses of those data.

**2.2      System Organization**

In this section, provide a brief description of the system structure, major
system components, and the functions of each major system component. Include
charts, diagrams, and graphics as necessary.

**2.3      Security and
the Privacy Act**

This section provides an overview of the system's security controls and the
need for security and protection of sensitive data. For example, include information
regarding procedures to log on/off of the system, provisions for the use of
special passwords, access verification, and access statuses as appropriate.
If the system handles sensitive or Privacy Act information, include information
regarding labeling system outputs as sensitive, or Privacy Act-related. In addition,
if the system is covered by the Privacy Act, include a warning of the Privacy
Act's civil and criminal penalties concerning the unauthorized use and disclosure
of system data.

**2.4      System Requirements
Cross-Reference**

This section contains an exhibit that cross-references the detailed system
requirements with the system design document and test plan. This document, also
referred to as a traceability matrix in other documents, assists maintenance
personnel by tracing how the user requirements developed in the FRD are met
in other products of the life cycle. Because this information is provided in
the system design document, it may be appropriate to repeat or enhance that
information in this section.

**3.0      SUPPORT ENVIRONMENT**

This section describes the operating and support environment for the system
and program(s). Include a discussion of the equipment, support software, database
characteristics, and personnel requirements for supporting maintenance of the
system and its programs.

**3.1      Equipment Environment**

This section describes the equipment support environment, including the development,
maintenance, and target host computer environments. Describe telecommunications
and facility requirements, if any.

> **3.1.1 Computer Hardware**
>
> This section discusses the computer configuration on which the software
> is hosted and its general characteristics. The section should also identify
> the specific computer equipment required to support software maintenance if
> that equipment differs from the host computer. For example, if software development
> and maintenance are performed on a platform that differs from the target host
> environment, describe both environments. Describe any miscellaneous computer
> equipment required in this section, such as hardware probe boards that perform
> hardware-based monitoring and debugging of software. Include any telecommunications
> equipment.
>
> **3.1.2 Facilities**
>
> This section describes the special facility requirements, if any, for system
> and program maintenance and includes any telecommunications facilities required
> to test the software.

**3.2      Support Software**

This section lists all support software--such as operating systems, transaction
processing systems, and database management systems (DBMSs)--as well as software
used for the maintenance and testing of the system. Include the appropriate
version or release numbers, along with their documentation references, with
the support softwarelists.

**3.3      Database Characteristics**

This section contains an overview of the nature and content of each database
used by the system. Reference other documents for a detailed description, including
the system design document as appropriate.

**3.4      Personnel**

This section describes the special skills required for the maintenance personnel.
These skills may include knowledge of specific versions of operating systems,
transaction processing systems, high-level languages, screen and display generators,
DBMSs, testing tools, and computer-aided system engineering tools.

**4.0      SYSTEM MAINTENANCE
PROCEDURES**

This section contains information on the procedures necessary for programmers
to maintain the software.

**4.1      Conventions**

This section describes all rules, schemes, and conventions used within the
system. Examples of this type of information include the following:

**•**System-wide labeling,
tagging, and naming conventions for programs, units, modules,  
 procedures, routines,
records, files, and data element fields  
**•**Procedures and standards
for charts and listings  
**•**Standards for including
comments in programs to annotate maintenance modifications and  
 changes  
**•**Abbreviations and
symbols used in charts, listings, and comments sections of programs

If the conventions follow standard programming practices and a standards document,
that document may be referenced, provided that it is available to the maintenance
team.

**4.2      Verification
Procedures**

This section includes requirements and procedures necessary to check the performance
of the system following modification or maintenance of the system's software
components. Address the verification of the system-wide correctness and performance.

Present, in detail, system-wide testing procedures. Reference the original
development test plan if the testing replicates development testing. Describe
the types and source(s) of test data in detail.

**4.3      Error Conditions**

This section describes all system-wide error conditions that may be encountered
within the system, including an explanation of the source(s) of each error and
recommended methods to correct each error.

**4.4      Maintenance
Software**

This section references any special maintenance software and its supporting
documentation used to maintain the system.

**4.5      Maintenance
Procedure**

This section describes step-by-step, system-wide maintenance procedures, such
as procedures for setting up and sequencing inputs for testing. In addition,
present standards for documenting modifications to the system.

**5.0      SOFTWARE UNIT
MAINTENANCE PROCEDURES**

For each software unit within the system, provide the information requested.
If the information is identical for each of the software units, it is not necessary
to repeat it for each software unit. If the information in any of the areas
discussed below is identical to information provided in Section 4, System Maintenance
Procedures, for the system maintenance procedures, then reference that area.
This section should contain the following:

**•**Unit Name And Identification--Provide
the name or identification of each software unit  
 that is a component of
the system. Repeat the following information for each unit name.

**•**Description--Provide
a brief narrative description of the software unit. Reference other  
 sections within the life
cycle that contains more detailed descriptive material.

**•**Requirements Cross-Reference--Include
the detailed user requirements satisfied by this  
 particular software unit.
It may be a matrix that traces the system requirements from the  
 FRD through the system
design document and test plan for the specific software units.  
 Other life cycle documentation
may be referenced as appropriate.

**•**Conventions--Describe
all rules, schemes, and conventions used within the program. If  
 this information is program-specific,
provide that information here. If the conventions are  
 all system-wide, discuss
them Section 4. If the conventions follow standard programming  
 practices and a standards
document, that document may be referenced here.

**•**Verification Procedures--Include
the requirements and procedures necessary to check  
 the performance of the
program following modification or maintenance and addresses the  
 verification of program
correctness, performance, and detailed testing procedures. If the  
 testing replicates development
testing, it may be appropriate to reference the original  
 development test plan.

**•**Error Conditions--Describe
all program-specific error conditions that may be  
 encountered provide an
explanation of the source(s) of each error, and recommend  
 methods to correct each
error. If these error conditions are the same as the system-wide  
 error conditions described
in Section 4.3, Error Conditions, that section may be  
 referenced here.

Listings--Provide a reference to the location of the program listings.

**Maintenance Manual Outline**

**Cover Page  
Table of Contents**

**1.0       INTRODUCTION**  
            1.1Purpose  
            1.2Points
of Contact  
            1.3Project
References  
            1.4Glossary

**2.0       SYSTEM DESCRIPTION**   
            2.1System
Application  
            2.2System
Organization  
            2.3Security
and the Privacy Act  
            2.4System
Requirements Cross-Reference

**3.0       SUPPORT ENVIRONMENT**   
            3.1Equipment
Environment  
            3.2Support
Software  
            3.3Database
Characteristics  
            3.4Personnel

**4.0       SYSTEM MAINTENANCE PROCEDURES**
  
            4.1Conventions  
            4.2Verification
Procedures  
            4.3Error
Conditions  
            4.4Maintenance
Software  
            4.5Maintenance
Procedures

**5.0       SOFTWARE UNIT MAINTENANCE
PROCEDURES**