# bimeta

bimeta is a centralized cyber threat intelligence collections platform which provides a variety of autonomous intelligence collections capabilities to onboarded organizations. bimeta is a modular platform, providing specific capabilities through various plugins. Some examples of bimeta functionality include:

* badpanda - mimicking domain detection capability
* credparser - leaked credentials detection and processing capability
* observatory-collectors - detection of keywords and mentions from various sources (e.g. pastebin, darknet markets, social media etc.)
* expose - detection of accidentaly exposed data from sources including s3 buckets, rsync servers etc.
* pandaX - tactical event-driven communications across the TLP spectrum
* oneoff - variety of one-off research efforts by blueintel leverages bimeta data to relate findings to specific organizations

New capabilities and expanded coverage for existing one is being added continuously.

bimeta functionality is automatic. Once onboarded, you will automatically receive the benefits provided by bimeta capabilities without any additional input or effort by you. bimeta operates on per-organization metadata provided by individual organizations. For example, a list of legitimate domains used by your organization will be used by badpanda and credparser capabilities to provide you with relevant intelligence.

# What does bimeta cost?

bimeta is created and operated by blueintel - the Blue Cross Blue Shield system-wide cyber threat intelligence team. bimeta is provided at no cost to NH-ISAC members.

# Is the metadata from bimeta shared with anyone?

No. Metadata is used exclusively to produce relevant intelligence for your organization, and is not shared with any third party for any reason. It is visible only to you and the blueintel administrative users. Aggregate data may be used to produce broad statistics regarding threat actors targeting healthcare or TTPs used against healthcare entities. Aggregate statistics are anonymized (no attribution to specific organization). 

# Is the metadata in bimeta secure?

bimeta was designed from the ground up with security in mind, and is closely monitored by the team. It features a granular role-based access control and HMAC signed, time-sensitive API requests over SSL channel.  

# Terms of use

By using bimeta system or any of its outputs in any capacity or capability, you release all claims of damages and shall not hold or perceive any liability against the publisher for:  damage, unexpected events or results, decision, or reputation damage, even those resulting from wilful or intentional neglect.  No claims made against this data shall be honored; no assertions have been made about the quality, accuracy, usability, actionability, reputation, merit, or hostility of the returned findings.  Use the returned results at your own risk.  In no event will the publisher be liable for any damages whatsoever arising out of or related to this output, any website or service or output operated by a third party or any information contained in this output or any other medium, including, but not limited to, direct, indirect, incidental, special, consequential or punitive damages, including, but not limited to, lost data, lost revenue, or lost profits, under any theory, whether under a contract, tort (including negligence) or any other theory of liability, even if the publisher is aware of the possibility of such damages.  By using this service, you agree to pursue no legal action in any form for any reason.  You may not use this data to source information about a competing party for leverage or competitive advantage. 

Access to the system may be revoked at any time for any reason at sole discretion of blueintel. 

# What is the license for the code?

bimeta client source code is published under the MIT license.

# How do I get a bimeta account? 

You can request bimeta access from any of the members of the NH-ISAC TIC (threat intelligence commitee) on the weesecrets platform. TIC members include:
* @tr-
* @mike_kp
* @sean_aetna
* @krausedw_hca
* @elise_ucdavis
* @jfellers-chc

Onboarding is a very short process. Once complete you will receive a set of API keys which will allow you to access and manage your orgs data inside bimeta.

# How do I use bimeta?

You will need a bimeta client, which, once supplied with your API keys, will allow you to view and edit metadata for your org, including keywords, configuration files, IP ranges, yara rules and other metadata. bimeta client will also allow you to manage authorized recipients for intelligence produced by bimeta for your org. See the bimeta client documentation for details.

# Can I see the server side code?
No.

# Can I contribute to bimeta?
We applaud your initiative and would love to have your contributions, under these conditions:

* The work you produce must be licensed under MIT license
* You grant perpetual unlimited license for your work to all current and future users of bimeta

In other words - we want your contributions if they are useful to the community. In terms of contributions the following is of interest:

* Collection targets - if there is a forum/blog/service/adversary space marketplace for which you believe coverage would be useful, tell us about it and we'll build it
* Collector modules - if you are a python3 developer interested in contributing code for autonomous collectors, let us know and we'll get you onboarded.

 
