
uniform float uBorderState;
uniform vec4 uHoverBorderColor;
uniform vec4 uActiveBorderColor;
uniform float uBorderWidth;

out vec4 fragColor;

vec2 uRes = uTD2DInfos[0].res.zw;

float borderLeft() {
	return (1. - step(uBorderWidth, gl_FragCoord.x));
}

float borderRight() {
	return step(uRes.x - uBorderWidth, gl_FragCoord.x);
}

float borderBottom() {
	return (1. - step(uBorderWidth, gl_FragCoord.y));
}

float borderTop() {
	return step(uRes.y - uBorderWidth, gl_FragCoord.y);
}

float isBorderState(float check) {
	return step(check, uBorderState) - step(check + .5, uBorderState);
}

void main()
{
	float isBorder = min(1, borderLeft() + borderRight() + borderBottom() + borderTop());
	float hoverBorderPct = isBorderState(1.) * isBorder;
	float activeBorderPct = isBorderState(2.) * isBorder;

	vec4 color = texture(sTD2DInputs[0], vUV.st) * max(0, (1 - hoverBorderPct - activeBorderPct))
		+ hoverBorderPct * uHoverBorderColor
		+ activeBorderPct * uActiveBorderColor;

	fragColor = TDOutputSwizzle(color);
}
