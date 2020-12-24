from tda import LoadableExt
from tdaUtils import addSectionParameters, intIfSet, layoutComps

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

	def ClearEffectState(self, effectContainerAddress):
		# TODO: when clip (or layer?) deleted, call this to ensure we have no leaks
		pass


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
		# TODO: is there a better way?
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
					'Sourceeffectid': intIfSet(effect.par.Sourceeffectid.eval())
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
		# TODO: reset all order params after creation?
		addSectionParameters(tox, order=len(self.effects), opacity=1.0)
		# TODO: after tox loaded, addSectionParameters
		# TODO: after tox loaded, addMixParameters

		self.headEffectID = effect.digits

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
			f'/composition/clips/{ownerComponent.parent.clip.digits}/effects'
		)