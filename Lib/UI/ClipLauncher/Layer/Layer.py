from tda import BaseExt


class Layer(BaseExt):
	@property
	def LayerID(self):
		return self.ownerComponent.digits

	@property
	def LayerNumber(self):
		return self.ownerComponent.par.alignorder.eval()

	def __init__(self, ownerComponent, logger, uiState):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.uiState = uiState
		self.popMenu = op.TDResources.op('popMenu')

	def OpenRightClickMenu(self):
		self.popMenu.Open(
			items=['Insert Above', 'Insert Below', 'Remove'],
			callback=self.onMenuClick,
			dividersAfterItems=['Insert Below']
		)

	def onMenuClick(self, click):
		if click['callbackName'] != 'onSelect':
			raise NotImplementedError(
				f'unsupported click callback {click["callbackName"]}'
			)

		deckLayerNumber = int(self.LayerNumber - 1)
		if click['item'] == 'Insert Above':
			self.uiState.SendMessage(
				f'/selecteddeck/layers/{deckLayerNumber}/insert', 'above'
			)
		elif click['item'] == 'Insert Below':
			self.uiState.SendMessage(
				f'/selecteddeck/layers/{deckLayerNumber}/insert', 'below'
			)
		elif click['item'] == 'Remove':
			# TODO: don't allow removal of last layer
			self.uiState.SendMessage(f'/selecteddeck/layers/{deckLayerNumber}/remove')
		else:
			raise NotImplementedError(
				f'Handler for layer menu item "{click["item"]}" not implemented'
			)
