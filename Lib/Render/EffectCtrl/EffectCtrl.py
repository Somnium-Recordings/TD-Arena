from tda import LoadableExt
from tdaUtils import (
	EffectLocation,
	addSectionParameters,
	filePathToName,
	intIfSet,
	layoutComps,
	mapAddressToEffectLocation,
)

DEFAULT_STATE = {}


class EffectCtrl(LoadableExt):

	def Init(self, _renderState):  # noqa: ANN001
		self.setUnloaded()

		self.saveState = None
		self.effectsContainers = {}

		self.logInfo('initialized')

	def Load(self, saveState=None):  # noqa: ANN001
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

	def AddEffect(self, containerAddress, effectPath, index=None):  # noqa: ANN001
		assert containerAddress in self.effectsContainers, f'unknown effects container {containerAddress}'
		self.effectsContainers[containerAddress].AddEffect(effectPath, index)

	def RegisterEffectsContainer(
		self,
		address: str,
		containerComp  # noqa: ANN001
	):
		self.logDebug(f'registering effects container at {address}')

		if not hasattr(self, 'saveState') or self.saveState is None:
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
		assert containerAddress in self.effectsContainers, (
			f'effects container {containerAddress} not found in {self.effectsContainers.keys()}'
		)

		self.logDebug(f'clearing effect {effectID} from {containerAddress}')
		self.effectsContainers[containerAddress].ClearEffect(effectID)

	def MoveEffect(
		self, effectLocation: EffectLocation, position: str, targetEffectAddress: str
	):
		containerAddress, effectID = effectLocation
		self.logDebug(
			f'moving {containerAddress}/{effectID} {position} {targetEffectAddress}'
		)

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


def getSourceID(effectOp):  # noqa: ANN001
	return intIfSet(effectOp.par.Sourceeffectid.eval()) if effectOp else None


class EffectsContainer(LoadableExt):

	@property
	def headEffectID(self):
		return intIfSet(self.ownerComponent.par.Headeffectid.eval())

	@headEffectID.setter
	def headEffectID(self, value):  # noqa: ANN001, ANN202
		self.ownerComponent.par.Headeffectid.val = value

	@property
	def address(self):
		return self.ownerComponent.par.Address.eval()

	def __init__(
		self,
		ownerComponent,  # noqa: ANN001
		logger,  # noqa: ANN001
		effectCtrl: EffectCtrl
	):
		super().__init__(ownerComponent, logger)
		self.effectCtrl = effectCtrl
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

	def Load(self, saveState=None):  # noqa: ANN001
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
			)

		assert headEffectId == self.headEffectID, (
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

	def AddEffect(  # To bottom
		self, effectPath, effectID: int = None, # sourceEffectID: int = None,  # noqa: ANN001
	):
		self.logDebug(f'adding {effectPath}')

		effect = self.createNextEffect(effectID)
		effect.par.Effectpath = effectPath
		if effectID is None:
			# we need to get id from created effect when creating new one
			effectID = effect.digits

		tox = effect.op('./tox')
		tox.par.reinitnet.pulse()
		tox = effect.op('./tox')  # need new handle on tox since we reinitalized it
		# TODO(#40): reset all order params after creation?
		addSectionParameters(
			tox, order=len(self.effects), opacity=1.0, name=filePathToName(effectPath)
		)

		self.insertIntoChain(effect, effectID)

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

		if position == 'below':
			if targetEffectID == self.headEffectID:
				targetEffectID = None  # insert at head
			else:
				effectBelowTarget = self.findEffectWithSource(targetEffectID)
				targetEffectID = effectBelowTarget.digits

		self.insertIntoChain(effect, effectID, targetEffectID)

	def insertIntoChain(
		self,
		effect,  # noqa: ANN001
		effectID,  # noqa: ANN001
		targetEffectID=None  # noqa: ANN001
	):
		if targetEffectID is None:
			self.logDebug(f'inserting effect {effectID} at head')
			effect.par.Sourceeffectid = self.headEffectID
			self.headEffectID = effectID
		else:
			self.logDebug(f'inserting effect {effectID} at {targetEffectID}')
			targetEffect = self.effects[targetEffectID]
			effect.par.Sourceeffectid = getSourceID(targetEffect)
			targetEffect.par.Sourceeffectid = effectID

		self.updateEffectOrder()

	def removeFromChain(self, effect, effectID: int):  # noqa: ANN001
		sourceID = getSourceID(effect)

		if self.headEffectID == effectID:
			self.logDebug(f'removing effect {effectID}, updating head -> {sourceID}')
			self.headEffectID = sourceID
		else:
			previousEffect = self.findEffectWithSource(effectID)
			self.logDebug(
				f'removing effect {effectID}, updating {previousEffect.digits} -> {sourceID}'
			)
			previousEffect.par.Sourceeffectid = sourceID

		effect.par.Sourceeffectid = None

	def updateEffectOrder(self):
		order = len(self.effects)

		nextEffectID = self.headEffectID
		while nextEffectID is not None:
			assert order > 0, 'effect order should never drop below 1'
			effect = self.effects[nextEffectID]
			sectionOrder = effect.op('./tox').par.Sectionorder
			if sectionOrder.eval() != order:
				self.logDebug(f'setting {nextEffectID} section order to {order}')
				sectionOrder.val = order
			order -= 1
			nextEffectID = getSourceID(effect)

	def ClearEffect(self, effectID: int):
		effect = self.effects.pop(effectID, None)

		if effect is None:
			self.logWarning(f'could not find requested effect {effectID} to clear')
			return

		self.removeFromChain(effect, effectID)

		effect.destroy()
		self.updatEffectNetworkPositions()
		self.logDebug(f'effect {effectID} cleared')

	def findEffectWithSource(self, effectID: int):
		self.logDebug(f'looking for effect -> {effectID}')
		effect = self.effects[self.headEffectID]
		sourceEffectID = getSourceID(effect)

		while sourceEffectID != effectID:
			effect = self.effects[sourceEffectID] if sourceEffectID is not None else None
			assert effect is not None, f'could not find effect -> {effectID}'
			sourceEffectID = getSourceID(effect)

		self.logDebug(f'found {effect.digits} -> {effectID}')
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
