Thialfi
=======

Email to SMS gateway with web interface

High level overview
-------------------

Thialfi is an external "relay" for Postfix that forwards emails to SMS based on the original email recipient. It is designed primarily for _on call_ groups supporting multiple customers.

Let's say we've got 4 engineers: Two Oracle DBAs _David_ and _Darren_ and two System engineers _Simon_ and _Sally_. Thialfi knows the SMS mobile number for each of them.

Quite clearly the DBAs don't want to be called out on System issues and the System engineers don't care about Oracle issues. So we create two groups: _Oracle DBA_ and _Systems support_ and assign the engineers appropriately. One engineer in each group will be chosen as the _on call_ one.

Now we're ready to serve our customers. We can create a couple of email addresses under our _sms.example.com_ domain: cust1-dba@sms.example.com, cust1-sys@, cust2-dba@, cust3-unix@, etc, each of them linked to one of our two support groups.

Couple of notes
---------------

Why not email the support groups directly? It's simple - as the contract grows you may need to reassign the alerts to dedicated groups. In our company we formed a dedicated team for Customer 1 one year into the contract - all it took on the Thialfi side was creating a few new groups and reassigning some engieers. We didn't need to change anything on the Customer side to reroute the alerts to the new contacts.

Needless to say that each engineer may be a member of multiple groups - that can be handy if Sally is on extended leave and Darren has some Sysadmin skills he can go on-call for both _Oracle DBA_ and _Systems support_ groups. 

TODO
----

Thialfi has been in use in our company for quite some time now but we have only implemented the features we needed. There is a couple of things we want to do next:

* _Call escallation_ - the on-call engineer should reply to the SMS to acknowledge it. Failure to do so should trigger an escallation, possibly to all other engineers in the group.
* _Email forwarding_ - the emails received by Thialfi should not only be forwarded to SMS but also forwarded as emails to all (or only _on-call_) engineers. 
* Etc.. let us know what features you'd like to see.

Author
------

Michal Ludvig <mludvig@logix.net.nz> 
for Enterprise IT Ltd, Auckland, New Zealand
see http://enterpriseit.co.nz
