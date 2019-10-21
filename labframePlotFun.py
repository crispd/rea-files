from flame import Machine
import scipy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pt

def labframePlot(filename, ax=None, starting_element=0, **kwargs):
	f = open(filename, 'rb')
	M = Machine(f)
	
	#if ax==None:
	#	fig = plt.figure()
	#	ax = fig.add_subplot(111)
	
	# Start element index (Note 79 will currently start it at LINAC exit)
	start = starting_element
	# End element index
	end = len(M)
	
	pos = np.array([0.0, 0.0])      # Starting Point (x, y)
	pos_max = np.array([0.0, 0.0])  # Max limit of labframe
	pos_min = np.array([0.0, 0.0])  # Min limit of labframe
	ang = 0.0                       # Accumulated bend angle 
	s = 0.3                         # Size scale of the optical element

	# Element count
	nb = 0
	nvb = 0
	nq = 0
	ns = 0
	nr = 0
	nf = 0
	nv = 0
	nc = 0

	# Coordinate sign 
	lsign = 1.0 # (1.0: beam advances to right, -1.0: beam advances to left)

	#Color for elements
	colors = {'drift':'black',
			  'sbend':'green',
			  'edipole':'lime',
			  'v-bend':'lime',
			  'quadrupole':'blue',
			  'rfcavity':'orange',
			  'solenoid':'purple', 
			  'monitor':'red',
			  'FC':'red',
			  'viewer':'cyan',
			  'corrector':'magenta'
			  }

	# Shape of bending element
	sector = True

	# Orientation: 0.0, flattens; 1.0, sets clockwise; -1.0 counter-clockwise
	angFact = 0.0

	for i in range(start, end):
		cf = M.conf(i)
		
		pos_max[0] = max(pos_max[0], pos[0])
		pos_max[1] = max(pos_max[1], pos[1])
		pos_min[0] = min(pos_min[0], pos[0])
		pos_min[1] = min(pos_min[1], pos[1])
		
		rot = np.array([np.cos(np.pi*ang/180.0), np.sin(np.pi*ang/180.0)])
		roti = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])
		if cf['type'] == 'drift':
			l = lsign*cf['L']
			pos1 = pos + l*rot
			ln = plt.Line2D([pos[0], pos1[0]], [pos[1], pos1[1]], color=colors['drift'], zorder=-1)
			ax.add_line(ln)
			pos = pos1
		elif cf['type'] == 'sbend' or cf['type'] == 'edipole':
			l = lsign*cf['L']
			_phi = cf['phi']/2.0
			rad = _phi*np.pi/180.0
			#ll = l*360.0/cf['phi']/np.pi*np.sin(cf['phi']*np.pi/360.0)
			#ll = l * (180.0/(_phi*np.pi)) * np.sin(_phi*np.pi/180.0)
			ll = l * (1/rad) * np.sin(rad)

			if angFact==0.0:
				sc1 = s
				sc2 = s
			else:
				sc1 = s * (1 - ll*np.sin(angFact*rad))
				sc2 = s * (1 + ll*np.sin(angFact*rad))

			if sector:
				ang += (-cf['phi']/2.0) * angFact
				rot = np.array([np.cos(np.pi*ang/180.0), np.sin(np.pi*ang/180.0)])
				roti = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])
				pos1 = pos + l*rot
				posm1 = pos + s*l*rot
				posm2 = pos + (1.0-s)*l*rot
				box = np.array([pos, pos, posm1, posm2, pos1, pos1, posm2, posm1])
				box += np.array([s*roti, -s*roti, -sc1*roti, -sc1*roti,
								 -s*roti, s*roti, sc2*roti, sc2*roti])
				ang += (-cf['phi']/2.0) * angFact
			else:
				rot1 = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])
				ang += (-cf['phi']*s) * angFact
				rot2 = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])
				ang += (-cf['phi']*(0.5-s)) * angFact
				rot = np.array([np.cos(np.pi*ang/180.0), np.sin(np.pi*ang/180.0)])
				ang += (-cf['phi']*(0.5-s)) * angFact
				rot3 = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])
				ang += (-cf['phi']*s) * angFact
				rot4 = np.array([np.sin(-np.pi*ang/180.0), np.cos(-np.pi*ang/180.0)])

				pos1 = pos + l*rot
				posm1 = pos + s*l*rot
				posm2 = pos + (1.0-s)*l*rot
				box = np.array([pos, pos, posm1, posm2, pos1, pos1, posm2, posm1])
				
				box += np.array([s*rot1, -s*rot1, -sc1*rot2, -sc1*rot3,
								 -s*rot4, s*rot4, sc2*rot3, sc2*rot2])

			
			if 'DV' in cf['name']:
				ax.add_patch(plt.Polygon(box, color=colors['v-bend'], ec=None, label='Vert. Bend' if nvb == 0 else ""))
				nvb += 1
			elif cf['type'] == 'edipole':
				ax.add_patch(plt.Polygon(box, color=colors['edipole'], ec=None, label='E-Bend' if nvb == 0 else ""))
				nvb += 1
			else:
				ax.add_patch(plt.Polygon(box, color=colors['sbend'], ec=None, label='Bend' if nb == 0 else ""))
				nb += 1
			pos = pos1

		
		elif cf['type'] == 'quadrupole' or cf['type'] == 'equad':
			l = lsign*cf['L']
			pos1 = pos + l*rot
			box = np.array([pos, pos, pos1, pos1])
			box += np.array([s*roti, -s*roti, -s*roti, s*roti])
			ax.add_patch(plt.Polygon(box, color=colors['quadrupole'], ec=None, label='Quadrupole' if nq == 0 else ""))
			nq += 1
			pos = pos1
		elif cf['type'] == 'rfcavity':
			l = lsign*cf['L']
			pos1 = pos + l*rot
			box = np.array([pos, pos, pos1, pos1])
			box += np.array([s*roti, -s*roti, -s*roti, s*roti])
			ax.add_patch(plt.Polygon(box, color=colors['rfcavity'], ec=None, label='RF cavity' if nr == 0 else ""))
			nr += 1
			pos = pos1
		elif cf['type'] == 'solenoid':
			l = lsign*cf['L']
			pos1 = pos + l*rot
			box = np.array([pos, pos, pos1, pos1])
			box += np.array([s*roti, -s*roti, -s*roti, s*roti])
			ax.add_patch(plt.Polygon(box, color=colors['solenoid'], ec=None, label='Solenoid' if ns == 0 else ""))
			ns += 1
			pos = pos1
		elif cf['type'] == 'marker':
			box = np.array([pos, pos, pos1, pos1])
			box += np.array([s*roti, -s*roti, -s*roti, s*roti])
			if False:
				ax.add_patch(plt.Polygon(box, color=colors['monitor'], label='Monitor' if nf == 0 else ""))
				nf += 1
			elif 'FC' in cf['name']:
				ax.add_patch(plt.Polygon(box, color=colors['FC'], label='Faraday Cup' if nf == 0 else ""))
				nf += 1
			elif 'VD' in cf['name']:
				ax.add_patch(plt.Polygon(box, color=colors['viewer'], label='Viewer' if nv == 0 else ""))
				nv += 1
		elif cf['type'] == 'orbtrim':
			if not 'xyrotate' in cf:
				box = np.array([pos, pos, pos1, pos1])
				box += np.array([s*roti, -s*roti, -s*roti, s*roti])
				ax.add_patch(plt.Polygon(box, color=colors['corrector'], zorder=5, label='Corrector' if nc == 0 else ""))
				nc += 1

	# Additional setting for plot
	#plt.xlim(0,17.5)
	#plt.ylim(-4,6)

	if angFact==0.0:
		pos_max[1] += 2
		#ax.yticks([])
		ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5, borderaxespad=3, title='ReA: HEBT Layout')
	else:
		if pos_max[1] < 6:
			pos_max[1] += 5
		else:
			pos_max[1] = 13
		
		ax.legend(loc='upper left', ncol=3, title='ReA: HEBT Layout')
		#ax.ylabel('[m]')

	xmin = pos_min[0]
	xmax = pos_max[0] + 1
	ymin = pos_min[1] - 2
	ymax = pos_max[1]

	#plt.xlim(xmin, xmax)
	#plt.ylim(ymin, ymax)

	#plt.axes().set_aspect('equal')
	#plt.xlabel('[m]')
	#plt.show()
		
	return ax, xmin, xmax, ymin, ymax


def plotTest(ax):
	ln =  plt.Line2D([0.0, 10.0], [0.0, 0.0], color='black', zorder=-1)
	ax.add_line(ln)
	return ax
