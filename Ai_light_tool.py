
# -*- coding: utf-8 -*-

##      @file           Ai_light_tool.py
##      @author         Bilal Malik
##      @contact        echopraxiavfx@gmail.com
##
##      @desc           Change mutiple Arnold light paramters in selection with UI.
##----------------------------------------------------------------------------------------

'''
    Tool to alter Arnold light node parameters in selection with new Colour/Intensity/AOV/Light Groups.
    Uses Qt.py to load UI file to provide the interface.
    This application can be used as either a Python Panel tool in houdini with one varialbe change.

'''

import hou, sys, os

#Set the Application as Python panel or Shelf Tool.
isPanel = False

#Points to Qt Modules Path from Houini Enviroment File (Named with VAR = 'PYUI').
(lambda __g: [(sys.path.insert(0, str(ui_l)), None)[1] for __g['ui_l'] in [(hou.getenv('PYUI'))]][0])(globals())
from Qt import QtWidgets, QtCompat, QtGui, QtCore
from Qt.QtGui import QColor, QPixmap, QPainter

#Point this Path to Rootlocation of Folder with appropriate Paths
rootLoc = "PATH_HERE"
file_interface = os.path.join(rootLoc + "\GUI\GUIForm.ui")
file_pix = os.path.join(rootLoc +"\GUI\Header.png")
cd_pix2 = os.path.join(rootLoc +"\GUI\Colour2.png")
cd_pix2_alpha = os.path.join(rootLoc +"\GUI\Colour2_alpha.png")
int_pix = os.path.join(rootLoc +"\GUI\Intensity.png")
bgFill = os.path.join(rootLoc +"\GUI\BGLeft.png")

#Global Vars
selNodes = []
cdR = 0.5
cdG = 0.5
cdB = 0.5

#Main Class Object.
class MyWindow(QtWidgets.QMainWindow):
    
    def procMain(self,*args):
        self.consoleUpdate('Selecting Nodes')
        global selNodes
 
        selNodes = []
        self.getNodes()
        self.main_widget.nodeListV.clear()
        self.main_widget.lcdNumber.display(0)
        
        nonAiLight = ''
        if self.main_widget.node_errorOp.isChecked() == True:
            nonAiLight = 'Abort'
        else:
            nonAiLight = 'Pass'
        if self.checkNodes(nonAiLight) == True:
            #Populate ListView with Selected Nodes Names.
            for i in selNodes:    
                item = str(i)
                self.main_widget.nodeListV.addItem(item)
        self.main_widget.lcdNumber.display(len(selNodes))

    #De-Selects all Nodes and resets list view and lcd number.
    def deSel(self,*args):
        global selNodes
        selNodes = []
        self.main_widget.nodeListV.clear()
        self.main_widget.lcdNumber.display(0)
        
    #Check for Arnold Lights (Stops if Error Is Detected.)
    def checkNodes(self,signal):
        global selNodes
        status = signal
        wNode = 0
        nodeRemove = []
        for each in selNodes:
            itemType = str(each.type())
            itemType = itemType.rsplit(' ', 1)[-1]
            if not itemType == 'arnold_light' + '>':
                wNode = 1
                nodeRemove.append(each)
        tmpLst = [x for x in selNodes if x not in nodeRemove]
        selNodes = tmpLst
        if status == 'Abort':
            if wNode == 1:
                self.consoleUpdate('Non Arnold Light Detected, Aborting')
                return False   
            elif wNode == 0:
                return True
        elif status == 'Pass':
            return True
            
    #update console label in app not the python shell.    
    def consoleUpdate(self,message):
        self.main_widget.lblOUT.setText(("Console: "+str(message)))
        
    #Gets node selection
    def getNodes(self):
        global selNodes
        selNodes = hou.selectedNodes()
        
    #Initialization of App    
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        self.main_widget = QtCompat.loadUi(file_interface)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Arnold Light Tool V2")
        self.main_widget.lighttar_list.clear()
        stylesheet = hou.qt.styleSheet()
        self.setStyleSheet(stylesheet)

        
        #Image Init
        #Image Display (Header)
        pixmap = QPixmap(file_pix)
        self.main_widget.lblHeader.setPixmap(pixmap)
        
        #Colour Image Display
        cdmap2 = QPixmap(cd_pix2)
        cdmap2a = QPixmap(cd_pix2_alpha)
        self.main_widget.lbl_LGTC_PRV.setPixmap(cdmap2)
        self.main_widget.lbl_LGTC_PRV_M.setPixmap(cdmap2a)
                
        #Button Assignment
        #Node Selection Buttons
        self.main_widget.bttn_nodes.clicked.connect(self.procMain)
        self.main_widget.bttn_deSelNodes.clicked.connect(self.deSel)
        
        #Exposure Buttons
        self.main_widget.bttn_setExposure.clicked.connect(self.setExpVal)
        self.main_widget.bttn_multiply.clicked.connect(self.setExpMult)

        #Light Target Buttons
        self.main_widget.bttn_lightgroup.clicked.connect(self.getTarget)
        self.main_widget.bttn_clearTar.clicked.connect(self.clearTar)
        self.main_widget.bttn_removeTar.clicked.connect(self.removeTar)
        
        #Light Group Buttons
        self.main_widget.bttn_setLG.clicked.connect(self.setLG)
        self.main_widget.bttn_LGClear.clicked.connect(self.clearLG)
        
        #Colour Sliders
        self.main_widget.Cd_Slider_R.valueChanged.connect(lambda: self.cdSet("r"))
        self.main_widget.Cd_Slider_G.valueChanged.connect(lambda: self.cdSet("g"))
        self.main_widget.Cd_Slider_B.valueChanged.connect(lambda: self.cdSet("b"))
        
        #Clear Fields
        self.main_widget.nodeListV.clear()
        self.main_widget.lcdNumber.display(0)
        
        #Init Fields
        #Set Colour Params in Preview
        self.cdSet("r")
        self.cdSet("g")
        self.cdSet("b")
        
        
    #EXPOSURE SETTING SUBROUTINES AND FUNCTIONS    
    def setExpVal(self,*args):
        
        
        minVal = self.main_widget.MindoubleSpinBox.value()
        maxVal = self.main_widget.MaxdoubleSpinBox.value()
        
        self.consoleUpdate('Setting Exposure Values')
        for each in selNodes:
            if minVal != 0:
                hou.parm('/obj/'+ str(each) +'/ar_intensity').set(minVal)
            if maxVal != 0:    
                hou.parm('/obj/'+ str(each) +'/ar_exposure').set(maxVal)
            
    def setExpMult(self,*args):
        multVal = self.main_widget.multSpinBox.value()
        self.consoleUpdate('Multiplying Values.')
        for each in selNodes:
            inV = hou.parm('/obj/'+ str(each) +'/ar_intensity').eval()
            expV = hou.parm('/obj/'+ str(each) +'/ar_exposure').eval()
            print (inV,expV)
            inV = inV*multVal
            expV = expV*multVal
            print (inV,expV)
            if multVal != 0:
                hou.parm('/obj/'+ str(each) +'/ar_intensity').set(inV)
                hou.parm('/obj/'+ str(each) +'/ar_exposure').set(expV)
                
                
    #TARGET LIGHTS FUNC
    def getTarget(self,*args):
        self.main_widget.lighttar_list.clear()
        try:
            targNode = hou.selectedNodes()[0]
            self.main_widget.lighttar_list.addItem(str(targNode))
            addNode = '/obj/' + str(targNode) + '/' 
            print(targNode)
            global selNodes
            for each in selNodes:
                hou.parm('/obj/' + str(each) + '/lookatpath').set(addNode)
        except:
            self.consoleUpdate("Please Select a Node to Target.")
    def clearTar(self,*args):
        self.main_widget.lighttar_list.clear()
    def removeTar(self,*args):
        global selNodes
        for each in selNodes:
            hou.parm('/obj/' + str(each) + '/lookatpath').set('')
            
    #LIGHT GROUP FUNC
    def setLG(self,*args):
        aovG = self.main_widget.lineEdit.text()
        if aovG != '':
            global selNodes
            for each in selNodes:
                hou.parm('/obj/' + str(each) + '/ar_aov').set(aovG)
        else:
            self.consoleUpdate("Please Enter a Light Group name.")
    def clearLG(self,*args):
        global selNodes
        for each in selNodes:
            hou.parm('/obj/' + str(each) + '/ar_aov').set('')
            
    #Colour Set
    def cdMapper(self,*args):
        global cdR, cdG, cdB
        
        temp2 = QPixmap(cd_pix2)
        mask = QPixmap(cd_pix2_alpha)
        
        mult = 255
        R = cdR * mult
        G = cdG *mult
        B = cdB * mult
        colour = QColor(R,G,B)
        #print("R:" + str(cdR) + " G:" + str(cdG) + " B:" + str(cdB))
        
        #Paint Lines
        painter2 = QPainter(temp2)
        painter2.setCompositionMode(painter2.CompositionMode_Overlay)
        painter2.fillRect(temp2.rect(), colour)
        painter2.end()
         
        #Update Image
        self.main_widget.lbl_LGTC_PRV.setPixmap(temp2)

                
    #Colour Set Parse (R, G, B)
    def cdSet(self,chan):
        global cdR, cdG, cdB 
        #Get Value from Channel
        if chan == 'r':
            cdV = float(self.main_widget.Cd_Slider_R.value())/100
            self.main_widget.r_out.setText("R: " + str(cdV))
            cdR = cdV
        elif chan == 'g':
            cdV = float(self.main_widget.Cd_Slider_G.value())/100
            self.main_widget.g_out.setText("G: " + str(cdV))
            cdG = cdV
        elif chan == 'b':
            cdV = float(self.main_widget.Cd_Slider_B.value())/100
            self.main_widget.b_out.setText("B: " + str(cdV))
            cdB = cdV
        #Update Cd
        self.cdMapper()
        #Update Node Tree
        for each in selNodes:
            hou.parm('/obj/'+ str(each) +'/ar_color' + chan).set(cdV)
            
if isPanel == True:
    #Create Interface Python Panel
    def onCreateInterface():
        my_window = MyWindow()
        my_window.show()
        return my_window
elif isPanel == False:
    #Create Interface Shelf.
    try:
        my_window.close()
    except:
        pass
    my_window = MyWindow()
    my_window.resize(301,729)
    my_window.show()