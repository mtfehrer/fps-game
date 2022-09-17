from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


MAP_SIZE = (5, 5)
MAP = [["01", "00", "01", "00", "01"],
       ["00", "00", "00", "00", "00"],
       ["01", "00", "02", "00", "01"],
       ["00", "00", "00", "00", "00"],
       ["01", "00", "01", "00", "01"]]

FLOOR_SIZE = (120, 120)
ENEMY_MAX_HP = 20
PLAYER_MIN_SPEED = 15
PLAYER_MAX_SPEED = 50
ACCELERATION = 40
FRICTION = 3

class Game(Ursina):
	def __init__(self):
		super().__init__()
		global ursfx
		from ursina.prefabs.ursfx import ursfx
		window.fullscreen = True
		window.exit_button.visible = False
		Entity.default_shader = lit_with_shadows_shader

		self.sun = DirectionalLight()
		self.sun.look_at((-1, -1, -1))
		self.ground = Entity(model="quad", texture="grass", scale_x=FLOOR_SIZE[0], scale_y=FLOOR_SIZE[1], rotation_x=90, color=color.white, collider="box")
		self.walls = self.create_walls()
		self.player = FirstPersonController(model="cube", speed=PLAYER_MIN_SPEED, mouse_sensitivity=(80, 80), position=(0, 5, 0))
		self.player.collider = BoxCollider(self.player, size=(1, 3, 1))
		self.gun = Entity(parent=camera, model="cube", scale=(2, 0.3, 0.3), texture="white_cube", color=color.black, position=(1, -0.5, 1), rotation=(90, 0, 90), on_cooldown=False)
		self.gun.muzzle_flash = Entity(parent=self.gun, model="cube", scale=(2, 2, 0.1), position=(-0.6, 0, 0), rotation_y=90, color=color.yellow, enabled=False)
		self.enemies = [Enemy() for num in range(5)]

	def create_walls(self):
		walls = []
		scale = (FLOOR_SIZE[0] / MAP_SIZE[0], 5, FLOOR_SIZE[1] / MAP_SIZE[1])
		for o, row in enumerate(MAP):
			for i, col in enumerate(row):
				if col != "00":
					x = (scale[0] * i) - (FLOOR_SIZE[0] / 2) + (scale[0] / 2)
					y = int(col)
					z = (scale[2] * o) - (FLOOR_SIZE[1] / 2) + (scale[2] / 2)
					walls.append(Entity(model="cube", texture="brick", collider="box", scale=scale, position=(x, y, z)))
		return walls

	def shoot(self):
		if not self.gun.on_cooldown:
			self.gun.on_cooldown = True
			ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
			self.gun.muzzle_flash.enabled = True
			invoke(setattr, self.gun.muzzle_flash, "enabled", False, delay=0.05)
			if mouse.hovered_entity and mouse.hovered_entity.name == "enemy":
				mouse.hovered_entity.hp -= 1
				mouse.hovered_entity.blink(color.red, duration=0.1)
			invoke(setattr, self.gun, "on_cooldown", False, delay=0.12)

	def update(self):
		if held_keys["escape"]: sys.exit()
		if held_keys["left mouse"]: self.shoot()
		
		if not self.player.grounded:
			self.player.speed += ACCELERATION * time.dt
		else:
			drop = self.player.speed * FRICTION * time.dt
			self.player.speed *= max(PLAYER_MIN_SPEED, self.player.speed - drop) / self.player.speed
			if self.player.speed > PLAYER_MAX_SPEED: self.player.speed = PLAYER_MAX_SPEED

class Enemy(Entity):
	def __init__(self):
		x, z = random.randint(-FLOOR_SIZE[0] / 2, FLOOR_SIZE[0] / 2), random.randint(-FLOOR_SIZE[0] / 2, FLOOR_SIZE[1] / 2)
		super().__init__(model="cube", scale=(2, 3, 2), position=(x, 1.5, z), color=color.white, collider="box")
		self.hp = 20
		self.health_bar = Entity(parent=self, model="cube", color=color.red, scale=(self.hp / ENEMY_MAX_HP, 0.1, 0.1), position=(0, 0.8, 0))

	def update(self):
		if self.hp <= 0:
			destroy(self)
			return
		self.health_bar.scale_x = self.hp / ENEMY_MAX_HP
		self.look_at_2d(player.position, axis="y")
		hit_info = raycast(self.position, self.forward, distance=FLOOR_SIZE[0], ignore=(self,))
		if hit_info.entity == player:
			if distance_xz(player.position, self.position) > 5:
				self.position += self.forward * time.dt * 2

if __name__ == "__main__":
	game = Game()
	update = game.update
	player = game.player
	game.run()