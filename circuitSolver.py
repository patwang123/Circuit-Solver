"""
Solver for EECS 16A circuits
Note: This only includes voltage sources, resistors, and current sources so far. TBD on other components.
This also can only solve for numerical variables, not theoretical knowns like 'Vs' and 'R1'. Variable implementation TBD.
"""

#USE 0 TO DENOTE GROUND FOR NODE
import numpy as np
#kind of implemented poorly, component is independent of node, but whatever
#i use classes for organization purposes here.
class Component:
	def __init__(self,type,idx,value,node1,node2,size,total): #node1 is positive side
		self.type = type
		self.idx = idx
		self.value = value
		self.node1 = node1
		self.node2 = node2
		self.num_nodes = size
		self.total = total
	def get_type(self):
		return self.type
	def get_id(self):
		return self.idx
	def get_value(self,nodeNum): #returns values to be plugged into KCL
		if self.type == 'R': #I = V/R
			if nodeNum == self.node1:
				return [-1/self.value,self.node1,self.node2]
			if nodeNum == self.node2:
				return [1/self.value,self.node1,self.node2]
		if self.type == 'I':
			if nodeNum == self.node1:
				return -1*self.value
			if nodeNum == self.node2:
				return 1*self.value
		if self.type == 'V': # V = u1-u2. [... 0 0 1 -1 0 0 ... | V] (unless ground)
			res = [0 for _ in range(self.total+1)]
			res[self.node1] = 1
			res[self.node2] = -1
			res[-1] = self.value

			return [res,self.idx,-1 if nodeNum == self.node1 else 1]
	def get_positive(self):
		return self.node1
	def get_negative(self):
		return self.node2
	def to_string(self):
		return str([self.type,self.idx,self.value,self.node1,self.node2])
class Node:
	def __init__(self,idx,connections,size,total):
		self.idx = idx
		self.connections = connections
		self.num_nodes = size
		self.total = total
	def kcl(self): #returns a row of the matrix (or more)
		rows = []
		row = [0 for _ in range(self.total+1)]
		for c in self.connections:
			print(row)
			val = c.get_value(self.idx)
			c_type = c.get_type()
			if c_type == 'V':
				rows.append(val[0])
				row[val[1]] += val[2]
			elif c_type == 'R':
				input(val)
				row[val[1]] += val[0]
				row[val[2]] -= val[0]
			elif c_type == 'I':
				row[-1] += -1*val
		rows.append(row)
		return rows
	def to_string(self):
		return str([self.idx,[c.to_string() for c in self.connections]])
class CircuitSolver:
	def __init__(self,num_nodes,components,num_voltages): #components: [TYPE, ID, VALUE, node1, node2]. Node1 is positive
		#init kinda badly implemented and repetitive, but for low # of nodes it is irrelevant
		#LET NODE 0 BE GROUND
		self.num_nodes = num_nodes
		self.num_voltages = num_voltages
		self.total = num_nodes + num_voltages
		self.components = []
		for c in components:#
			self.components.append(Component(c[0],c[1],c[2],c[3],c[4],num_nodes,self.total))
		self.connections = [[] for _ in range(num_nodes)]
		for c in self.components:
			self.connections[c.get_positive()].append(c)
			self.connections[c.get_negative()].append(c)
		self.nodes = [Node(i,self.connections[i],num_nodes,self.total) for i in range(len(self.connections))]
	def solve(self):
		aug_matrix = []
		for n in self.nodes:
			arr = n.kcl()
			for a in arr:
				if not a in aug_matrix and not [-1*x for x in a] in aug_matrix and not np.all((np.array(a) == 0)):
					aug_matrix.append(a)
		aug_matrix.append([1] + [0 for _ in range(self.total)])
		aug_matrix = np.array(aug_matrix)
		print(aug_matrix)
		self.node_voltages = np.linalg.solve(aug_matrix[:,:-1],aug_matrix[:,-1])
	#implementation of currents and voltages TBD

num_nodes = 2
num_voltages = 1
components = [['V',2,5,1,0],['R',1,5,1,0],['R',2,1,1,0]]
circuit = CircuitSolver(num_nodes,components,num_voltages)
circuit.solve()
print(circuit.node_voltages)

"""
COMPONENTS WITH 'V' START WITH ID >= num_nodes.

e.g. numnodes = 2
V1's ID is 2, V2's is 3, etc.
"""