---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/appendixc16.htm
---

### APPENDIX C-16

### INTERFACE CONTROL DOCUMENT

**1.0      SCOPE**

This document provides an outline for use in the specification of requirements
imposed on one or more system, subsystems, Hardware Configuration Items (HCIs)
Computer Software Configuration Items (CSCIs), manual operations, or other system
components to achieve one or more interfaces among these entities. The Interface
Control Document (ICD) created using this template will define one or more interfaces
between two systems.

Overall, an ICD can cover requirements for any number of interfaces to a system.

> |  |
> | --- |
> | **Note:** If there are multiple interfaces, they can be listed in a single ICD or multiple ICDs as needed. For example: <System1> has an interface with <System2> and <System3>, multiple ICDs can be written describing <System1> to <System2>; <System1> to <System2> - or - a single ICD can include both. In this latter case, each section in this template would be repeated to describe each interface.  Sample wording follows:  This Interface Control Document (ICD) specifies the interface(s) between <System1> and <System2>, up through <System N>. Upon formal approval by the IRM Manager responsible for each participating system, this ICD shall be incorporated into the requirements baseline for each system. |

**1.1System Identification**

The following subsections shall contain a full identification of the systems
participating in the interface, the contractors who are developing the systems,
the interfacing entities, and the interfaces to which this document applies,
including, as applicable, identification numbers(s), title(s), abbreviation(s),
version number(s), release number(s), or any lower level version descriptors
used. A separate paragraph should be included for each system that comprises
the interface.

> **1.1.1 System 1**
>
> The information provided in this paragraph should be sufficiently detailed
> so as to definitively identify the systems participating in the interface,
> the contractors developing/maintaining the systems, and the IRM Manager.
>
> **1.1.2 System 2**
>
> The information provided should be similar to that provided in Section 1.1.1

**1.2      Document Overview**

Sample wording follows:

The purpose of the ICD is to specify interface requirements to be met by the
participating systems. It describes the concept of operations for the interface,
defines the message structure and protocols which govern the interchange of
data, and identifies the communication paths along which the data is expected
to flow. The document is organized as:

Section 1.0Scope
of the Document  
Section 2.0Concept
of Operations  
Section 3.0Detailed
Interface Requirements  
Section 4.0Qualification
Methods  
Section 5.0Notes  
Section 6.0Appendices

**1.3      Applicable Documents**

This section shall list the number, title, revision, and date of all documents
referenced or used in the preparation of this document. Document types included
would be standards, Government documents, and other documents. This section
shall also identify the source for all documents not available through DOJ.

**2.0      DESCRIPTION**

Provide a description of the interface between <System1> and <System
2>.

**2.1 System Overview**

This section should illustrate the interface and the data exchanged between
the interfaces. Further information on the functionality and architecture of
the participating systems is given the subsequent sections. In particular, each
system should be briefly summarized with special emphasis on the functionality
related to the interface. The hardware and software components of each system
are also identified.

> **2.1.1 Interface Overview**
>
> Describe the functionality and architecture of the interfacing system as
> it relates to the proposed interface. Briefly summarize the system, placing
> special emphasis on functionality, including identification of key hardware
> and software components, as they relate to the interface. If more than one
> external system is to be part of the interface being defined, then include
> additional sections at this level for each additional external system.

**2.2      Functional Allocation**

Briefly describe what operations are performed on each system involved in the
interface and how the end users will interact with the interface being defined.
If the end user does not interact directly with the interface being defined,
describe the events that trigger the movement of information using the interface
being defined.

**2.3      Data Transfer**

Briefly describe how data will be moved among component systems of the interface
being defined. Include descriptions and diagrams of how connectivity among the
systems will be implemented and of the type of messaging or packaging of data
that will be used to transfer data among the systems. If more than one interface
between these two system is defined by this ICD, each should be identified in
this section. A separate subsection (2.4.1, 2.4.2 etc.) may be included for
each interface.

This ICD template will be primarily used for specification of interfaces that
move information between two systems. Where an interface contains physical requirements
that are imposed upon one or both of the interfacing systems, these physical
requirements should be described in Section 2.4, and defined in Section 3.1.5,
Physical Requirements. If an interface has no physical requirements, then so
state.

**2.4      Transactions**

Briefly describe the types of transactions that will be utilized to move data
among the component systems of the interface being defined. If multiple types
of transactions will be utilized for different portions of the interface, a
separate section may be included for each interface.

**2.5      Security and Integrity**

If the interface defined has security and integrity requirements, briefly describe
how access security will be implemented and how data transmission security will
be implemented for the interface being defined. Include a description of the
transmission medium to be used and whether it is a public or a secure line.
Include a brief description of how data will be protected during transmission
and how data integrity will be guaranteed. Include a description of how the
tow systems can be certain that they are communicating with each other and not
with another system masquerading as one of them. Describe how an individual
on one system can be audited and held accountable for resulting actions on the
other component of the interface. Normally, this section should be an overview
of how security and integrity will be implemented, with Section 3.1.4 contains
a detailed description of specified requirements.

An interface that is completely self-contained, such as movement of data between
systems resident in the same computer room, may not have any security requirements.
In this case, it should be so stated with an explanation of why the interface
has no security and integrity requirements.

**3.0      DETAILED INTERFACE REQUIREMENTS**

This section specifies the requirements for one or more interfaces between
two systems. This includes explicit definitions of the content and format of
every message or file that may pass between the two systems and the conditions
under which each message or file is to be sent. If an interface between the
two systems is t be implemented incrementally, identify the implementation phase
in which each message will be available The structure in paragraph 3.1 should
be replicated for each interface between the two participating systems.

The template contained in Section 3.1 including subsections, provides a generic
approach to interface requirements definition. The specific interface definition
should include only subsections relevant to the interface being defined and
considerable liberty may be taken in the organization of Section 3.1 subsections.
Where types of information not specified in Section 3.1 are required to clearly
define the interface, additional subsections should be added. Other readily
available documents (such as data dictionaries, standards for communication
protocols, and standards for user interfaces) may reference in place of stating
the information here. It may useful to include copies of such documents as attachments
to the ICD. Where possible, the use of tables and figures is encouraged to enhance
the understandability of the interface definition. In defining interface requirements,
clearly state which of the interfacing systems the requirement is being imposed
upon.

> |  |
> | --- |
> | **Note:** For ease of updates and understanding systems with multiple interfaces, this section may be included as an Appendix to the ICD rather than as a section of the ICD. |

**3.1      Interface 1 Requirements**

Briefly summarize the interface. Indicate what data protocol, communication
methods and processing priority are used by the interface. Data protocols used
may include messages and custom ASCII files. Communication methods may include
electronic networks or magnetic media. Indicate processing priority if information
is required to be formatted and communicated as the data is created, as a batch
of data is created by operator action, or in accordance with some periodic schedule.
Requirements for specific messages or files to be delivered within a set interval
of time should be included in Paragraphs 3.1.1 or 3.1.2.

> **3.1.1 Interface Processing Time Requirements**
>
> If information is required to be formatted and communicated as the data
> is created, as a batch of data is created by operator action, or in accordance
> with some periodic schedule, indicate processing priority. Requirements for
> specific messages or files to be delivered to the communication medium within
> a set interval of time should be included in Subsection 3.1.2. State the priority
> that the interfacing entities must assign to the interface. Priority may be
> stated as performance or response time requirements defining how quickly incoming
> traffic or data requests must be processed by the interfacing system to meet
> the requirements of the interface. Considerable latitude should be given in
> defining performance requirements to account for differences in hardware and
> transaction volumes at different installation sites of the interfacing systems.
> Response time requirements, which are impacted by resources and beyond the
> control of the interfacing systems (i.e., communication networks), are beyond
> the scope of an ICD.
>
> **3.1.2 Message (or File) Requirements**
>
> This subsection specifies the requirements for one or more interfaces between
> two systems. This includes explicit definitions of and the conditions under
> which each message is to be sent. The definition, characteristics and attributes
> of the command are described.
>
> > **3.1.2.1 Data Assembly Characteristics**. Use the following
> >   
> >             
> > paragraphs to define the content and format of every message,   
> >             
> > file, or other data element assembly (records, arrays, displays,   
> >              reports,
> > etc.) Specified in Paragraph 3.1.2. In defining interfaces   
> >             
> > where data is moved among systems, define the packaging of   
> >             
> > data to be utilized. The origin, structure, and processing of such  
> >             
> > packets will be dependent on the techniques used to implement   
> >             
> > the interface. Define required characteristics of data element  
> >             
> > assemblies that the interfacing entities must provide, store, send,  
> >             
> > access, receive, etc.

When relevant to the packaging technique used, the following information should
be provided:

**•**Names/identifiers

**•**Project-unique
identifier

**•**Non-technical (natural
language) name

**•**Technical name
(e.g., record or data structure name in code or database)

**•**Abbreviations or
synonymous names

**•**Structure of data
element assembly

**•**Visual and auditory
characteristics of displays and other outputs (such as colors, layouts,  
 fonts, icons and other
display elements, beeps, lights) where relevant

**•**Relationships among
different types of data element assemblies used for the interface

**•**Priority, timing,
frequency, volume, sequencing, and other constraints, such as whether the  
 assembly may be updated
and whether business rules apply

**•**Sources (setting/sending
entities) and recipients (using/receiving entities)

> **3.1.2.2 Field/Element Definition**. Define the characteristics
> of   
>             
> individual data elements that comprise the data packets defined   
>             
> in Section 3.1.2.1. Sections 3.1.2.1 and 3.1.2.2 may be combined   
>             
> into one section in which the data packets and their component   
>             
> data elements are defined in a single table. Data element definitions   
>             
> should include only features relevant to the interface being defined  
>             
> and may include such features as:

**•**Names/identifiers

**•**Project-unique
identifier

**•**Priority, timing,
frequency, volume, sequencing, and other constraints, such as whether the  
 data element may be updated
and whether business rules apply

**•**DOJ standard data
element name

**•**Non-technical (natural-language)
name

**•**Technical name
(e.g. variable or field name in code or database)

**•**Abbreviation or
synonymous names

**•**Data type (alphanumeric,
integer, etc.)

**•**Size and format
(such as length and punctuation of a character string)

**•**Units of measurement
(such as meters, dollars, nanoseconds)

**•**Range or enumeration
of possible values (such as 0-99)

**•**Accuracy (how correct)
and precision (number of significant digits)

**•**Security and privacy
constraints

**•**Sources (setting/sending
entitles) and recipients (using/receiving entities)

> **3.1.3 Communication Methods**
>
> Communication requirements include all aspects of the presentation, session,
> network and data layers of the communication stack to which both systems participating
> in the interface must conform. The following subsections should be included
> in this discussion as appropriate to the interface being defined and may be
> supplemented by additional information as appropriate.

> **3.1.3.1 Interface Initiation**. Define the sequence of
> events by which  
>             
> the connections between the participating systems will be initiated.   
>             
> Include the minimum and maximum number of conceptions that   
>             
> may be supported by the interface. Also include availability   
>             
> requirements for the interface (e.g., 24 hours a day, 7 days a week)   
>             
> that are dependent on the interfacing systems. Availability  
>             
> requirements beyond the control of the interfacing systems,   
>             
> such as network availability, are beyond the scope of an ICD.
>
> **3.1.3.2 Flow Control**. Specify the sequence numbering,
> legality checks,   
>             
> error control and recovery procedures that will be used to manage   
>             
> the interface. Include any acknowledgment (ACK/NAK)   
>             
> messages related to these procedures.

> **3.1.4 Security Requirements**

> Specify the security features that are required to be implemented within
> the message or file structure or in the communications processes. Security
> of the communication methods used (include safety/security/privacy considerations,
> such as encryption, user authentication, compartmentalization, and auditing).
> For interactive interfaces, security features may include identification,
> authentication, encryption and auditing. Simple message broadcast or ASCII
> file transfer interfaces are likely to rely on features provided by communication
> services. Do not specify the requirements for features that are not provided
> by the systems to which the ICD applies. If the interface relies solely on
> physical security or on the security of the networks and firewalls through
> which the systems are connected, so state.

**3.2 Interface 2 Requirements**

When more than one interface between two systems is being defined in a single
ICD, each should be defined separately, including all of the characteristics
described in Section 3.1 for each. There is no limit on the number of unique
interfaces that can be defined in a single Interface Control Document. In general,
all interfaces defined should involve the same two systems.

**4.0      QUALIFICATION METHODS**

This section defines a set of qualification methods to be used to verify that
the requirements for the interfaces defined in Section 3 have been met. Qualification
methods include:

**Demonstration** - The operation of interfacing entities that
relies on observable functional operation not requiring the use of instrumentation,
special test equipment, or subsequent analysis.

**Test** - The operation of interfacing entities using instrumentation
or special test equipment to collect data for later analysis.

**Analysis** - The processing of accumulated data obtained from
other qualification methods. Examples are reduction, interpretation, or extrapolation
of test results.

**Inspection** - The visual examination of interfacing entities,
documentation, etc.

**Special qualification methods** - Any special qualification
methods for the interfacing entities, such as special tools, techniques, procedures,
facilities, and acceptance limits.

**5.0      NOTES**

This section contains any general information that aids in understanding the
document (e.g., background information, glossary).

**6.0      APPENDICES**

Appendices may be used to provide information published separately for convenience
in document maintenance (e.g. , acronyms, abbreviations).

**7.0      APPROVALS**

A page shall be included in the Interface Control Document (ICD) for signature
of those individuals who have agreed to the interface defined in the ICD. At
a minimum, the signatures of the IRM Managers for the two systems that will
be interfacing are required. Sample wording and suggestions or other sign-offs
that may be included follow:

Approvals for the Interface Control Document for Interfaces between System
1 and System 2 , Version Number.

System 1 IRM Manager \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Date\_\_\_\_\_\_\_\_\_\_\_\_\_

Printed name and title \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

System 2 IRM Manager \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Date\_\_\_\_\_\_\_\_\_\_\_\_\_

Printed name and title \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

System 1 Configuration Control Board \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_Date\_\_\_\_\_\_\_\_\_\_\_\_\_

Printed name and title \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

System 2 Configuration Control Board \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_Date\_\_\_\_\_\_\_\_\_\_\_\_\_

Printed name and title \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**8.0      RECORD OF CHANGES**

This record is maintained throughout the life of the document and summarizes
the changes between approved versions of this document. Each new version of
the document submitted for approval receives a sequential venison number. For
instance, the first version of the document will be revision number 1.0. The
old paragraph will designate the paragraph number and title where the information
existed in the previous document if applicable. The revision comments will contain
an explanation of the changes made and any new paragraph number and title if
needed.

**Interface Control Document Outline**

**1.0       SCOPE**  
            1.1System
Identification  
                        1.1.1System  
                        1.1.2System  
            1.2Document
Overview  
            1.3Applicable
Documents

**2.0       CONCEPT OF OPERATIONS**  
            2.1System
Overviews  
                        2.11Interface
Overview  
            2.2Functional
Allocation  
            2.3Data
Transfer  
            2.4Transactions  
            2.5Security
and Integrity

**3.0       DETAILED INTERFACE REQUIREMENTS**  
            3.1Interface
1 Requirements  
                        3.1.1Interface
Processing Time Requirements  
                        3.1.2Message
(or File) Requirements  
                        3.1.3Communication
Methods  
                        3.1.4Security
Requirements  
            3.2Interface
2 Requirements

**4.0       QUALIFICATION METHODS**

**5.0       NOTES**

**6.0       APPENDICES**

**7.0       APPROVALS**

**8.0       RECORD OF CHANGES**