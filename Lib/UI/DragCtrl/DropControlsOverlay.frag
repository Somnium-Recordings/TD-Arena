uniform float uDividerWidth;
uniform vec4 uAccentColor;
uniform float uDropState;
uniform float uCornerSize;
uniform float uBoxSize;
uniform float uTotalBoxes;
uniform float uActiveBoxIndex;
uniform vec4 uInactiveBoxColor;

vec2 uRes = uTDOutputInfo.res.zw;

float isDropState(float check) {
	return step(check, uDropState) - step(check + .5, uDropState);
}

float borderLeft() {
	return (1. - step(uDividerWidth, gl_FragCoord.x));
}

float borderRight() {
	return step(uRes.x - uDividerWidth, gl_FragCoord.x);
}

float borderBottom() {
	return (1. - step(uDividerWidth, gl_FragCoord.y));
}

float borderTop() {
	return step(uRes.y - uDividerWidth, gl_FragCoord.y);
}

float cornerSide(float edgeSize, float coord) {
	return 1. - (step(uCornerSize, coord) - step(edgeSize - uCornerSize, coord));
}

float corners() {
	return min(1.,
		borderLeft() * cornerSide(uRes.y, gl_FragCoord.y)
		+ borderRight() * cornerSide(uRes.y, gl_FragCoord.y)
		+ borderBottom() * cornerSide(uRes.x, gl_FragCoord.x)
		+ borderTop() * cornerSide(uRes.x, gl_FragCoord.x)
	);
}

float box(vec2 bottomLeft, vec2 topRight) {
	vec2 pct = step(bottomLeft, gl_FragCoord.xy) - step(topRight, gl_FragCoord.xy);

	return pct.x * pct.y;
}

float activeBox() {
	float halfBoxSize = uBoxSize / 2.;
	float boxContainerLeft = -1. * (uTotalBoxes * uBoxSize) / 2.;
	float activeBoxXOffset = boxContainerLeft + (uActiveBoxIndex * uBoxSize) + halfBoxSize;

	vec2 midPoint = uRes * .5;
	midPoint.x += activeBoxXOffset;

	return box(
	  midPoint - halfBoxSize,
	  midPoint + halfBoxSize
	);
}

float inactiveBoxes() {
	vec2 midPoint = uRes * .5;
	float halfBoxSize = uBoxSize / 2.;
  float containerSize = uTotalBoxes * uBoxSize;

  vec2 bottomLeft = midPoint - vec2(containerSize / 2, halfBoxSize);
  vec2 topRight = midPoint + vec2(containerSize / 2, halfBoxSize);

	return box(bottomLeft, topRight);
}

out vec4 fragColor;
void main()
{
  float activeBoxPct = step(2., uTotalBoxes) * activeBox();
  float inactiveBoxesPct = isDropState(1.) * step(2., uTotalBoxes) * (inactiveBoxes() - activeBoxPct);
	float dropControlPct = isDropState(1.) * min(1, corners() + activeBoxPct);
	dropControlPct += isDropState(2.) * borderLeft();
	dropControlPct += isDropState(3.) * borderRight();
	dropControlPct += isDropState(4.) * borderBottom();
	dropControlPct += isDropState(5.) * borderTop();

	vec4 color = dropControlPct * uAccentColor;

  color += inactiveBoxesPct * uInactiveBoxColor;

	fragColor = TDOutputSwizzle(color);
}
