from tkinter import *
from tkinter import simpledialog
import re
import math


"""Define some constants going to use. 1280x720 is used. DELAY is for speed of the game(around 60 Frames per second)."""
class constants:
	width = 1280
	height = 700
	DELAY = 100//6
	lives = 3                   #Default Lives
	bricks_per_line = 17		#Bricks per line

"""Main Class for brick,ball, and paddle."""
class game_objects:
	def __init__(self,canvas,obj):
		self.canvas = canvas
		self.obj = obj

	##Return Position
	def get_position(self):
		return self.canvas.coords(self.obj)

	def move_to(self,x,y):
		self.canvas.move(self.obj,x,y)

	def delete(self):
		self.canvas.delete(self.obj)

	def reset(self,x0,y0,x1,y1):
		self.canvas.coords(self.obj,x0,y0,x1,y1)

	def configure(self,color):
		self.canvas.itemconfig(self.obj,fill=color)

"""Ball Class Inherited from game_objects. Speed,radius, and initial angle defined"""
class ball(game_objects):
	def __init__(self,canvas):
		self.radius = 10
		self.speed = 7
		self.angle = math.radians(90)
		item = canvas.create_oval(0, 0, 0, 0)
		super(ball,self).__init__(canvas,item)

    # Move things with reflection defined except for bottom
	def update(self):
		pos = self.get_position()
		if pos[0]<0 or pos[2]>constants.width:
			self.angle = math.radians(180) - self.angle
		elif pos[1]<40:
			self.angle = -self.angle
		self.move_to(self.speed*math.cos(self.angle),-self.speed*math.sin(self.angle))

"""Paddle Class Inherited from game_objects. Speed,Width,Height defined. self.thrown is for whether ball is thrown from the bar or not(initiated with FALSE)"""
class paddle(game_objects):
	def __init__(self,canvas):
		self.thrown = False
		self.width = 120
		self.height = 25
		self.speed = 10
		item = canvas.create_rectangle(0, 0, 0, 0, width=0)
		super(paddle,self).__init__(canvas,item)

# Move paddle horizontally. Called when left or right buttons are pressed.
	def move(self,x_move):
		pos = self.get_position()
		if pos[0] < 10 and x_move < 0:
			x_move = -pos[0]
		elif pos[2] > constants.width - 10 and x_move > 0:
			x_move = constants.width - pos[2]
		self.move_to(x_move, 0)

"""Brick Class Inherited from game_objects. Colors with red,yellow,light green,light blue with hits respect to 4,3,2,1. Layers of bricks can be made from this."""
class brick(game_objects):
	colours = {4:"#FF0000",3:"#FFFF00",2:"#90ee90",1:"#add8e6"}
	width = 75
	height = 20
	def __init__(self,canvas,x0,y0,x1,y1,hits):
		self.hits = hits
		item = canvas.create_rectangle(x0,y0,x1,y1,fill=brick.colours[hits],width = 2,outline="#ffffff",state="normal")
		super(brick, self).__init__(canvas, item)

"Main Game Board Class initiated. Define constants and status flags. Created some text to display on canvas."
class Game_Board(Canvas):            #construct a window
	bricks = []
	cheatcode = "LLRRLLRR"					"""Cheat Code -->   <Left><Left><Right><Right><Left><Left><Right><Right>"""
	keyString = ""
	saveSequence = "SSSS"
	name = ""
	lead_board = ""
	def __init__(self,root):
		Canvas.__init__(self,root, bg='#ffffff', bd=0,highlightthickness=0,width=constants.width,height=constants.height)
		self.pack()
		self.saved = False
		self.level = 1
		self.key_input = [None,None,None,None]			#Left,Right,Pause(Return),Boss Key
		self.lives = constants.lives
		self.seconds = 0								#Timer
		self.score = 0
		self.lead_up = False							#Leader Board Upload Flag
		self.reload = False
		self.leader = False
		self.won = False
		self.lose = False
		self.cheated = 0
		self.NumBricks = constants.bricks_per_line * 4		#Number of bricks for one level
		self.ball = ball(self)
		self.pauseText = self.create_text(constants.width/2, constants.height/2,text="Paused\n\n\n\nPress <Return> to Resume\n\nPress <Down> for Leader Board",font=("Arial", 20),fill="#cccccc",justify="center",state="hidden")
		self.timeCounter = self.drawText(constants.width/2,10,"00:00:00",20)
		self.paddle = paddle(self)
		self.livesCounter = self.drawText(constants.width/4,10,'Lives: %s' % self.lives,20)
		self.scoreCounter = self.drawText(constants.width*3/4,10,'Score: %s' % self.score,20)
		self.Boss_text = self.create_text(constants.width/2, constants.height/2,text="Excel Loading...",font=("Arial", 25),justify="center",state="hidden")
		self.loading_bricks(self.level)
		self.game_main_loop()

		#place ball and paddle
	def configure_paddle_ball(self):
		self.itemconfig(self.livesCounter,text='Lives: %s' % self.lives)
		self.paddle.reset((constants.width - self.paddle.width)/2, constants.height - self.paddle.height,
		(constants.width + self.paddle.width)/2, constants.height)
		self.paddle.configure("#7f8c8d")
		self.ball.reset(constants.width/2 - self.ball.radius, constants.height - self.paddle.height - 2*self.ball.radius,
		constants.width/2 + self.ball.radius, constants.height - self.paddle.height)
		self.ball.configure("black")

		#Reset all properties Function.Called each time when it is loaded or win or lose.
	def reset(self):
		self.key_input = [None,None,None,None]
		self.lives = constants.lives
		self.won = False
		self.saved = False
		self.lose = False
		if self.level == 1:
			self.score = 0
		self.reload = False
		self.cheated = 0
		self.paddle.thrown = False
		self.ball.speed = 8
		self.NumBricks = constants.bricks_per_line * 4
		self.configure_paddle_ball()
		self.instruction = self.create_text(constants.width/2, constants.height/2, text="Press <Space> to Start\n\nPress <Return> to Pause\n\nPress <Space> 4 Times to Save\n\nPress <Up> to Reload\n\nPress <Down> for Leader Board", fill="#cccccc", font=("Arial", 20), justify="center")
		self.itemconfig(self.timeCounter,text ="%02d:%02d:%02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100))
		self.itemconfig(self.scoreCounter,text='Score: %s' % self.score)
		for brick in self.bricks:
			brick.delete()
			del brick
		self.bricks.clear()

#Load Bricks with respect to level. amt for amount of bricks per line. lyr for layer number. 2 layers for each color. 4 layers total.
#Display Level at very start. Default at level 1
	def loading_bricks(self,level):
		self.reset()
		if level == 1:
			for i in range(constants.bricks_per_line * 2):
				lyr = i // constants.bricks_per_line
				amt = i % constants.bricks_per_line
				self.bricks.append(brick(self,amt*brick.width,lyr*brick.height+25,(amt+1)*brick.width,(lyr+1)*brick.height+25,2))
			for i in range(constants.bricks_per_line * 2):
				lyr = i // constants.bricks_per_line
				amt = i % constants.bricks_per_line
				self.bricks.append(brick(self,amt*brick.width,(lyr+2)*brick.height+25,(amt+1)*brick.width,(lyr+3)*brick.height+25,1))
		if level == 2:
			for i in range(constants.bricks_per_line * 2):
				lyr = i // constants.bricks_per_line
				amt = i % constants.bricks_per_line
				self.bricks.append(brick(self,amt*brick.width,lyr*brick.height+25,(amt+1)*brick.width,(lyr+1)*brick.height+25,4))
			for i in range(constants.bricks_per_line * 2):
				lyr = i // constants.bricks_per_line
				amt = i % constants.bricks_per_line
				self.bricks.append(brick(self,amt*brick.width,(lyr+2)*brick.height+25,(amt+1)*brick.width,(lyr+3)*brick.height+25,3))
		self.lead_upload()
		self.showText("Level \n"+ str(level))

		#Draw Text on Canvas.Initial Options Defined.
	def drawText(self,x,y,text,size):
		font = ("Arial",size)
		return self.create_text(x,y,text=text,font=font,justify="center")

		#Create and Show Text for 3 seconds, then hideText is called..Initial Options Defined.Showed for default 2.5 seconds.
	def showText(self,text,hide=True,callback = None,speed = 2500):
		self.textStatus = True
		self.textContainer = self.create_rectangle(0, 0, constants.width, constants.height, fill="#ffffff", width=0)
		self.text = self.create_text(constants.width/2, constants.height/2, text=text, font=("Arial", 25), justify="center")
		if hide:
			self.after(speed,self.hideText)
		if callback != None:
			self.after(speed, callback)

		#Hide text. If ball is not thrown,No pause can occur. Boss Key reset for Boss_text.
	def hideText(self):
		self.textStatus = False
		self.key_input[3] = 0
		if not self.paddle.thrown:
			self.key_input[2] = 0
		self.delete(self.textContainer)
		self.delete(self.text)

            #Check Collision. Classified collisions according to where obj2 has been touched.
            #1 for Left.2 for top.3 for right.4 for bottom.
	def check_collisions(self,obj1,obj2):
		counter = 0
		obj1_coords = obj1.get_position()
		obj2_coords = obj2.get_position()
		if obj1_coords[2] < obj2_coords[0]:
			counter = 1
		if obj1_coords[3] < obj2_coords[1]:
			counter = 2
		if obj1_coords[0] > obj2_coords[2]:
			counter = 3
		if obj1_coords[1] > obj2_coords[3]:
			counter =4
		return counter

	        #Score Updating Function. Speed of paddle and ball increased when score at 100,200,300... for 1.
	def score_update(self):
		self.score += 10
		self.itemconfig(self.scoreCounter,text='Score: %s' % self.score)
		if self.score % 100 == 0:
			self.ball.speed += 1
			self.paddle.speed += 1

			#Cheat Code Function. Only Once can be used.
	def cheat_code(self):
		if self.cheatcode in self.keyString:
			if not self.cheated:
				self.lives += 10
				self.cheated = 1
				self.itemconfig(self.livesCounter,text='Lives: %s' % self.lives)

            #Saving the coordinates and number of bricks,scores,lives,time,cheated........
            #in the file Saved.txt if saving is not done yet
	def saving(self):
		if self.saveSequence in self.keyString:
			if not self.saved:
				output_text = open("Saved.txt","w")
				for i in range(len(self.bricks)):
					list = self.bricks[i].get_position()
					output_text.write(str((list[0],list[1],list[2],list[3],float(self.bricks[i].hits)))+"\n")
				output_text.write(str(self.lives)+ "\n")
				output_text.write(str(self.level)+ "\n")
				output_text.write(str(self.seconds)+ "\n")
				output_text.write(str(self.score)+"\n")
				output_text.write(str(self.cheated)+"\n")
				output_text.write(str(self.ball.speed)+"\n")
				output_text.write(str(self.paddle.speed)+"\n")
				output_text.write(str(self.NumBricks)+"\n")
				output_text.close()
				self.saved = True

        #Leaderboard function to be called from the main game loop
	def leaderboard(self):
		self.showText(self.lead_board)
		self.leader = False
		self.game_main_loop()

        #To save a leaderboard to a file.
	def lead_save(self):
		output_text = open("Leader File.txt","w")
		if self.name != None:
			self.lead_board += self.name + "\t\t" + str(self.score) + "\n"
		output_text.write(self.lead_board)
		output_text.close()

    	#To Load a leaderboard file to lead_board string.Text will show if there's no file.
	def lead_upload(self):
		try:
			if not self.lead_up:
				file = open("Leader File.txt")
				contents = []
				for x in file:
					contents.append(x.strip())
				self.lead_board += contents[0] +"\n\n"
				for i in range(2,len(contents)):
					self.lead_board += contents[i] + "\n"
				file.close()
				self.lead_up = True
		except IOError:
			self.showText("You Didn't Have A Leader Board File")

            #Reloading from saved.txt file using regex.Text will show if there is no file.
	def reloading(self):
		try:
			file = open("Saved.txt")
			contents = []
			for brickg in self.bricks:
				brickg.delete()
				del brickg
			self.bricks.clear()
			self.won = False
			self.saved = False
			self.lose = False
			self.paddle.thrown = False
			self.configure_paddle_ball()
			for x in file:
				contents.append(x.strip("\n"))
			file.close()
			self.lives,self.level,self.seconds,self.score,self.cheated,self.ball.speed,self.paddle.speed,self.NumBricks = int(contents[-8]),int(contents[-7]),float(contents[-6]),int(contents[-5]),int(contents[-4]),int(contents[-3]),int(contents[-2]),int(contents[-1])
			brick_1 = contents[:self.NumBricks]
			for x in brick_1:
				i = re.findall(r'[0-9]+\.[0-9]',x)
				self.bricks.append(brick(self,float(i[0]),float(i[1]),float(i[2]),float(i[3]),float(i[4])))
			self.itemconfig(self.timeCounter,text ="%02d:%02d:%02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100))
			self.itemconfig(self.livesCounter,text='Lives: %s' % self.lives)
			self.itemconfig(self.scoreCounter,text='Score: %s' % self.score)
			self.showText("Reloading....")
			self.reload = False
			self.game_main_loop()
		except IOError:
			self.showText("You Didn't Saved A File")
			self.reload = False
			self.game_main_loop()

            #main game loop. Game starts when only paddle.thrown is true.
            #score_update for each collision. Brick color changes also. brick will be deleted if hits of bricks reach as soon as 0.
            #Implemented the collision between bricks and paddle, and paddle and ball.
            #implemented the ball bouncing back from paddle with a math equation.(angle is updated).
            #Loses if lives < 0. Win if length of bricks hit zero.when ball dropped to the bottom, reinitiate the paddle and ball to initial situation.
            #If win or lose, call the loading_bricks to start the game again according to level. if level >2, then game ended and restart from level 1 agian.
	def game_main_loop(self):
		if not self.leader:
			if not self.reload:
				if not self.key_input[3]:
					if not self.key_input[2]:
						if self.paddle.thrown and not(self.textStatus):
							self.ball.update()
							self.seconds += 1/60
							self.itemconfig(self.timeCounter,text ="%02d:%02d:%02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100))
							i = 0
							col = self.check_collisions(self.ball,self.bricks[i])
							while i < len(self.bricks):
								if not self.check_collisions(self.ball,self.bricks[i]):
									if col ==1 or col == 3:
										self.ball.angle = math.radians(180) - self.ball.angle
									elif col ==2 or col ==4:
										self.ball.angle = -self.ball.angle
									self.bricks[i].hits -= 1
									self.score_update()
									if self.bricks[i].hits == 0:
										self.bricks[i].delete()
										del self.bricks[i]
										self.NumBricks -= 1
									else:
										self.bricks[i].configure(brick.colours[self.bricks[i].hits])
								i += 1
							self.won = len(self.bricks)==0
							if not (self.check_collisions(self.ball,self.paddle)):
								self.ball.angle = math.radians(90)- math.atan((self.ball.get_position()[0] + self.ball.radius - self.paddle.get_position()[0]-self.paddle.width/2)/70)
							elif self.ball.get_position()[3] >= constants.height:
								self.lives -= 1
								if self.lives < 0:
									self.lose = True
								else:
									self.paddle.thrown = False
									self.textStatus = False
									self.after(1,self.configure_paddle_ball)
						if self.key_input[0]:
							self.paddle.move(-self.paddle.speed)
							if not (self.paddle.thrown) and self.paddle.get_position()[0] > 0:
								self.ball.move_to(-self.paddle.speed,0)
						elif self.key_input[1]:
							self.paddle.move(self.paddle.speed)
							if not (self.paddle.thrown) and self.paddle.get_position()[2] < constants.width:
								self.ball.move_to(self.paddle.speed,0)
						self.cheat_code()
						self.saving()
						if not (self.textStatus):
							if self.won:
								self.level += 1
								if self.level <= 2:
									self.showText("You WIN!",callback = lambda:self.loading_bricks(self.level))
								else:
									self.level = 1
									self.showText("GAME ENDED!!!",callback = lambda:self.loading_bricks(self.level))
							elif self.lose:
								self.lead_save()
								self.showText("You LOSE!",callback = lambda:self.loading_bricks(self.level))
						self.after(constants.DELAY,self.game_main_loop)
					else:
						self.after(constants.DELAY,self.game_main_loop)
				else:
					if self.paddle.thrown:
						self.itemconfig(self.pauseText,state="normal")
					self.after(constants.DELAY,self.game_main_loop)

			else:
				self.reloading()

		else:
			self.leaderboard()

"""Function for key pressed"""
"""Left Key,or Right key Pressed. if ball is thrown,keyString will be passed L or R"""
def Pressed(event):
	global board
	if event.keysym == "Left":
		board.key_input[0] = 1
		if board.paddle.thrown:
			board.keyString += "L"
	elif event.keysym == "Right":
		board.key_input[1] = 1
		if board.paddle.thrown:
			board.keyString += "R"
	elif board.paddle.thrown == False and not board.key_input[2] and event.keysym == "Up":      #Only Reload works before the game started.
		board.reload = True
	elif (board.paddle.thrown == False or board.key_input[2]) and event.keysym == "Down":       #Leadership board works only before the game started and the game is paused.
		board.leader = True
	elif event.keysym == "space" and board.paddle.thrown:                                       #for saving.Only when gmae is not paused.
		board.keyString += "S"
	elif event.keysym == "space" and board.textStatus == False and not board.key_input[3]:      #to start a game.
		board.paddle.thrown = True
		board.delete(board.instruction)
	elif event.keysym == "Return" and board.paddle.thrown:                                      #To pause and resume a game.
		if board.key_input[2]:
			board.key_input[3] = 0
			board.key_input[2] = 0
			board.itemconfig(board.pauseText,state="hidden")
		else:
			board.key_input[2] = 1
			board.itemconfig(board.pauseText,state="normal")
	elif event.keysym == "BackSpace":                                                           #Boss key. paused and text will be showed for 7000 seconds. Have to resume by click return.
		if  not board.key_input[3]:
			board.key_input[3] = 1
			board.key_input[2] = 1
			board.showText("Excel Loading...",speed = 7000)

"""Function for key released.Left Key,or Right key Released."""
def Released(event):
	global board
	if event.keysym == "Left":
		board.key_input[0] = 0
	elif event.keysym == "Right":
		board.key_input[1] = 0

"""Initiated, disabled resizing in both dimension. used pixel scaling with factor 4.0"""
root = Tk()
root.title("Break Things Up!!!")

ws = root.winfo_screenwidth() # computers screen size
hs = root.winfo_screenheight()
x = (ws/2) - (constants.width/2) # calculate center
y = (hs/2) - (constants.height/2)
root.geometry('%dx%d+%d+%d' % (constants.width, constants.height, x, y))#show the window at the middle of the screen
root.resizable(False, False)
root.tk.call("tk", "scaling", 4.0)
root.bind('<KeyPress>',Pressed)
root.bind('<KeyRelease>',Released)

board = Game_Board(root)
"""Ask for the name.Leaderboard will update only name is put."""
while board.name == "":
	board.name = simpledialog.askstring("Name", "What is your name?",parent=root)
board.mainloop()
