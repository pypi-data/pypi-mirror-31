
from xdevs import INFINITY
from xdevs.models import Atomic, Coupled
from abc import ABC, abstractmethod
import logging

class SimulationClock:

	def __init__(self, time = 0):
		self.time = time


class AbstractSimulator(ABC):

	def __init__(self, clock):
		self.clock = clock
		self.time_last = 0
		self.time_next = 0
		
	@abstractmethod
	def initialize(self):
		pass
		
	@abstractmethod
	def exit(self):
		pass
		
	@abstractmethod
	def ta(self):
		pass
		
	@abstractmethod
	def lambdaf(self):
		pass
		
	@abstractmethod
	def deltfcn(self):
		pass
		
	@abstractmethod
	def clear(self):
		pass
		
		
class Simulator(AbstractSimulator):
	
	def __init__(self, clock, model):
		super().__init__(clock)
		self.model = model
		
	@property
	def ta(self):
		return self.model.ta
		
	def initialize(self):
		self.model.initialize()
		self.time_last = self.clock.time
		self.time_next = self.time_last + self.model.ta
		
	def exit(self):
		self.model.exit()
		
	def deltfcn(self):
		t = self.clock.time
		in_empty = self.model.in_empty()
		
		if in_empty:
			if t != self.time_next:
				return
			self.model.deltint()
		else:
			e = t - self.time_last
			self.model.sigma -= e
			
			if t == self.time_next:
				self.model.deltcon(e)
			else:
				self.model.deltext(e)
			
		self.time_last = t
		self.time_next = self.time_last + self.model.ta
		
	def lambdaf(self):
		if self.clock.time == self.time_next:
			self.model.lambdaf()

	def clear(self):
		for in_port in self.model.in_ports:
			in_port.clear()
			
		for out_port in self.model.out_ports:
			out_port.clear()


class Coordinator(AbstractSimulator):

	def __init__(self, model, clock = SimulationClock(), flatten = False):
		super().__init__(clock)
		self.model = model.flatten() if flatten else model
		self.simulators = []
		
	def initialize(self):
		self._build_hierarchy()
		
		for sim in self.simulators:
			sim.initialize()
			
		self.time_last = self.clock.time
		self.time_next = self.time_last + self.ta()
		
	def _build_hierarchy(self):
		for comp in self.model.components:
			logging.info("%s -> %s" % (self, comp))
			if isinstance(comp, Coupled):
				self.simulators.append(Coordinator(self.clock, comp))
			elif isinstance(comp, Atomic):
				self.simulators.append(Simulator(self.clock, comp))
			
	def exit(self):
		for sim in self.simulators:
			sim.exit()
			
	def ta(self):
		return min([sim.time_next for sim in self.simulators]) - self.clock.time
		
	def lambdaf(self):
		for sim in self.simulators:
			sim.lambdaf()
			
		self.propagate_output()
		
	def propagate_output(self):
		for coup in self.model.ic:
			coup.propagate()
			
		for coup in self.model.eoc:
			coup.propagate()
		
	def deltfcn(self):
		self.propagate_input()
		
		for sim in self.simulators:
			sim.deltfcn()
			
		self.time_last = self.clock.time
		self.time_next = self.time_last + self.ta()
	
	def propagate_input(self):
		for coup in self.model.eic:
			coup.propagate()
			
	def clear(self):
		for sim in self.simulators:
			sim.clear()
		
		for in_port in self.model.in_ports:
			in_port.clear()
			
		for out_port in self.model.out_ports:
			out_port.clear()
			
	def inject(port, values, e = 0):
		time = time_last + e
		if type(values) is not list:
			values = [values]
		
		if time <= self.time_next:
			port.extend(values)
			clock.time = time
			deltfcn()
		else:
			logging.error("Time %d - Input rejected: elapsed time %d is not in bounds" % (self.time_last, e))
			
	def simulate(self, num_iters = 10000):
		logging.info("START SIMULATION")
		self.clock.time = self.time_next
		
		cont = 0
		while cont < num_iters and self.clock.time < INFINITY:
			self.lambdaf()
			self.deltfcn()
			self.clear()
			self.clock.time = self.time_next
			cont += 1
		
	def simulate_time(self, time_interv = 10000):
		logging.info("START SIMULATION")
		self.clock.time = self.time_next
		tf = self.clock.time + time_interv
		
		while self.clock.time < tf:
			self.lambdaf()
			self.deltfcn()
			self.clear()
			self.clock.time = self.time_next
		