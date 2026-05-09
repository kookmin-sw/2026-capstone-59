---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/appendixc18.htm
---

### APPENDIX C-18

### CONVERSION PLAN

The Conversion Plan describes the strategies involved in converting data from an existing system to
another hardware or software environment. It is appropriate to reexamine the original system's
functional requirements for the condition of the system before conversion to determine if the original
requirements are still valid. An outline of the Conversion Plan is shown below.

**1.0      INTRODUCTION**

This section provides a brief description of introductory material.

**1.1      Purpose
and Scope**

This section describes the purpose and scope of the Conversion Plan. Reference the information
system name and provide identifying information about the system undergoing conversion.

**1.2      Points
of Contact**

This section identifies the System Proponent. Provide the name of the responsible organization and
staff (and alternates, if appropriate) who serve as points of contact for the system conversion. Include
telephone numbers of key staff and organizations.

**1.3      Project
References**

This section provides a bibliography of key project references and deliverables that have been
produced before this point in the project development. These documents may have been produced in a
previous development life cycle that resulted in the initial version of the system undergoing conversion or
may have been produced in the current conversion effort as appropriate.

**1.4      Glossary**

This section contains a glossary of all terms and abbreviations used in the plan. If it is several pages in
length, it may be placed in an appendix.

**2.0      CONVERSION
OVERVIEW**

This section provides an overview of the aspects of the conversion effort, which are discussed in the
subsequent sections.

**2.1      System
Overview**

This section provides an overview of the system undergoing conversion. The general nature or type of
system should be described, including a brief overview of the processes the system is intended to
support. If the system is a database or an information system, also include a general discussion of the
type of data maintained, the operational sources, and the uses of those data.

**2.2      System
Conversion Overview**

This section provides an overview of the planned conversion effort.

> **2.2.1 Conversion Description**
>
> This section provides a description of the system structure and major components.
> If only selected parts of the system will undergo conversion, identify which
> components will and will not be converted.
>
> If the conversion process will be organized into discrete phases, this section
> should identify which components will undergo conversion in each phase. Include
> hardware, software, and data as appropriate. Charts, diagrams, and graphics
> may be included as necessary. Develop and continuously update a milestone
> chart for the conversion process.
>
> **2.2.2 Type of Conversion**
>
> This section describes the type of conversion effort. The software part
> of the conversion effort usually falls into one of the following categories:
>
> **•**Intralanguage
> conversion is a conversion between different versions of the same  
>  computer language or
> different versions of a software system, such as a  
>  database management
> system (DBMS), operating system, or local area  
>  network (LAN) management
> system.  
> **•**Interlanguage
> conversion is the conversion from one computer language to  
>  another or from one
> software system to another.  
> **•**Same compiler
> conversions use the same language and compiler versions.  
>  Typically, these conversions
> are performed to make programs conform to  
>  standards, improve program
> performance, convert to a new system concept,  
>  etc. These conversions
> may require some program redesign and generally  
>  require some reprogramming.
>
> In addition to the three categories of conversions described above, other
> types of conversions may be defined as necessary.
>
> **2.2.3 Conversion Strategy**
>
> This section describes the strategies for conversion of system hardware,
> software, and data.
>
> > **2.2.3.1 Hardware Conversion Strategy**. This section describes
> >   
> >             
> > the strategy to be used for the conversion of system   
> >             
> > hardware, if any. Describe the new (target) hardware   
> >             
> > environment, if appropriate.
> >
> > **2.2.3.2 Software Conversion Strategy**. This section describes
> >   
> >             
> > the conversion strategy to be used for software.
> >
> > **2.2.3.3 Data Conversion Strategy**. This section describes
> > the   
> >             
> > data conversion strategy, data quality assurance, and   
> >             
> > the data conversion controls.
> >
> > **2.2.3.4 Data Conversion Approach**. This section describes
> > the   
> >             
> > specific data preparation requirements and the data that   
> >             
> > must be available for the system conversion. If data will   
> >             
> > be transported from the original system, provide a detailed   
> >             
> > description of the data handling, conversion, and loading   
> >             
> > procedures. If these data will be transported using machine-  
> >             
> > readable media, describe the characteristics of those media.
> >
> > **2.2.3.5 Interfaces**. In the case of a hardware platform  
> >             
> > conversion--such as mainframe to client/server--the   
> >             
> > interfaces to other systems may need reengineering.   
> >             
> > This section describes the affected interfaces and the   
> >             
> > revisions required in each.
> >
> > **2.2.3.6 Data Quality Assurance and Control**. This section
> >   
> >             
> > describes the strategy to be used to ensure data quality   
> >             
> > before and after all data conversions. This section also   
> >             
> > describes the approach to data scrubbing and quality   
> >             
> > assessment of data before they are moved to the new or   
> >             
> > converted system. The strategy and approach may be   
> >             
> > described in a formal transition plan or a document if   
> >             
> > more appropriate.
>
> **2.2.4 Conversion Risk Factors**
>
> This section describes the major risk factors in the conversion effort and
> strategies for their control or reduction. Descriptions of the risk factors
> that could affect the conversion feasibility, the technical performance of
> the converted system, the conversion schedule, or costs should be included.
> In addition, a review should be made to ensure that the current backup and
> recovery procedures are adequate as well as operational.

**2.3      Conversion
Tasks**

This section describes the major tasks associated with the conversion, including planning and
preconversion tasks.

> **2.3.1 Conversion Planning**.
>
> This section describes planning for the conversion effort. If planning and
> related issues have been addressed in other life-cycle documents, reference
> those documents in this section. The following list provides some examples
> of conversion planning issues that could be addressed:
>
> **•**Analysis of the
> workload projected for the target conversion environment to  
>  ensure that the projected
> environment can adequately handle that workload and  
>  meet performance and
> capacity requirements
>
> **•**Projection of
> the growth rate of the data processing needs in the target  
>  environment to ensure
> that the system can handle the projected near-term  
>  growth, and that it
> has the expansion capacity for future needs
>
> **•**Analysis to identify
> missing features in the new (target) hardware and software  
>  environment that were
> supported in the original hardware and software and  
>  used in the original
> system
>
> **•**Development of
> a strategy for recoding, reprogramming, or redesigning the  
>  components of the system
> that used hardware and software features not  
>  supported in the new
> (target) hardware and software environment but used in  
>  the original system
>
> **2.3.2 Preconversion Tasks**
>
> This section describes all tasks that are logically separate from the conversion
> effort itself but that must be completed before the initiation, development,
> or completion of the conversion effort. Examples of such preconversion tasks
> include:

**•**Finalize decisions
regarding the type of conversion to be pursued.

**•**Install changes
to the system hardware, such as a new computer or communications  
 hardware, if necessary.

**•**Implement changes
to the computer operating system or operating system components,  
 such as the installation
of a new LAN operating system or a new windowing system.

**•**Acquire and install
other software for the new environment, such a new DBMS or  
 document imaging system.

> **2.3.3 Major Tasks and Procedures**
>
> This section addresses the major tasks associated with the conversion and
> the procedures associated with those tasks.
>
> > **2.3.3.1 Major Task Name**. Provide a name for each major
> > task.   
> >             
> > Provide a brief description of each major task required for   
> >             
> > the conversion of the system, including the tasks required to   
> >             
> > perform the conversion, preparation of data, and testing of   
> >             
> > the system. If some of these tasks are described in other   
> >             
> > life-cycle documents, reference those documents in this   
> >             
> > section.
> >
> > **2.3.3.2 Procedures**. This section should describe the
> > procedural   
> >             
> > approach for each major task. Provide as much detail as   
> >             
> > necessary to describe these procedures.

**2.4      Conversion
Schedule**

This section provides a schedule of activities to be accomplished during the conversion. Preconversion
tasks and major tasks for all hardware, software, and data conversions described in Section
2.3,Conversion Tasks, should be described here and should show the beginning and end dates of each
task. Charts may be used as appropriate.

**2.5      Security**

If appropriate for the system to be implemented, provide an overview of the system security features
and the security during conversion.

> **2.5.1 System Security Feature**
>
> The description of the system security features, if provided, should contain
> a brief overview and discussion of the security features that will be associated
> with the system when it is converted. Reference other life-cycle documents
> as appropriate. Describe the changes in the security features or performance
> of the system that would result from the conversion.
>
> **2.5.2 Security During Conversion**
>
> This section addresses security issues specifically related to the conversion
> effort.

**3.0      CONVERSION
SUPPORT**

This section describes the support necessary to implement the system. If there are additional support
requirements not covered by the categories shown here, add other subsections as needed.

**3.1      Hardware**

This section lists support equipment, including all hardware to be used for the conversion.

**3.2      Software**

This section lists the software and databases required to support the conversion. It describes all
software tools used to support the conversion effort, including the following types of software tools, if
used:

**•**Automated conversion
tools, such as software translation tools for translating among  
 different computer languages
or translating within software families (such as, between  
 release versions of compilers
and DBMSs)

**•**Automated data
conversion tools for translating among data storage formats associated  
 with the different implementations
(such as, different DBMSs or operating systems)

**•**Quality assurance
and validation software for the data conversion that are automated  
 testing tools

**•**Computer-aided
software engineering (CASE) tools for reverse engineering of the  
 existing application

**•**CASE tools for
capturing system design information and presenting it graphically

**•**Documentation tools
such as cross-reference lists and data attribute generators

**•**Commercial off-the-shelf
software and software written specifically for the conversion  
 effort

**3.3      Facilities**

This section identifies the physical facilities and accommodations required during the conversion period.

**3.4      Materials**

This section lists support materials.

**3.5      Personnel**

This section describes personnel requirements and any known or proposed staffing, if appropriate.
Also describe the training, if any, to be provided for the conversion staff.

> **3.5.1 Personnel Requirements and Staffing**
>
> This section describes the number of personnel, length of time needed, types
> of skills, and skill levels for the staff required during the conversion period.
>
> **3.5.2 Training of Conversion Staff**
>
> This section addresses the training, if any, necessary to prepare the staff
> for converting the system. It should provide a training curriculum, which
> lists the courses to be provided, a course sequence, and a proposed schedule.
> If appropriate, it should identify by job description which courses should
> be attended by particular types of staff. Training for users in the operation
> of the system is not presented in this section, but is normally included in
> the Training Plan.

**Conversion Plan Outline**

**Cover Page  
Table of Contents**

**1.0       Introduction**  
1.1Purpose and Scope  
1.2Points of Contact  
1.3Project References  
1.4Glossary

**2.0       Conversion Overview**  
            2.1System
Overview  
            2.2System
Conversion Overview  
                        2.2.1Conversion
Description  
                        2.2.2Type
of Conversion  
                        2.2.3Conversion
Strategy  
                                       2.2.3.1Hardware
Conversion Strategy  
                                       2.2.3.2Software
Conversion Strategy  
                                       2.2.3.3Data
Conversion Strategy  
                                       2.2.3.4Data
Conversion Approach  
                                       2.2.3.5Interfaces  
                                       2.2.3.6Data
Quality Assurance and Control  
                        2.2.4Conversion
Risk Factors  
            2.3Conversion
Tasks  
                        2.3.1Conversion
Planning  
                        2.3.2Preconversion
Tasks  
                        2.3.3Major
Tasks and Procedures  
                                       2.3.3.1Major
Task Name  
                                       2.3.3.2Procedures  
            2.4Conversion
Schedule  
            2.5Security  
                        2.5.1System
Security Feature  
                        2.5.2Security
During Conversion

**3.0       Conversion Support**  
            3.1Hardware  
            3.2Software  
            3.3Facilities  
            3.4Materials  
            3.5Personnel
  
                        3.5.1Personnel
Requirements and Staffing  
                        3.5.2Training
of Conversion Staff