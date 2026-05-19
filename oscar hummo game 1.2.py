import pyxel

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        
        self.sprites = [
            [32, 0],   
            [48, 0],   
            [32, 16],  
            [48, 16]   
        ]
        self.current_direction = 1 

    def update(self):
        self.last_x = self.x  
        self.last_y = self.y

        if pyxel.btn(pyxel.KEY_UP): 
            self.y -= self.speed
            self.current_direction = 0
            
        elif pyxel.btn(pyxel.KEY_DOWN): 
            self.y += self.speed
            self.current_direction = 1

        elif pyxel.btn(pyxel.KEY_LEFT): 
            self.x -= self.speed
            self.current_direction = 3 

        elif pyxel.btn(pyxel.KEY_RIGHT): 
            self.x += self.speed
            self.current_direction = 2  

    def undo_move(self):
        self.x = self.last_x
        self.y = self.last_y

    def draw(self):
        u_source = self.sprites[self.current_direction][0]
        v_source = self.sprites[self.current_direction][1]
        pyxel.blt(self.x, self.y, 0, u_source, v_source, 16, 16, 0)

class Game:
    def __init__(self):
        pyxel.init(192, 128, title="Project Exodus (12x8 Grid Mode)")
        
        try:
            pyxel.load("assets.pyxres")
        except:
            pass # Fails gracefully if assets don't exist yet
        
        # Original colors for reverting Map palettes
        self.original_color_3 = pyxel.colors[3]
        self.original_color_11 = pyxel.colors[11]
        
        self.player = Player(128, 64) 
        
        # --- MAP AND STATE VARIABLES ---
        self.state = 0
        self.map_coords = (0, 0) # Coordinate Grid System
        self.valid_maps = [
            (0, 0), # Map 0: Cryopod Room
            (1, 0), # Map 1: Wasteland
            (2, 0)  # Map 2: Further Wasteland
        ]
        
        self.inventory = ['key']  # Start with the key for testing
        self.intro_timer = 100  
        
        
        # --- COLLISION DICTIONARY ---
        self.colliders = [
            # --- MAP 0 (Cryopod Room) ---
            # Invisible Wall Above the Door
            {"rect": (176, 0, 192, 48), "state": 0, "text": None, "item": None, "portrait": None},
            # Invisible Wall Below the Door
            {"rect": (176, 72, 192, 128), "state": 0, "text": None, "item": None, "portrait": None},
            # Cryopods
            {"rect": (56, 90, 152, 128), "state": 0, "text": ["A row of cryopods.", "This cracked one is mine."], "item": None, "portrait": None},
            # Chest
            {"rect": (0, 0, 36, 20), "state": 0, "text": ["An old chest.", 'Inside, you find a key!'], "item": "key", "portrait": None},
            # Door
            {"rect": (176, 48, 192, 72), "state": 0, "text": ["A sealed door. Requires a key."], "item": None, "portrait": None, "playerCanPass": lambda: "key" in self.inventory},
            
            # The Lake (Map 1)
            {"rect": (72, 72, 96, 80), "state": 1, "text": ["A beautiful lake.", "Water is purple and murky.", "You can barely see something shiny at the bottom"], "item": None, "portrait": None},
            {"rect": (64, 80, 112, 96), "state": 1, "text": ["A beautiful lake.", "Water is purple and murky.", "You can barely see something shiny at the bottom"], "item": None, "portrait": None},
            {"rect": (72, 96, 104, 104), "state": 1, "text": ["A beautiful lake.", "Water is purple and murky.", "You can barely see something shiny at the bottom"], "item": None, "portrait": None},
            {"rect": (80, 104, 96, 112), "state": 1, "text": ["A beautiful lake.", "Water is purple and murky.", "You can barely see something shiny at the bottom"], "item": None, "portrait": None},
            
            # Fisherman
            {"rect": (112, 80, 128, 96), "state": 1, "text": ["Quiet down, you'll scare the fish.", "Hope you're ready for what's out here."], "item": None, "portrait": (0, 0)}
        ]
        
        self.active_dialogue = None
        self.can_interact = False
        
        pyxel.run(self.update, self.draw)

    def update(self):
        # 1. Intro Timer
        if self.intro_timer > 0:
            self.intro_timer -= 1
        
        # 2. Main Game Loop (Only runs if timer is done and no dialogue is open)
        elif self.active_dialogue == None:  
            self.player.update()
            self.collide()
            self.handle_boundaries() # <--- ALL map logic is handled entirely by this!
            
        # 3. Interactions (Runs constantly so you can press Space to close text)
        self.interaction()

    def handle_boundaries(self):
        current_x, current_y = self.map_coords
        
        # --- GOING LEFT ---
        if self.player.x < 0:
            target_map = (current_x - 1, current_y)
            self.change_map(target_map, spawn_x=176, spawn_y=self.player.y)

        # --- GOING RIGHT ---
        elif self.player.x > 176:
            target_map = (current_x + 1, current_y)
            self.change_map(target_map, spawn_x=16, spawn_y=self.player.y)
                
        # --- GOING DOWN ---
        elif self.player.y > 114:
            target_map = (current_x, current_y + 1)
            self.change_map(target_map, spawn_x=self.player.x, spawn_y=16)
                
        # --- GOING UP ---
        elif self.player.y < 0:
            target_map = (current_x, current_y - 1)
            self.change_map(target_map, spawn_x=self.player.x, spawn_y=114)

    def change_map(self, target_map, spawn_x, spawn_y):
        # Checks if the map actually exists
        if target_map in self.valid_maps:
            self.map_coords = target_map
            self.player.x = spawn_x
            self.player.y = spawn_y
            
            # --- SYNCRONIZE SYSTEM ---
            # Update self.state so the colliders and drawing engine know where we are!
            if target_map == (0, 0): 
                self.state = 0
                # Revert to Map 0 Colors
                #pyxel.colors[3] = self.original_color_3
                #pyxel.colors[11] = self.original_color_11
                
            elif target_map == (1, 0): 
                self.state = 1
                # Wasteland Colors
                #pyxel.colors[11] = 0x2d5c27  
                #pyxel.colors[3]  = 0x4a3d28  
                
            elif target_map == (2, 0): 
                self.state = 2
                
        else:
            # If map doesn't exist, push player back inside the screen!
            if self.player.x < 0: self.player.x = 0
            if self.player.x > 176: self.player.x = 176
            if self.player.y < 0: self.player.y = 0
            if self.player.y > 114: self.player.y = 114

    def collide(self):
        for collider in self.colliders:
            x1, y1, x2, y2 = collider["rect"]
            state = collider["state"]
            
            if x1 <= self.player.x <= x2 and y1 <= self.player.y <= y2 and self.state == state:
                if "playerCanPass" in collider and callable(collider["playerCanPass"]):
                    if not collider["playerCanPass"]():
                        self.player.undo_move()
                else:
                    self.player.undo_move()
                
    def interaction(self):
        self.can_interact = False 
        margin = 5 
        
        if self.active_dialogue != None:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.active_dialogue = None 
            return 
            
        for collider in self.colliders:
            x1, y1, x2, y2 = collider["rect"]
            if (x1 - margin) <= self.player.x <= (x2 + margin) and \
               (y1 - margin) <= self.player.y <= (y2 + margin) and \
               self.state == collider["state"] and \
               collider["text"] != None: # <--- The Magic Line
                   
                self.can_interact = True
                if pyxel.btnp(pyxel.KEY_SPACE):
                    self.active_dialogue = collider
                    
                    item = collider["item"]
                    if item != None and item not in self.inventory:
                        self.inventory.append(item)

    def draw(self):
        pyxel.cls(0)
        if self.state in [1, 2]:
            pyxel.pal(12, 3)
            # Replace the Green base (11) with Red (8)
            pyxel.pal(11, 9)
            # Replace the Highlights/Greys (3) with Orange (9)
            pyxel.pal(3, 4)
            # Optional: Turn the water/details into Yellow (10) for a lava vibe
            pyxel.pal(5, 10) 
            
        # --- DRAW MAPS ---
        if self.state == 0 :
            pyxel.bltm(0, 0, 0, 0, 0, 192, 128)
            self.player.draw()
            if self.intro_timer > 0:
                pyxel.rect(35, 5, 120, 30, 0) 
                pyxel.text(60, 10, "STATUS: WAKING...", 2)
                pyxel.text(40, 20, "LOCATION : CRYOPOD CHAMBER", 2)
                pyxel.rect(46, 28, self.intro_timer // 1.5, 2, 2)
            
        elif self.state == 1:
            pyxel.bltm(0, 0, 0, 192, 0, 192, 128)
            self.player.draw()

        elif self.state == 2:
            pyxel.bltm(0, 0, 0, 384, 0, 192, 128)
            self.player.draw()

        # --- DRAW TOOLTIPS ---
        if self.can_interact == True and self.state == 0:
            prompt = "? PRESS SPACE"
            box_x = self.player.x - 16 
            if self.player.y < 64: box_y = self.player.y + 20
            else:                  box_y = self.player.y - 14
            pyxel.rect(box_x, box_y, 56, 11, 0)      
            pyxel.text(box_x + 3, box_y + 3, prompt, 7) 
            
        elif self.can_interact == True and self.state != 0:
            prompt = "?"
            box_x = self.player.x + 3
            if self.player.y < 64: box_y = self.player.y + 5
            else:                  box_y = self.player.y - 14
            pyxel.rect(box_x, box_y, 9, 9, 0)       
            pyxel.text(box_x + 3, box_y + 2, prompt, 7) 

        # --- DIALOGUE DRAWING ---
        if self.active_dialogue != None:
            # Draw Face
            if "portrait" in self.active_dialogue and self.active_dialogue["portrait"] != None:
                pyxel.cls(0) 
                u, v = self.active_dialogue["portrait"]
                pyxel.blt(64, 10, 1, u, v, 64, 64, 0)
                
            # Draw Text Box
            pyxel.rect(10, 80, 172, 45, 0)
            pyxel.rectb(10, 80, 172, 45, 7)
            
            lines = self.active_dialogue["text"]
            y_offset = 86
            for line in lines:
                pyxel.text(16, y_offset, line, 7)
                y_offset += 10 
        pyxel.pal()

Game()