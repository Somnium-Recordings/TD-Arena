from tda import LoadableExt
from tdaUtils import (EffectLocation, addSectionParameters, filePathToName,
                      intIfSet, layoutComps, mapAddressToEffectLocation)

DEFAULT_STATE = {}


class EffectCtrl(LoadableExt):
	def Init(self):
		self.setUnloaded()

		self.saveState = None
		self.effectsContainers = {}

		self.logInfo('initialized')

	def Load(self, saveState=None):
		self.setLoading()

		self.saveState = saveState or DEFAULT_STATE

		# Async effect loading flow is:
		# 1. State calls EffectsCtrl.load(saveState) and stores state
		# 2. Layer/Effects are created containing Effects container
		# 3. Effects extension init calls EffectsCtrl.RegisterEffectsContainer
		# 4. EffectsCtrl.RegisterEffect stores reference and calls Effects.Load
		#    with previous save state if set
		# 5. Effects.load loads any necessary effect toxes

		self.logInfo('save state loaded')
		self.setLoaded()

	def GetSaveState(self):
		return {
			address: container.GetSaveState()
			for (address, container) in self.effectsContainers.items()
		} if self.Loaded else None

	def AddEffect(self, containerAddress, effectPath, index=None):
		assert containerAddress in self.effectsContainers, f'unknown effects container {containerAddress}'
		self.effectsContainers[containerAddress].AddEffect(effectPath, index)

	def RegisterEffectsContainer(self, address: str, containerComp):
		self.logDebug(f'registering effects container at {address}')

		if not hasattr(self, 'saveState'):
			self.logWarning(
				f'effect ({address}) cannot be initialized before save state is loaded.'
				' NOTE: If this warning occured during extension modifification,'
				' it can be safely ignored'
			)
			return

		# NOTE: we pop values from saveState as they are requested
		#       to avoid initializing with a previous save value if a
		# 		parameter with the same address is created in the
		#       future
		saveState = self.saveState.pop(address, None)
		self.effectsContainers[address] = containerComp
		containerComp.Load(saveState)

	def ClearEffectContainer(self, effectContainerAddress: str):
		# TODO(#42): ensure this is called when layers are deleted
		self.logDebug(f'clearing effect container at {effectContainerAddress}')
		container = self.effectsContainers.pop(effectContainerAddress, None)
		if container is None:
			self.logWarning(
				f'attempted to clear effect unkown container at {effectContainerAddress}'
			)

	def ClearEffect(self, effectLocation: EffectLocation):
		containerAddress, effectID = effectLocation
		print(f'{self.effectsContainers.keys()}')
		assert containerAddress in self.effectsContainers, f'unknown effects container {containerAddress}'

		self.logDebug(f'clearing effect {effectID} from {containerAddress}')
		self.effectsContainers[containerAddress].ClearEffect(effectID)

	# pylint: disable=no-self-use
	def MoveEffect(
		self, effectLocation: EffectLocation, position: str, targetEffectAddress: str
	):
		containerAddress, effectID = effectLocation
		self.logDebug(
			f'moving {containerAddress}/{effectID} {position} {targetEffectAddress}'
		)

		# remember we're going to need to handle "add effect" too, so make reordering generic
		# insert into new home in linked list
		# update align order? for each one
		# update OSR reploy thing to send Ordering updates back to UI
		#    - is there any need to do this in a certain order to avoid flickering?
		assert containerAddress in self.effectsContainers, f'unknown effects container {containerAddress}'

		targetContainerAddress, targetEffectID = mapAddressToEffectLocation(
			targetEffectAddress
		)
		if targetContainerAddress != containerAddress:
			raise NotImplementedError(
				'moving effects between containers not implemented yet'
			)

		self.effectsContainers[containerAddress].MoveEffect(
			effectID, position, targetEffectID
		)


def getSourceID(effectOp):
	return intIfSet(effectOp.par.Sourceeffectid.eval()) if effectOp else None


class EffectsContainer(LoadableExt):
	@property
	def headEffectID(self):
		return intIfSet(self.ownerComponent.par.Headeffectid.eval())

	@headEffectID.setter
	def headEffectID(self, value):
		self.ownerComponent.par.Headeffectid.val = value

	def __init__(
		self, ownerComponent, logger, effectCtrl: EffectCtrl, address: str
	):
		super().__init__(ownerComponent, logger)
		self.effectCtrl = effectCtrl
		self.address = address
		self.effectTemplate = effectCtrl.op('./effectTemplate')
		self.selectFinalTexture = ownerComponent.op('select_finalTexture')

		assert hasattr(
			ownerComponent.par, 'Headeffectid'
		), 'expected effect container to have "Headeffectid" par'

		if 'Template' in ownerComponent.path:
			self.logDebug('skipping initialization of template')
			return

		self.Init()

	def Init(self):
		self.setUnloaded()

		self.nextEffectID = 0
		self.effects = {}
		self.headEffectID = None

		# Delaying registration to avoid "Cannot use an extension during its initialization"
		# TODO(#45): is there a better way?
		run(
			'args[0].effectCtrl.RegisterEffectsContainer(args[0].address, args[0].ownerComponent)',
			self,
			delayFrames=1
		)

		self.logInfo('initialized')

	def Load(self, saveState=None):
		self.setLoading()

		headEffectId = saveState['Headeffectid'] if saveState is not None else None

		effectsToCreate = []
		nextEffectID = headEffectId
		while nextEffectID is not None:
			# NOTE: We can't store numeric dict keys in json, so we
			#       have to lookup by str
			effect = saveState['effects'][str(nextEffectID)]
			effectsToCreate.append((nextEffectID, effect))
			nextEffectID = effect['Sourceeffectid']

		# We create effects in the reverse order of the "linked list"
		# to avoid having an effect point to a non-existent texture.
		for (effectID, effect) in reversed(effectsToCreate):
			self.AddEffect(
				effectID=effectID,
				effectPath=effect['Effectpath'],
				sourceEffectID=effect['Sourceeffectid']
			)

		if headEffectId != self.headEffectID:
			self.logWarning(
				'loading save state did not result in expected Headeffectid'
			)

		self.logInfo(f'loaded {len(effectsToCreate)} effects into chain')
		self.setLoaded()

	def GetSaveState(self):
		return {
			'Headeffectid': self.headEffectID,
			'effects': {
				id: {
					'Effectpath': effect.par.Effectpath.eval(),
					'Sourceeffectid': getSourceID(effect)
				}
				for (id, effect) in self.effects.items()
			}
		}

	def AddEffect(
		self, effectPath, sourceEffectID: int = None, effectID: int = None
	):
		self.logDebug(f'adding {effectPath}')

		effect = self.createNextEffect(effectID)
		effect.par.Effectpath = effectPath

		if sourceEffectID is None and self.headEffectID is not None:
			sourceEffectID = self.headEffectID
		effect.par.Sourceeffectid = sourceEffectID

		tox = effect.op('./tox')
		tox.par.reinitnet.pulse()
		tox = effect.op('./tox')  # need new handle on tox since we reinitalized it
		# TODO(#40): reset all order params after creation?
		addSectionParameters(
			tox, order=len(self.effects), opacity=1.0, name=filePathToName(effectPath)
		)

		self.headEffectID = effect.digits

	def MoveEffect(self, effectID: int, position: str, targetEffectID: int):
		if effectID not in self.effects:
			self.logWarning(f'could not find requested effectID {effectID} to move')
			return
		effect = self.effects[effectID]

		if targetEffectID not in self.effects:
			self.logWarning(f'could not find requested target ID {targetEffectID}')
			return

		self.logDebug(f'moving effectID {effectID} {position} {targetEffectID}')

		self.removeFromChain(effect, effectID)

		# move to `insertIntoChain`
		if position == 'above':
			insertionID = targetEffectID
		elif position == 'below':
			insertionEffect = self.findEffectWithSource(targetEffectID)
			insertionID = insertionEffect.digits if insertionEffect else insertionEffect
		else:
			raise NotImplementedError(f'moving {position} an effect is not implemented')

		effect.par.Sourceeffectid = insertionID
		if self.headEffectID == insertionID:
			self.logDebug(f'inserting at head {self.headEffectID} == {insertionID}')
			self.headEffectID = effectID
		else:
			self.logDebug('inserting at previous effect')
			previousEffect = self.findEffectWithSource(insertionID)
			previousEffect.par.Sourceeffectid = effectID

		# TODO: reorder?

	def removeFromChain(self, effect, effectID: int):
		if self.headEffectID == effectID:
			self.headEffectID = getSourceID(effect)
		else:
			previousEffect = self.findEffectWithSource(effectID)
			previousEffect.par.Sourceeffectid = getSourceID(effect)

	def ClearEffect(self, effectID: int):
		effect = self.effects.pop(effectID, None)

		if effect is None:
			self.logWarning(f'could not find requested effect {effectID} to clear')
			return

		self.removeFromChain(effect, effectID)

		effect.destroy()
		self.updatEffectNetworkPositions()
		self.logDebug(f'effect {effectID} cleared')

	def findEffectWithSource(self, sourceEffectID: int):
		effect = self.effects[self.headEffectID]
		while getSourceID(effect) != sourceEffectID:
			effect = self.effects[getSourceID(effect)]
			assert effect is not None, f'could not find effect pointing to ID {sourceEffectID}'

		return effect

	def createNextEffect(self, effectID: int = None):
		if effectID is None:
			effectID = self.nextEffectID
			self.nextEffectID += 1
		elif effectID >= self.nextEffectID:
			self.nextEffectID = effectID + 1

		effect = self.ownerComponent.copy(
			self.effectTemplate, name=(f'effect{effectID}')
		)
		self.effects[effectID] = effect

		self.updatEffectNetworkPositions()

		return effect

	def updatEffectNetworkPositions(self):
		layoutComps(self.effects.values())


class ClipEffectsContainer(EffectsContainer):
	def __init__(self, ownerComponent, logger, effectCtrl: EffectCtrl):
		super().__init__(
			ownerComponent, logger, effectCtrl,
			f'/composition/clips/{ownerComponent.parent.clip.digits}/video/effects'
		)
