"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
import os
import re

from tda import LoadableExt
from tdaUtils import layoutComps


def getClipLocation(address):
	m = re.match(r'/composition/layers/(\d+)/clips/(\d+)/?.*', address)
	assert m, 'expected to match layer and clip number in {}'.format(address)

	return (int(m.group(1)), int(m.group(2)))


def toxPath(toxName):
	return 'composition://{}.tox'.format(toxName)


def autoloadIfNecessary(compositionCtrl, waitTime=0, waitUntil=5):
	if compositionCtrl.Loaded:
		compositionCtrl.logDebug(
			'autoload unncessary, composition Loaded by other means'
		)
		return

	if waitTime < waitUntil:
		compositionCtrl.logDebug(
			'waiting {}/{} frames before autoloading'.format(waitTime, waitUntil)
		)
		run(
			'args[0](args[1], waitTime=args[2])',
			autoloadIfNecessary,
			compositionCtrl,
			waitTime + 1,
			delayFrames=1
		)
		return

	compositionCtrl.logInfo(
		'autolating composition after waiting {} frames'.format(waitUntil)
	)
	compositionCtrl.Reload()


class CompositionCtrl(LoadableExt):
	@property
	def compositionToxPath(self):
		return toxPath(self.render.par.Compositionname)

	@property
	def compositionFilePath(self):
		return tdu.expandPath(self.compositionToxPath)

	def __init__(
		self, ownerComponent, logger, dispatcher, render, clipCtrl, deckCtrl,
		layerCtrl, thumbnails
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.dispatcher = dispatcher
		self.render = render
		self.clipCtrl = clipCtrl
		self.deckCtrl = deckCtrl
		self.layerCtrl = layerCtrl
		self.thumbnails = thumbnails

		self.initTemplate = ownerComponent.op('execute_initTemplate')
		# TODO: should we initialize/reset this to None this like in the other controllers?
		self.compositionContainer = ownerComponent.op('../composition')

		dispatcher.MapMultiple(
			{
				'/composition/reload': {
					'handler': self.Reload,
					'sendAddress': False
				},
				'/composition/reinit': {
					'handler': self.reinit,
					'sendAddress': False
				},
				'/composition/new': {
					'handler': self.New,
					'sendAddress': False
				},
				'/composition/save': {
					'handler': self.Save,
					'sendAddress': False
				},
				'/composition/layers/*/clips/*/connect': {
					'handler': self.ConnectClip
				},
				'/composition/layers/*/clips/*/clear': {
					'handler': self.ClearClip
				},
				'/composition/layers/*/clips/*/source/load': {
					'handler': self.LoadClip
				},
			}
		)

		self.logInfo('initialized')
		autoloadIfNecessary(self)

	def reinit(self):
		"""
		This is mainly for debugging the initial state before things are loaded
		"""
		self.setUnloaded()
		self.reinitControllers()
		self.clearCompositionContents()
		self.logInfo('reinitialized')

	def New(self):
		self.Reload(createNew=True)

	def Reload(self, createNew=False):
		self.setLoading()

		if not createNew and not os.path.isfile(self.compositionFilePath):
			self.logDebug(
				'configured composition does not exist, creating new instead of loading'
			)
			createNew = True

		if createNew:
			self.logInfo('creating new composition')
		else:
			self.logInfo('reloading composition')

		self.reinitControllers()
		self.clearCompositionContents()
		self.compositionContainer.par.externaltox = self.compositionToxPath

		if not createNew:
			self.logDebug('calling reinitnet on composition')
			self.compositionContainer.par.reinitnet.pulse()
			# NOTE: composition init script will call "Load"
			return

		self.logDebug('copying init script into composition')
		initScript = self.compositionContainer.copy(
			self.initTemplate, name='execute_onInit'
		)
		initScript.par.active = 1

		self.Load()
		self.layoutCompositionContainer()

	def Load(self, fromComp=False):
		"""
		NOTE: This is called in the init script injection into compositions
		to finish bootstraping
		"""
		self.logger.Info(fromComp or self.ownerComponent, 'loading composition')

		self.loadControllers()
		self.setLoaded()
		self.thumbnails.Sync()
		self.logInfo('loaded')

	# TODO: saveAs
	def Save(self):
		if not self.Loaded:
			self.logWarning('composition not loaded, cannot save')
			return

		savePath = self.compositionFilePath
		self.logInfo('saving composition to {}'.format(savePath))
		self.compositionContainer.save(savePath)

	def OnCompNameChange(self):
		# TODO: noop if not different?
		setPath = self.compositionContainer.par.externaltox
		newPath = self.compositionToxPath
		self.logInfo('composition changed from {} to {}'.format(setPath, newPath))
		self.Reload()

	def reinitControllers(self):
		self.logInfo('reinitilizing controllers')
		self.clipCtrl.Reinit()
		self.deckCtrl.Reinit()
		self.layerCtrl.Reinit()

	def loadControllers(self):
		self.logInfo('loading controllers')
		self.clipCtrl.Load()
		self.deckCtrl.Load()
		self.layerCtrl.Load()

	def clearCompositionContents(self):
		self.logInfo('clearing composition container')
		for op in self.compositionContainer.findChildren(depth=1):
			self.logDebug('clearing {}'.format(op.path))
			op.destroy()
		self.compositionContainer.par.externaltox = ''

	def LoadClip(self, clipAddress, sourceType, name, path):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.GetClipID(clipLocation)

		if clipID is not None:
			self.clipCtrl.ReplaceSource(sourceType, name, path, clipID)
		else:
			clip = self.clipCtrl.CreateClip(sourceType, name, path)
			self.deckCtrl.SetClip(clipLocation, clip.digits)

	def ClearClip(self, clipAddress):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.ClearClip(clipLocation)

		if clipID is not None:
			self.clipCtrl.DeleteClip(clipID)
			self.layerCtrl.ClearClipID(clipID)

	def ConnectClip(self, clipAddress):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.GetClipID(clipLocation)
		previousClipID = self.layerCtrl.SetClip(clipLocation[0], clipID)

		if clipID is not None:
			self.clipCtrl.ActivateClip(clipID)

		if previousClipID is not None and previousClipID != clipID:
			self.clipCtrl.DeactivateClip(previousClipID)

	def layoutCompositionContainer(self):
		layoutComps(self.compositionContainer.findChildren(depth=1))
