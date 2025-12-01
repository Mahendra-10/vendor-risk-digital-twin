[00:00] Speaker A: I, I've been in cyber security for about 20 years. I was in the army, retired out of the
Army. I retired as a cyber warfare officer, both doing defensive cyber and offensive cyber for the last
five years. Been in industry, worked for a small business for about three years running a huge cyber
portfolio. And I've been with CGI for the last two and a half years or so. The first year running our, our
penetration testers and red teamers and this last year pretty much dedicated to the, to the FAA project
that Mahindra is getting to enjoy. So. Yeah, so definitely a offensive minded person. But I, I know a lot
about the defense and policy because right now I'm making sure this whole FAA thing is fully compliant
to federal regulations and standards. So. Yeah. So yeah. How y' all doing?
[00:59] Speaker B: We're doing good. And thank you, Jay Z, for your introduction. Like I mentioned to
you guys, Jizzy is a team lead at my project, so he has a huge responsibility and a lot of things to
consider. And FFA is a huge project where we have to, you know, take a lot of regulation, rules,
evidence collection, collection, compliance into account. And that's something I'm learning a lot into
account. So I think I know I told you briefly about the project over the chat.
[01:29] Speaker A: It's really exciting.
[01:31] Speaker C: Yeah.
[01:31] Speaker B: So we're basically trying to create a cloud framework or a. Just a. Because we're
not really trying to build a product in a full fledged product. We're just offering a potential solution to
solve a vendor risk problem, you know, and before I go into our vision or our product details, I would
like to know, how does CGI approach vendor risk management and supply risk in cloud, native or digital
environment? How are, how is CGI doing that currently?
[02:04] Speaker A: So we follow the NIST framework for the most part. So the 800, the special
publication 800 series really covers risk and risk management. So because I'm in the federal sector.
We're in the federal sector, we were beholden to US federal laws. So things like the federal Information
Protection standards, fips, of course, nist, the National Institute Standard Technology already
mentioned. We do. So yeah. How do we do. So what was the question?
[02:44] Speaker B: Oh, it was just like how does CZI currently approach vendor risk management?
[02:49] Speaker A: Oh, so, so you're talking about us for our vendors or us as the vendor?
[02:54] Speaker B: I think, I guess if a CZI wants to bring third party tool to our project, how would you
guys know that? Like, okay, this, this vendor is good. Or like how or whether you guys need a
framework to make sure. Okay, it's Good to bring into our work or bring to cgi. Just, just general project.
[03:11] Speaker A: Yeah. So, so we carefully vet any, any software or any supplier really supplier of
anything. A big thing is we look for them to be US owned. If they're not US owned, then there's some
things we have to do with trade compliance to make sure that whatever it is, if it's a piece of software,
for example, we got a. You all know what WSUS is. You know, Windows is automatic updating system.
So there's some, some in Linux there's really no such thing like that. But we have a huge Linux. Sorry,
we have a huge Linux backbone in our servers. And so in order to ensure that we push patches and
everything consistently, we bought from a Polish company software that kind of does what WSUS does,
except for Linux. So before we could do that, first we had to do the trade compliance, make sure they
weren't on any terrorist watch list or any embargo list or whatever. So once the legal stuff was checked,
we actually got the code and then we put it in a sandbox, a Linux sandbox, some machines that needed
patches and stuff, things that the software is supposed to do, but it was a sandbox. So we ran the
software and saw if it was calling out, calling home. Now obviously it's an update software, so it's going
to where the dependencies live and getting the updates. But was it also sending any side channel
information about our, our infrastructure or sending anything to the company that wrote it or some other
government? So we watched every single packet what it was, analyzed it and ensured that it was just
doing what it was supposed to do, nothing more. And that was, that was about a three week test for
things like in the faa we've got a, we've got a Slovenian company that's working with us. So that was a
big concern for our client at faa, but they're the only company in the world that does this one airport
airfield tracking software, the only one whole world. So we, what we do with them is they give us their
code and we do a static test of it, compile it and then we test it again in a sandbox. So the static test is a
piece of software that goes through it, builds the code line by line and sees if there's anything malicious
happening. I'm running line 1 million. Does it cause a conflict previously, if so, or a vulnerability to open
up? So we meticulously look at it line by line, then compile it, run it in a sandbox, look for things like I
was talking about Callbacks, extra functionalities that shouldn't be accessing data that it doesn't need.
Yeah. So it's kind of a holistic process. And then we monitor it with our security operations center along
with all the other software. But the foreign made, foreign owned software we keep a special eye on. We
have special rules that make sure that we do check up on them and that we don't suppress errors too
much. So, yeah, there's, there's some risk there that US Companies could be malicious. Right, right.
We're just basing it on nationality. Right. So we watch all of our vendors in a similar way when we're
bringing in software that's going to do something sensitive. Financial, personal information, health,
sensitive information. We do a lot of stuff with the US Department of Health. We run the whole Medicaid
program. We run the program that, that issues US visas and passports. So we're handling all kinds of
sensitive information. We do the accounting for 13 government agencies. All of their books, we do
them. And the writing of checks and all of that, that's cgi. So anytime we're bringing anything into our
ecosystem, whether we write it ourselves or most especially if we're getting it from somewhere else, a
new dependency, an update, whatever, we thoroughly test it in a, in a sandbox. Almost a digital twin of
the real world environment. As close as we can get just to make sure nothing sneaky is going to
happen and nothing bad happens. You know, like the crowdstrike thing. Their patch last summer
conflicted with Microsoft's patch the same day. The banking world, the airline world were all shut down
until both companies issued hotfixes. So we don't want that to happen either. So we look for not just the
cyber security risk, but also the operational risk. And that all happens after the legal risk is done.
Another part of the acquisition cycle is our people who do these contracts with these software vendors,
they do a background check on the companies that are vending the software. Right. They have any
pending legal action. What does the Better Business Bureau say about them? And there's some other
databases that we check in. Oh, gosh, yeah. Broad Street. Yeah. Anyways, there's a bunch of different
ways we look at a company to see if they're legit. And, and we should do business with them. And that
includes when we're working on winning a federal contract, when we're writing to the US Government,
hey, we can do this. We bring in a partner company, we vet them too. So, yeah, and I'm sure, like
Hydra, when you got hired, you probably had to do the background check. Right. You got a fat
envelope in the mail afterwards, like, oh yeah, you did go to high school here. Yeah. You really do have
this.
[09:03] Speaker B: Give me a whole seven years of my background.
[09:06] Speaker A: Yep. So they do a background show. So we do background checks on all of our
employees too to make sure that the degrees they're claiming. I actually went to those colleges. I
actually got this degree. There's no criminal record, there's no, you know, none of that stuff. So we, we
do a lot, a lot of vetting on different levels. Does that answer your questions, I hope?
[09:30] Speaker B: Yeah, I think that answers the question. So basically you guys have to make sure
like you know, they missed. I'm assuming you also have to make sure they're meeting all the NIST
security controls there. Like you know, sort of if you bring some tools that are fedramp high. And so
yeah, there's a lot of legal procedure that goes into it and I'm assuming some of that is very manual.
Like you have to sort of like check, it's like a checklist. And do they meet this, this or not? They say
okay.
[09:54] Speaker A: Especially on the contract, the legality side, the trade compliance, the contracts,
you know, procurements, that's, that's a lot of manual work and sometimes they get tricked. Yeah. And
on the cyber side, yeah, we make sure that no vulnerabilities are created that could be exploited and
the business function of the system is still operational and functional. Right. Because perfect security is.
Nobody's allowed on the system. So we don't, we can't have perfect security and block all the users. So
we make sure that whatever it is we apply, whatever update we do, we don't pull a crowd, strike and
break everything that makes sense or anything.
[10:39] Speaker B: Are you aware of any tools or tools that the CCI uses currently? Because I know
like for third party risk there is tool like Bitsight. I don't know if you heard of it, bit side OneTrust. Does
CGI utilize any of those? I don't know if it's like project is like based on the project. But does CGI use
any of those? Third party risk tool?
[11:04] Speaker A: Yeah, yeah. So we use the tenable suite nasis for a lot of the software. In our
particular project we're using the Google suite of tools, Google Security Operations and Google
Security Command center. We've got CrowdStrike deployed all over on everything. So. So yeah, so
there's lots of ways that we, we manage risk and assess it as well. We have Cyber Threat, we've got
lots of feeds into cyber threat intel sources. So not just looking at, is there a common vulnerability
exploit, a CVE out there. We're also looking at the open source intelligence. Like what, what bad guys
are out there that would want to attack, say, one of our federal accounting programs? Like who wants
to shut down the comptroller of the US Currency, you know? Right. So shut down this agency. You
know, it in a great way. The best way to stop something from happening is to cut off the money. So we
look for threats like that. Who would want to do something, you know, or we've come up with something
proprietary. We don't want to lose it. Who would want to steal this trade secret from us, you know,
something like that, or from our, our client. If we're working a DOD program, we know something about
weapon systems, we definitely don't want that going into the wild. Although it turns out if the Chinese
steal the plan for the F35 and then they build it, it doesn't work, which is really funny.
[12:38] Speaker B: But. Right. So, I mean, I know that one of the problem that we talked about with
this traditional third party risk management is obviously there's a lot of manual work that goes into it.
You need to be more careful. Any other problem that you can think of like that you think is there's a
problem when you're doing this vendor risk management, you know, like humans can easily miss it.
Yeah. What are other problems or challenges that you see in this?
[13:07] Speaker A: Yeah, so, so you're relying on the information that's out there. So new companies
don't have any information or say a company does something bad, so they rebrand. Now you don't
know that. You know, this company name is associated with this new company name. Yeah. So there,
there's, there's really just the info mapping information is, is really hard or a person, it happens all the
time. People change their names. When women in the US get married, they change the last name.
Right. So I mean, it's a normal thing when people immigrate. They, they change their name to, to the,
the local. So it can be written in a local language. Right. So it's, how do I know that you know, this
person who came over from Canada? You know, I, I don't know. So it's, it's a big problem of having
good data, having not stale data and reliable data. So it's, it's like doing a credit, credit lookup on
someone. Right. It's only as good as the information that's in there. Somebody's had their identity
stolen. There's Going to be stuff in there that's negative. Or if somebody stole an identity and went
bankrupt with that fake identity, it's not on their actual identity, so they still look clean. So that, that can
be, you know, trickery can, can be a problem. We see that a lot when we're doing business deals. A
company will say that they can do something or they have done something and they can't when it
comes delivery time. And that's a big problem because we just got hired to do this thing and we
promise that our partner can do it.
[14:49] Speaker B: Yeah, that, that makes sense. And I'm assuming sometimes, I mean, you have to,
they might be able to provide you with some documentation as a proof to saying, hey, we have
delivered this on time, so you can trust us. But like you said, it's always hard to map out everything.
Yeah, you don't know everything. You just have to go with what they say.
[15:09] Speaker A: It's just like when you applied for the job, right. They said they want your transcript.
Okay. But they wouldn't take the one that you had on your hard drive. You had to put into some agency
that did a special, you know, out of band email to same thing when you applied for, for college. Right.
You know, you couldn't just provide these official documents. You'd have some outside source who
was verified, you know, impartial. Or at least when you do graduate, you know, you're always going to
have to release your transcripts, you know, tell the school to send it to this place and then they'll look at
it, the, the official transcripts. So, so being able to trust the information that somebody gives us, you
know, there's the implicit trust. I mean, I have to trust them to trust the proof that they're handing me. So
having a, a way to find impartial outside sources to validate information or to find new information is, is
really helpful. Again, the credit report is, is a famous example of that. Right, Right. Go to buy a new car,
you can tell the dealer that you got all the responsibility in the world, but they're going to pull that credit
report and they're going to see what the real story is, how much debt you got, how well you pay your
debts, and so on. So having something like that and there's systems out there, but again, it's only as
good as the information they get. And my company does something bad, so I shut it down and I just
stand up. A new company, why not? Same services. Yeah, that happens sometimes, not often.
[16:49] Speaker B: That makes sense. Yeah. So coming to. Now, coming to Our product or our vision.
The framework that we are working on is supposed to sort of accelerate the things that you were
saying, like especially the manual check. So let's say I have an organization, I want to bring a third
party tool, third party vendor. How do I know, you know if it's trustful? Does it meet all the compliance
check, does it meet all the NIST frameworks or whatever? So, so ours is basically like, okay, so you
have this tool and once you, before you even integrate it, let's say you're trying to integrate a stripe
payment to your organization so that it will help you simulate, okay, how would this no.1 impact your
operations overall, but also your financial results and compliance posture. So like you don't even need
to integrate it in the system. You're just able to ask this framework be like, hey, how would this impact?
And it will give you a whole detailed report on how this is going to impact. And also let's say you already
have a third party tool integrated in your system and you want to test, okay, what would happen if this
goes down? You know, AWS it had an outtase and many, many companies weren't prepared for it. So
our system says, hey, you want to know how this would impact you? Like you know, in terms of code? I
mean nowadays, yeah, something like if something happens, like obviously there will be some changes
to your code, but if you also want to know how would it change your business processes, you know, full
detailed report, how much finance like compliance, what compliance would go down? You just
simulation. Okay, help me simulate how would this go down and it will give you a full detailed report.
And this is based on like what we're talking about. This is more like advanced zrc. You know, I know
that the tools that we have aren't capable of this and this is pretty advanced, but what do you just think
of the idea that you're able to simulate things, you know, before. That way you can, that way you can,
you can avoid bad businesses, you know, bad vendors and. Yeah. So what do you think about that
whole idea overall?
[18:50] Speaker A: Yeah, that's great. So that's kind of what I'm doing my dissertation on actually. I'm
looking at critical infrastructure that's production only. You know, there's only the real world
instantiation. So whenever you push a patch, you're taking a risk of breaking something operationally.
But if you don't take that risk, you're leaving a vulnerability open that can be exploited and impact
operations. Right. So it's constantly a balancing act. So what you're proposing is similar to what I was.
What I'm proposing is make a digital twin of the real world system. So stand up all of the similar ports,
protocols, services, all the things that it does, all the interconnections in a cloud environment. So
basically creating a CICD process.
[19:38] Speaker C: Where.
[19:38] Speaker A: You'Ve got multiple environments where you develop, test, but you take this real
world digital twin, put it in your development environment, and you mess with it. Okay, I'm going to push
this patch. What happens? Well, it doesn't break anything. Great. So that's, that's safe or it does break
something. Well, why did it break it? We need this patch because the security vulnerability is really bad.
But we don't want to stop the, the power grid from putting out power. So how do we balance that risk
and, and doing that in a real world only? That's, I mean, that's risky. That's why our infrastructure is
generally unpatched, because the risk to the infrastructure itself by patching. So being able to do what
you're suggesting, simulate, okay, I'm going to do this thing or hey, this service is breaks, or it turns out
that this dependency, this is completely compromised. You know the, the, the Chinese got into their git
lab, you know that recently happened, right, with Cisco. So, and, and F5. So yeah, it can, there's a
supply chain completely compromised from the very beginning. So. All right, if I turn off all my Cisco
devices, what's going to happen to my business functions here, all the routers, all the different
switches.
[21:03] Speaker B: Is my camera frozen?
[21:05] Speaker A: Yeah, you're frozen. I thought I was frozen. So, yeah.
[21:09] Speaker B: We can use to.
[21:10] Speaker A: Okay, you're moving again. Yep.
[21:12] Speaker B: Okay, so, so that makes sense. Go ahead, continue.
[21:16] Speaker A: Yeah, so I'm thinking along the same lines you guys are. It's, you know, take the
risk away from upgrading or updating or whatever it is, changing the system. Right. I want to replace
this old legacy part because it's old and not as efficient. But if I pull it out and put this new thing in there,
is it going to break everything else that's old and legacy and the way it's set up? Well, let's test that out.
Digital twins. And you'll see and the Navy's doing this right now with their ships and aircraft. They've got
every little component digitally twins. When they get a new, when they get a new circuit board from,
from the vendor, they do, they get a dish, they make a digital twin of it. Every little bit of it. So now I've
got a missile system. I've Got to replace this card on it, put this new card in there and then they can
actually simulate if anything's going to change. And they've, they've caught some malicious stuff there,
you know and they, they've been able to detect how it would spread. So, so yeah, so this is, this is a
very important project you guys are working on. A very interesting to the community and what it is, is
what you're suggesting is called Industry 5.0. So the fifth industrial revolution, which is an AI driven
model and simulation. Are you familiar with Industry 5.0?
[22:47] Speaker B: The one I mean I actually was inspired for this research. I was inspired by this
article that I found online which was saying that the thing that I would describe is based on GRC 6.0
and I think this concept is not that popular. But I hear you in a sense that next phase will definitely be
more predictive analytics. You can simulate more things, more advanced.
[23:13] Speaker A: We have currently simulated before you do it in the real world. That's basically
what you're suggesting and that's a great idea. Or simulate your disaster recovery. Like you said, AWS
broke. Well, how's my bank going to function now? Do we have a backup? Is there any way, you know,
is it worth the money to go multi cloud to pay for AWS and Azure, you know, just to have that backup? If
one cloud goes down, do we lose more money in a three day outage than it would cost for, you know,
two years of having two clouds doing the exact same thing? You know, they can actually do a real cost
benefit analysis and see the impact.
[23:54] Speaker B: Oh that's, that's a good example. I'm writing that down that you mentioned,
especially making business decision. You know, some people might say like after the AWS outage, let's
go multi cloud. But on the. So like the system that we're presenting, suggesting will actually help you
simulate that. Okay, is it worth multi cloud for one time that AWS happened? Hopefully it doesn't
happen more but just give you better understanding. And also I think this system can really help in a
supply chain type of attack where the company might not be attacked itself. But you know, you have
this third party, third party long down on the chain getting attacked and now you have the ripple effect
attacking. You know, you can simulate that.
[24:30] Speaker A: No, whole supply chain. Yeah, it, it Travels up. Right. F5 had their code base
owned by the Chinese. All right, great. So what does that mean? Any F5 code since that that breach
could be compromised.
[24:45] Speaker B: Right.
[24:45] Speaker A: And it's going to check out as being good because you know, it's authentic and it's
from the actual repositories that F5 really uses. Every day you slip a little code in there, but it still gets
the Microsoft Cryptologic you'll seal of approval. So yeah, so things like that, but also for robustness
testing or cost benefit analysis like do we do multi cloud or do we need to buy another server? What
happens if our demand for our small business goes up a little bit more? You know, how much, how
much can this, this old Dell 920 handle? Right? Yeah, so, so yeah, so it's generalizable. Your, your
solution as well. So that's why I'm throwing all these different concepts out. Because once you can twin
something, once you've. The hardest part is figuring out how to twin operational technology. You know,
the industrial control systems, Internet of things, you know, the computer stuff that interacts with the
physical world, actuators, sensors. Because they're all running on proprietary operating systems,
they're called binaries. They've got their own proprietary logic and signaling and timing. It's not like, you
know, your laptop, my laptop, your guys's laptop, they all do generally the same thing. Some go faster
than others, some can hold more memory than others. But in the end they're all running the same type
of operating system. They're all running Zoom right now. You can't take a Siemens sensor and a
Honeywell sensor and program them the same way. They have to be programmed completely different.
And so that's, that's the hardest part of. Because then you got to model that. How do you model that
this thing signaling different than this other thing and they're all talking to one computer. The human
interface device. Hid. Yeah. So, yeah, so that, that's, that's, that's where I'm at with my research. So
that's why I'm really excited when you said this, Mahindra, I was like, man, this is exactly what I'm
looking at. Yes. And I did my proposal defense Yesterday and the four PhDs on the line were like, wow,
we really need this. We got to write some papers. So if you make progress here, write some academic
papers, get it out there, that's going to really help you with jobs and grad school. So just saying.
[27:15] Speaker B: Let me also share my screen so I can show you something. Just quickly.
[27:21] Speaker C: Hi John. I also had one question I want to ask you a little bit about the digital twin
work stuff. One of the question has, obviously there's a lot of upside and like opportunity, you know,
with this industry 5.0, if it was to happen. One thing I wanted to ask you was just on maybe some of the,
the risks or the assumptions that organizations, federal agencies have to take into account if you were
to implement something like this. So just wanted to hear your thoughts on some of those risks or things
that we'd have to change in our process if we want to let AI have more control over teams and systems.
[27:57] Speaker A: Right? Yeah. So the trust, the machine trust. I just talked in San Diego about this
trust at machine speed. Got all these AIs that can do lots of good things. So one, it's the fidelity, you
know, for a digital twin. How close is your twin to the actual real world thing? You know, you've got a
digital twin of a laptop, but does it have all the little components and all the things that are inside a
laptop or is it just a virtual machine running an operating system? A generic virtual machine. So that's
one of the risks is when you abstract to a digital twin, you can get bare functionality, but not necessarily
all functionality. You have to be really, really precise. You have to go down to the gate level basically on
anything that you're twinning. Otherwise you take the risk of not having an accurate response to
whatever it is you're putting your inputs. As far as trust of AI, again, that goes to the fidelity of the
training data. What you know, how well has it been trained? Ultimately, what the Navy says and what,
what a lot of people say is, yeah, it's great as a decision aid, but not as a decision tool. Right. So it can
get into your, your UDA loop, your, your observe, orient, decide and act loop. It can speed that up, it
can help with your observations and, and your decisions in that can present you with decisions. But
making that final decision, launch the missile, close that, close that, that Internet port, you know, erase
the database. The company recently was, was vibe coding with, with AI and replit erased to their
corporate database. It just did. It just, you know, Bobby drop tabled it and they lost everything. So, so
with AI, it's kind of a trust thing because when you trust humans, they can make mistakes too. They
can, they can blank a database just as easily as a computer can, but maybe not as fast and maybe
they'll think twice before they do it. So trust it at machine speed is is really a real question. And looking
at it in from warfare terms, I mean, we're seeing it play out now in several places in the world where you
have robots fighting robots, drones fighting drones, right? So when you take humans out of inherently
Human endeavors. I mean war is messy and ugly, but it's humans fighting humans for whatever
reason. But when you start automating everything, decisions start changing. It's, it's, it's a whole ethical
problem. So what we say is use it as a decision aid to help you come up with courses of action. But the
human makes the decision that helps the human in the loop. And that's what NIST says to do with their
AI Risk Management Framework 2.0.
[31:08] Speaker C: Yeah, thank you so much.
[31:11] Speaker A: I know it's a lot, I've thought about it a lot. So sorry. Yeah, so this is your tool that
you've got up? Yes, very good question, William. Thank you. It's a good, timely question.
[31:23] Speaker B: So for our relationship, because obviously now like you were saying, there's going
to be a lot of relationship this and that. And one of the way we thought we could present that is through.
So we're using this software called Neo4j Browser. It helps you see. Let's say as an organization, I'm
using Stripe, MongoDB, Autho, a lot of companies use. Some companies use Autho, sendgrant,
datadog. So this is here to help you visualize, okay, how are all the compliance connected? And you're
able to check to see what part of the functionality is connected to which one and everything. And this is
something that we created just to visualize the graph because as a company you are going to have a
lot of vendors, 40 plus vendor, doing everything as, and connect it to different parts of cloud, cloud
function, cloud run. And we thought like this is one of the ways to visualize everything. And this is
something that we will be mentioning in our final project as well. Just easy to visualize and everything.
[32:23] Speaker A: Okay, yeah, I think I'm following because what you're saying is a new product
introduced could actually change the compliance status of products that are already on the system just
because of the way they interact.
[32:40] Speaker B: Right, right. And okay, and an idea here is that I guess in the future obviously this
is here supposed to sort of like the twin that you were talking about. Supposed to. So okay, this right
here is your company twin or environment compliance twin where you're able to visualize everything
that is going on. Like how are everything connected? And something like that. The way we, for
example, like. And this is the detailed part I was talking about is. Let me just. So for example here the
idea is to, let's say you run a, let's say your stripe goes down, you know, then it's simulating stripe field
for four hours. And it does everything, the impact score and it is able to give you all this detailed report.
And that's something I think many of.
[33:38] Speaker A: The.
[33:40] Speaker B: Current vendors don't do it. And then after that, once we have that, we have a Neo
4J to help us visualize the graphs and everything. And you're able to manipulate data from here, look at
the business process. How are they all connected? What depends on what and sorts and. But yeah,
that's like the idea that we're thinking is just because what we're suggesting is obviously doesn't exist,
this feature doesn't exist yet. And our goal with this research is like, hey, we're not trying to build our
own independent feature. It's actually build on top of existing GRC tools. Like I'm sure you heard, like
ServiceNow. There's also Archer Archer, Venta, Drata. So that's what we're thinking so far. I think in
our next phase, because right now the data and the vendor that you see is based on the like sample
data will actually be for our next phase, we'll actually be using GCP to, you know, get the actual
functionality. And basically we want to present that this can be integrated with the existing workflows
without building it separately because billing is separately could be time consuming in the future. And
some of the GRC tool are already advanced enough for us to just build on top of it, go along with their
integrate with their GRC tool. So that's like the idea here is like, how can we present it in a way that this
is like something that companies can add on top of it, not as use it as a separate feature, but add on top
of it to whatever they're using.
[35:09] Speaker A: Yeah, yeah, you sort of see that with the Google Security command center. Do you
have access to that at work? Yeah. So you see how it looks. It looks at the CIS standards or the NIST
standards or whatever, and it tells you how compliant your environment is, but it's just looking at that
environment. So if you're able to expand that to not just the environment, the Google stuff running in the
environment, but also the database we've built in there, the various containers and microservices we
have running, track them back to their dependencies and everything. So that's, I think what you're
suggesting doing and that would be very useful, I mean, even for the task you're on right now, which is
to collect the evidence that we're compliant with the things we're claiming we're compliant with, wouldn't
it be great If Google had a dashboard that had all of the NIST controls and you just haven't spit out a
screenshot or a table or whatever, proving that you're meeting that requirement across the board yet.
So that would really, really make GRC much, much easier. But also risk management as well because I
would know, hey, I upgrade this dependency and then I look at my dashboard, did anything change and
do it in a pre production environment like I were talking about the digital twin type thing, test it there.
Same thing, bad going to happen. Security, operational, business wise. Yeah. So you're onto
something really good there. I think that's, that's fantastic. I wish I was smart as you guys. I'm trying to
build my infrastructure right now. Just test it. Yeah, yeah.
[36:52] Speaker B: And what do you, what do you think of like us suggesting that, that this can be
integrated with the existing tool and just building on top of it not having its own independent.
[37:02] Speaker A: Well, yes, it's a great idea. You'd have to prove it though. So you'd have to have
several use cases. So you've got a bunch of them right there where you've got the different business
tools that you're looking at. So that's the right approach. You'll just have to have several of those
general but then also be able to give a custom example to a client. They give you their software. Bill of
materials. Hey, we use this database, we use this operating system, we use this and that. Okay, well
here's how our product would integrate all those things. This is our edr, you know, whatever, you know,
so. And then you know, you're basically doing as a company what their. So what your software is going
to do for their enterprise.
[37:51] Speaker B: Absolutely. And, and I think that's you, William. I know we're also coming to an end.
[37:56] Speaker C: Thank you so much.
[37:58] Speaker B: But yeah, absolutely. J.J. like you said, that's something we're working on. The
next phase of our project is how can we, like you said, how can we use the APIs integration tools that
they have and connect it? Maybe give a custom example. But yeah, overall I really liked your insights
and I'm sure my team members also liked your insights, especially in the examples that you gave about
business operations. Should we make this decision? That decision. But yeah, let me think if I have any
other more questions. But I think you covered