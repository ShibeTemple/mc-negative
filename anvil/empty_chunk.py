from typing import List
from .block import Block
from .empty_section import EmptySection
from .errors import OutOfBoundsCoordinates, EmptySectionAlreadyExists
from nbt import nbt

from gc import get_objects
from collections import defaultdict

class EmptyChunk:
	"""
	Used for making own chunks

	Attributes
	----------
	x: :class:`int`
		Chunk's X position
	z: :class:`int`
		Chunk's Z position
	sections: List[:class:`anvil.EmptySection`]
		List of all the sections in this chunk
	version: :class:`int`
		Chunk's DataVersion
	"""
	__slots__ = ('x', 'z', 'sections', 'version', 'TileEntities', 'Entities')
	def __init__(self, x: int, z: int):
		self.x = x
		self.z = z
		self.sections: List[EmptySection] = [None]*16
		self.version = 1976
		self.TileEntities = None
		self.Entities = None

	def setTileEntities(self,input):
		self.TileEntities = input

	def setEntities(self,input):
		self.Entities = input

	def add_section(self, section: EmptySection, replace: bool = True):
		"""
		Adds a section to the chunk

		Parameters
		----------
		section
			Section to add
		replace
			Whether to replace section if one at same Y already exists

		Raises
		------
		anvil.EmptySectionAlreadyExists
			If ``replace`` is ``False`` and section with same Y already exists in this chunk
		"""
		if self.sections[section.y] and not replace:
			raise EmptySectionAlreadyExists(f'EmptySection (Y={section.y}) already exists in this chunk')
		self.sections[section.y] = section

	def get_block(self, x: int, y: int, z: int) -> Block:
		"""
		Gets the block at given coordinates

		Parameters
		----------
		int x, z
			In range of 0 to 15
		y
			In range of 0 to 255

		Raises
		------
		anvil.OutOfBoundCoordidnates
			If X, Y or Z are not in the proper range

		Returns
		-------
		block : :class:`anvil.Block` or None
			Returns ``None`` if the section is empty, meaning the block
			is most likely an air block.
		"""
		if x < 0 or x > 15:
			raise OutOfBoundsCoordinates(f'X ({x!r}) must be in range of 0 to 15')
		if z < 0 or z > 15:
			raise OutOfBoundsCoordinates(f'Z ({z!r}) must be in range of 0 to 15')
		if y < 0 or y > 255:
			raise OutOfBoundsCoordinates(f'Y ({y!r}) must be in range of 0 to 255')
		section = self.sections[y // 16]
		if section is None:
			return
		return section.get_block(x, y % 16, z)

	def set_block(self, block: Block, x: int, y: int, z: int):
		"""
		Sets block at given coordinates

		Parameters
		----------
		int x, z
			In range of 0 to 15
		y
			In range of 0 to 255

		Raises
		------
		anvil.OutOfBoundCoordidnates
			If X, Y or Z are not in the proper range

		"""
		if x < 0 or x > 15:
			raise OutOfBoundsCoordinates(f'X ({x!r}) must be in range of 0 to 15')
		if z < 0 or z > 15:
			raise OutOfBoundsCoordinates(f'Z ({z!r}) must be in range of 0 to 15')
		if y < 0 or y > 255:
			raise OutOfBoundsCoordinates(f'Y ({y!r}) must be in range of 0 to 255')
		section = self.sections[y // 16]
		if section is None:
			#print('empty section')
			section = EmptySection(y // 16)
			self.add_section(section)
		"""before = defaultdict(int)
		after = defaultdict(int)

		for i in get_objects():
			before[type(i)] += 1
		"""
		section.set_block(block, x, y % 16, z)
		"""
		for i in get_objects():
			after[type(i)] += 1
			leaks = [(k, after[k] - before[k]) for k in after if after[k] - before[k]]
			if not leaks == []:
				print(leaks)"""

	def save(self) -> nbt.NBTFile:
		"""
		Saves the chunk data to a :class:`NBTFile`

		Notes
		-----
		Does not contain most data a regular chunk would have,
		but minecraft stills accept it.
		"""
		#print("EMPTY_CHUNK.PY save() method called!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		root = nbt.NBTFile()
		root.tags.append(nbt.TAG_Int(name='DataVersion',value=self.version))
		level = nbt.TAG_Compound()
		# Needs to be in a separate line because it just gets
		# ignored if you pass it as a kwarg in the constructor
		level.name = 'Level'

		print("[anvil] saving chunk with entity data --empty_chunk.py")
		level.tags.extend([
			nbt.TAG_List(name='Entities', type=nbt.TAG_Compound),
			nbt.TAG_List(name='TileEntities', type=nbt.TAG_Compound),
			nbt.TAG_List(name='LiquidTicks', type=nbt.TAG_Compound),
			nbt.TAG_Int(name='xPos', value=self.x),
			nbt.TAG_Int(name='zPos', value=self.z),
			nbt.TAG_Long(name='LastUpdate', value=0),
			nbt.TAG_Long(name='InhabitedTime', value=0),
			nbt.TAG_Byte(name='isLightOn', value=1),
			nbt.TAG_String(name='Status', value='full')
		])

		updatedEntities = False

		if self.TileEntities != None and len(self.Entities) > 0:
			print("INPUT: self.TileEntities",self.TileEntities)
			print("INPUT TYPE:",type(self.TileEntities))

			print("pre: TileEntities",level["TileEntities"])
			level["TileEntities"].extend(self.TileEntities)
			print("post: TileEntities",level["TileEntities"])

			updatedEntities = True

		if self.Entities != None and len(self.Entities) > 0:
			print("INPUT: self.Entities",self.Entities)
			print("INPUT TYPE:",type(self.Entities))

			print("pre: Entities",level["Entities"])
			level["Entities"].extend(self.Entities)
			print("post: Entities",level["Entities"])

			updatedEntities = True

		if updatedEntities:
			print("---")

		sections = nbt.TAG_List(name='Sections', type=nbt.TAG_Compound)
		for s in self.sections:
			if s:
				p = s.palette()
				# Minecraft does not save sections that are just air
				# So we can just skip them
				if len(p) == 1 and p[0].name() == 'minecraft:air':
					continue
				sections.tags.append(s.save())
		level.tags.append(sections)
		root.tags.append(level)
		return root
