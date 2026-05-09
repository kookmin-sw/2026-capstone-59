---
source: https://www.justice.gov/archive/jmd/irm/lifecycle/appendixc35.htm
---

### APPENDIX C-35

### IN-PROCESS REVIEW REPORT

The purpose of the In-Process Review is to assess the system's performance
and user satisfaction. This review process occurs repeatedly to ensure that
the system is performing cost-effectively and that it continues to meet the
functional needs of the user. The report provides a description of the review
process, its focus, and results. The report also may be used to document management
approvals regarding further enhancements or development of the system under
review. Depending on the timing and focus of the review, it may involve investigation
of system response time, data base capacity, newer technologies available, business
functions, and continued user satisfaction with the system.

**1.0      INTRODUCTION**

This section provides a brief description of introductory material in this
section. Whenever appropriate, other information may be added.

**1.1      Purpose**

Describe the purpose of the In-Process Review in this section. Provide the
name and identifying information about the system reviewed. Provide the timing
of the review to differentiate the In-Process Review Reports created in the
life of a system.

**1.2      Scope**

This section defines the boundaries of the system review. Because this review
may address initial production performance and/or continued user satisfaction
with the system, describe the specific aspects of the review conducted.

**1.3      Project References**

This section provides a bibliography of key project references produced for
this system.

**1.4      Points of Contact**

Identify the System Proponent in this section. Provide the name of the responsible
organization(s) and titles of the staff that conducted the system review.

**1.5      Glossary**

Provide a glossary of all terms and abbreviations used in the report that may
be unfamiliar to the reader. If it is several pages in length, it may be placed
as an appendix.

**2.0      REVIEW PROCESS**

This section provides an overview of the review process and its approach. This
information may differ, depending on if the system review focused on performance,
user satisfaction, or both.

**2.1      System Overview**

In this section, provide a brief general overview of the system reviewed. Examples
of information that would be relevant to this section include the following:

**•**System name  
**•**Date of initial
implementation  
**•**Date of latest modification  
**•**Type of system (such
as, administrative, financial)  
**•**Type of processing
(batch, online, transaction processing)  
**•**Functional requirements
traceability matrix  
**•**System diagram and
narrative description  
**•**Number of computer
programs within the system  
**•**Programming language(s)
and database management systems ( DBMSs) used  
**•**Processing frequency  
**•**Total monthly processing
hours  
**•**System origination
(commercial off-the-shelf or Department of Justice (DOJ)-developed)  
**•**Testing methodology
(test data, live data) for initial system tests  
**•**Testing methodology
(test data, live data) for latest modification  
**•**Availability of
test results  
**•**Date of last system
review, if any  
**•**List of users  
**•**List of issues identified
in last system review

Expand or contract this list as necessary to include all important aspects
of the system that are relevant to the system review. It is not necessary to
provide information on all the items in the list above if they are not relevant
to the review.

**2.2      Functional System Description
and Data Usage**

This section briefly describes what the system does functionally and how the
data are used by the system.

**2.3      Performance Review**

This section should address the review, system response, capacity, correctness,
and other pertinent performance factors.

> **2.3.1 System Response .** To evaluate the responsiveness
> of the system, it may be appropriate to use a system monitor on mainframe-based
> systems. For example, for a transaction processing system, data on the number
> of times each of the system's programs have been executed during a workday,
> week, or month should be collected as appropriate. The monitor may also provide
> data on the average and worst-case delay experienced by the programs and the
> average and worst-case queue lengths. To evaluate the responsiveness of the
> system for LAN-based systems, it may be appropriate to place a monitor or
> protocol analyzer on the LAN.
>
> **2.3.2 System Capacity.** This section examines the ability
> of the system being reviewed to determine if any performance limitations result
> from operating the system near the limits of its capacity. For example, for
> mainframe computer applications using a DBMS, lack of main memory or selection
> of inappropriate buffer sizing during system generation could result in excessive
> disk reads and writes that would slow the applications' response. Similarly,
> a lack of adequate excess hard disk storage could result in large queues at
> disk controllers, substantially slowing the actual, observed average disk
> access time. On LAN-based systems, hosting all applications on a server with
> only one large disk drive and controller could lead to bottlenecks in performance
> for LAN-based applications. In addition, there may be simple system capacity
> considerations, such as in an application hosted on a system that has only
> enough hard disk space available for a limited number of data records.
>
> **2.3.3 System Correctness.** Depending on the purpose of the
> review, it may be appropriate to examine the correctness of the system calculations,
> output, and reports. Presumably, this was done during unit testing and system
> testing. The intent of examining correctness during the Periodic System Review
> is to determine if the system is operating correctly with actual operational
> data inputs because the operational data may differ somewhat from the test
> data. Examples of items to be evaluated include the following:
>
> –            Values
> used for case codes  
> –            Correctness
> of field definitions  
> –            Values
> within data fields  
> –            Combinations
> of data fields  
> –            Calculations  
> –            Missing
> data  
> –            Extraneous
> data  
> –            Amounts  
> –            Units  
> –            Logic
> paths and decisions  
> –            Limits
> or reasonableness checks  
> –            Signs  
> –            Cross-footing
> of quantitative data  
> –            Control
> totals
>
> If the system maintains an audit trail log of hardware and software failures,
> examine this log to determine the failure modes of the system.
>
> **2.3.4 Other.** This section discusses the approach to any
> performance issues that are not easily categorized under the topics listed
> in the previous sections.

**2.4      User Satisfaction Review**

A User Satisfaction Review records the effectiveness, correctness, and ease
of use of the system from the users' perspective. If appropriate, this review
can be used at any point during the information systems life cycle.Summarize the results of the review.

**3.0      FINDINGS**

This section describes the major findings, results, or conclusions of the review.
The intent is to provide management with information for decision making about
the system under review. Rank or prioritize the findings by importance, if applicable.
Otherwise, group them logically, as appropriate. The ranking, prioritizing,
or grouping facilitates making a logical linkage to Sectionon
Recommendations, which provides recommendations regarding the findings. Provide
as much detail as necessary to describe the findings clearly and to support
the recommendations. The following list provides some examples of information
that might be included in this section:

**•**What and where
short-term problem areas exist (such as, missing tapes, misrouted  
 material)  
**•**What and where long-term
problem areas exist (such as, machine capacity problems)  
**•**References to meetings,
interviews, and surveys conducted, with a description of their  
 results or outcomes  
**•**References to supporting
statistics or reports

**4.0      RECOMMENDATIONS**

This section presents the recommendations derived from the findings of the
system review. These recommendations should be phrased as proposals for management
consideration and approval.

Depending on the purpose and scope of the specific system review as defined
by DOJ management, it may be appropriate to provide multiple alternative recommendations
for the findings. If alternative recommendations are provided, then describe
the advantages, disadvantages, costs, tradeoffs, etc. associated with each alternative.Rank, prioritize, or group the recommendations logically, as appropriate.
Relate the ranking, prioritization, or grouping of the recommendations to that
of the findings in Section - Findings.

**5.0      APPROVALS AND APPENDICES**

Reference any management approvals and include any appendices needed to support
the In-Process Review Report in this section.

**5.1      Approval**

Reference or describe the final approval of the In-Process Review Report, which
may come from different levels of authority within the organization, depending
on the size and importance of the items being reviewed. Thus, complete this
section after the initial In-Process Review Report has been presented to management.
After management approval of the report, update this section. Also update this
section to provide an annotation of the recommendations or course of action
selected by management, if appropriate.

**5.2      Appendices**

In this section, reference any additional items necessary to support the system
review from other documents, or add to the appendices, as appropriate.

**In-Process Review Report Outline**

**Cover Page**  
**Table of Contents**

**1.0       Introduction**  
            1.1Purpose  
            1.2Scope  
            1.3Project
References  
            1.4Points
of Contact  
            1.5Glossary

**2.0       Review Process**  
            2.1System
Overview  
            2.2Functional
System Description and Data Usage  
            2.3Performance
Review  
                        2.3.1System
Response  
                        2.3.2System
Capacity  
                        2.3.3System
Correctness  
                        2.3.4Other  
            2.4User
Satisfaction Review

**3.0       Findings**

**4.0       Recommendations**

**5.0       Approvals and Appendices**  
            5.1Approvals  
            5.2Appendices