import random
import math


tags = ['broadband', 'hvac', 'plumbing', 'home security', 'installation' , 'repair/maintenance', 'replacement', 'delivery', 'meter reading', 'estimate/inspection']

people = {'customers':[['Rick','103764585826277201640'], ['Robert','108560908635605545932'], ['Ryan','102345940077083980832'],['Rachel','107612119418245526899'],['Rose','108612246962932756480']],
          'engineers':[['Joe','110257721827374623737'],['Josephine','117685299168782698970'],['Jeremy','101967792556257735208'],['Jhon','103387629180365578874'],['James','101447084593147265288'],['Jenny','102417683683083682579'],['Jeff','115781491509522514753'],['Jason','105193078925726528104'],['Jenna','109061817072269062716']],
          'experts':[['TWC','112739138406530779564'],['Cisco','110132770680215220078'],['Verizon','108741317245837764468'],['Belkin','112043759976089842597'],['Apple','103675625919779944270'],['Netgear','118014758899268715696']]}

tags_to_people = {}

id_to_people = {}
for e in people['engineers']:
	id_to_people[e[1]] = e[0]

for e in people['experts']:
	id_to_people[e[1]] = e[0]

def assign_tags(assignees, role):
	for person_id in assignees:
		curr_tags = set()
		while len(curr_tags) < 3:
			idx = int(random.uniform(0, len(tags)))
			curr_tag = tags[idx]
			if curr_tag not in tags_to_people:
				tags_to_people[curr_tag] = {}
			if role not in tags_to_people[curr_tag]:
				tags_to_people[curr_tag][role] = []
			tags_to_people[curr_tag][role].append([id_to_people[person_id], person_id])
			curr_tags.add(curr_tag)

assignee_roles = ['engineers', 'experts']
for role in assignee_roles:
	assignees = set([e[1] for e in people[role]])
	assign_tags(assignees, role)

print(tags_to_people)

print(len(tags_to_people), len(tags))
