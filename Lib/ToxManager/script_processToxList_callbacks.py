import re

from tdaUtils import filePathToName, filePathToStemSlug, getCellValues


# me - this DAT
# scriptOp - the OP which is cooking
#
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
def onSetupParameters(_scriptOp):  # noqa: ANN001
	return


# called whenever custom pulse parameter is pushed
def onPulse(_par):  # noqa: ANN001
	return


NAME_COL = 0
PATH_COL = 1
FILE_PATH_COL = 3

COMPOSITION_ROOT = '/tdArena/render/composition'

# /tdArena/render/composition/clips/clip0/video/effects/effect0/tox
# /tdArena/render/composition/layers/layer1/video/effects/effect0/tox
# -> (clip0, effect0) and (layer1, effect0)
EFFECT_SLUG_RE = re.compile(
	r'/tdArena/render/composition/(?:clips|layers)/(.*)/video/effects/(.*)/tox'
)
# /tdArena/render/composition/clips/clip0/video/source/tox
# -> (clip0)
GENERATOR_SLUG_RE = re.compile(
	r'/tdArena/render/composition/clips/(.*)/video/source/tox'
)

STATIC_PATHS = [
	# Name          path                       networkPath                    filePath   dirty  lastEditedTime
	['TD Arena',    '/tdArena',                '/tdArena',                    '',        '',    ''],
	['Composition', '/composition',            COMPOSITION_ROOT,              '',        '',    ''],
	['Effects',     '/composition/effects',    '',                            '',        '',    ''],
	['Generators',  '/composition/generators', '',                            '',        '',    '']
] # yapf: disable


def onCook(scriptOp):  # noqa: ANN001
	baseGeneratorPath = tdu.expandPath('generator://')
	baseEffectPath = tdu.expandPath('effect://')

	scriptOp.clear()
	heading, *toxList = scriptOp.inputs[0].rows()
	scriptOp.appendRow(heading)
	scriptOp.appendRows(STATIC_PATHS)

	compositionRoots = {}

	for row in toxList:
		toxData = getCellValues(row)

		# This should always be manually saved, and rarely so
		if toxData[PATH_COL] == COMPOSITION_ROOT:
			continue

		toxData[NAME_COL] = filePathToName(toxData[FILE_PATH_COL])
		if toxData[NAME_COL] == 'T D Arena Render':
			toxData[NAME_COL] = 'Render'

		if toxData[FILE_PATH_COL].startswith(baseEffectPath):
			rootSlug = filePathToStemSlug(toxData[FILE_PATH_COL])
			rootPath = f'/composition/effects/{rootSlug}'
			compositionRoots[toxData[NAME_COL]] = rootPath

			m = re.match(EFFECT_SLUG_RE, toxData[PATH_COL])
			effectSlug = f'{m.group(1)}-{m.group(2)}'
			toxData[PATH_COL] = f'{rootPath}/{effectSlug}'
			toxData[NAME_COL] = effectSlug
		elif toxData[FILE_PATH_COL].startswith(baseGeneratorPath):
			rootSlug = filePathToStemSlug(toxData[FILE_PATH_COL])
			rootPath = f'/composition/generators/{rootSlug}'
			compositionRoots[toxData[NAME_COL]] = rootPath

			m = re.match(GENERATOR_SLUG_RE, toxData[PATH_COL])
			generatorSlug = m.group(1)
			toxData[PATH_COL] = f'{rootPath}/{generatorSlug}'
			toxData[NAME_COL] = generatorSlug

		scriptOp.appendRow(toxData)

	for rootName, rootPath in compositionRoots.items():
		scriptOp.appendRow([rootName, rootPath])
