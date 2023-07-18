from .utils import normalizeSourcePath


def test_normalizeSourcePath():
	assert normalizeSourcePath('/foo') == '/foo'
	assert normalizeSourcePath('/foo/render/bar') == '/foo/render/bar'
	assert normalizeSourcePath('/render') == '/tdArena/engine_render'
	assert normalizeSourcePath('/render/foo') == '/tdArena/engine_render/foo'
