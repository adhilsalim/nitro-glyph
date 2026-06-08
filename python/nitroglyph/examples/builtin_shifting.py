from nitroglyph import NitroGlyphController, Direction

ngc = NitroGlyphController()

for dir in [Direction.RIGHT_TO_LEFT, Direction.LEFT_TO_RIGHT]:
    ngc.shifting(
		color=(255, 0, 0),
		speed=5,
		brightness=100,
		direction=dir,
		duration=2
	)

ngc.clear()
