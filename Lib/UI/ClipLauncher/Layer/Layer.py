from tda import BaseExt


class Layer(BaseExt):

	@property
	def LayerID(self):
		return self.ownerComponent.digits

	@property
	def LayerNumber(self):
		return self.ownerComponent.par.alignorder.eval()

	@property
	def CtrlSrcName(self) -> str:
		return f'ui:clipLauncher:{self.ownerComponent.name}'

	@property
	def ctrlOpacityAddress(self) -> str:
		return f'/composition/layers/{self.LayerID}/video:Opacity'

	def __init__(self, ownerComponent, logger, uiState):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.uiState = uiState
		self.popMenu = op.TDResources.op('popMenu')
		self.opacityCtrl = ownerComponent.op('sliderVert')
		self.registerLayerOpacityCtrl()

	def OpenRightClickMenu(self):
		self.popMenu.Open(
			items=['Insert Above', 'Insert Below', 'Remove'],
			callback=self.onMenuClick,
			dividersAfterItems=['Insert Below']
		)

	def onMenuClick(self, click):  # noqa: ANN001
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

	def updateOpacityCtrlValue(self, _address: str, newValue: float) -> None:
		self.opacityCtrl.par.Value0 = newValue

	def registerLayerOpacityCtrl(self):
		if 'Template' in self.ownerComponent.name:
			return

		self.opacityCtrl.par.Onvaluechangescript0 = (
			f"op.ui_state.UpdateCtrlValue('{self.ctrlOpacityAddress}', me.par.Value0.eval(), '{self.CtrlSrcName}')"
		)

		self.uiState.RegisterCtrl(
			self.ctrlOpacityAddress, self.CtrlSrcName, self.updateOpacityCtrlValue
		)

	def OnBeforeDestroy(self):
		self.uiState.DeregisterCtrl(self.ctrlOpacityAddress, self.CtrlSrcName)
