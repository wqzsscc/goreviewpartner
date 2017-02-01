from functools import partial
from copy import deepcopy as copy

space=20

fuzzy=0.2


from random import random

from Tkinter import Canvas


class Goban(Canvas):
	def __init__(self,dim,**kwargs):
		self.dim=dim
		Canvas.__init__(self,**kwargs)
		self.prepare_mesh()
		
	def prepare_mesh(self):
		f=fuzzy
		self.mesh=[[[0.0,0.0] for row in range(self.dim)] for col in range(self.dim)]
		for i in range(self.dim):
			f1=random()*f-f/2
			f2=random()*f-f/2
			for j in range(self.dim):
				self.mesh[i][j][1]=f1
				self.mesh[j][i][0]=f2
		
	def ij2xy(self,i,j):
		global space
		dim=self.dim
		y=(.5+dim-(0.5+i))*space
		#y=((1.+i))*space
		x=(1.+j)*space
		return x,y

	def xy2ij(self,x,y):
		dim=self.dim
		return int(round(dim-1.*y/space)),int(round(1.*x/space)-1)

	def draw_point(self,i,j,diameter,color="black",outline="black",width=1):
		global space
		x,y=self.ij2xy(i,j)
		radius=diameter*space/2
		oval=self.create_oval(x-radius,y-radius,x+radius,y+radius,fill=color,outline=outline,width=width)
		return oval

	def draw_line(self,i1,j1,i2,j2,color="black",width=1):
		x1,y1=self.ij2xy(i1,j1)
		x2,y2=self.ij2xy(i2,j2)
		self.create_line(x1,y1,x2,y2,fill=color,width=width)

	def draw_rectangle(self,i1,j1,i2,j2,color="black"):
		x1,y1=self.ij2xy(i1,j1)
		x2,y2=self.ij2xy(i2,j2)
		self.create_rectangle(x1,y1,x2,y2,fill=color)


	def display(self,grid,markup,freeze=False):
		global space
		dim=self.dim
		bg="#dddddd"
		bg="#ECCE7C"
		for item in self.find_all():self.delete(item)
		self.config(width=space*(1+dim), height=space*(1+dim))
		
		if freeze:
			black="red"
		else:
			black="black"
		
		self.draw_rectangle(-0.1,-0.1,dim-1+0.1,dim-1+0.1,black)
		self.draw_rectangle(0,0,dim-1,dim-1,bg)
		for i in range(dim):
			self.draw_line(i,0,i,dim-1,color=black)
			self.draw_line(0,i,dim-1,i,color=black)

		if dim==19:
			for i,j in [[3,3],[3,9],[9,9],[3,15],[15,15],[15,9],[9,15],[15,3],[9,3]]:
				self.draw_point(i,j,0.3,black)

		for i in range(dim):
			for j in range(dim):
				markup_color='black'
				u=i+self.mesh[i][j][0]
				v=j+self.mesh[i][j][1]
				if grid[i][j]==1:
					#black
					self.draw_point(u,v,1.0,"black")
					markup_color='white'
				if grid[i][j]==2:
					self.draw_point(u,v,1.0,"white")
				
				if type(markup[i][j]) is int:
					if markup[i][j]==0:
						if grid[i][j]==0:
							self.draw_point(u,v,0.6,color=bg,outline=bg)
						k=0.6
						
						self.draw_line(u+0.5*k,v-0*k,u-0.255*k,v+0.435*k,markup_color,width=2)
						self.draw_line(u-0.255*k,v+0.435*k,u-0.255*k,v-0.435*k,markup_color,width=2)
						self.draw_line(u-0.255*k,v-0.435*k,u+0.5*k,v-0*k,markup_color,width=2)
					else:
						x,y=self.ij2xy(u,v)
						self.create_text(x,y, text=str(markup[i][j]),font=("Arial", str(int(space/2))),fill=markup_color)
						
						
				elif markup[i][j]=="":
					#do nothing
					pass
				else:
					sequence=markup[i][j]
					markup_color=sequence[0][4]
					x,y=self.ij2xy(u,v)
					self.draw_point(u,v,0.8,color=bg,outline=markup_color)
					self.create_text(x,y, text=sequence[0][2],font=("Arial", str(int(space/2))),fill=markup_color)
					local_area=self.draw_point(u,v,1,color="",outline="")
					self.tag_bind(local_area, "<Enter>", partial(show_variation,goban=self,grid=grid,markup=markup,i=i,j=j))
		self.update_idletasks()



def show_variation():
	pass



def countlib(grid,i,j,lib=0,tab=None):
	dim=len(grid)

	if not tab:
		start=True
		tab=[]
		for p in range(dim):tab.append([0]*dim)
	else:start=False
	color=grid[i][j]
	if color==0:
		return -1
	tab[i][j]=1

	for x,y in neighborhood(i,j,dim):
		if grid[x][y]==color and tab[x][y]==0:
			lib,tab=countlib(grid,x,y,lib,tab)
		elif grid[x][y]==0 and tab[x][y]==0:
			tab[x][y]=2
			lib+=1

	if start:
		return lib
	else:
		return lib,tab

def remove_group(grid,i,j):
	color=grid[i][j]
	grid[i][j]=0
	dim=len(grid)
	for x,y in neighborhood(i,j,dim):
		if grid[x][y]==color:
			remove_group(grid,x,y)

def place(grid,i,j,color):
	grid[i][j]=color
	dim=len(grid)
	for x,y in neighborhood(i,j,dim):
		if grid[x][y]>0 and grid[x][y]!=color:
			if countlib(grid,x,y)==0:
				remove_group(grid,x,y)


def neighborhood(i,j,dim):
	list=[]
	if 0 <= i+1 <= dim-1 and 0 <= j <= dim-1:
		list.append([i+1,j])
	if 0 <= i-1 <= dim-1 and 0 <= j <= dim-1:
		list.append([i-1,j])
	if 0 <= i <= dim-1 and 0 <= j-1 <= dim-1:
		list.append([i,j-1])
	if 0 <= i <= dim-1 and 0 <= j+1 <= dim-1:
		list.append([i,j+1])
	return list