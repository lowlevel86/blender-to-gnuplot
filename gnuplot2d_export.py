#!BPY

"""
Name: 'gnuplot2d (.gnu)...'
Blender: 249
Group: 'Export'
Tip: 'Export for use with gnuplot.'
"""

# You can do whatever you want with this code

# Usage:

# Press 'n' to view the "Transform Properties" window
# Change the object name "OB:" to control line, point, or face style and color

# Examples:

# To render an object with green points and a point size of 0.4
# p0.4-#00FF00-Cube

# To render an object with red lines and a line width of 1.3
# l1.3-red-Cone

# To render an object with with gray polygons and a opacity of 80%
# f0.8-#888888-Plane


import Blender
from Blender import Window, Draw, BGL
import math
from subprocess import call, os


# change these toggles if you want a different setting on startup
removeMarginsToggle = 0
hideGraphToggle = 0
hideKeyToggle = 0
lockZoomToggle = 0
renderImgToggle = 1
showGnuplotWinToggle = 0
showBlenderWinToggle = 1


# rotate point using degrees
def degRot(horiP, vertP, degrees):

	hUc = math.cos(degrees * (math.pi * 2.0 / 360.0))
	vUc = math.sin(degrees * (math.pi * 2.0 / 360.0))

	hLine1 = hUc
	vLine1 = vUc
	hLine2 = -vUc
	vLine2 = hUc

	h = vertP * hLine2 + horiP * vLine2
	v = horiP * vLine1 + vertP * hLine1
	horiP = h
	vertP = v

	return (horiP, vertP)

# make triangle data compatible with gnuplot
def makeTri(x1, y1, x2, y2, x3, y3):
	
	# find if "x1" is horizontally between two points
	if (x1 >= x2 and x1 <= x3) or (x1 <= x2 and x1 >= x3):
		if x2 != x3:
			xA = x2
			yA = y2
			xB = x3
			yB = y3
			xMid = x1
			yMid1 = y1
			# find the vertical mid point to make two trangles become one
			yMid2 = y2 - (x2 - xMid) / (x2 - x3) * (y2 - y3)
			
			return (xA, yA, yA, xMid, yMid1, yMid2, xB, yB, yB)
		

	# find if "x2" is horizontally between two points
	if (x2 >= x1 and x2 <= x3) or (x2 <= x1 and x2 >= x3):
		if x1 != x3:
			xA = x1
			yA = y1
			xB = x3
			yB = y3
			xMid = x2
			yMid1 = y2
			# find the vertical mid point to make two trangles become one
			yMid2 = y1 - (x1 - xMid) / (x1 - x3) * (y1 - y3)

			return (xA, yA, yA, xMid, yMid1, yMid2, xB, yB, yB)

	# find if "x3" is horizontally between two points
	if (x3 >= x1 and x3 <= x2) or (x3 <= x1 and x3 >= x2):
		if x1 != x2:
			xA = x1
			yA = y1
			xB = x2
			yB = y2
			xMid = x3
			yMid1 = y3
			# find the vertical mid point to make two trangles become one
			yMid2 = y1 - (x1 - xMid) / (x1 - x2) * (y1 - y2)

			return (xA, yA, yA, xMid, yMid1, yMid2, xB, yB, yB)

	return (x1, y1, y1, x2, y2, y2, x3, y3, y3)

# script main function
def ExportToGNU(file_name):
	
	# add up the selected layers after converting to binary
	selectedLayers = Blender.Window.ViewLayers()
	selectedLayersMask = 0
	for aL in selectedLayers:
		selectedLayersMask += 1<<(aL-1)
	
	# get a list of meshes
	scene = Blender.Scene.GetCurrent()
	meshes = []
	for ob in scene.objects:
		if selectedLayersMask & ob.Layer: # use only meshes in selected layers
			obtype = ob.type
			if obtype == "Mesh":
				meshes.append(ob)
	# return if found no meshes
	
	if meshes == []:
		print("No meshes found.")
		return

	# sort meshes alphabetically
	meshNames = []
	sortedMeshNames = []
	for mesh in meshes:
		meshNames.append(mesh.getName().split('-')[-1])
		sortedMeshNames.append(mesh.getName().split('-')[-1])
	
	sortedMeshNames.sort()
	
	sortedMeshes = []
	for sortedMeshName in sortedMeshNames:
		sortedMeshes.append(meshes[meshNames.index(sortedMeshName)])
	meshes = sortedMeshes

	# change to object mode
	in_editmode = Window.EditMode()
	if in_editmode: Window.EditMode(0)


	# get the background color
	bgColor = Blender.World.GetCurrent().getHor()

	bgR = format((int(round(bgColor[0] * 255.0))), '02x')
	bgG = format((int(round(bgColor[1] * 255.0))), '02x')
	bgB = format((int(round(bgColor[2] * 255.0))), '02x')


	# find the furthest vertice values
	boundBoxObj = meshes[0].getBoundBox(1)
	xVertIni = boundBoxObj[0][0]
	yVertIni = boundBoxObj[0][1]
	xVertMax = xVertIni
	xVertMin = xVertIni
	yVertMax = yVertIni
	yVertMin = yVertIni
	for mesh in meshes:
		boundBoxObjs = mesh.getBoundBox(1)
		for i in range(0, 8):

			if xVertMin > boundBoxObjs[i][0]:
				xVertMin = boundBoxObjs[i][0]
			if xVertMax < boundBoxObjs[i][0]:
				xVertMax = boundBoxObjs[i][0]

			if yVertMin > boundBoxObjs[i][1]:
				yVertMin = boundBoxObjs[i][1]
			if yVertMax < boundBoxObjs[i][1]:
				yVertMax = boundBoxObjs[i][1]


	context = scene.getRenderingContext()


	file = open(file_name, "w")
	
	# write initial configuration info to the .gnu file

	# output to png
	if renderImgToggle:
		file.write("set terminal pngcairo size "+str(context.sizeX)+","+str(context.sizeY)+"; set output \""+context.getFrameFilename(1).split('\\')[-1].split('/')[-1].split('.')[0]+".png\"\n")
		file.write("\n")

	file.write("#set title \"Graph Title\"\n")
	file.write("#set xlabel \"X\"\n")
	file.write("#set ylabel \"Y\"\n")
	file.write("\n")
	file.write("# sets background color\n")
	file.write("set object 1 rectangle from screen -0.1,-0.1 to screen 1.1,1.1 fillcolor rgb \"#"+bgR+bgG+bgB+"\" behind\n")
	file.write("\n")
	file.write("# changes border color\n")
	file.write("set border linecolor rgb \"#555555\"\n")
	file.write("\n")
	file.write("# displays the x and y axis\n")
	file.write("set xzeroaxis linewidth 0.5 linecolor rgb \"#555555\" linetype 1\n")
	file.write("set yzeroaxis linewidth 0.5 linecolor rgb \"#555555\" linetype 1\n")
	file.write("\n")
	file.write("# displays the x and y grid\n")
	file.write("set grid xtics linecolor rgb \"#888888\" linewidth 0.2 linetype 9\n")
	file.write("set grid ytics linecolor rgb \"#888888\" linewidth 0.2 linetype 9\n")
	file.write("\n")

	if lockZoomToggle:
		if (xVertMax - xVertMin) > (yVertMax - yVertMin):
			xVertMin = -10 * (float(context.sizeX) / float(context.sizeY))
			xVertMax = 10 * (float(context.sizeX) / float(context.sizeY))
			yVertMin = -10
			yVertMax = 10
		else:
			xVertMin = -10
			xVertMax = 10
			yVertMin = -10 * (float(context.sizeY) / float(context.sizeX))
			yVertMax = 10 * (float(context.sizeY) / float(context.sizeX))
		
	file.write("# sets the axis range\n")
	file.write("set xrange ["+str(xVertMin)+":"+str(xVertMax)+"]\n")
	file.write("set yrange ["+str(yVertMin)+":"+str(yVertMax)+"]\n")
	file.write("set size ratio "+str((yVertMax-yVertMin) / (xVertMax-xVertMin))+"\n")
	file.write("\n")
	file.write("# moves the key out of the graph\n")
	file.write("set key outside vertical top right\n")
	file.write("\n")

	if hideKeyToggle:
		file.write("# hides the key\n")
		file.write("set key off\n")
		file.write("\n")

	if hideGraphToggle:
		file.write("# hides the graph\n")
		file.write("unset border\n")
		file.write("unset xtics;\n")
		file.write("unset ytics;\n")
		file.write("unset xzeroaxis;\n")
		file.write("unset yzeroaxis;\n")
		file.write("\n")

	if removeMarginsToggle:
		file.write("# removes the margins\n")
		file.write("set lmargin 0\n")
		file.write("set rmargin 0\n")
		file.write("set tmargin 0\n")
		file.write("set bmargin 0\n")
		file.write("\n")

	file.write("plot\\\n")

	skipALoop = 1
	keyNameArray = []
	pointLineFaceArray = [] #[p, l, f]

	for mesh in meshes:
		pointLineFace = ""
		pointLineFaceStopRead = "FALSE"
		sizeOrWidth = ""
		sizeOrWidthStopRead = "FALSE"
		hexColor = ""
		hexColorStopRead = "FALSE"
		keyName = ""

		for objNameChar in mesh.getName():

			# get the key name
			if hexColorStopRead == "TRUE":
				if objNameChar != ".":
					keyName += str(objNameChar)
				else:
					keyName += "_"


			# get the hex color value
			if sizeOrWidthStopRead == "TRUE":
				if objNameChar == "-":
					hexColorStopRead = "TRUE"
				if hexColorStopRead == "FALSE":
					hexColor += str(objNameChar)


			# get the size of the point or the width of the line
			if objNameChar == "-":
				sizeOrWidthStopRead = "TRUE"

			if pointLineFaceStopRead == "TRUE":
				if sizeOrWidthStopRead == "FALSE":
					sizeOrWidth += str(objNameChar)


			# get the first letter of the name to see if it is a point, line, or face
			if pointLineFaceStopRead == "FALSE":
				pointLineFace = objNameChar

			pointLineFaceStopRead = "TRUE"


		if skipALoop == 0:
			file.write(",\\\n")
		else:
			skipALoop = 0

		if pointLineFace != "" and sizeOrWidth != "" and hexColor != "" and keyName != "":

			keyNameArray.append(keyName)
			pointLineFaceArray.append(pointLineFace)

			if pointLineFace == "p":
				file.write("\""+keyName+".dat\" title \""+keyName+"\" with points pointsize "+sizeOrWidth+" pointtype 7 linecolor rgb \""+hexColor+"\"")

			if pointLineFace == "l":
				file.write("\""+keyName+".dat\" title \""+keyName+"\" with lines linewidth "+sizeOrWidth+" linecolor rgb \""+hexColor+"\"")

			if pointLineFace == "f":
				file.write("\""+keyName+".dat\" title \""+keyName+"\" with filledcurve fill transparent solid "+sizeOrWidth+" noborder linecolor rgb \""+hexColor+"\"")
		else:

			# get the key name
			keyName = ""
			for objNameChar in mesh.getName():
				if objNameChar != ".":
					keyName += str(objNameChar)
				else:
					keyName += "_"

			keyNameArray.append(keyName)
			pointLineFaceArray.append("p")

			file.write("\""+keyName+".dat\" title \""+keyName+"\" with points pointsize 0.5 pointtype 7")

		file.write("\n")

	file.close()
	
	
	#Write data to .dat files
	meshInc = 0
	for mesh in meshes:
		gnuWorkingDir = Blender.sys.dirname(file_name) + "/"
		datFileName = gnuWorkingDir + keyNameArray[meshInc] + ".dat"

		file = open(datFileName, "w")

		xVert = []
		yVert = []
		zVert = []
		for verts in mesh.getData().verts:
			# apply object size
			verts[0] *= mesh.size[0]
			verts[1] *= mesh.size[1]
			verts[2] *= mesh.size[2]

			# apply object x axis rotation
			vertsRot = degRot(verts[1], verts[2], mesh.rot[0] / (math.pi * 2.0 / 360.0))
			verts[1] = vertsRot[0]
			verts[2] = vertsRot[1]
			
			# apply object y axis rotation
			vertsRot = degRot(verts[0], verts[2], -mesh.rot[1] / (math.pi * 2.0 / 360.0))
			verts[0] = vertsRot[0]
			verts[2] = vertsRot[1]
			
			# apply object z axis rotation
			vertsRot = degRot(verts[0], verts[1], mesh.rot[2] / (math.pi * 2.0 / 360.0))
			verts[0] = vertsRot[0]
			verts[1] = vertsRot[1]
			
			# apply object location
			verts[0] += mesh.loc[0]
			verts[1] += mesh.loc[1]
			verts[2] += mesh.loc[2]

			xVert.append(verts[0])
			yVert.append(verts[1])
			zVert.append(verts[2])

		if pointLineFaceArray[meshInc] == "p":
			for vInc in range(0, len(mesh.getData().verts)):
				file.write("%f %f\n" % (xVert[vInc], yVert[vInc]))
				file.write("\n")
	
		if pointLineFaceArray[meshInc] == "l":
			for edges in mesh.getData().edges:
				file.write("%f %f\n" % (xVert[edges.v1.index], yVert[edges.v1.index]))
				file.write("%f %f\n" % (xVert[edges.v2.index], yVert[edges.v2.index]))
				file.write("\n")
				file.write("\n")
	
		if pointLineFaceArray[meshInc] == "f":
			for face in mesh.getData().faces:
				if len(face) == 4:
					gnuTri = makeTri(xVert[face[0].index], yVert[face[0].index], xVert[face[1].index], yVert[face[1].index], xVert[face[2].index], yVert[face[2].index])
					file.write("%f %f %f\n" % (gnuTri[0], gnuTri[1], gnuTri[2]))
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("\n")
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("%f %f %f\n" % (gnuTri[6], gnuTri[7], gnuTri[8]))
					file.write("\n")
					gnuTri = makeTri(xVert[face[0].index], yVert[face[0].index], xVert[face[3].index], yVert[face[3].index], xVert[face[2].index], yVert[face[2].index])
					file.write("%f %f %f\n" % (gnuTri[0], gnuTri[1], gnuTri[2]))
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("\n")
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("%f %f %f\n" % (gnuTri[6], gnuTri[7], gnuTri[8]))
					file.write("\n")
					
				if len(face) == 3:
					gnuTri = makeTri(xVert[face[0].index], yVert[face[0].index], xVert[face[1].index], yVert[face[1].index], xVert[face[2].index], yVert[face[2].index])
					file.write("%f %f %f\n" % (gnuTri[0], gnuTri[1], gnuTri[2]))
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("\n")
					file.write("%f %f %f\n" % (gnuTri[3], gnuTri[4], gnuTri[5]))
					file.write("%f %f %f\n" % (gnuTri[6], gnuTri[7], gnuTri[8]))
					file.write("\n")
	
		meshInc+=1
		file.close()

	
	
	# save the image type and render location
	savedImgType = context.imageType
	savedRenderPath = context.getRenderPath()

	# temporary set the image type and render location
	context.setImageType(17)# 4=jpeg 17=png
	context.setRenderPath(gnuWorkingDir)

	# render to image file
	if renderImgToggle:
		try:
			call(['gnuplot', file_name.split('\\')[-1].split('/')[-1]], cwd=gnuWorkingDir)
		except OSError as e:
			if e.errno == os.errno.ENOENT:
				print("Note: The blender python script needs to be able to execute gnuplot.")
	
	
	# display in wxWidgets windowed
	if showGnuplotWinToggle:
		file_name_wxt = file_name.replace(".gnu", "Wxt.gnu")
		
		file = open(file_name, "r")
		file2 = open(file_name_wxt, "w")
		
		file.next()
		file2.write("set terminal wxt size "+str(context.sizeX)+","+str(context.sizeY)+"\n")
		for line in file:
			file2.write(line)
		
		file.close()
		file2.close()

		try:
			call(['wgnuplot', '-persist', file_name_wxt.split('\\')[-1].split('/')[-1]], cwd=gnuWorkingDir)
		except OSError as e:
			if e.errno == os.errno.ENOENT:
				try:
					call(['gnuplot', '-persist', file_name_wxt.split('\\')[-1].split('/')[-1]], cwd=gnuWorkingDir)
				except OSError as e:
					if e.errno == os.errno.ENOENT:
						print("Note: The blender python script needs to be able to execute gnuplot.")
	

	if showBlenderWinToggle:
		context.play()
	
	# set the image type and render location back to the way it was
	context.setImageType(savedImgType)# 4=jpeg 17=png
	context.setRenderPath(savedRenderPath)

	
	
def FileSelectorCB(file_name):

	if not file_name.lower().endswith('.gnu'):
		file_name += '.gnu'
	ExportToGNU(file_name)

# handle input events
def event(evt, val):

	# exit when user presses ESC
	if evt == Draw.QKEY:
		Draw.Exit()

# handle button events
def button_event(evt):

	global removeMarginsToggle
	global hideGraphToggle
	global hideKeyToggle
	global lockZoomToggle
	global renderImgToggle
	global showGnuplotWinToggle
	global showBlenderWinToggle

	# save to .blend file path
	if evt == 1:
		ExportToGNU(Blender.sys.makename(ext='.gnu'))

	# save to animations path
	if evt == 2:
		file_name = Blender.sys.makename(ext='.gnu').split('/')[-1]
		file_path = Blender.Scene.GetCurrent().getRenderingContext().getRenderPath()
		ExportToGNU(file_path+file_name)

	# choose a directory to save in
	if evt == 3:
		Blender.Window.FileSelector(FileSelectorCB, "Export for gnuplot", Blender.sys.makename(ext='.gnu'))

	# exit when user clicks the Exit button
	if evt == 4:
		Draw.Exit()

	# show in blender window
	if evt == 5:
		showBlenderWinToggle = 1^showBlenderWinToggle
		showGnuplotWinToggle = 0
		Draw.Redraw(1)

	# show in gnuplot window
	if evt == 6:
		showGnuplotWinToggle = 1^showGnuplotWinToggle
		showBlenderWinToggle = 0
		Draw.Redraw(1)

	# render image
	if evt == 7:
		renderImgToggle = 1^renderImgToggle

	if renderImgToggle == 0:
		showBlenderWinToggle = 0
		showGnuplotWinToggle = 0
		Draw.Redraw(1)

	# lock zoom
	if evt == 8:
		lockZoomToggle = 1^lockZoomToggle

	# hide key
	if evt == 9:
		hideKeyToggle = 1^hideKeyToggle

	# hide graph
	if evt == 10:
		hideGraphToggle = 1^hideGraphToggle

	# hide margins
	if evt == 11:
		removeMarginsToggle = 1^removeMarginsToggle

# draw to screen
def gui():

	global removeMarginsToggle
	global hideGraphToggle
	global hideKeyToggle
	global lockZoomToggle
	global renderImgToggle
	global showGnuplotWinToggle
	global showBlenderWinToggle

	BGL.glClearColor(0.72,0.7,0.7,1)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

	Draw.Toggle("remove margins", 11, 10, 280, 155, 20, removeMarginsToggle, "Remove margins.")
	Draw.Toggle("hide graph", 10, 10, 255, 155, 20, hideGraphToggle, "Hide the graph.")
	Draw.Toggle("hide key", 9, 10, 230, 155, 20, hideKeyToggle, "Hide the key.")
	Draw.Toggle("lock zoom", 8, 10, 205, 155, 20, lockZoomToggle, "Keep from zooming to the image.")
	Draw.Toggle("render image", 7, 10, 180, 155, 20, renderImgToggle, "Render image using the gnuplot data.")
	Draw.Toggle("show in gnuplot window", 6, 10, 155, 155, 20, showGnuplotWinToggle, "Use the gnuplot wxWidgets window for displaying rendered images.")
	Draw.Toggle("show in blender window", 5, 10, 130, 155, 20, showBlenderWinToggle, "Use the same window used for blender animations to display rendered images.")
	Draw.Button("Save to .blend file path", 1, 10, 95, 155, 25, "Save and render in the same directory as this .blend file.")
	Draw.Button("Save to animations path", 2, 10, 65, 155, 25, "Save and render in the same directory animations are saved. This directory can be changed through the 'Buttons Window' under 'Output'.")
	Draw.Button("Choose a directory...", 3, 10, 35, 155, 25, "Choose a directory to save and render in.")
	Draw.Button("Exit", 4, 10, 5, 155, 25, "Exit the script.")

	BGL.glColor3f(0.25,0.25,0.25)
	BGL.glRasterPos2i(180, 105)
	Draw.Text("In the '3D View' window press 'n' to view the 'Transform Properties' window.")
	BGL.glRasterPos2i(180, 90)
	Draw.Text("Change the object name 'OB:' to control line, point, or face style and color.")
	BGL.glRasterPos2i(180, 70)
	Draw.Text("Examples:")
	BGL.glRasterPos2i(180, 55)
	Draw.Text("'p0.4-#00FF00-Cube' renders an object with green points and a point size of 0.4.")
	BGL.glRasterPos2i(180, 40)
	Draw.Text("'l1.3-red-Cone' renders an object with red lines and a line width of 1.3.")
	BGL.glRasterPos2i(180, 25)
	Draw.Text("'f0.8-#888888-Plane' renders an object with gray polygons and a opacity of 80%.")

# registering the 3 callbacks
Draw.Register(gui, event, button_event)
