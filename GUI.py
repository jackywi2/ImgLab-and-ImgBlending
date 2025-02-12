from PyQt6 import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import numpy as np
import sys
import cv2

class MyWidget(QtWidgets.QWidget):
    def __init__(self, is_confirm_quit: bool = True):
        super().__init__()
        self.setWindowTitle('ImgLab and ImgBlending')
        self.resize(1300, 770)
        self.setUpdatesEnabled(True)
        self.is_confirm_quit = is_confirm_quit
        self.x, self.y = None, None   # 設定兩個變數紀錄滑鼠座標
        self.last_x, self.last_y = None, None   # 設定兩個變數紀錄滑鼠座標
        self.ith = None
        self.ui()
        self.adjustUi()

    def ui(self):
        global btn_label, btn_paste, action_load, action_label, action_paste, btn_loadlab, btn_showlab, action_show
        ### 畫布 ###
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(120, 20, 852, 602)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.scrollArea = QtWidgets.QScrollArea(self.verticalLayoutWidget)
        self.scrollArea.setWidgetResizable(True)
        
        self.pmap = QtWidgets.QLabel()
        self.pmap.setGeometry(0, 0, 852,602) # (x, y, width, length)
        self.pmap.setCursor(Qt.CursorShape.CrossCursor)
        self.scrollArea.setWidget(self.pmap)

        self.verticalLayout.addWidget(self.scrollArea)

        ### control zoom ###
        self.btn_zoom_in = QtWidgets.QPushButton(self.centralwidget)
        self.btn_zoom_in.setGeometry(QRect(150, 650, 89, 25))
        self.btn_zoom_in.setText("zoom_in")
        self.btn_zoom_in.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_zoom_in.setDisabled(True)
        self.btn_zoom_in.clicked.connect(self.set_zoom_in)
        
        
        self.slider_zoom = QtWidgets.QSlider(self.centralwidget)
        self.slider_zoom.setGeometry(QRect(250, 650, 231, 21))
        self.slider_zoom.setProperty("value", 50)
        self.slider_zoom.setOrientation(Qt.Orientation.Horizontal)
        self.slider_zoom.setDisabled(True)
        self.slider_zoom.valueChanged.connect(self.getslidervalue)
        
        self.label_ratio = QtWidgets.QLabel(self.centralwidget)
        self.label_ratio.setGeometry(QRect(610, 650, 641, 21))
        
        self.btn_zoom_out = QtWidgets.QPushButton(self.centralwidget)
        self.btn_zoom_out.setGeometry(QRect(500, 650, 89, 25))
        self.btn_zoom_out.setText("zoom_out")
        self.btn_zoom_out.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_zoom_out.setDisabled(True)
        self.btn_zoom_out.clicked.connect(self.set_zoom_out)
        
        ### mouseMove ###
        self.pmap.setMouseTracking(True)
        self.pmap.mouseMoveEvent = self.get_position
        self.label_get_pos = QtWidgets.QLabel(self)
        self.label_get_pos.setGeometry(700,650,190,20)
        self.label_get_pos.setText('current position = (x,y)')
        self.label_get_pos.setStyleSheet('font-size: 12px;')
        
        ### mousePress ###
        self.pmap.mousePressEvent = self.get_clicked_position
        self.label_click_pos = QtWidgets.QLabel(self)
        self.label_click_pos.setGeometry(700,670,190,20)
        self.label_click_pos.setText('clicked position = (x,y)')
        self.label_click_pos.setStyleSheet('font-size: 12px;')

        ### show img.shape ###
        self.label_img_shape = QtWidgets.QLabel(self)
        self.label_img_shape.setGeometry(575, 710,500,20)

        
        ### label_button ###
        btn_label = QtWidgets.QPushButton(self)
        btn_label.setText('Create RectBox')
        btn_label.setGeometry(980, 20, 100, 24)
        btn_label.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        btn_label.setDisabled(True)
        btn_label.clicked.connect(self.make_label)

        ### label_list ###
        self.label_list = QtWidgets.QLabel(self)
        self.label_list.setText('Box Labels')
        self.label_list.setGeometry(980,45,150,30)
        self.label_list.setStyleSheet('font-size: 12px;')

        self.hideBox = QtWidgets.QCheckBox(self)    
        self.hideBox.move(980, 70)
        self.hideBox.setText('Hide Box')
        self.hideBox.clicked.connect(lambda:self.hideBbox(self.hideBox))
        
        self.listwidget = QtWidgets.QListWidget(self)
        self.listwidget.addItems([])
        self.listwidget.setGeometry(980,96,315,140)
        self.listwidget.setStyleSheet('''
            QListWidget::item{
                font-size:20px;
            }
            QListWidget::item:pressed{
                color:#fff;
                background:#C4E1FF;
            }
        ''')
        self.listwidget.clicked.connect(self.showObject)  # 點擊項目時執行函式
        self.listwidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listwidget.customContextMenuRequested.connect(self.on_context_menu_labimg)
        
        self.label_clear = QtWidgets.QPushButton(self)
        self.label_clear.setText('Delete all')
        self.label_clear.setGeometry(1235,242,60,20)
        self.label_clear.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.label_clear.clicked.connect(self.allbboxClear)
        
        ### paste_button ###
        btn_paste = QtWidgets.QPushButton(self)
        btn_paste.setText('Paste Image')
        btn_paste.setGeometry(980, 275, 100, 24)
        btn_paste.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        btn_paste.setDisabled(True)
        btn_paste.clicked.connect(self.pasteImg)

        self.label_pasteimg = QtWidgets.QLabel(self)
        self.label_pasteimg.setText('Image')
        self.label_pasteimg.setGeometry(980,300,80,30)
        self.label_pasteimg.setStyleSheet('font-size: 12px;')

        self.Hflip = QtWidgets.QCheckBox(self)    
        self.Hflip.move(1020, 306)
        self.Hflip.setText('HorizontalFlip')
        self.Hflip.setDisabled(True)
        self.Hflip.clicked.connect(lambda:self.Hflippimg(self.Hflip))

        self.white_canvas = QPixmap(100,100)         # 建立畫布元件
        self.white_canvas.fill(QColor('#ffffff'))    # 預設填滿白色
        self.pmap_pasteimg = QtWidgets.QLabel(self)    # 建立 QLabel 元件，作為顯示圖片使用
        self.pmap_pasteimg.setGeometry(980, 330, 100, 100) # 設定位置和尺寸
        self.pmap_pasteimg.setStyleSheet('border: 1px solid #D3D3D3;')
        self.pmap_pasteimg.setPixmap(self.white_canvas)      # 放入畫布元件

        self.btn_chooseimg = QtWidgets.QPushButton(self)
        self.btn_chooseimg.setText('Choose')
        self.btn_chooseimg.setGeometry(1030,436,50,20)
        self.btn_chooseimg.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_chooseimg.clicked.connect(self.chooseImg)

        self.btn_add = QtWidgets.QPushButton(self)
        self.btn_add.setText('Add')
        self.btn_add.setGeometry(1030,462,50,20)
        self.btn_add.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_add.setDisabled(True)
        self.btn_add.clicked.connect(self.inputPimg)

        self.btn_reset = QtWidgets.QPushButton(self)
        self.btn_reset.setText('Reset')
        self.btn_reset.setGeometry(1245,495,50,20)
        self.btn_reset.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_reset.clicked.connect(self.resetVal)

        ### Paste_imgae_QListWidget ###
        self.pimg_list = QtWidgets.QLabel(self)
        self.pimg_list.setText('Paste Images')
        self.pimg_list.setGeometry(980,510,180,30)
        self.pimg_list.setStyleSheet('font-size: 12px;')
        
        self.pimglistwidget = QtWidgets.QListWidget(self)
        self.pimglistwidget.addItems([])
        self.pimglistwidget.setGeometry(980,542,315,140)
        self.pimglistwidget.setStyleSheet('''
            QListWidget::item{
                font-size:20px;
            }
            QListWidget::item:pressed{
                color:#fff;
                background:#C4E1FF;
            }
        ''')
        self.pimglistwidget.clicked.connect(self.showPimg)  # 點擊項目時執行函式
        self.pimglistwidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pimglistwidget.customContextMenuRequested.connect(self.on_context_menu_pasteimg)
        
        self.pimg_clear = QtWidgets.QPushButton(self)
        self.pimg_clear.setText('Delete all')
        self.pimg_clear.setGeometry(1235,688,60,20)
        self.pimg_clear.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.pimg_clear.clicked.connect(self.allpimgClear)


        self.mbox = QtWidgets.QMessageBox(self)

        ### menu_File ###
        self.menubar = QtWidgets.QMenuBar(self)     # 建立 menubar

        self.menu_file = QtWidgets.QMenu('File')    # 建立一個 File 選項 ( QMenu )

        self.action_open = QAction('Open Image')    # 建立一個 Open 選項 ( QAction )
        self.action_open.setShortcut('Ctrl+o')
        self.action_open.triggered.connect(self.newFile)
        self.menu_file.addAction(self.action_open)  # 將 Open 選項放入 File 選項裡



        self.action_input = QAction('Input Object')    # 建立一個 Open 選項 ( QAction )
        self.action_input.setShortcut('Ctrl+i')
        self.action_input.setDisabled(True)
        self.action_input.triggered.connect(self.inputObj)
        self.menu_file.addAction(self.action_input)  # 將 Open 選項放入 File 選項裡

        self.menu_file.addSeparator()    # 加入分隔線

        action_load = QAction('Load Label')    # 建立一個 Open 選項 ( QAction )
        action_load.setShortcut('Ctrl+l')
        action_load.setDisabled(True)
        action_load.triggered.connect(self.loadLabel)
        self.menu_file.addAction(action_load)  # 將 Open 選項放入 File 選項裡

        self.menu_file.addSeparator()    # 加入分隔線

        self.action_saveimg = QAction('Save Image')
        self.action_saveimg.setDisabled(True)
        self.action_saveimg.triggered.connect(self.saveFile)
        self.menu_file.addAction(self.action_saveimg)  

        self.action_savelab = QAction('Save Label')
        self.action_savelab.setDisabled(True)
        self.action_savelab.triggered.connect(self.saveLabel)
        self.menu_file.addAction(self.action_savelab)

        self.menubar.addMenu(self.menu_file)        # 將 File 選項放入 menubar 裡
        
        ### menu_Edit ###
        self.menu_edit = QtWidgets.QMenu('Edit')
        
        self.action_undo = QAction('Undo')
        
        action_label = QAction('Create RectBox')
        action_label.setDisabled(True)
        action_label.triggered.connect(self.make_label)
        self.menu_edit.addAction(action_label)

        action_paste = QAction('Paste Image')
        action_paste.setDisabled(True)
        action_paste.triggered.connect(self.pasteImg)
        self.menu_edit.addAction(action_paste)

        self.menu_edit.addSeparator()    # 加入分隔線

        action_show = QAction('Show Label')
        action_show.setDisabled(True)
        action_show.triggered.connect(self.showLabel)
        self.menu_edit.addAction(action_show)

        self.menubar.addMenu(self.menu_edit)
        
        
        ### open_button ###
        self.btn_open = QtWidgets.QPushButton(self)
        self.btn_open.setText('Open Image')
        self.btn_open.setGeometry(10, 20, 100, 24)
        self.btn_open.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_open.clicked.connect(self.newFile)

        ### inputobj_button ###
        self.btn_inputobj = QtWidgets.QPushButton(self)
        self.btn_inputobj.setText('Input Class')
        self.btn_inputobj.setGeometry(10, 54, 100, 24)
        self.btn_inputobj.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_inputobj.setDisabled(True)
        self.btn_inputobj.clicked.connect(self.inputObj)

        ### loadlab_button ###
        btn_loadlab = QtWidgets.QPushButton(self)
        btn_loadlab.setText('Load Label')
        btn_loadlab.setGeometry(10, 108, 100, 24)
        btn_loadlab.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        btn_loadlab.setDisabled(True)
        btn_loadlab.clicked.connect(self.loadLabel)

        ### showlab_button ###
        btn_showlab = QtWidgets.QPushButton(self)
        btn_showlab.setText('Show Label')
        btn_showlab.setGeometry(10, 162, 100, 24)
        btn_showlab.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        btn_showlab.setDisabled(True)
        btn_showlab.clicked.connect(self.showLabel)
        
        ### saveimg_button ###
        self.btn_saveimg = QtWidgets.QPushButton(self)
        self.btn_saveimg.setText('Save Image')
        self.btn_saveimg.setGeometry(10, 566, 100, 24)
        self.btn_saveimg.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_saveimg.setDisabled(True)
        self.btn_saveimg.clicked.connect(self.saveFile)

        ### savelab_button ###
        self.btn_savelab = QtWidgets.QPushButton(self)
        self.btn_savelab.setText('Save Label')
        self.btn_savelab.setGeometry(10, 600, 100, 24)
        self.btn_savelab.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
            QPushButton:disabled {
                color:#fff;
                background:#ccc;
                border: 1px solid #aaa;
            }
        ''')
        self.btn_savelab.setDisabled(True)
        self.btn_savelab.clicked.connect(self.saveLabel)
        
        
        ### close_button ###
        self.btn_close = QtWidgets.QPushButton(self)
        self.btn_close.setText('Quit')
        self.btn_close.setGeometry(10, 684, 100, 24)
        self.btn_close.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #E0E0E0;
                border: 1px solid #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #fff;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_close.clicked.connect(self.closeFile)

    def adjustUi(self):
        self.label_adj_1 = QtWidgets.QLabel(self)       # 調整size說明文字
        self.label_adj_1.setGeometry(1125, 330, 100, 15)
        self.label_adj_1.setText('Resize')
        self.label_adj_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_val_1 = QtWidgets.QLabel(self)       # 調整size數值
        self.label_val_1.setGeometry(1260, 350, 40, 20)
        self.label_val_1.setText("100 %")
        self.label_val_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_1 = QtWidgets.QSlider(self)         # 調整size滑桿
        self.slider_1.setOrientation(Qt.Orientation.Horizontal)
        self.slider_1.setGeometry(1090,350,170,20)
        self.slider_1.setRange(0, 100)
        self.slider_1.setValue(50)
        self.slider_1.valueChanged.connect(self.controlpimg)
        
        self.label_adj_2 = QtWidgets.QLabel(self)       # 調整rotated說明文字
        self.label_adj_2.setGeometry(1125, 370, 100, 15)
        self.label_adj_2.setText('Rotate')
        self.label_adj_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_val_2 = QtWidgets.QLabel(self)       # 調整rotated數值
        self.label_val_2.setGeometry(1260, 390, 40, 20)
        self.label_val_2.setText('0 °')
        self.label_val_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_2 = QtWidgets.QSlider(self)         # 調整rotated滑桿
        self.slider_2.setOrientation(Qt.Orientation.Horizontal)
        self.slider_2.setGeometry(1090,390,170,20)
        self.slider_2.setRange(0, 360)
        self.slider_2.setValue(0)
        self.slider_2.valueChanged.connect(self.controlpimg)
        
        self.label_adj_3 = QtWidgets.QLabel(self)       # 調整brightness說明文字
        self.label_adj_3.setGeometry(1125, 410, 100, 15)
        self.label_adj_3.setText('Brightness')
        self.label_adj_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_val_3 = QtWidgets.QLabel(self)       # 調整brightness數值
        self.label_val_3.setGeometry(1260, 430, 40, 20)
        self.label_val_3.setText('100')
        self.label_val_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_3 = QtWidgets.QSlider(self)         # 調整brightness滑桿
        self.slider_3.setOrientation(Qt.Orientation.Horizontal)
        self.slider_3.setGeometry(1090,430,170,20)
        self.slider_3.setRange(0, 200)
        self.slider_3.setValue(100)
        self.slider_3.valueChanged.connect(self.controlpimg)

        self.label_adj_4 = QtWidgets.QLabel(self)       # 調整contrast說明文字
        self.label_adj_4.setGeometry(1125, 450, 100, 15)
        self.label_adj_4.setText('Contrast')
        self.label_adj_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_val_4 = QtWidgets.QLabel(self)       # 調整contrast數值
        self.label_val_4.setGeometry(1260, 470, 40, 20)
        self.label_val_4.setText('100')
        self.label_val_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_4 = QtWidgets.QSlider(self)         # 調整contrast滑桿
        self.slider_4.setOrientation(Qt.Orientation.Horizontal)
        self.slider_4.setGeometry(1090,470,170,20)
        self.slider_4.setRange(0, 200)
        self.slider_4.setValue(100)
        self.slider_4.valueChanged.connect(self.controlpimg)
        

    
    def getslidervalue(self):
        self.set_slider_value(self.slider_zoom.value()+1)

    def set_img_ratio(self):
        self.ratio_rate = pow(10, (self.ratio_value - 50)/50)
        self.qpixmap_height = int(self.origin_height * self.ratio_rate)
        self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
        
        qpainter = QPainter()                  # 建立 QPainter 元件
        qpainter.begin(self.canvas)            # 在畫布中開始繪圖
        if self.hideBox.isChecked() == False:
            for datas in self.data + self.pimg_data:
                x1,y1,x2,y2,w,h = datas[1:]

                x1 *= self.canvas.width() / w
                y1 *= self.canvas.height() / h
                x2 *= self.canvas.width() / w
                y2 *= self.canvas.height() / h
                
                qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                
                qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))

        for data in self.paste_images:
            img,norm_x,norm_y,norm_w,norm_h = data

            x = norm_x * self.canvas.width()
            y = norm_y * self.canvas.height()
            w = norm_w * self.canvas.width()
            h = norm_h * self.canvas.height()
            
            qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)
            
        qpainter.end()                         # 結束繪圖
        self.pmap.setPixmap(self.canvas)
        self.update()

        
        self.__update_img()
        self.__update_text_ratio()
        self.__update_text_img_shape()

    def __update_img(self):       
        self.pmap.setPixmap(self.canvas)
        self.pmap.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def __update_text_ratio(self):
        self.label_ratio.setText(f"{int(100*self.ratio_rate)} %")
    
    def __update_text_get_position(self, x, y):
        self.label_get_pos.setText(f'Current position = ({x}, {y})')

    def set_zoom_in(self):
        self.ratio_value = max(0, self.ratio_value - 1)
        self.set_img_ratio()

    def set_zoom_out(self):
        self.ratio_value = min(100, self.ratio_value + 1)
        self.set_img_ratio()

    def set_slider_value(self, value):
        self.ratio_value = value
        self.set_img_ratio()
    
    def get_position(self, event):
        mx = int(QEnterEvent.position(event).x())
        my = int(QEnterEvent.position(event).y())
        try:
            if mx < self.canvas.width() and my < self.canvas.height():
                self.__update_text_get_position(mx, my)
        except:
            self.__update_text_get_position(mx, my)

    def __update_text_clicked_position(self, x, y):
        self.label_click_pos.setText(f'Clicked position = ({x}, {y})')

    def get_clicked_position(self, event):
        mx = int(QEnterEvent.position(event).x())
        my = int(QEnterEvent.position(event).y())
        
        self.__update_text_clicked_position(mx, my)

    def __update_text_img_shape(self):
        current_text = f"Current img shape = ({self.canvas.width()}, {self.canvas.height()})"
        origin_text = f"Origin img shape = ({self.origin_width}, {self.origin_height})"
        self.label_img_shape.setText(current_text+"\t"+origin_text)


    def make_label(self):
        self.hideBox.setChecked(False)
        self.hideBbox(self.hideBox)
        self.pmap.mousePressEvent = self.paint

    def paint(self,event):
        mx = int(QEnterEvent.position(event).x())
        my = int(QEnterEvent.position(event).y())

        self.__update_text_clicked_position(mx, my)

        if mx < self.canvas.width() and my < self.canvas.height():        
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(self.canvas)            # 在畫布中開始繪圖
            qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
            qpainter.drawPoint(mx, my)             # 下筆畫出一個點
            qpainter.end()                         # 結束繪圖
            self.pmap.setPixmap(self.canvas)
            self.update()                          # 更新主視窗內容
            if self.x == None and self.y == None:
                self.x, self.y = mx, my
            else:
                if mx > self.x and my > self.y:
                    self.last_x, self.last_y = mx, my
                    qpainter = QPainter()                  # 建立 QPainter 元件
                    qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                    qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                    qpainter.drawRect(self.x, self.y, abs(self.x - self.last_x), abs(self.y - self.last_y))
                    qpainter.end()                         # 結束繪圖
                    self.pmap.setPixmap(self.canvas)
                    self.update()
                    self.qInput()
                    self.x, self.y = None, None
                        
                else:
                    self.x, self.y = None, None
                    if self.hideBox.isChecked():
                        self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                        self.pmap.setPixmap(self.canvas)
                        self.update()
                    else:
                        self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                        qpainter = QPainter()                  # 建立 QPainter 元件
                        qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                        for datas in self.data + self.pimg_data:
                            x1,y1,x2,y2,w,h = datas[1:]

                            x1 *= self.canvas.width() / w
                            y1 *= self.canvas.height() / h
                            x2 *= self.canvas.width() / w
                            y2 *= self.canvas.height() / h
                            
                            qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                            qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                            qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                            qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                            
                            qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                            qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                                
                        qpainter.end()                         # 結束繪圖
                        self.pmap.setPixmap(self.canvas)
                        self.update()

    def qInput(self):
        global object_list, real_data
        item, ok = QtWidgets.QInputDialog().getItem(self, '', 'Enter object name', object_list, 0)
        if ok:
            self.listwidget.addItem(item)
            if item not in object_list:
                object_list.append(item)
            self.data.append([item, self.x, self.y, self.last_x, self.last_y, self.canvas.width(), self.canvas.height()])
            
            real_x = int(self.x * self.origin_width / self.canvas.width())
            real_y = int(self.y * self.origin_height / self.canvas.height())
            real_last_x = int(self.last_x * self.origin_width / self.canvas.width())
            real_last_y = int(self.last_y * self.origin_height / self.canvas.height())
            
            real_data.append([item, real_x, real_y, real_last_x, real_last_y])

            self.label_list.setText(f'Box Labels  (Totle: {len(real_data)})')

            if self.hideBox.isChecked():
                self.hideBox.toggle()	                  #切換
                qpainter = QPainter()                  # 建立 QPainter 元件
                qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                for datas in self.data[:-1] + self.pimg_data:
                    x1,y1,x2,y2,w,h = datas[1:]

                    x1 *= self.canvas.width() / w
                    y1 *= self.canvas.height() / h
                    x2 *= self.canvas.width() / w
                    y2 *= self.canvas.height() / h
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                    qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                        
                qpainter.end()                         # 結束繪圖
                self.pmap.setPixmap(self.canvas)
                self.update()
            
        else:
            if self.hideBox.isChecked():
                self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                self.pmap.setPixmap(self.canvas)
                self.update()
            else:
                self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                qpainter = QPainter()                  # 建立 QPainter 元件
                qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                for datas in self.data + self.pimg_data:
                    x1,y1,x2,y2,w,h = datas[1:]

                    x1 *= self.canvas.width() / w
                    y1 *= self.canvas.height() / h
                    x2 *= self.canvas.width() / w
                    y2 *= self.canvas.height() / h
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                    qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                        
                qpainter.end()                         # 結束繪圖
                self.pmap.setPixmap(self.canvas)
                self.update()


    def hideBbox(self, cb):
        try:
            if cb.isChecked():
                self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)

                qpainter = QPainter()                  # 建立 QPainter 元件
                qpainter.begin(self.canvas)
                for data in self.paste_images:
                    img,norm_x,norm_y,norm_w,norm_h = data
                        
                    x = norm_x * self.canvas.width()
                    y = norm_y * self.canvas.height()
                    w = norm_w * self.canvas.width()
                    h = norm_h * self.canvas.height()

                    qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)

                qpainter.end() 
                self.pmap.setPixmap(self.canvas)
                self.update()
            else:
                qpainter = QPainter()                  # 建立 QPainter 元件
                qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                for datas in self.data + self.pimg_data:
                    x1,y1,x2,y2,w,h = datas[1:]

                    x1 *= self.canvas.width() / w
                    y1 *= self.canvas.height() / h
                    x2 *= self.canvas.width() / w
                    y2 *= self.canvas.height() / h
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                    qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                    qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                    
                    qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                    qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))

                    
                qpainter.end()                         # 結束繪圖
                self.pmap.setPixmap(self.canvas)
                self.update()
        except:
            return
        
    def showObject(self):
        num = self.listwidget.currentIndex().row()   # 取得項目編號
        self.ith1 = num
        
        x1,y1,x2,y2,w,h = self.data[num][1:]
        x1 *= self.canvas.width() / w
        y1 *= self.canvas.height() / h
        x2 *= self.canvas.width() / w
        y2 *= self.canvas.height() / h
        
        copy_canvas = self.canvas.copy()
        qpainter = QPainter()                  # 建立 QPainter 元件
        qpainter.begin(copy_canvas)            # 在畫布中開始繪圖
        color = QColor(30,144,255,120)
        qpainter.fillRect(int(x1), int(y1), abs(int(x2 - x1)) + 1, abs(int(y2 - y1)) + 1, color)
        qpainter.end()                         # 結束繪圖
        self.pmap.setPixmap(copy_canvas)
        self.update()
        

    def bboxClear(self):
        global real_data
        try:
            self.data.pop(self.ith1)
            real_data.pop(self.ith1)
            self.listwidget.takeItem(self.ith1)

            self.label_list.setText(f'Box Labels  (Totle: {len(real_data)})')
            
            self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(self.canvas)            # 在畫布中開始繪圖

            for data in self.paste_images:
                img,norm_x,norm_y,norm_w,norm_h = data

                x = norm_x * self.canvas.width()
                y = norm_y * self.canvas.height()
                w = norm_w * self.canvas.width()
                h = norm_h * self.canvas.height()
                
                qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)
                    
            qpainter.end()                         # 結束繪圖
            self.pmap.setPixmap(self.canvas)
            self.update()
            
            self.hideBox.setChecked(False)
            self.hideBbox(self.hideBox)
        except:
            return

    def allbboxClear(self):
        global real_data
        try:
            ret = self.mbox.question(self, 'question', 'Delete all?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
            if ret == self.mbox.StandardButton.Ok:
                self.data.clear()
                real_data.clear()

                self.label_list.setText(f'Box Labels  (Totle: {len(real_data)})')
                
                self.listwidget.clear()

                self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                qpainter = QPainter()                  # 建立 QPainter 元件
                qpainter.begin(self.canvas)            # 在畫布中開始繪圖

                for data in self.paste_images:
                    img,norm_x,norm_y,norm_w,norm_h = data

                    x = norm_x * self.canvas.width()
                    y = norm_y * self.canvas.height()
                    w = norm_w * self.canvas.width()
                    h = norm_h * self.canvas.height()
                    
                    qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)
                        
                qpainter.end()                         # 結束繪圖
                self.pmap.setPixmap(self.canvas)
                self.update()
                
                self.hideBox.setChecked(False)
                self.hideBbox(self.hideBox)
        except:
            return

    def bboxRename(self):
        global object_list, real_data
        try:
            text, ok = QtWidgets.QInputDialog().getItem(self, '', 'Enter object name', object_list, 0)
            if ok:
                self.data[self.ith1][0] = text
                real_data[self.ith1][0] = text
                item = self.listwidget.item(self.ith1)
                item.setText(text)
                if text not in object_list:
                    object_list.append(text)
        except:
            return


    def chooseImg(self):
        filePath , filetype = QtWidgets.QFileDialog.getOpenFileName(directory='rembg_img',filter='IMAGE(*.jpg *.png *.gif *.bmp)')
        if filePath:
            self.pasteimg = cv2.imread(filePath , cv2.IMREAD_UNCHANGED)
            
            oW = np.sum(self.pasteimg[:,:,3],axis=0)
            oW[oW != 0] = 1
            min_x = np.min(np.where(oW == 1))
            max_x = np.max(np.where(oW == 1))
            oH = np.sum(self.pasteimg[:,:,3],axis=1)
            oH[oH != 0] = 1
            min_y = np.min(np.where(oH == 1))
            max_y = np.max(np.where(oH == 1))
            self.pasteimg = self.pasteimg[min_y:max_y+1,min_x:max_x+1,:]
            self.pasteimg = np.pad(self.pasteimg, ((1,1),(1,1),(0,0)),"constant", constant_values=0)
            self.origin_pasteimg = self.pasteimg.copy()
            
            self.resetVal()

            self.Hflip.setDisabled(False)
            self.Hflip.setChecked(False)
            self.Hflippimg(self.Hflip)

    def Hflippimg(self, cb):
        if cb.isChecked():
            img_center = np.array(self.origin_pasteimg.shape[:2])[::-1]/2
            img_center = np.hstack((img_center, img_center))

            self.pasteimg = self.origin_pasteimg[:, ::-1, :]

            pasteimg = cv2.cvtColor(self.pasteimg, cv2.COLOR_BGRA2RGBA)
            self.pasteimg_height, self.pasteimg_width, self.pasteimg_channel = self.pasteimg.shape
            
            bytesPerline = self.pasteimg_channel * self.pasteimg_width
            pimg = QImage(pasteimg, self.pasteimg_width, self.pasteimg_height, bytesPerline, QImage.Format.Format_RGBA8888)
            self.paste_canvas = QPixmap.fromImage(pimg)

            if self.pasteimg_width < self.pasteimg_height:
                self.paste_canvas = self.paste_canvas.scaled(int(100*self.pasteimg_width/self.pasteimg_height),100)
            else:
                self.paste_canvas = self.paste_canvas.scaled(100,int(100*self.pasteimg_height/self.pasteimg_width))

            self.pmap_pasteimg.setPixmap(self.paste_canvas)
        else:
            self.pasteimg = self.origin_pasteimg

            pasteimg = cv2.cvtColor(self.pasteimg, cv2.COLOR_BGRA2RGBA)
            self.pasteimg_height, self.pasteimg_width, self.pasteimg_channel = self.pasteimg.shape
            
            bytesPerline = self.pasteimg_channel * self.pasteimg_width
            pimg = QImage(pasteimg, self.pasteimg_width, self.pasteimg_height, bytesPerline, QImage.Format.Format_RGBA8888)
            self.paste_canvas = QPixmap.fromImage(pimg)

            if self.pasteimg_width < self.pasteimg_height:
                self.paste_canvas = self.paste_canvas.scaled(int(100*self.pasteimg_width/self.pasteimg_height),100)
            else:
                self.paste_canvas = self.paste_canvas.scaled(100,int(100*self.pasteimg_height/self.pasteimg_width))

            self.pmap_pasteimg.setPixmap(self.paste_canvas)


    def inputPimg(self):
        global output, object_list, real_pimg_data
        item, ok = QtWidgets.QInputDialog().getItem(self, '', 'Enter object name', object_list, 0)
        if ok:
            self.pimglistwidget.addItem(item)
            self.bbox_pimg.insert(0,item)
            self.real_bbox_pimg.insert(0,item)
            
            if item not in object_list:
                object_list.append(item)
                
            self.pimg_data.append(self.bbox_pimg)
            real_pimg_data.append(self.real_bbox_pimg)
            self.paste_images.append(self.norm_pimg)

            self.pimg_list.setText(f'Paste Images  (Totle: {len(real_pimg_data)})')
            
            self.canvas = self.pasteimg_canvas
            self.btn_add.setDisabled(True)
        else:
            self.pmap.setPixmap(self.canvas)

        output = self.pmap
        self.cX, self.cY = None, None
       
        
    def showPimg(self):
        num = self.pimglistwidget.currentIndex().row()   # 取得項目編號
        self.ith2 = num
        
        x1,y1,x2,y2,w,h = self.pimg_data[num][1:]
        x1 *= self.canvas.width() / w
        y1 *= self.canvas.height() / h
        x2 *= self.canvas.width() / w
        y2 *= self.canvas.height() / h
        
        copy_canvas = self.canvas.copy()
        qpainter = QPainter()                  # 建立 QPainter 元件
        qpainter.begin(copy_canvas)            # 在畫布中開始繪圖
        color = QColor(30,144,255,120)
        qpainter.fillRect(int(x1), int(y1), abs(int(x2 - x1)) + 1, abs(int(y2 - y1)) + 1, color)
        qpainter.end()                         # 結束繪圖
        self.pmap.setPixmap(copy_canvas)
        self.update()

    def pimgClear(self):
        global real_pimg_data
        try:
            self.pimg_data.pop(self.ith2)
            real_pimg_data.pop(self.ith2)
            self.paste_images.pop(self.ith2)

            self.pimg_list.setText(f'Paste Images  (Totle: {len(real_pimg_data)})')
            
            self.pimglistwidget.takeItem(self.ith2)
            
            self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
            
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(self.canvas)            # 在畫布中開始繪圖
            
            for data in self.paste_images:
                img,norm_x,norm_y,norm_w,norm_h = data
                    
                x = norm_x * self.canvas.width()
                y = norm_y * self.canvas.height()
                w = norm_w * self.canvas.width()
                h = norm_h * self.canvas.height()
                
                qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)
                
            qpainter.end() 
            self.pmap.setPixmap(self.canvas)
            self.update()
            
            self.hideBox.setChecked(False)
            self.hideBbox(self.hideBox)
        except:
            return

    def allpimgClear(self):
        global real_pimg_data
        try:
            ret = self.mbox.question(self, 'question', 'Delete all?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
            if ret == self.mbox.StandardButton.Ok:
                self.pimg_data.clear()
                real_pimg_data.clear()
                self.paste_images.clear()

                self.pimg_list.setText(f'Paste Images  (Totle: {len(real_pimg_data)})')
                
                self.pimglistwidget.clear()

                self.canvas = self.origin_canvas.scaledToHeight(self.qpixmap_height)
                self.pmap.setPixmap(self.canvas)
                self.update()
                
                self.hideBox.setChecked(False)
                self.hideBbox(self.hideBox)
        except:
            return

    def pimgRename(self):
        global object_list, real_pimg_data
        try:
            text, ok = QtWidgets.QInputDialog().getItem(self, '', 'Enter object name', object_list, 0)
            if ok:
                self.pimg_data[self.ith2][0] = text
                real_pimg_data[self.ith2][0] = text
                
                item = self.pimglistwidget.item(self.ith2)
                item.setText(text)
                
                if text not in object_list:
                    object_list.append(text)
        except:
            return
        
    
    def resetVal(self):
        self.slider_1.setValue(50)        # 滑桿預設值 0
        self.slider_2.setValue(0)        # 滑桿預設值 0
        self.slider_3.setValue(100)        # 滑桿預設值 0
        self.slider_4.setValue(100)        # 滑桿預設值 0
        self.label_val_1.setText('100 %')    # 滑桿數值顯示 0
        self.label_val_2.setText('0 °')    # 滑桿數值顯示 0
        self.label_val_3.setText('100')    # 滑桿數值顯示 0
        self.label_val_4.setText('100')    # 滑桿數值顯示 0
    
    def controlpimg(self):
        val1 = self.slider_1.value()         # 取得滑桿數值
        val2 = self.slider_2.value()         # 取得滑桿數值
        val3 = self.slider_3.value()         # 取得滑桿數值
        val4 = self.slider_4.value()         # 取得滑桿數值

        rate1 = pow(10, (val1 - 50)/50)
        
        try:            
            width = int(self.pasteimg_width * rate1)
            height = int(self.pasteimg_height * rate1)
            dim = (width, height)
            self.resizeimg = cv2.resize(self.pasteimg,dim,interpolation=cv2.INTER_AREA)

            rH,rW = self.resizeimg.shape[:2]

            if rH % 2 == 0:
                self.resizeimg = np.pad(self.resizeimg, ((1,0),(0,0),(0,0)),"constant", constant_values=0)
                rH += 1
            if rW % 2 == 0:
                self.resizeimg = np.pad(self.resizeimg, ((0,0),(1,0),(0,0)),"constant", constant_values=0)
                rW += 1

            (cX,cY) = (rW//2,rH//2)
            M = cv2.getRotationMatrix2D((cX, cY), -val2, 1) #
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            # compute the new bounding dimensions of the image
            nW = int((rH * sin) + (rW * cos))
            nH = int((rH * cos) + (rW * sin))
            # adjust the rotation matrix to take into account translation
            M[0, 2] += (nW-rW)/2 #(nW // 2) - cX - 0.5
            M[1, 2] += (nH-rH)/2 #(nH // 2) - cY - 0.5
            self.rotated = cv2.warpAffine(self.resizeimg, M, (nW, nH),flags=cv2.INTER_AREA)

            b = val3 - 100
            c = max(-99,val4 -100)
            bc_img = self.rotated[:,:,:3] * (c/100 + 1) - c + b    # 轉換公式
            bc_img = np.clip(bc_img, 0, 255)
            bc_img = np.uint8(bc_img)
            self.bc_image = np.dstack((bc_img,self.rotated[:,:,3]))
            
            (nX,nY) = (nW//2,nH//2)
            left = self.cX - nX
            top = self.cY - nY        
            right = self.cX + nW - nX
            down = self.cY + nH - nY  
            
            self.pasteimg_canvas = self.canvas.copy()
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(self.pasteimg_canvas)            # 在畫布中開始繪圖

            pimg = cv2.cvtColor(self.bc_image, cv2.COLOR_BGRA2RGBA)
            bytesPerline = 4 * nW
            pimage = QImage(pimg, nW, nH, bytesPerline, QImage.Format.Format_RGBA8888)
            qpainter.drawImage(QRect(left, top, nW, nH), pimage)

            qpainter.end()
            self.pmap.setPixmap(self.pasteimg_canvas)
            self.update()

            W = np.sum(self.bc_image[:,:,3],axis=0)
            W[W != 0] = 1
            x1 = left + np.min(np.where(W == 1)) - 1
            x2 = right - (W.shape[0] - np.max(np.where(W == 1))) + 1
            H = np.sum(self.bc_image[:,:,3],axis=1)
            H[H != 0] = 1
            y1 = top + np.min(np.where(H == 1)) - 1
            y2 = down - (H.shape[0] - np.max(np.where(H == 1))) + 1

            real_x1 = max( 0, int(x1 * self.origin_width / self.pasteimg_canvas.width()) )
            real_y1 = max( 0, int(y1 * self.origin_height / self.pasteimg_canvas.height()) )
            real_x2 = min( int(x2 * self.origin_width / self.pasteimg_canvas.width()), self.origin_width )
            real_y2 = min( int(y2 * self.origin_height / self.pasteimg_canvas.height()), self.origin_height )

            self.norm_pimg = [pimage, left/self.pasteimg_canvas.width(), top/self.pasteimg_canvas.height(),nW/self.pasteimg_canvas.width(),nH/self.pasteimg_canvas.height()] 
            self.bbox_pimg = [x1,y1,x2,y2,self.pasteimg_canvas.width(),self.pasteimg_canvas.height()]
            self.real_bbox_pimg = [real_x1,real_y1,real_x2,real_y2]
            
        except:
            pass
        
        
        self.label_val_1.setText(f"{int(100*rate1)} %")  # 顯示滑桿數值
        self.label_val_2.setText(str(val2)+' °')  # 顯示滑桿數值
        self.label_val_3.setText(str(val3))  # 顯示滑桿數值
        self.label_val_4.setText(str(val4))  # 顯示滑桿數值
    
    def pasteImg(self):
        self.hideBox.setChecked(True)
        self.hideBbox(self.hideBox)
        self.pmap.mousePressEvent = self.paste

    def paste(self,event):
        x = int(QEnterEvent.position(event).x())
        y = int(QEnterEvent.position(event).y())

        self.__update_text_clicked_position(x, y)
        
        if x < self.canvas.width() and y < self.canvas.height():
            self.hideBox.setChecked(True)
            self.hideBbox(self.hideBox)
            self.btn_add.setDisabled(False)
            self.cX, self.cY = x, y
            self.controlpimg()


    def on_context_menu_labimg(self, pos):
        context = QtWidgets.QMenu(self)
        self.action_labimgrename = QAction("Rename", self)
        self.action_labimgdelete = QAction("Delete", self)
        
        context.addAction(self.action_labimgrename)
        context.addAction(self.action_labimgdelete)

        self.action_labimgrename.triggered.connect(self.bboxRename)
        self.action_labimgdelete.triggered.connect(self.bboxClear)
        
        context.exec(self.mapToGlobal(pos+QPoint(980,96)))

    def on_context_menu_pasteimg(self, pos):
        context = QtWidgets.QMenu(self)
        self.action_pimgrename = QAction("Rename", self)
        self.action_pimgdelete = QAction("Delete", self)
        
        context.addAction(self.action_pimgrename)
        context.addAction(self.action_pimgdelete)

        self.action_pimgrename.triggered.connect(self.pimgRename)
        self.action_pimgdelete.triggered.connect(self.pimgClear)
        
        context.exec(self.mapToGlobal(pos+QPoint(980,542)))
            
    
    def newFile(self):
        global output, real_data, real_pimg_data, image_width, image_height, imgfilePath
        imgfilePath , filetype = QtWidgets.QFileDialog.getOpenFileName(directory='dataset',filter='IMAGE(*.jpg *.png *.gif *.bmp)')
        if imgfilePath:
            ret = self.mbox.question(self, 'question', 'New File?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
            if ret == self.mbox.StandardButton.Ok:
                self.setWindowTitle('ImgLab and ImgBlending   ' + imgfilePath)
                self.img = cv2.imread(imgfilePath , cv2.IMREAD_UNCHANGED)

                self.btn_zoom_in.setDisabled(False)
                self.slider_zoom.setDisabled(False)
                self.btn_zoom_out.setDisabled(False)

                self.btn_inputobj.setDisabled(False)
                self.btn_saveimg.setDisabled(False)
                self.btn_savelab.setDisabled(False)
                
                self.action_input.setDisabled(False)
                self.action_saveimg.setDisabled(False)
                self.action_savelab.setDisabled(False)
                
                self.paste_images = []
                
                real_data = []
                self.data = []
                
                real_pimg_data = []
                self.pimg_data = []
                
                self.label_list.setText(f'Box Labels  (Totle: {len(real_data)})')
                self.pimg_list.setText(f'Paste Images  (Totle: {len(real_pimg_data)})')
                
                self.listwidget.clear()
                self.pimglistwidget.clear()
                self.resetVal()

                if self.img.ndim == 2:
                    img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2RGB)
                elif self.img.ndim == 3:
                    img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                    
                self.origin_height, self.origin_width, self.origin_channel = img.shape
                image_width, image_height = self.origin_width, self.origin_height
                
                bytesPerline = 3 * self.origin_width
                qimg = QImage(img, self.origin_width, self.origin_height, bytesPerline, QImage.Format.Format_RGB888)
                self.canvas = QPixmap.fromImage(qimg)
                self.origin_canvas = self.canvas.copy()
                
                self.pmap.setPixmap(self.canvas)
                    
                output = self.pmap
                self.ratio_value = 50
                self.set_img_ratio()
            else:
                return

    def inputObj(self):
        self.nw2 = inputWindow(is_confirm_quit=True)      # 連接新視窗
        self.nw2.show()              # 顯示新視窗
    
    def loadLabel(self):
        global object_list, real_data, imgfilePath, image_width, image_height
        filePath , filetype = QtWidgets.QFileDialog.getOpenFileName(directory='dataset/labels',filter='TXT(' + imgfilePath.split('/')[-1][:-4] + '.txt)')
        if filePath:
            ret = self.mbox.question(self, 'question', 'New Coordinate Label File?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
            if ret == self.mbox.StandardButton.Ok:
                with open(filePath) as file_obj:
                    qpainter = QPainter()                  # 建立 QPainter 元件
                    qpainter.begin(self.canvas)            # 在畫布中開始繪圖
                    for line in file_obj:
                        line = line.strip('\n')
                        data = line.split()
                        obj, x, y, w, h = data
                        x1 = int(float(x)*image_width - float(w)*image_width/2)
                        y1 = int(float(y)*image_height - float(h)*image_height/2)
                        x2 = int(float(x)*image_width + float(w)*image_width/2)
                        y2 = int(float(y)*image_height + float(h)*image_height/2)
                        obj_name = object_list[int(obj)]
                        
                        real_data.append([obj_name, x1, y1, x2, y2])
                        self.data.append([obj_name, x1, y1, x2, y2, self.origin_width, self.origin_height])

                        self.listwidget.addItem(obj_name)

                        x1 *= self.canvas.width() / self.origin_width
                        y1 *= self.canvas.height() / self.origin_height
                        x2 *= self.canvas.width() / self.origin_width
                        y2 *= self.canvas.height() / self.origin_height

                        qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                        qpainter.drawPoint(int(x1), int(y1))             # 下筆畫出一個點

                        qpainter.setPen(QPen(QColor('#00ff00'), 3)) # 設定畫筆樣式
                        qpainter.drawPoint(int(x2), int(y2))             # 下筆畫出一個點
                        
                        qpainter.setPen(QPen(QColor('#00ff00'), 1)) # 設定畫筆樣式
                        qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                        
                    qpainter.end()                         # 結束繪圖
                    self.pmap.setPixmap(self.canvas)
                    self.update()
                    

                self.label_list.setText(f'Box Labels  (Totle: {len(real_data)})')

                self.hideBox.setChecked(False)
                self.hideBbox(self.hideBox)
                
    def showLabel(self):
        global showimg
        showimg = self.origin_canvas.copy()
        
        qpainter = QPainter()                  # 建立 QPainter 元件
        qpainter.begin(showimg)
        for data in self.paste_images:
            img,norm_x,norm_y,norm_w,norm_h = data
                
            x = norm_x * showimg.width()
            y = norm_y * showimg.height()
            w = norm_w * showimg.width()
            h = norm_h * showimg.height()

            qpainter.drawImage(QRect(int(x), int(y), int(w), int(h)), img)

        qpainter.end()

        self.nw4 = showlabWindow()      # 連接新視窗
        self.nw4.show()              # 顯示新視窗

    def saveFile(self):
        self.nw = saveimgWindow()      # 連接新視窗
        self.nw.show()              # 顯示新視窗

    def saveLabel(self):
        self.nw3 = savelabWindow()      # 連接新視窗
        self.nw3.show()              # 顯示新視窗
        
    def closeFile(self):
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.is_confirm_quit:
            reply = self.mbox.question(self, 'question', 'Quit Application?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
            if reply == self.mbox.StandardButton.Ok:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class inputWindow(QtWidgets.QWidget):
    def __init__(self, is_confirm_quit: bool = True):
        global object_list, btn_label, btn_paste, action_load, action_label, action_paste, btn_loadlab, btn_showlab, action_show
        super().__init__()
        self.setWindowTitle('Input Class')    # 新視窗標題
        self.resize(300, 240)
        
        self.is_confirm_quit = is_confirm_quit
        
        try:
            object_list
        except NameError:
            self.object = []
        else:
            self.object = object_list.copy()
            
        btn_label.setDisabled(True)
        btn_paste.setDisabled(True)
        action_load.setDisabled(True)
        action_label.setDisabled(True)
        action_paste.setDisabled(True)
        btn_loadlab.setDisabled(True)
        btn_showlab.setDisabled(True)
        action_show.setDisabled(True)
        
        self.ui()

    def ui(self):
        self.label_format = QtWidgets.QLabel(self)   # 存檔格式說明文字
        self.label_format.setGeometry(10, 20, 100, 20)
        self.label_format.setText('Object name: ')

        self.input = QtWidgets.QLineEdit(self)   # 建立單行輸入框
        self.input.setGeometry(105,20,100,20)     # 設定位置和尺寸

        self.btn_input = QtWidgets.QPushButton(self)
        self.btn_input.setText('Enter')
        self.btn_input.setGeometry(230, 20, 60, 20)
        self.btn_input.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_input.clicked.connect(self.addObject)
        
        self.listwidget = QtWidgets.QListWidget(self)
        self.listwidget.addItems(self.object)
        self.listwidget.setGeometry(10,50,200,120)
        self.listwidget.setStyleSheet('''
            QListWidget::item{
                font-size:20px;
            }
            QListWidget::item:pressed{
                color:#fff;
                background:#C4E1FF;
            }
        ''')
        self.listwidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listwidget.customContextMenuRequested.connect(self.on_context_menu)


        self.btn_delete = QtWidgets.QPushButton(self)
        self.btn_delete.setText('Delete all')
        self.btn_delete.setGeometry(230, 120, 60, 20)
        self.btn_delete.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_delete.clicked.connect(self.clearAll)

        self.btn_save = QtWidgets.QPushButton(self)
        self.btn_save.setText('Save')
        self.btn_save.setGeometry(230, 150, 60, 20)
        self.btn_save.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                color: #000;
                background: #f5f5f5;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #000;
                background: #C4E1FF;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_save.clicked.connect(self.save_yaml)

        self.btn_ok = QtWidgets.QPushButton(self)    # 確定儲存按鈕
        self.btn_ok.setText('OK')
        self.btn_ok.setGeometry(155, 190, 90, 30)
        self.btn_ok.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #FFF;
                background: #0066FF;
                border-radius: 5px;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_ok.clicked.connect(self.saveObjname)  # 串連儲存函式

        self.btn_cancel = QtWidgets.QPushButton(self)  # 取消儲存按鈕
        self.btn_cancel.setText('Cancel')
        self.btn_cancel.setGeometry(55, 190, 90, 30)
        self.btn_cancel.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #000;
                background: #E0E0E0;
                border-radius: 5px;
            }
            QPushButton:pressed {
                color: #000;
                background: #a9a9a9;
            }
        ''')
        self.btn_cancel.clicked.connect(self.closeWindow)  # 串連關閉視窗函式


    def addObject(self):
        item = self.input.text()
        if item not in self.object and len(item) != 0:
            self.object.append(item)
            self.listwidget.addItem(item)
        self.input.setText('')

    def renameObject(self):
        try:
            name, ok = QtWidgets.QInputDialog().getText(self, '', 'Enter object name')
            if ok and len(name) != 0:
                if name not in self.object:
                    num = self.listwidget.currentIndex().row()   # 取得項目編號
                    item = self.listwidget.item(num)
                    item.setText(name)
                    self.object[num] = name
                
                else:
                    mbox = QtWidgets.QMessageBox(self)
                    mbox.setText('Object name already exists!')   # 通知文字
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
                    mbox.exec()
        except:
            return

    def deleteObject(self):
        try:
            num = self.listwidget.currentIndex().row()   # 取得項目編號
            self.listwidget.takeItem(num)  
            self.object.pop(num)
            
        except:
            return

    def saveObjname(self):
        global object_list, btn_label, btn_paste, action_load, action_label, action_paste, btn_loadlab, btn_showlab, action_show
        if len(self.object) == 0:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setText('Not enter any object name!')   # 通知文字
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
            mbox.exec()

        else:
            object_list = self.object.copy()
            
            btn_label.setDisabled(False)
            btn_paste.setDisabled(False)
            action_load.setDisabled(False)
            action_label.setDisabled(False)
            action_paste.setDisabled(False)
            btn_loadlab.setDisabled(False)
            btn_showlab.setDisabled(False)
            action_show.setDisabled(False)
            
            self.close()
            

    def closeWindow(self):
        global object_list, btn_label, btn_paste, action_load, action_label, action_paste, btn_loadlab, btn_showlab, action_show
        try:
            object_list
        except NameError:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setText('Not save any object name!')   # 通知文字
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
            mbox.exec()
        else:
            if len(object_list) == 0:
                mbox = QtWidgets.QMessageBox(self)
                mbox.setText('Not save any object name!')   # 通知文字
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
                mbox.exec()
            else:
                btn_label.setDisabled(False)
                btn_paste.setDisabled(False)
                action_load.setDisabled(False)
                action_label.setDisabled(False)
                action_paste.setDisabled(False)
                btn_loadlab.setDisabled(False)
                btn_showlab.setDisabled(False)
                action_show.setDisabled(False)
                self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        global object_list
        try:
            object_list
        except NameError:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setText('Not save any object name!')   # 通知文字
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
            mbox.exec()
            event.ignore()
        else:
            if len(object_list) == 0:
                mbox = QtWidgets.QMessageBox(self)
                mbox.setText('Not save any object name!')   # 通知文字
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # 加入問號 icon
                mbox.exec()
                event.ignore()
            else:
                btn_label.setDisabled(False)
                btn_paste.setDisabled(False)
                action_load.setDisabled(False)
                action_label.setDisabled(False)
                action_paste.setDisabled(False)
                btn_loadlab.setDisabled(False)
                btn_showlab.setDisabled(False)
                action_show.setDisabled(False)
                event.accept()

    def on_context_menu(self, pos):
        context = QtWidgets.QMenu(self)
        self.action_rename = QAction("Rename", self)
        self.action_delete = QAction("Delete", self)
        
        context.addAction(self.action_rename)
        context.addAction(self.action_delete)

        self.action_rename.triggered.connect(self.renameObject)
        self.action_delete.triggered.connect(self.deleteObject)
        
        context.exec(self.mapToGlobal(pos))

    def clearAll(self):
        global object_list
        self.mbox = QtWidgets.QMessageBox(self)
        ret = self.mbox.question(self, 'question', 'Delete all?',self.mbox.StandardButton.Cancel,self.mbox.StandardButton.Ok)
        if ret == self.mbox.StandardButton.Ok:
            self.object.clear()
            self.listwidget.clear()
            object_list.clear()

    def save_yaml(self):
        filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory='data.yaml', filter='YAML(*.yaml)')
        if filePath:
            with open(filePath, 'w') as file:
                file.write('train: ' + '\n')
                file.write('val: ' + '\n')
                file.write('\n')
                file.write('nc: %d \n' %len(self.object))
                file.write('name: ' + str(self.object))
    

class showlabWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Show Object Bounding Box')    # 新視窗標題
        self.resize(1100, 700)                # 新視窗尺寸
        self.ui()

    def ui(self):
        global object_list, showimg, real_data, real_pimg_data
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(10, 10, 852, 602)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.scrollArea = QtWidgets.QScrollArea(self.verticalLayoutWidget)
        self.scrollArea.setWidgetResizable(True)
        
        self.pixmap = QtWidgets.QLabel()
        self.pixmap.setGeometry(0, 0, 852,602) # (x, y, width, length)
        
        self.scrollArea.setWidget(self.pixmap)

        self.verticalLayout.addWidget(self.scrollArea)

        self.label = QtWidgets.QLabel(self)
        self.label.setText('Choose object:')
        self.label.setGeometry(888,95,100,10)

        self.box = QtWidgets.QComboBox(self)   # 加入下拉選單
        self.box.addItems(object_list)
        self.box.insertItem(0, 'All')
        self.box.setCurrentIndex(0) 
        self.box.setGeometry(880,110,200,30)
        self.box.currentIndexChanged.connect(self.showobjlab)

        np.random.seed(12)
        self.colors = [[np.random.randint(0, 255) for _ in range(3)] for _ in object_list]

        copy_showimg = showimg.copy()

        qpainter = QPainter()                  # 建立 QPainter 元件
        qpainter.begin(copy_showimg)            # 在畫布中開始繪圖
        for datas in real_data + real_pimg_data:
            name,x1,y1,x2,y2 = datas

            r,g,b = self.colors[object_list.index(name)]
            qpainter.setPen( QPen( QColor( r,g,b ), 1 )) # 設定畫筆樣式
            qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                
        qpainter.end()                         # 結束繪圖
        self.pixmap.setPixmap(copy_showimg)

    def showobjlab(self):
        copy_showimg = showimg.copy()
        text = self.box.currentText()
        num = self.box.currentIndex()

        if num == 0:
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(copy_showimg)            # 在畫布中開始繪圖
            for datas in real_data + real_pimg_data:
                name,x1,y1,x2,y2 = datas

                r,g,b = self.colors[object_list.index(name)]
                qpainter.setPen( QPen( QColor( r,g,b ), 1 )) # 設定畫筆樣式
                qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                    
            qpainter.end()                         # 結束繪圖
            self.pixmap.setPixmap(copy_showimg)
            self.update()

        else:
            qpainter = QPainter()                  # 建立 QPainter 元件
            qpainter.begin(copy_showimg)            # 在畫布中開始繪圖
            for datas in real_data + real_pimg_data:
                name,x1,y1,x2,y2 = datas

                if name == text:
                    r,g,b = self.colors[object_list.index(name)]
                    qpainter.setPen( QPen( QColor( r,g,b ), 1 )) # 設定畫筆樣式
                    qpainter.drawRect(int(x1), int(y1), abs(int(x2 - x1)), abs(int(y2 - y1)))
                    
            qpainter.end()                         # 結束繪圖
            self.pixmap.setPixmap(copy_showimg)
            self.update()

        


class saveimgWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Select Savable Format')    # 新視窗標題
        self.resize(240, 180)                # 新視窗尺寸
        self.ui()

    def ui(self):
        self.label_format = QtWidgets.QLabel(self)   # 存檔格式說明文字
        self.label_format.setGeometry(10, 0, 100, 30)
        self.label_format.setText('Format')

        self.format = 'JPG'                          # 預設格式

        self.box_format  = QtWidgets.QComboBox(self) # 下拉選單元件
        self.box_format.addItems(['JPG','PNG','BMP'])      # 兩個選項
        self.box_format.setGeometry(10,30,100,30)
        self.box_format.currentIndexChanged.connect(self.changeFormat) # 串連改變時的程式

        self.label_jpg = QtWidgets.QLabel(self)      # 壓縮品質說明文字
        self.label_jpg.setGeometry(10, 60, 150, 30)
        self.label_jpg.setText('JPG Compression quality')

        self.val = 90                               # 預設 JPG 壓縮品質

        self.label_jpg_val = QtWidgets.QLabel(self)  # 壓縮品質數值
        self.label_jpg_val.setGeometry(120, 90, 100, 30)
        self.label_jpg_val.setText(str(self.val))

        self.slider = QtWidgets.QSlider(self)        # 壓縮品質調整滑桿
        self.slider.setOrientation(Qt.Orientation.Horizontal)                # 水平顯示
        self.slider.setGeometry(10,90,100,30)
        self.slider.setRange(0, 100)                 # 數值範圍
        self.slider.setValue(self.val)               # 預設值
        self.slider.valueChanged.connect(self.changeVal)  # 串連改變時的函式

        self.btn_ok = QtWidgets.QPushButton(self)    # 確定儲存按鈕
        self.btn_ok.setText('OK')
        self.btn_ok.setGeometry(125, 130, 90, 30)
        self.btn_ok.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #FFF;
                background: #0066FF;
                border-radius: 5px;
            }
        ''')
        self.btn_ok.clicked.connect(self.saveImage)  # 串連儲存函式

        self.btn_cancel = QtWidgets.QPushButton(self)  # 取消儲存按鈕
        self.btn_cancel.setText('Cancel')
        self.btn_cancel.setGeometry(25, 130, 90, 30)
        self.btn_cancel.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #000;
                background: #E0E0E0;
                border-radius: 5px;
            }
        ''')
        self.btn_cancel.clicked.connect(self.closeWindow)  # 串連關閉視窗函式

    # 改變格式
    def changeFormat(self):
        self.format = self.box_format.currentText()  # 顯示目前格式
        if self.format == 'JPG':
            self.label_jpg.setDisabled(False)        # 如果是 JPG，啟用 JPG 壓縮品質調整相關元件
            self.label_jpg_val.setDisabled(False)
            self.slider.setDisabled(False)
        else:
            self.label_jpg.setDisabled(True)        # 如果是 JPG，停用 JPG 壓縮品質調整相關元件
            self.label_jpg_val.setDisabled(True)
            self.slider.setDisabled(True)

    # 改變數值
    def changeVal(self):
        self.val = self.slider.value()              # 取得滑桿數值
        self.label_jpg_val.setText(str(self.slider.value()))

    # 存檔
    def saveImage(self):
        global output, imgfilePath
        if self.format == 'JPG':
            filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory=imgfilePath.split('/')[-1][:-4] + '.jpg', filter='JPG(*.jpg)')
            if filePath:
                output.pixmap().save(filePath, quality=self.val)  # JPG 存檔
                self.close()
        elif self.format == 'PNG':
            filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory=imgfilePath.split('/')[-1][:-4] + '.png', filter='PNG(*.png)')
            if filePath:
                output.pixmap().save(filePath, 'png')                        # PNG 存檔
                self.close()
        elif self.format == 'BMP':
            filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory=imgfilePath.split('/')[-1][:-4] + '.bmp', filter='PNG(*.bmp)')
            if filePath:
                output.pixmap().save(filePath, 'bmp')                        # PNG 存檔
                self.close()

    def closeWindow(self):
        self.close()


class savelabWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Select Savable Format')    # 新視窗標題
        self.resize(240, 150)                # 新視窗尺寸
        self.ui()

    def ui(self):
        self.label_format = QtWidgets.QLabel(self)   # 存檔格式說明文字
        self.label_format.setGeometry(10, 0, 100, 30)
        self.label_format.setText('Format')

        self.format = 'JPG'                          # 預設格式

        self.box_format  = QtWidgets.QComboBox(self) # 下拉選單元件
        self.box_format.addItems(['YOLO(v5~10)','Bounding Boxes'])      # 兩個選項
        self.box_format.setGeometry(10,30,150,30)

        self.btn_ok = QtWidgets.QPushButton(self)    # 確定儲存按鈕
        self.btn_ok.setText('OK')
        self.btn_ok.setGeometry(125, 100, 90, 30)
        self.btn_ok.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #FFF;
                background: #0066FF;
                border-radius: 5px;
            }
        ''')
        self.btn_ok.clicked.connect(self.saveLabel)  # 串連儲存函式

        self.btn_cancel = QtWidgets.QPushButton(self)  # 取消儲存按鈕
        self.btn_cancel.setText('Cancel')
        self.btn_cancel.setGeometry(25, 100, 90, 30)
        self.btn_cancel.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #000;
                background: #E0E0E0;
                border-radius: 5px;
            }
        ''')
        self.btn_cancel.clicked.connect(self.closeWindow)  # 串連關閉視窗函式

    # 存檔
    def saveLabel(self):
        global object_list, real_data, real_pimg_data, image_width, image_height, imgfilePath
        self.format = self.box_format.currentText()  # 顯示目前格式
        if self.format == 'YOLO(v5~10)':
            filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory=imgfilePath.split('/')[-1][:-4] + '.txt', filter='TXT(*.txt)')
            if filePath:
                with open(filePath, 'w') as file:
                    for data in real_data + real_pimg_data:
                        name, x1, y1, x2, y2 = data
                        numobj = object_list.index(name)
                        n_x = (x1 + x2)/2.0/image_width
                        n_y = (y1 + y2)/2.0/image_height
                        n_w = (x2 - x1)/image_width
                        n_h = (y2 - y1)/image_height
                        file.write('%s %s %s %s %s\n' %(numobj, n_x, n_y, n_w, n_h))
                self.close()
        else:
            filePath, filterType = QtWidgets.QFileDialog.getSaveFileName(directory=imgfilePath.split('/')[-1][:-4] + '_bbox.txt', filter='TXT(*.txt)')
            if filePath:
                with open(filePath, 'w') as file:
                    for data in real_data + real_pimg_data:
                        name, x1, y1, x2, y2 = data
                        numobj = object_list.index(name)
                        file.write('%s %s %s %s %s\n' %(x1, y1, x2, y2, numobj))
                self.close()
            

    def closeWindow(self):
        self.close()


        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget(is_confirm_quit=True)
    Form.show()
    sys.exit(app.exec())

