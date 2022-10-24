from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QGridLayout, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from argparse import ArgumentParser
import sys, glob, os
import pandas as pd
import numpy as np

app = None

class MyMainWindow(QMainWindow):
    def __init__(self, df, dfpath, image_dir, app,
                 shuffle=False):
        super().__init__()
        if shuffle:
            self.df = df.sample(frac=1).reset_index(drop=True)
        else:
            self.df = df

        self.dfpath = dfpath
        self.image_dir = image_dir
        self.app = app
        self.initUI()

    def initUI(self):
        self.resize(1600, 900)
        self.move(50, 50)
        central_widget = MyCentralWidget(self, self.app)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Inspector')
        self.statusBar().showMessage('Waiting...')

    def auto(self):
        self.central_widget.auto()

class MyCentralWidget(QWidget):

    def __init__(self, main_window, app):
        super().__init__()
        self.main_window = main_window
        self.idx = -1
        self.app = app
        self.initUI()

#  "aperiodic", "contact_rot", "dsct_bcep", "eclipse", "gdor_spb", "rrlyr_cepheid", "solarlike", "constant"
    def initUI(self):

        grbox = QGridLayout()

        keys = ['aperiodic', 'contact_rot', 'dsct_bcep', 'eclipse', 'gdor_spb', 'rrlyr_cepheid', 'solarlike', 'constant']
        for i, key in enumerate(keys):
            primary = QPushButton(f'P {key}', self)
            primary.clicked.connect(lambda checked, x=key: self.write_primary(x))
            grbox.addWidget(primary, 0, i)
 
            secondary = QPushButton(f'S {key}', self)
            secondary.clicked.connect(lambda checked, x=key: self.write_secondary(x))
            grbox.addWidget(secondary, 1, i)
        
        # Weirdness line input
        self.line = QLineEdit(self)
        grbox.addWidget(self.line, 0, len(keys)+1)

        # Additional boxes here
        skip_button = QPushButton('Next (&save)', self)
        skip_button.setShortcut('s')
        skip_button.clicked.connect(self.on_skip_button_clicked)
        grbox.addWidget(skip_button, 1, len(keys)+1)


        # define label
        self.label = QLabel(self)
        self.my_widget = MyWidget(self.label, self.main_window.df, self.main_window.image_dir)
 
        # place gridbox and label into vbox
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addLayout(grbox)
        self.setLayout(vbox)
        self.next_image()

    def next_image(self):

        self.idx += 1
        
        while len(self.main_window.df.loc[self.idx, 'Variability_type_WG_lc']) > 0:

            self.idx += 1

            if (self.idx in self.main_window.df.index) == False:
                print('Finished going through CSV file')
                print('If any unclassified targets remain, they may not have associated png files')
                sys.exit()

        id = self.main_window.df.loc[self.idx, 'TIC']
 
        self.psdfile = glob.glob(os.path.join(*[self.main_window.image_dir, f'{id}.png']))
         
        if len(self.psdfile)==0:
            self.my_widget.show_image(os.path.join(*[os.getcwd(),'failed.jpg']))
            mess = f"{id}.png not found, so I skipped it"
            print(mess)
            self.write_verdict(mess)
        else:
            self.my_widget.show_image(self.psdfile[0])

    # def on_psd_button_clicked(self):
    #     self.my_widget.show_image(self.psdfile[0])

    # def on_echelle_button_clicked(self):
    #     if len(self.echellefile) == 0:
    #         id = self.main_window.df.loc[self.idx].ID
    #         message = f'No echelle diagram for {id}'
    #         self.main_window.statusBar().showMessage(message)
    #     else:
    #         try:
    #             self.my_widget.show_image(self.echellefile[0])
    #         except:
    #             message = f'Failed to load echelle diagram for {id}'
    #             self.main_window.statusBar().showMessage(message)

 
    def on_skip_button_clicked(self):
        self.assignMulti()

         
        self.write_verdict('')
        self.line.clear()

    def write_primary(self, classification):
         
        self.main_window.df.at[self.idx, 'Variability_type_WG_lc'] = classification.upper()

    def write_secondary(self, classification):
         
        s = self.main_window.df.loc[self.idx, 'Variability_type_extra_lc']
        
        prim = self.main_window.df.at[self.idx, 'Variability_type_WG_lc']

        if classification.upper() in prim:
            self.main_window.statusBar().showMessage('Secondary cannot be same as primary. No secondary assigment made.')
            print('Secondary cannot be same as primary. No secondary assigment made.')

        if len(prim)>0:
            if (classification.upper() not in s) and (classification.upper() not in prim):
                s += f'+{classification}'
            

            if s.startswith('+'):
                s = s[1:]
            
            self.main_window.df.at[self.idx, 'Variability_type_extra_lc'] = s.upper()
        else:
            self.main_window.statusBar().showMessage('Assign primary variability first.')
            print('Assign primary variability first.')
        
      
    
    def assignMulti(self,):
        if len(self.main_window.df.loc[self.idx, 'Variability_type_extra_lc']) == 0:
            self.main_window.df.at[self.idx, 'Variability_multi_class_lc'] = 0
        else:
            self.main_window.df.at[self.idx, 'Variability_multi_class_lc'] = 1
    
 

    def write_verdict(self, mess):
        self.main_window.df.at[self.idx, 'TESS_LC_weirdness_lc'] = self.line.text()
        perc = '%i / %i' % (self.idx+1, len(self.main_window.df))
        self.main_window.statusBar().showMessage(perc + ' - ' + mess)
        self.main_window.df.to_csv(self.main_window.dfpath, index=False)

        if self.idx < len(self.main_window.df) - 1:
            self.next_image()
        else:
            self.main_window.statusBar().showMessage('Finished')
            sys.exit()

class MyWidget():
    def __init__(self, label, df, image_dir):
        self.label = label

    def show_image(self, sfile):
        pixmap = QPixmap(sfile)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

def main(df, dfpath, image_dir, shuffle=True):
    '''
    app must be defined already!!!
    '''
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    w = MyMainWindow(df, dfpath, image_dir, app, shuffle=shuffle)
    w.show()
    app.exit(app.exec_())

parser = ArgumentParser()
parser.add_argument('target_list', type=str)
parser.add_argument('image_dir', type=str)
parser.add_argument('--shuffle', action='store_true', dest='shuffle',
                    help="shuffle the list of targets")
parser.add_argument('--no-shuffle', action='store_false', dest='shuffle',
                    help="don't shuffle the list of targets (default)")
parser.set_defaults(feature=False)

if __name__ == "__main__":
    args = parser.parse_args()

    conv = {'TIC': str, 
            'Variability_type_WG_lc': str,
            'Variability_multi_class_lc': str,
            'Variability_type_extra_lc': str,
            'TESS_LC_weirdness_lc': str,
            'Variability_type_WG_sc': str,
            'Variability_multi_class_sc': str,	
            'Variability_type_extra_sc': str,	
            'TESS_LC_weirdness_sc': str,
            }
    try:
        df = pd.read_csv(args.target_list, converters=conv)
    except:
        df = pd.read_csv(args.target_list, converters=conv, delimiter=';')
        print('Who uses semi-colon as a delimiter, this is madness!')
        print('Output will be comma-separated.')

    if len(df) > 100:
        sys.setrecursionlimit(len(df))
 
    main(df, args.target_list, args.image_dir, shuffle=args.shuffle)




        # # Aperiodic
        # prim_aperiodic_button = QPushButton('P aperiodic', self)
        # prim_aperiodic_button.clicked.connect(self.prim_aperiodic_clicked)

        # sec_aperiodic_button = QPushButton('S aperiodic', self)
        # sec_aperiodic_button.clicked.connect(self.sec_aperiodic_clicked)

        # # Contact rotation
        # prim_contact_rot_button = QPushButton('P contact_rot', self)
        # prim_contact_rot_button.clicked.connect(self.prim_contact_rot_clicked)

        # sec_contact_rot_button = QPushButton('S contact_rot', self)
        # sec_contact_rot_button.clicked.connect(self.sec_contact_rot_clicked)

        # # dsct bcep
        # prim_dsct_bcep_button = QPushButton('P dsct_bcep', self)
        # prim_dsct_bcep_button.clicked.connect(self.prim_dsct_bcep_clicked)

        # sec_dsct_bcep_button = QPushButton('S dsct_bcep', self)
        # sec_dsct_bcep_button.clicked.connect(self.sec_dsct_bcep_clicked)

        # # ecplipse
        # prim_eclipse_button = QPushButton('P eclipse', self)
        # prim_eclipse_button.clicked.connect(self.prim_eclipse_clicked)

        # sec_eclipse_button = QPushButton('S eclipse', self)
        # sec_eclipse_button.clicked.connect(self.sec_eclipse_clicked)

        # # gdor spb
        # prim_gdor_spb_button = QPushButton('P gdor_spb', self)
        # prim_gdor_spb_button.clicked.connect(self.prim_gdor_spb_clicked)

        # sec_gdor_spb_button = QPushButton('S gdor_spb', self)
        # sec_gdor_spb_button.clicked.connect(self.sec_gdor_spb_clicked)

        # # rrlyr cepheid
        # prim_rrlyr_cepheid_button = QPushButton('P rrlyr_cepheid', self)
        # prim_rrlyr_cepheid_button.clicked.connect(self.prim_rrlyr_cepheid_clicked)

        # sec_rrlyr_cepheid_button = QPushButton('S rrlyr_cepheid', self)
        # sec_rrlyr_cepheid_button.clicked.connect(self.sec_rrlyr_cepheid_clicked)

        # # solarlike
        # prim_solarlike_button = QPushButton('P solarlike', self)
        # prim_solarlike_button.clicked.connect(self.prim_solarlike_clicked)

        # sec_solarlike_button = QPushButton('S solarlike', self)
        # sec_solarlike_button.clicked.connect(self.sec_solarlike_clicked)

        # # constant
        # prim_constant_button = QPushButton('P constant', self)
        # prim_constant_button.clicked.connect(self.prim_constant_clicked)

        # sec_constant_button = QPushButton('S constant', self)
        # sec_constant_button.clicked.connect(self.sec_constant_clicked)


        # echelle_button = QPushButton('&Echelle diagram', self)
        # echelle_button.setShortcut('e')
        # echelle_button.clicked.connect(self.on_echelle_button_clicked)
